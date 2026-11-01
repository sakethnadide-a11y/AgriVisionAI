from pathlib import Path
import re

ROOT = Path(r"datasets/AgriVisionAI_Split")

renamed = 0
conflicts = 0

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    old_name = path.name

    # Remove spaces/tabs before the file extension
    new_name = re.sub(r"\s+\.", ".", old_name)

    # Remove leading/trailing whitespace from the filename
    new_name = new_name.strip()

    if new_name == old_name:
        continue

    new_path = path.with_name(new_name)

    # Never overwrite another file
    if new_path.exists():
        print(f"CONFLICT: {path}")
        print(f"       -> {new_path}")
        conflicts += 1
        continue

    path.rename(new_path)
    renamed += 1

print()
print("================================")
print("FILENAME CLEANUP COMPLETE")
print("================================")
print(f"Files renamed : {renamed}")
print(f"Conflicts     : {conflicts}")

if conflicts == 0:
    print("No filename conflicts found.")
else:
    print("WARNING: Some files could not be renamed.")