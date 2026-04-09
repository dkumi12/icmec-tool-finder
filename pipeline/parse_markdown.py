"""
Step 2: Parse awesome-list markdown files into raw JSON
Extracts [Tool Name](url) - description patterns
"""

import re
import json
import urllib.request
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MARKDOWN_SOURCES = {
    "awesome_osint": "https://raw.githubusercontent.com/jivoi/awesome-osint/master/README.md",
    "awesome_forensics": "https://raw.githubusercontent.com/cugu/awesome-forensics/master/README.md",
    "dark_web_osint": "https://raw.githubusercontent.com/apurvsinghgautam/dark-web-osint-tools/master/README.md",
    "blockchain_osint": "https://raw.githubusercontent.com/aaarghhh/awesome_osint_blockchain_analysis/main/README.md",
    "awesome_incident": "https://raw.githubusercontent.com/meirwah/awesome-incident-response/master/README.md",
}

# Category detection from markdown headings
CATEGORY_KEYWORDS = {
    "OSINT": ["osint", "reconnaissance", "intelligence", "search engine", "username", "email", "phone", "social media"],
    "Forensics": ["forensic", "disk", "memory", "evidence", "artifact", "recover", "acquisition"],
    "Crypto": ["bitcoin", "crypto", "blockchain", "wallet", "transaction", "chain"],
    "Dark Web": ["dark web", "tor", "onion", "deep web", "hidden service"],
    "Threat Intel": ["threat", "malware", "ioc", "indicator", "cti", "sandbox"],
    "CSAM": ["csam", "child", "exploitation", "abuse", "grooming", "trafficking"],
}

def detect_category(text, current_heading=""):
    combined = (text + " " + current_heading).lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return cat
    return "OSINT"  # default

def parse_markdown(content, source_name):
    tools = []
    lines = content.split("\n")
    current_heading = ""

    for line in lines:
        # Track headings for context
        heading_match = re.match(r"^#{1,3}\s+(.+)", line)
        if heading_match:
            current_heading = heading_match.group(1).strip()
            continue

        # Match: - [Tool Name](url) - optional description
        link_match = re.match(
            r"[-*]\s+\[([^\]]+)\]\((https?://[^\)]+)\)[\s\-:]*(.*)$", line
        )
        if link_match:
            name = link_match.group(1).strip()
            url = link_match.group(2).strip()
            desc = link_match.group(3).strip()

            # Skip if name is just punctuation or very short
            if len(name) < 2:
                continue

            tools.append({
                "name": name,
                "url": url,
                "description": desc if desc else "",
                "subcategory": current_heading,
                "category": detect_category(name + " " + desc, current_heading),
                "source": source_name,
            })

    return tools

def fetch_and_parse(name, url):
    print(f"Fetching & parsing {name}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
        tools = parse_markdown(content, name)
        out_path = os.path.join(OUTPUT_DIR, f"{name}_parsed.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(tools, f, indent=2, ensure_ascii=False)
        print(f"  Extracted {len(tools)} tools -> {out_path}")
        return tools
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

if __name__ == "__main__":
    total = 0
    for name, url in MARKDOWN_SOURCES.items():
        tools = fetch_and_parse(name, url)
        total += len(tools)
    print(f"\nTotal tools parsed from markdown: {total}")
