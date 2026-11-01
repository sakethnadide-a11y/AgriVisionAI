from pathlib import Path
import shutil

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

QUARANTINE_DIR = DATASET_DIR / "class_quarantine"

CLASSES_TO_QUARANTINE = {
    ("Banana", "Yellow_Sigatoka"),
    ("Banana", "Panama_Disease"),
    ("Cabbage", "Bacterial_Spot_Rot"),
    ("Cabbage", "Downy_Mildew"),
    ("Cauliflower", "Healthy"),
    ("Rice", "Leaf_Smut"),
}

QUARANTINE_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("AGRI VISION AI - TINY CLASS QUARANTINE")
print("=" * 60)

total_moved = 0

log_file = DATASET_DIR / "tiny_class_quarantine_log.txt"

with open(log_file, "w", encoding="utf-8") as log:

    for crop, class_name in CLASSES_TO_QUARANTINE:

        source = DATASET_DIR / crop / class_name

        if not source.exists():
            print(f"\nNOT FOUND: {crop}/{class_name}")
            continue

        destination = (
            QUARANTINE_DIR / crop / class_name
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        count = sum(
            1 for f in source.rglob("*")
            if f.is_file()
        )

        print(f"\nQuarantining: {crop}/{class_name}")
        print(f"Images: {count}")

        try:
            shutil.move(
                str(source),
                str(destination)
            )

            total_moved += count

            log.write(
                f"MOVED: {source}\n"
                f"TO: {destination}\n"
                f"FILES: {count}\n"
                + "-" * 80 + "\n"
            )

        except Exception as e:

            print(f"ERROR: {e}")

            log.write(
                f"ERROR: {source}\n"
                f"{e}\n"
                + "-" * 80 + "\n"
            )


print("\n" + "=" * 60)
print("QUARANTINE COMPLETE")
print("=" * 60)

print(f"\nTotal files moved: {total_moved}")

print(f"\nQuarantine:")
print(QUARANTINE_DIR)

print("\nNothing was permanently deleted.")