from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import os

DATASET_DIR = Path(r"datasets/AgriVisionAI_Dataset")

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png",
    ".bmp", ".webp",
    ".tif", ".tiff"
}


def check_image(file):
    try:
        with Image.open(file) as img:
            img.verify()
        return None
    except Exception as e:
        return (str(file), str(e))


print("=" * 60)
print("AGRI VISION AI - FAST CORRUPTED IMAGE CHECK")
print("=" * 60)

files = [
    f for f in DATASET_DIR.rglob("*")
    if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
]

print(f"\nImages found: {len(files):,}")
print("Checking images...\n")

workers = min(16, (os.cpu_count() or 4) * 2)

with ThreadPoolExecutor(max_workers=workers) as executor:
    results = list(executor.map(check_image, files))

corrupted = [r for r in results if r is not None]

print("\n" + "=" * 60)
print("SCAN COMPLETE")
print("=" * 60)

print(f"Total images scanned : {len(files):,}")
print(f"Corrupted images     : {len(corrupted):,}")

report = DATASET_DIR / "corrupted_images.txt"

with open(report, "w", encoding="utf-8") as f:
    for path, error in corrupted:
        f.write(f"FILE: {path}\n")
        f.write(f"ERROR: {error}\n")
        f.write("-" * 80 + "\n")

print(f"\nReport saved to:\n{report}")