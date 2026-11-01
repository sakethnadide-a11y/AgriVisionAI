from pathlib import Path
import shutil

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

REPORT = DATASET_DIR / "cross_class_exact_conflicts.txt"

QUARANTINE_DIR = (
    DATASET_DIR / "cross_class_quarantine"
)

QUARANTINE_DIR.mkdir(exist_ok=True)


print("=" * 60)
print("AGRI VISION AI - EXACT CROSS-CLASS CONFLICT CLEANER")
print("=" * 60)


if not REPORT.exists():
    print("\nERROR: cross_class_exact_conflicts.txt not found.")
    exit()


# ---------------------------------------------------------
# Read all conflicting files
# ---------------------------------------------------------

files = set()

with open(
    REPORT,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if line.startswith("FILE 1 :"):
            path = line.replace(
                "FILE 1 :", ""
            ).strip()

            files.add(Path(path))

        elif line.startswith("FILE 2 :"):
            path = line.replace(
                "FILE 2 :", ""
            ).strip()

            files.add(Path(path))


print(
    f"\nUnique conflicting files found: "
    f"{len(files):,}"
)


# ---------------------------------------------------------
# Move conflicting files
# ---------------------------------------------------------

moved = 0
missing = 0
failed = 0

log_file = (
    DATASET_DIR /
    "cross_class_quarantine_log.txt"
)


with open(
    log_file,
    "w",
    encoding="utf-8"
) as log:

    for source in sorted(
        files,
        key=lambda x: str(x)
    ):

        if not source.exists():

            missing += 1

            log.write(
                f"NOT FOUND: {source}\n"
            )

            continue


        try:

            relative = source.relative_to(
                DATASET_DIR
            )

            destination = (
                QUARANTINE_DIR / relative
            )

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            # Avoid overwriting
            if destination.exists():

                counter = 1

                while True:

                    destination = (
                        destination.parent
                        /
                        f"{destination.stem}"
                        f"_conflict_{counter}"
                        f"{destination.suffix}"
                    )

                    if not destination.exists():
                        break

                    counter += 1


            shutil.move(
                str(source),
                str(destination)
            )

            moved += 1

            log.write(
                f"MOVED: {source}\n"
                f"TO: {destination}\n"
                + "-" * 80
                + "\n"
            )


        except Exception as e:

            failed += 1

            log.write(
                f"FAILED: {source}\n"
                f"ERROR: {e}\n"
                + "-" * 80
                + "\n"
            )


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(
    f"\nConflicting files identified : "
    f"{len(files):,}"
)

print(
    f"Files moved to quarantine     : "
    f"{moved:,}"
)

print(
    f"Files already missing        : "
    f"{missing:,}"
)

print(
    f"Move failures                : "
    f"{failed:,}"
)

print("\nQuarantine:")
print(QUARANTINE_DIR)

print("\nLog:")
print(log_file)

print("\nIMPORTANT:")
print("Only exact cross-class conflicts were moved.")
print("Distance 2, 4 and 6 conflicts were NOT touched.")
print("Nothing was permanently deleted.")

print("\nDone.")