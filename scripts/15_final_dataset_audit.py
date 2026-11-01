from pathlib import Path
import csv

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}

IGNORED_FOLDERS = {
    "duplicate_quarantine",
    "class_quarantine",
    "cross_class_quarantine"
}


print("=" * 70)
print("AGRI VISION AI - FINAL DATASET AUDIT")
print("=" * 70)


rows = []

for crop_dir in sorted(DATASET_DIR.iterdir()):

    if not crop_dir.is_dir():
        continue

    if crop_dir.name in IGNORED_FOLDERS:
        continue

    for class_dir in sorted(crop_dir.iterdir()):

        if not class_dir.is_dir():
            continue

        image_count = sum(
            1
            for file in class_dir.iterdir()
            if (
                file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            )
        )

        if image_count > 0:

            rows.append({
                "Crop": crop_dir.name,
                "Class": class_dir.name,
                "Images": image_count
            })


# ---------------------------------------------------------
# Statistics
# ---------------------------------------------------------

crops = sorted(
    set(row["Crop"] for row in rows)
)

classes = len(rows)

total_images = sum(
    row["Images"]
    for row in rows
)

print("\nFINAL DATASET")
print("-" * 70)

print(f"Crops        : {len(crops)}")
print(f"Classes      : {classes}")
print(f"Images       : {total_images:,}")


# ---------------------------------------------------------
# Crop statistics
# ---------------------------------------------------------

print("\nIMAGES PER CROP")
print("-" * 70)

crop_counts = {}

for crop in crops:

    count = sum(
        row["Images"]
        for row in rows
        if row["Crop"] == crop
    )

    crop_counts[crop] = count

    print(
        f"{crop:20} {count:8,}"
    )


# ---------------------------------------------------------
# Small classes
# ---------------------------------------------------------

small_classes = [
    row
    for row in rows
    if row["Images"] < 100
]

print("\nCLASSES BELOW 100 IMAGES")
print("-" * 70)

if small_classes:

    for row in small_classes:

        print(
            f"{row['Crop']:15} "
            f"{row['Class']:40} "
            f"{row['Images']:5}"
        )

else:

    print("None")


# ---------------------------------------------------------
# Very small classes
# ---------------------------------------------------------

very_small = [
    row
    for row in rows
    if row["Images"] < 50
]

print("\nCLASSES BELOW 50 IMAGES")
print("-" * 70)

if very_small:

    for row in very_small:

        print(
            f"{row['Crop']:15} "
            f"{row['Class']:40} "
            f"{row['Images']:5}"
        )

else:

    print("None")


# ---------------------------------------------------------
# Healthy classes
# ---------------------------------------------------------

healthy_classes = [
    row
    for row in rows
    if row["Class"].lower() == "healthy"
]

print("\nHEALTHY CLASSES")
print("-" * 70)

for row in healthy_classes:

    print(
        f"{row['Crop']:20} "
        f"{row['Images']:8,}"
    )


# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------

output = (
    DATASET_DIR /
    "final_dataset_statistics.csv"
)

with open(
    output,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Crop",
            "Class",
            "Images"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)


print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)

print("\nReport saved to:")
print(output)

print("\nIMPORTANT:")
print("Quarantine folders were excluded.")
print("No images were changed.")
print("No images were deleted.")

print("\nDone.")