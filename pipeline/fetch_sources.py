"""
Step 1: Fetch structured JSON sources
Downloads arf.json (OSINT Framework) and database.json (OSINT-Map)
"""

import json
import urllib.request
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SOURCES = {
    "arf.json": "https://raw.githubusercontent.com/lockfale/OSINT-Framework/master/public/arf.json",
    "osint_map.json": "https://raw.githubusercontent.com/Malfrats/OSINT-Map/main/database.json",
}

def fetch(name, url):
    print(f"Fetching {name}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out_path = os.path.join(OUTPUT_DIR, name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {out_path}")
        return data
    except Exception as e:
        print(f"  ERROR fetching {name}: {e}")
        return None

if __name__ == "__main__":
    for name, url in SOURCES.items():
        fetch(name, url)
    print("\nDone. Raw files saved to pipeline/raw/")
