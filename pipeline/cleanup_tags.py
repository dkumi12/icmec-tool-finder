"""
Pass 2: Tag cleanup script
Fixes known false positives from Mistral tagging
and protects manually curated tools from bad overwrites.
Run after tag_with_bedrock.py completes.

Usage: python pipeline/cleanup_tags.py
"""

import json
import os
from collections import Counter

TOOLS_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "tools.json")
PUBLIC_PATH = os.path.join(os.path.dirname(__file__), "..", "public", "data", "tools.json")

# Sources that were manually curated — never touch their tags
PROTECTED_SOURCES = {"icmec_curated", "curated"}

# Keywords in name/description that should NEVER get crypto tracing tag
# (Mistral confuses "certificate", "encrypt", "hash" with crypto)
CRYPTO_FALSE_POSITIVE_KEYWORDS = [
    "certificate", "ssl", "tls", "x509", "encryption",
    "hash", "md5", "sha", "pgp", "gpg", "password",
    "imessage", "message", "email", "archive", "cache",
    "military", "airbase", "satellite", "map", "geo",
    "image", "photo", "video", "face", "reverse",
    "whois", "dns", "domain", "ip address", "subnet",
    "social media", "linkedin", "facebook", "twitter",
    "instagram", "reddit", "telegram", "discord",
]

# Keywords that SHOULD trigger crypto tracing
CRYPTO_TRUE_KEYWORDS = [
    "bitcoin", "ethereum", "blockchain", "wallet", "crypto",
    "transaction", "on-chain", "defi", "token", "coin",
    "chainalysis", "elliptic", "trm", "breadcrumbs",
    "blockchair", "etherscan", "monero", "ltc", "usdt",
]

# Keywords that should trigger dark web
DARK_WEB_KEYWORDS = [
    "tor", "onion", ".onion", "dark web", "darkweb",
    "hidden service", "deep web", "ahmia", "torbrowser",
]

# Keywords that should trigger CSAM detection
CSAM_KEYWORDS = [
    "csam", "child abuse", "child sexual", "photodna",
    "hash match", "exploitation material", "ncmec",
    "project vic", "griffeye", "caid",
]

def should_have_crypto(tool):
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    return any(kw in text for kw in CRYPTO_TRUE_KEYWORDS)

def has_false_positive_crypto(tool):
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    return any(kw in text for kw in CRYPTO_FALSE_POSITIVE_KEYWORDS)

def fix_crypto_tags(tool):
    types = tool.get("investigationTypes", [])
    if "crypto tracing" not in types:
        return types

    # Has crypto tag — is it legitimate?
    if should_have_crypto(tool):
        return types  # keep it
    if has_false_positive_crypto(tool):
        return [t for t in types if t != "crypto tracing"]  # remove it
    return types

def ensure_dark_web_tag(tool):
    types = tool.get("investigationTypes", [])
    text = (tool.get("name", "") + " " + tool.get("description", "") + " " + tool.get("category", "")).lower()
    if any(kw in text for kw in DARK_WEB_KEYWORDS) and "dark web" not in types:
        types = types + ["dark web"]
    return types

def ensure_csam_tag(tool):
    types = tool.get("investigationTypes", [])
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    if any(kw in text for kw in CSAM_KEYWORDS) and "CSAM detection" not in types:
        types = types + ["CSAM detection"]
    return types

def main():
    with open(TOOLS_PATH, encoding="utf-8") as f:
        tools = json.load(f)

    crypto_fixed = 0
    dark_web_added = 0
    csam_added = 0
    protected = 0

    for tool in tools:
        if tool.get("source") in PROTECTED_SOURCES:
            protected += 1
            continue

        original = tool.get("investigationTypes", [])

        # Fix false positive crypto tags
        fixed = fix_crypto_tags(tool)
        if fixed != original:
            crypto_fixed += 1

        # Ensure dark web tools are tagged
        fixed = ensure_dark_web_tag({**tool, "investigationTypes": fixed})
        if len(fixed) > len(tool.get("investigationTypes", [])):
            dark_web_added += 1

        # Ensure CSAM tools are tagged
        fixed = ensure_csam_tag({**tool, "investigationTypes": fixed})
        if len(fixed) > len(tool.get("investigationTypes", [])):
            csam_added += 1

        tool["investigationTypes"] = fixed

    # Save
    for path in [TOOLS_PATH, PUBLIC_PATH]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tools, f, indent=2, ensure_ascii=False)

    print(f"Cleanup complete:")
    print(f"  Protected (skipped):        {protected}")
    print(f"  Crypto false positives fixed: {crypto_fixed}")
    print(f"  Dark web tags added:          {dark_web_added}")
    print(f"  CSAM tags added:              {csam_added}")
    print(f"  Saved to: {TOOLS_PATH}")

    # Quick stats
    from collections import Counter
    all_types = []
    for t in tools:
        all_types.extend(t.get("investigationTypes", []))
    print(f"\nInvestigation type coverage:")
    for inv_type, count in Counter(all_types).most_common():
        print(f"  {inv_type}: {count} tools")

if __name__ == "__main__":
    main()
