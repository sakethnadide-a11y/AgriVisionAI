from pathlib import Path
from PIL import Image
import imagehash
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import os

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
    "class_quarantine"
}

HAMMING_THRESHOLD = 6


def calculate_hash(file_path):
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            phash = imagehash.phash(img)

        return file_path, phash

    except Exception:
        return None


print("=" * 60)
print("AGRI VISION AI - CORRECTED NEAR DUPLICATE CHECK")
print("=" * 60)

print("\nFinding active dataset images...")

image_files = []

for crop_dir in DATASET_DIR.iterdir():

    if not crop_dir.is_dir():
        continue

    if crop_dir.name in IGNORED_FOLDERS:
        continue

    for class_dir in crop_dir.iterdir():

        if not class_dir.is_dir():
            continue

        for file in class_dir.iterdir():

            if (
                file.is_file()
                and file.suffix.lower() in IMAGE_EXTENSIONS
            ):
                image_files.append(file)


print(f"Active images found: {len(image_files):,}")

print("\nExpected: approximately 82,156")
print("\nCalculating perceptual hashes...\n")


workers = min(16, (os.cpu_count() or 4) * 2)

hash_results = []

with ThreadPoolExecutor(max_workers=workers) as executor:

    for index, result in enumerate(
        executor.map(calculate_hash, image_files),
        start=1
    ):

        if result is not None:
            hash_results.append(result)

        if index % 5000 == 0:
            print(
                f"Processed: {index:,} / "
                f"{len(image_files):,}"
            )


print("\nHash calculation complete.")
print(f"Valid images: {len(hash_results):,}")

print("\nFinding visually similar images...")


# ---------------------------------------------------------
# Bucket hashes
# ---------------------------------------------------------

buckets = defaultdict(list)

for file_path, phash in hash_results:

    bucket_key = str(phash)[:4]

    buckets[bucket_key].append(
        (file_path, phash)
    )


near_duplicate_pairs = []

for bucket_items in buckets.values():

    for i in range(len(bucket_items)):

        file1, hash1 = bucket_items[i]

        for j in range(i + 1, len(bucket_items)):

            file2, hash2 = bucket_items[j]

            distance = hash1 - hash2

            if distance <= HAMMING_THRESHOLD:

                near_duplicate_pairs.append(
                    (file1, file2, distance)
                )


# ---------------------------------------------------------
# Separate same-class / cross-class
# ---------------------------------------------------------

same_class = []
cross_class = []

for file1, file2, distance in near_duplicate_pairs:

    class1 = file1.parent.name
    class2 = file2.parent.name

    if class1 == class2:
        same_class.append(
            (file1, file2, distance)
        )
    else:
        cross_class.append(
            (file1, file2, distance)
        )


print("\n" + "=" * 60)
print("NEAR DUPLICATE CHECK COMPLETE")
print("=" * 60)

print(
    f"\nNear-duplicate pairs found : "
    f"{len(near_duplicate_pairs):,}"
)

print(
    f"Same-class pairs           : "
    f"{len(same_class):,}"
)

print(
    f"Cross-class pairs          : "
    f"{len(cross_class):,}"
)


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

report_file = DATASET_DIR / "near_duplicates.txt"

with open(
    report_file,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "AGRI VISION AI - NEAR DUPLICATE REPORT\n\n"
    )

    f.write(
        f"Active images: {len(image_files):,}\n"
    )

    f.write(
        f"Hamming threshold: {HAMMING_THRESHOLD}\n\n"
    )

    f.write("=" * 80 + "\n")
    f.write("SAME-CLASS NEAR DUPLICATES\n")
    f.write("=" * 80 + "\n\n")

    for file1, file2, distance in same_class:

        f.write(f"Distance: {distance}\n")
        f.write(f"FILE 1: {file1}\n")
        f.write(f"FILE 2: {file2}\n")
        f.write("-" * 80 + "\n")


    f.write("\n")
    f.write("=" * 80 + "\n")
    f.write("CROSS-CLASS NEAR DUPLICATES\n")
    f.write("=" * 80 + "\n\n")

    for file1, file2, distance in cross_class:

        f.write(f"Distance: {distance}\n")
        f.write(f"FILE 1: {file1}\n")
        f.write(f"FILE 2: {file2}\n")
        f.write("-" * 80 + "\n")


print("\nReport saved to:")
print(report_file)

print("\nNo files were deleted or moved.")
print("Done.")