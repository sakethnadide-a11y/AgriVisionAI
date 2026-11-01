from pathlib import Path
from collections import Counter

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

REPORT = DATASET_DIR / "near_duplicates.txt"

if not REPORT.exists():
    print("ERROR: near_duplicates.txt not found.")
    exit()

same_class_distances = Counter()
cross_class_distances = Counter()

section = None

with open(REPORT, "r", encoding="utf-8") as f:

    lines = f.readlines()

for line in lines:

    line = line.strip()

    if line == "SAME-CLASS NEAR DUPLICATES":
        section = "same"
        continue

    if line == "CROSS-CLASS NEAR DUPLICATES":
        section = "cross"
        continue

    if line.startswith("Distance:"):

        try:
            distance = int(
                line.split(":")[1].strip()
            )

            if section == "same":
                same_class_distances[distance] += 1

            elif section == "cross":
                cross_class_distances[distance] += 1

        except ValueError:
            pass


print("=" * 60)
print("AGRI VISION AI - NEAR DUPLICATE ANALYSIS")
print("=" * 60)

print("\nSAME-CLASS PAIRS")
print("-" * 60)

same_total = sum(same_class_distances.values())

print(f"Total: {same_total:,}\n")

for distance in sorted(same_class_distances):

    count = same_class_distances[distance]

    print(
        f"Distance {distance}: {count:,}"
    )


print("\nCROSS-CLASS PAIRS")
print("-" * 60)

cross_total = sum(cross_class_distances.values())

print(f"Total: {cross_total:,}\n")

for distance in sorted(cross_class_distances):

    count = cross_class_distances[distance]

    print(
        f"Distance {distance}: {count:,}"
    )


print("\n" + "=" * 60)
print("RECOMMENDED CATEGORIES")
print("=" * 60)

print("\nDistance 0-2:")
print("Very strong visual match")

print("\nDistance 3-4:")
print("Strong visual match")

print("\nDistance 5-6:")
print("Possible near-duplicate; review before removal")

print("\nNo files were deleted or moved.")