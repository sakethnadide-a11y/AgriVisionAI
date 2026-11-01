from pathlib import Path
import csv

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png",
    ".bmp", ".webp",
    ".tif", ".tiff"
}

IGNORED_FOLDERS = {
    "duplicate_quarantine",
    "class_quarantine",
    "cross_class_quarantine"
}

rows = []

for crop_dir in sorted(DATASET_DIR.iterdir()):

    if not crop_dir.is_dir():
        continue

    if crop_dir.name in IGNORED_FOLDERS:
        continue

    for class_dir in sorted(crop_dir.iterdir()):

        if not class_dir.is_dir():
            continue

        count = sum(
            1
            for file in class_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            )
        )

        if count > 0:
            rows.append(
                (crop_dir.name, class_dir.name, count)
            )


total_images = sum(x[2] for x in rows)
total_classes = len(rows)
total_crops = len(set(x[0] for x in rows))

print("=" * 70)
print("AGRI VISION AI - FINAL CLASS BALANCE")
print("=" * 70)

print(f"\nCrops   : {total_crops}")
print(f"Classes : {total_classes}")
print(f"Images  : {total_images:,}")

print("\n" + "-" * 70)
print("ALL CLASSES")
print("-" * 70)

for crop, class_name, count in rows:

    print(
        f"{crop:18} "
        f"{class_name:40} "
        f"{count:6,}"
    )


print("\n" + "-" * 70)
print("CLASSES BELOW 100 IMAGES")
print("-" * 70)

small = [
    row for row in rows
    if row[2] < 100
]

if small:

    for crop, class_name, count in small:

        print(
            f"{crop:18} "
            f"{class_name:40} "
            f"{count:6,}"
        )

else:
    print("None")


print("\n" + "-" * 70)
print("CLASSES BELOW 200 IMAGES")
print("-" * 70)

very_small = [
    row for row in rows
    if row[2] < 200
]

if very_small:

    for crop, class_name, count in very_small:

        print(
            f"{crop:18} "
            f"{class_name:40} "
            f"{count:6,}"
        )

else:
    print("None")


# Save CSV
output = DATASET_DIR / "final_class_balance.csv"

with open(
    output,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Crop",
        "Class",
        "Images"
    ])

    writer.writerows(rows)


print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)

print(f"\nSaved to:")
print(output)

print("\nNo files were changed.")