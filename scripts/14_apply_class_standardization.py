from pathlib import Path
import importlib.util
import uuid

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

# Load the RENAMES dictionary from script 13
script_path = Path(__file__).parent / "13_standardize_classes.py"

spec = importlib.util.spec_from_file_location(
    "standardization_preview",
    script_path
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAMES = module.RENAMES


print("=" * 60)
print("AGRI VISION AI - APPLY CLASS STANDARDIZATION")
print("=" * 60)

print(f"\nMappings: {len(RENAMES)}")

# ---------------------------------------------------------
# Collect existing folders
# ---------------------------------------------------------

operations = []

for (crop, old_name), new_name in RENAMES.items():

    old_path = DATASET_DIR / crop / old_name
    new_path = DATASET_DIR / crop / new_name

    if not old_path.exists():
        print(
            f"\nSKIP - not found: "
            f"{crop}/{old_name}"
        )
        continue

    if old_path == new_path:
        continue

    if new_path.exists():
        print(
            f"\nERROR - destination already exists:"
            f"\n  {new_path}"
        )
        raise SystemExit(
            "Rename cancelled to prevent data loss."
        )

    operations.append(
        (old_path, new_path)
    )


print(
    f"\nFolders ready to rename: "
    f"{len(operations)}"
)

# ---------------------------------------------------------
# Two-phase rename
# This prevents Windows name collisions
# ---------------------------------------------------------

temporary_operations = []

print("\nPhase 1: Creating temporary names...")

for old_path, new_path in operations:

    temp_path = (
        old_path.parent
        /
        f"__TEMP__{uuid.uuid4().hex}"
    )

    old_path.rename(temp_path)

    temporary_operations.append(
        (temp_path, new_path, old_path)
    )


print("Phase 1 complete.")

print("\nPhase 2: Applying standardized names...")

renamed = 0

for temp_path, new_path, original_path in temporary_operations:

    temp_path.rename(new_path)

    renamed += 1

    print(
        f"{original_path.parent.name}/"
        f"{original_path.name}"
        f"  ->  "
        f"{new_path.name}"
    )


print("\n" + "=" * 60)
print("STANDARDIZATION COMPLETE")
print("=" * 60)

print(
    f"\nFolders renamed: {renamed}"
)

print("\nExample structure:")

print("""
Tomato/
    Healthy/
    Early_Blight/
    Late_Blight/

Wheat/
    Healthy/
    Leaf_Rust/
    Stem_Rust/
""")

print("\nImages were NOT changed.")
print("Only folder names were standardized.")

print("\nDone.")