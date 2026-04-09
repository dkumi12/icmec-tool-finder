"""
Step 3: Merge all raw sources into unified tools.json
Deduplicates by URL, normalises schema, outputs src/data/tools.json
"""

import json
import os
import re
import uuid

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "tools.json")

SKILL_KEYWORDS = {
    "beginner": ["web", "online", "browser", "search", "lookup", "check"],
    "advanced": ["cli", "python", "command", "install", "terminal", "script", "api", "framework"],
}

PLATFORM_KEYWORDS = {
    "cli": ["cli", "command line", "terminal", "python", "install", "pip ", "git clone"],
    "web": ["web", "online", "browser", "www", "http"],
    "api": ["api", "endpoint", "rest", "json response"],
    "desktop": ["windows", "linux", "macos", "download", "exe", "install"],
    "browser-extension": ["extension", "addon", "chrome", "firefox"],
}

INVESTIGATION_TYPE_KEYWORDS = {
    "CSAM detection": ["csam", "child sexual", "abuse material", "photodna", "hash match", "exploitation"],
    "online grooming": ["grooming", "predator", "minor", "child protection", "coercion"],
    "crypto tracing": ["bitcoin", "crypto", "blockchain", "wallet", "transaction", "chainalysis", "elliptic"],
    "dark web": ["dark web", "tor", "onion", "deep web", ".onion"],
    "trafficking": ["trafficking", "human trafficking", "smuggling"],
    "sextortion": ["sextortion", "image-based", "non-consensual"],
    "cross-border": ["interpol", "europol", "international", "cross-border", "jurisdiction"],
    "social media investigation": ["social media", "facebook", "instagram", "twitter", "username", "profile"],
    "digital forensics": ["forensic", "evidence", "artifact", "disk", "memory", "recover"],
    "threat intelligence": ["threat", "malware", "ioc", "indicator", "sandbox", "virus"],
}

def detect_platform(text):
    text_lower = text.lower()
    for platform, keywords in PLATFORM_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return platform
    return "web"

def detect_skill(text, platform):
    if platform == "cli":
        return "intermediate"
    text_lower = text.lower()
    for level, keywords in SKILL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return level
    return "intermediate"

def detect_investigation_types(text):
    text_lower = text.lower()
    types = []
    for inv_type, keywords in INVESTIGATION_TYPE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            types.append(inv_type)
    return types if types else ["social media investigation"]

def make_id(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{slug}-{str(uuid.uuid4())[:4]}"

def normalise(entry, source="unknown"):
    """Convert any raw entry format to unified schema."""
    name = entry.get("name", "").strip()
    url = entry.get("url", "").strip()
    description = entry.get("description", "").strip()
    category = entry.get("category", "OSINT")
    subcategory = entry.get("subcategory", "")

    if not name or not url:
        return None

    combined_text = f"{name} {description} {subcategory}"
    platform = detect_platform(combined_text)
    skill = detect_skill(combined_text, platform)
    inv_types = detect_investigation_types(combined_text)

    pricing = entry.get("pricing", "free")
    if not pricing or pricing not in ["free", "freemium", "paid"]:
        pricing = "free"

    return {
        "id": make_id(name),
        "name": name,
        "url": url,
        "description": description,
        "category": category,
        "subcategory": subcategory,
        "pricing": pricing,
        "platform": platform,
        "skillLevel": skill,
        "investigationTypes": inv_types,
        "input": entry.get("input", ""),
        "output": entry.get("output", ""),
        "opsec": entry.get("opsec", "active"),
        "requiresRegistration": entry.get("requiresRegistration", entry.get("registration", False)),
        "hasAPI": entry.get("hasAPI", entry.get("api", False)),
        "localInstall": entry.get("localInstall", platform == "cli"),
        "legalNotes": entry.get("legalNotes", ""),
        "tags": entry.get("tags", []),
        "source": source,
    }

def parse_arf(data):
    """Recursively extract tools from arf.json tree structure."""
    tools = []
    if isinstance(data, dict):
        if "name" in data and "url" in data and data.get("type") == "url":
            tools.append(data)
        else:
            for v in data.values():
                tools.extend(parse_arf(v))
    elif isinstance(data, list):
        for item in data:
            tools.extend(parse_arf(item))
    return tools

def parse_osint_map(data):
    """Extract tools from OSINT-Map nested category structure."""
    tools = []
    EMOJI_PRICING = {"🪙": "paid", "💵": "paid"}

    def recurse(node, parent_category="OSINT"):
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and value.startswith("http"):
                    # It's a tool entry: key = "emoji name", value = url
                    name = re.sub(r"[^\w\s\-\(\)]", "", key).strip()
                    pricing = "free"
                    for emoji, price in EMOJI_PRICING.items():
                        if emoji in key:
                            pricing = price
                            break
                    tools.append({
                        "name": name,
                        "url": value,
                        "description": "",
                        "category": parent_category,
                        "pricing": pricing,
                    })
                elif isinstance(value, dict):
                    recurse(value, key)
    recurse(data)
    return tools

def load_json_file(filename):
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        print(f"  Skipping {filename} (not found — run fetch_sources.py first)")
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def merge():
    all_tools = []
    seen_urls = set()

    # --- arf.json ---
    arf_data = load_json_file("arf.json")
    if arf_data:
        raw = parse_arf(arf_data)
        print(f"arf.json: {len(raw)} raw entries")
        for entry in raw:
            t = normalise(entry, "arf")
            if t and t["url"] not in seen_urls:
                seen_urls.add(t["url"])
                all_tools.append(t)

    # --- osint_map.json ---
    map_data = load_json_file("osint_map.json")
    if map_data:
        raw = parse_osint_map(map_data)
        print(f"osint_map.json: {len(raw)} raw entries")
        for entry in raw:
            t = normalise(entry, "osint_map")
            if t and t["url"] not in seen_urls:
                seen_urls.add(t["url"])
                all_tools.append(t)

    # --- Additional curated tools (crypto, dark web, Africa) ---
    extra_path = os.path.join(os.path.dirname(__file__), "add_missing_tools.json")
    if os.path.exists(extra_path):
        with open(extra_path, encoding="utf-8") as f:
            extra_data = json.load(f)
        print(f"add_missing_tools.json: {len(extra_data)} curated entries")
        for entry in extra_data:
            entry["id"] = make_id(entry["name"])
            entry.setdefault("source", "curated")
            if entry.get("url") not in seen_urls:
                seen_urls.add(entry["url"])
                all_tools.append(entry)

    # --- ICMEC curated tools (manually verified) ---
    icmec_path = os.path.join(os.path.dirname(__file__), "icmec_tools.json")
    if os.path.exists(icmec_path):
        with open(icmec_path, encoding="utf-8") as f:
            icmec_data = json.load(f)
        print(f"icmec_tools.json: {len(icmec_data)} curated entries")
        for entry in icmec_data:
            entry["id"] = make_id(entry["name"])
            entry.setdefault("source", "icmec_curated")
            if entry.get("url") not in seen_urls:
                seen_urls.add(entry["url"])
                all_tools.append(entry)

    # --- Parsed markdown files ---
    for fname in os.listdir(RAW_DIR):
        if fname.endswith("_parsed.json"):
            source_name = fname.replace("_parsed.json", "")
            data = load_json_file(fname)
            if data:
                print(f"{fname}: {len(data)} raw entries")
                for entry in data:
                    t = normalise(entry, source_name)
                    if t and t["url"] not in seen_urls:
                        seen_urls.add(t["url"])
                        all_tools.append(t)

    # Sort by category then name
    all_tools.sort(key=lambda x: (x["category"], x["name"].lower()))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_tools, f, indent=2, ensure_ascii=False)

    print(f"\nMerged {len(all_tools)} unique tools -> {OUTPUT_PATH}")

    # Stats
    from collections import Counter
    cats = Counter(t["category"] for t in all_tools)
    print("\nBy category:")
    for cat, count in cats.most_common():
        cat_safe = cat.encode("ascii", errors="replace").decode("ascii")
        print(f"  {cat_safe}: {count}")

if __name__ == "__main__":
    merge()
