import os
from pathlib import Path
from collections import Counter
import csv

# ============================================================
# CONFIGURATION
# ============================================================

# CHANGE THIS to your curated dataset folder
DATASET_DIR = Path(r"datasets/AgriVisionAI_Dataset")

# Supported image formats
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

# ============================================================
# SCAN DATASET
# ============================================================

crop_counts = Counter()
class_counts = Counter()

total_images = 0
total_classes = 0
empty_classes = []

rows = []

print("\nScanning dataset...\n")

# Each first-level folder = crop
for crop_dir in sorted(DATASET_DIR.iterdir()):

    if not crop_dir.is_dir():
        continue

    crop = crop_dir.name
    crop_total = 0

    # Each second-level folder = disease/healthy class
    for class_dir in sorted(crop_dir.iterdir()):

        if not class_dir.is_dir():
            continue

        disease = class_dir.name

        images = [
            file for file in class_dir.rglob("*")
            if file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        ]

        image_count = len(images)

        if image_count == 0:
            empty_classes.append(
                f"{crop}/{disease}"
            )

        crop_total += image_count
        total_images += image_count
        total_classes += 1

        crop_counts[crop] += image_count
        class_counts[f"{crop}/{disease}"] = image_count

        rows.append({
            "Crop": crop,
            "Class": disease,
            "Images": image_count
        })

# ============================================================
# PRINT RESULTS
# ============================================================

print("=" * 60)
print("AGRI VISION AI DATASET AUDIT")
print("=" * 60)

print(f"\nTotal crops       : {len(crop_counts)}")
print(f"Total classes     : {total_classes}")
print(f"Total images      : {total_images:,}")

print("\n" + "-" * 60)
print("IMAGES PER CROP")
print("-" * 60)

for crop, count in sorted(
    crop_counts.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{crop:25} {count:>10,}")

print("\n" + "-" * 60)
print("TOP 20 LARGEST CLASSES")
print("-" * 60)

for class_name, count in class_counts.most_common(20):
    print(f"{class_name:45} {count:>8,}")

print("\n" + "-" * 60)
print("BOTTOM 20 SMALLEST CLASSES")
print("-" * 60)

for class_name, count in sorted(
    class_counts.items(),
    key=lambda x: x[1]
)[:20]:
    print(f"{class_name:45} {count:>8,}")

print("\n" + "-" * 60)
print("EMPTY CLASSES")
print("-" * 60)

if empty_classes:
    for item in empty_classes:
        print(item)
else:
    print("None")

# ============================================================
# SAVE CSV REPORT
# ============================================================

report_path = DATASET_DIR / "dataset_report.csv"

with open(
    report_path,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=["Crop", "Class", "Images"]
    )

    writer.writeheader()
    writer.writerows(rows)

print("\n" + "=" * 60)
print(f"Report saved to:")
print(report_path)
print("=" * 60)