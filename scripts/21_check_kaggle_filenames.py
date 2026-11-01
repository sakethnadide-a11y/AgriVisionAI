from pathlib import Path
import re

ROOT = Path(r"datasets/AgriVisionAI_Split")

bad = []

for path in ROOT.rglob("*"):
    if path.is_file():
        # Check for whitespace immediately before the extension
        if re.search(r"\s+\.[^.]+$", path.name):
            bad.append(str(path))

print("================================")
print("KAGGLE FILENAME CHECK")
print("================================")
print(f"Problematic filenames: {len(bad)}")

if bad:
    print("\nExamples:")
    for item in bad[:20]:
        print(item)
else:
    print("✅ No problematic filenames found.")