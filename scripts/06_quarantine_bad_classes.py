from pathlib import Path
import shutil

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

QUARANTINE_DIR = DATASET_DIR / "class_quarantine"

# Classes that are not disease classes
CLASSES_TO_QUARANTINE = {
    ("Chilli", "Chili_Yellowish"),
    ("Chilli", "Chilli __Whitefly"),
    ("Pea", "Pea_Leafminner"),
    ("Tomato", "Tomato_Spider_Mites"),
}

QUARANTINE_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("AGRI VISION AI - BAD CLASS QUARANTINE")
print("=" * 60)

total_moved = 0

log_file = DATASET_DIR / "bad_class_quarantine_log.txt"

with open(log_file, "w", encoding="utf-8") as log:

    for crop, class_name in CLASSES_TO_QUARANTINE:

        source = DATASET_DIR / crop / class_name

        if not source.exists():

            print(
                f"\nNOT FOUND: {crop}/{class_name}"
            )

            continue

        destination = (
            QUARANTINE_DIR
            / crop
            / class_name
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"\nQuarantining:\n"
            f"  {crop}/{class_name}"
        )

        try:

            shutil.move(
                str(source),
                str(destination)
            )

            # Count images
            image_count = sum(
                1 for f in destination.rglob("*")
                if f.is_file()
            )

            total_moved += image_count

            log.write(
                f"MOVED: {source}\n"
                f"TO: {destination}\n"
                f"FILES: {image_count}\n"
                + "-" * 80
                + "\n"
            )

            print(
                f"  Images moved: {image_count}"
            )

        except Exception as e:

            print(f"  ERROR: {e}")

            log.write(
                f"ERROR: {source}\n"
                f"{e}\n"
                + "-" * 80
                + "\n"
            )


print("\n" + "=" * 60)
print("QUARANTINE COMPLETE")
print("=" * 60)

print(f"\nTotal files moved: {total_moved:,}")

print("\nQuarantine folder:")
print(QUARANTINE_DIR)

print("\nLog:")
print(log_file)

print("\nNothing was permanently deleted.")