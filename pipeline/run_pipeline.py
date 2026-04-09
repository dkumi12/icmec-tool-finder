"""
Master script — runs the full pipeline in one command:
  python pipeline/run_pipeline.py
"""

import subprocess
import sys
import os

PIPELINE_DIR = os.path.dirname(__file__)

steps = [
    ("Step 1: Fetching JSON sources", os.path.join(PIPELINE_DIR, "fetch_sources.py")),
    ("Step 2: Parsing markdown sources", os.path.join(PIPELINE_DIR, "parse_markdown.py")),
    ("Step 3: Merging into tools.json", os.path.join(PIPELINE_DIR, "merge.py")),
]

for label, script in steps:
    print(f"\n{'='*50}")
    print(f" {label}")
    print('='*50)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"\nERROR in {script}. Stopping pipeline.")
        sys.exit(1)

print("\n✅ Pipeline complete! src/data/tools.json is ready.")
