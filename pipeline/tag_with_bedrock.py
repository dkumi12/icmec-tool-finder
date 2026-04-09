"""
AI-assisted batch tagger using AWS Bedrock (Claude 3 Haiku)
Tags every tool in tools.json with investigationTypes based on name + description.

Usage:
  pip install boto3 python-dotenv
  python pipeline/tag_with_bedrock.py

Needs a .env file in the project root with:
  AWS_ACCESS_KEY_ID=...
  AWS_SECRET_ACCESS_KEY=...
  AWS_REGION=us-east-1
  AWS_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
"""

import json
import os
import time
import boto3
from dotenv import load_dotenv

# Load credentials from .env in project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TOOLS_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "tools.json")
PUBLIC_TOOLS_PATH = os.path.join(os.path.dirname(__file__), "..", "public", "data", "tools.json")

INVESTIGATION_TYPES = [
    "CSAM detection",
    "online grooming",
    "crypto tracing",
    "dark web",
    "trafficking",
    "sextortion",
    "cross-border",
    "social media investigation",
    "digital forensics",
    "threat intelligence",
]

MODEL_ID = os.getenv("AWS_MODEL_ID", "mistral.mistral-small-2402-v1:0")
REGION   = os.getenv("AWS_REGION", "us-east-1")

# Tools that already have good manual tags — skip them
SKIP_SOURCES = {"icmec_curated", "curated"}

# Only tag tools missing investigation types OR only tagged with the default
def needs_tagging(tool):
    if tool.get("source") in SKIP_SOURCES:
        return False
    types = tool.get("investigationTypes", [])
    # Only has the default catch-all tag
    if types == ["social media investigation"]:
        return True
    # Empty
    if not types:
        return True
    return False

def build_prompt(tool):
    return f"""You are helping classify investigative tools for a child protection platform used by law enforcement.

Tool name: {tool['name']}
Description: {tool.get('description', 'N/A')}
Category: {tool.get('category', 'N/A')}
Subcategory: {tool.get('subcategory', 'N/A')}

From this list, select ALL that apply to this tool:
{json.dumps(INVESTIGATION_TYPES)}

Rules:
- Only choose types genuinely relevant to this tool
- Most tools will match 1-3 types
- Generic tools (search engines, note-taking, etc.) should get ["social media investigation"] or ["digital forensics"] only
- CSAM tools must actually relate to child abuse material detection
- Reply with ONLY a valid JSON array, nothing else. Example: ["digital forensics", "social media investigation"]"""

def parse_response(text):
    """Extract JSON array from model response."""
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        result = json.loads(text[start:end+1])
        # Validate against known types
        valid = [t for t in result if t in INVESTIGATION_TYPES]
        return valid if valid else None
    except Exception:
        return None

def call_bedrock(client, prompt):
    if "mistral" in MODEL_ID:
        payload = {
            "prompt": f"<s>[INST] {prompt} [/INST]",
            "max_tokens": 100,
            "temperature": 0.1,
        }
    elif "claude" in MODEL_ID:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        }
    elif "llama" in MODEL_ID or "meta" in MODEL_ID:
        payload = {
            "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "temperature": 0.1,
            "max_gen_len": 100,
        }
    else:
        payload = {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 100,
            "temperature": 0.1,
        }

    response = client.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )
    body = json.loads(response["body"].read())

    if "mistral" in MODEL_ID:
        return body["outputs"][0]["text"]
    elif "claude" in MODEL_ID:
        return body["content"][0]["text"]
    elif "llama" in MODEL_ID or "meta" in MODEL_ID:
        return body["generation"]
    else:
        return body.get("completion", "")

def main():
    # Check credentials
    access_key = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("VITE_AWS_ACCESS_KEY")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("VITE_AWS_SECRET_KEY")

    if not access_key or not secret_key:
        print("ERROR: AWS credentials not found.")
        print("Create a .env file in E:\\Projects\\icmec-tool-finder\\ with:")
        print("  AWS_ACCESS_KEY_ID=your_key")
        print("  AWS_SECRET_ACCESS_KEY=your_secret")
        print("  AWS_REGION=us-east-1")
        return

    client = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    # Load tools
    with open(TOOLS_PATH, encoding="utf-8") as f:
        tools = json.load(f)

    to_tag = [t for t in tools if needs_tagging(t)]
    already_tagged = len(tools) - len(to_tag)

    print(f"Total tools: {len(tools)}")
    print(f"Already well-tagged (skipping): {already_tagged}")
    print(f"Need tagging: {len(to_tag)}")
    print(f"Model: {MODEL_ID}\n")

    tagged_count = 0
    error_count = 0
    BATCH_SIZE = 50  # Save progress every 50 tools

    for i, tool in enumerate(to_tag):
        try:
            prompt = build_prompt(tool)
            response_text = call_bedrock(client, prompt)
            types = parse_response(response_text)

            if types:
                # Update in the main tools list
                for t in tools:
                    if t["id"] == tool["id"]:
                        t["investigationTypes"] = types
                        break
                tagged_count += 1
                print(f"[{i+1}/{len(to_tag)}] {tool['name'][:40]:<40} -> {types}")
            else:
                print(f"[{i+1}/{len(to_tag)}] {tool['name'][:40]:<40} -> PARSE ERROR: {response_text[:60]}")
                error_count += 1

            # Save progress every BATCH_SIZE tools
            if (i + 1) % BATCH_SIZE == 0:
                _save(tools)
                print(f"\n  Progress saved ({i+1}/{len(to_tag)} processed)\n")

            # Rate limiting — Claude Haiku can handle ~50 req/min on Bedrock
            time.sleep(0.3)

        except Exception as e:
            print(f"[{i+1}/{len(to_tag)}] ERROR on {tool['name']}: {e}")
            error_count += 1
            time.sleep(2)  # Back off on error

    # Final save
    _save(tools)
    print(f"\nDone!")
    print(f"  Tagged:   {tagged_count}")
    print(f"  Errors:   {error_count}")
    print(f"  Saved to: {TOOLS_PATH}")

def _save(tools):
    for path in [TOOLS_PATH, PUBLIC_TOOLS_PATH]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tools, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
