from pathlib import Path
import hashlib
from collections import defaultdict

# CHANGE THIS ONLY IF YOUR DATASET IS IN A DIFFERENT LOCATION
DATASET_DIR = Path(r"datasets/AgriVisionAI_Dataset")

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}


def get_file_hash(file_path):
    """Calculate SHA-256 hash of an image."""
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(1024 * 1024):
                sha256.update(chunk)

        return sha256.hexdigest()

    except Exception:
        return None


print("=" * 60)
print("AGRI VISION AI - EXACT DUPLICATE CHECK")
print("=" * 60)

print(f"\nDataset: {DATASET_DIR}")
print("\nFinding images...\n")

image_files = [
    f for f in DATASET_DIR.rglob("*")
    if f.is_file()
    and f.suffix.lower() in IMAGE_EXTENSIONS
]

print(f"Total images found: {len(image_files):,}")
print("\nCalculating hashes...\n")

hash_groups = defaultdict(list)

for index, file in enumerate(image_files, start=1):

    file_hash = get_file_hash(file)

    if file_hash:
        hash_groups[file_hash].append(file)

    # Progress every 5,000 images
    if index % 5000 == 0:
        print(f"Processed: {index:,} / {len(image_files):,}")


# Only keep hashes that occur more than once
duplicates = {
    file_hash: files
    for file_hash, files in hash_groups.items()
    if len(files) > 1
}


print("\n" + "=" * 60)
print("DUPLICATE CHECK COMPLETE")
print("=" * 60)

duplicate_groups = len(duplicates)
duplicate_files = sum(len(files) - 1 for files in duplicates.values())

print(f"\nDuplicate groups : {duplicate_groups:,}")
print(f"Duplicate images : {duplicate_files:,}")


# Save report
report_file = DATASET_DIR / "exact_duplicates.txt"

with open(report_file, "w", encoding="utf-8") as f:

    if duplicates:

        for group_number, (file_hash, files) in enumerate(
            duplicates.items(), start=1
        ):

            f.write("=" * 80 + "\n")
            f.write(f"DUPLICATE GROUP {group_number}\n")
            f.write("=" * 80 + "\n")

            for file in files:
                f.write(f"{file}\n")

            f.write("\n")

    else:
        f.write("No exact duplicate images found.\n")


print(f"\nReport saved to:")
print(report_file)

print("\nIMPORTANT: No files were deleted.")
print("Done.")