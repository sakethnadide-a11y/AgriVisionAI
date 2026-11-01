from pathlib import Path
import shutil

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

DUPLICATE_REPORT = DATASET_DIR / "exact_duplicates.txt"

# Files will be moved here, NOT deleted
QUARANTINE_DIR = DATASET_DIR / "duplicate_quarantine"

QUARANTINE_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("AGRI VISION AI - SAFE EXACT DUPLICATE CLEANER")
print("=" * 60)

if not DUPLICATE_REPORT.exists():
    print("\nERROR: exact_duplicates.txt was not found.")
    print(DUPLICATE_REPORT)
    exit()

# Read duplicate report
with open(DUPLICATE_REPORT, "r", encoding="utf-8") as f:
    lines = f.readlines()

groups = []
current_group = []

for line in lines:

    line = line.strip()

    if line.startswith("DUPLICATE GROUP"):

        if current_group:
            groups.append(current_group)

        current_group = []

    elif line.startswith("C:\\"):

        current_group.append(Path(line))

if current_group:
    groups.append(current_group)


same_class_groups = 0
cross_class_groups = 0

files_to_move = []
cross_class_records = []

for group in groups:

    if len(group) < 2:
        continue

    # Class = parent folder
    classes = [file.parent.name for file in group]

    unique_classes = set(classes)

    if len(unique_classes) == 1:

        # Same class -> safe to keep first and quarantine the rest
        same_class_groups += 1

        keep = group[0]
        duplicates = group[1:]

        for duplicate in duplicates:
            files_to_move.append((duplicate, keep))

    else:

        # Different classes -> DO NOT TOUCH
        cross_class_groups += 1

        cross_class_records.append(group)


print(f"\nDuplicate groups found       : {len(groups):,}")
print(f"Same-class duplicate groups  : {same_class_groups:,}")
print(f"Cross-class duplicate groups : {cross_class_groups:,}")
print(f"Files to quarantine          : {len(files_to_move):,}")


# ---------------------------------------------------------
# Move same-class duplicates
# ---------------------------------------------------------

moved = 0
failed = 0

print("\nMoving same-class duplicates...")
print("Nothing will be permanently deleted.\n")

move_log = DATASET_DIR / "duplicate_move_log.txt"

with open(move_log, "w", encoding="utf-8") as log:

    for duplicate, keep in files_to_move:

        if not duplicate.exists():
            continue

        # Preserve original class structure
        relative_class = duplicate.parent.relative_to(DATASET_DIR)

        destination_dir = QUARANTINE_DIR / relative_class
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination = destination_dir / duplicate.name

        # Avoid overwriting
        if destination.exists():
            counter = 1

            while True:
                destination = (
                    destination_dir
                    / f"{duplicate.stem}_duplicate_{counter}{duplicate.suffix}"
                )

                if not destination.exists():
                    break

                counter += 1

        try:

            shutil.move(str(duplicate), str(destination))

            moved += 1

            log.write(
                f"MOVED: {duplicate}\n"
                f"KEPT : {keep}\n"
                f"TO   : {destination}\n"
                + "-" * 80
                + "\n"
            )

        except Exception as e:

            failed += 1

            log.write(
                f"FAILED: {duplicate}\n"
                f"ERROR : {e}\n"
                + "-" * 80
                + "\n"
            )


# ---------------------------------------------------------
# Save cross-class conflicts
# ---------------------------------------------------------

conflict_report = DATASET_DIR / "cross_class_duplicates.txt"

with open(conflict_report, "w", encoding="utf-8") as f:

    if cross_class_records:

        for number, group in enumerate(
            cross_class_records, start=1
        ):

            f.write("=" * 80 + "\n")
            f.write(f"CROSS-CLASS DUPLICATE GROUP {number}\n")
            f.write("=" * 80 + "\n")

            for file in group:
                f.write(f"{file}\n")

            f.write("\n")

    else:

        f.write("No cross-class duplicate groups found.\n")


print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"\nFiles moved to quarantine : {moved:,}")
print(f"Move failures            : {failed:,}")

print("\nQuarantine folder:")
print(QUARANTINE_DIR)

print("\nMove log:")
print(move_log)

print("\nCross-class conflicts:")
print(conflict_report)

print("\nIMPORTANT:")
print("No files were permanently deleted.")