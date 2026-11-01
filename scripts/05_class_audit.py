from pathlib import Path
from collections import defaultdict
import csv

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png",
    ".bmp", ".webp",
    ".tif", ".tiff"
}

counts = defaultdict(int)

for crop_dir in DATASET_DIR.iterdir():

    if not crop_dir.is_dir():
        continue

    # Ignore quarantine
    if crop_dir.name == "duplicate_quarantine":
        continue

    for class_dir in crop_dir.iterdir():

        if not class_dir.is_dir():
            continue

        for file in class_dir.iterdir():

            if (
                file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            ):
                counts[(crop_dir.name, class_dir.name)] += 1


rows = []

for (crop, class_name), count in sorted(counts.items()):

    rows.append({
        "Crop": crop,
        "Class": class_name,
        "Images": count
    })


output = DATASET_DIR / "class_audit_after_duplicates.csv"

with open(output, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=["Crop", "Class", "Images"]
    )

    writer.writeheader()
    writer.writerows(rows)


print("=" * 60)
print("AGRI VISION AI - CLASS AUDIT")
print("=" * 60)

print(f"\nCrops  : {len(set(r['Crop'] for r in rows))}")
print(f"Classes: {len(rows)}")
print(
    f"Images : {sum(r['Images'] for r in rows):,}"
)

print("\nSmall classes (<100 images):")

for row in rows:

    if row["Images"] < 100:

        print(
            f"{row['Crop']:15} "
            f"{row['Class']:45} "
            f"{row['Images']}"
        )

print("\nPotential pest/symptom classes:")

keywords = [
    "whitefly",
    "leafminner",
    "leafminer",
    "yellowish",
    "aphid",
    "mite",
    "thrips",
    "insect",
    "fly"
]

for row in rows:

    text = row["Class"].lower()

    if any(keyword in text for keyword in keywords):

        print(
            f"{row['Crop']:15} "
            f"{row['Class']:45} "
            f"{row['Images']}"
        )

print("\nReport saved to:")
print(output)

print("\nDone.")