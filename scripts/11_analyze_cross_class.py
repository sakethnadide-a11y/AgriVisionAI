from pathlib import Path
from collections import Counter

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

REPORT = DATASET_DIR / "near_duplicates.txt"

if not REPORT.exists():
    print("ERROR: near_duplicates.txt not found.")
    exit()


cross_class = []

section = None
distance = None
file1 = None

with open(REPORT, "r", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if line == "CROSS-CLASS NEAR DUPLICATES":
            section = "cross"
            continue

        if section != "cross":
            continue

        if line.startswith("Distance:"):
            distance = int(
                line.split(":")[1].strip()
            )

        elif line.startswith("FILE 1:"):
            file1 = Path(
                line.replace("FILE 1:", "").strip()
            )

        elif line.startswith("FILE 2:"):

            file2 = Path(
                line.replace("FILE 2:", "").strip()
            )

            if file1 is not None:

                class1 = file1.parent.name
                class2 = file2.parent.name

                pair = tuple(
                    sorted([class1, class2])
                )

                cross_class.append(
                    (
                        pair[0],
                        pair[1],
                        distance,
                        file1,
                        file2
                    )
                )


print("=" * 60)
print("AGRI VISION AI - CROSS-CLASS CONFLICT ANALYSIS")
print("=" * 60)

print(
    f"\nTotal cross-class pairs: "
    f"{len(cross_class):,}"
)


# ---------------------------------------------------------
# Distance distribution
# ---------------------------------------------------------

distance_counts = Counter(
    item[2]
    for item in cross_class
)

print("\nDistance distribution:")
print("-" * 60)

for distance in sorted(distance_counts):

    print(
        f"Distance {distance}: "
        f"{distance_counts[distance]:,}"
    )


# ---------------------------------------------------------
# Class-pair frequency
# ---------------------------------------------------------

pair_counts = Counter(
    (item[0], item[1])
    for item in cross_class
)


print("\nMost common conflicting class pairs:")
print("-" * 60)

for (class1, class2), count in pair_counts.most_common(30):

    print(
        f"{count:5}  "
        f"{class1}  <-->  {class2}"
    )


# ---------------------------------------------------------
# Exact cross-class matches
# ---------------------------------------------------------

exact_matches = [
    item
    for item in cross_class
    if item[2] == 0
]


print("\n" + "=" * 60)
print("EXACT CROSS-CLASS MATCHES")
print("=" * 60)

print(
    f"\nExact matches: "
    f"{len(exact_matches):,}"
)


exact_report = (
    DATASET_DIR /
    "cross_class_exact_conflicts.txt"
)

with open(
    exact_report,
    "w",
    encoding="utf-8"
) as f:

    for number, item in enumerate(
        exact_matches,
        start=1
    ):

        class1, class2, distance, file1, file2 = item

        f.write("=" * 80 + "\n")
        f.write(
            f"CONFLICT {number}\n"
        )
        f.write("=" * 80 + "\n")

        f.write(
            f"CLASS 1: {class1}\n"
        )

        f.write(
            f"FILE 1 : {file1}\n"
        )

        f.write(
            f"CLASS 2: {class2}\n"
        )

        f.write(
            f"FILE 2 : {file2}\n"
        )

        f.write("\n")


# ---------------------------------------------------------
# Save complete summary
# ---------------------------------------------------------

summary_report = (
    DATASET_DIR /
    "cross_class_conflict_summary.txt"
)

with open(
    summary_report,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "AGRI VISION AI - CROSS CLASS CONFLICT SUMMARY\n\n"
    )

    f.write(
        f"Total cross-class pairs: "
        f"{len(cross_class):,}\n"
    )

    f.write(
        f"Exact matches: "
        f"{len(exact_matches):,}\n\n"
    )

    f.write(
        "DISTANCE DISTRIBUTION\n"
    )

    f.write("-" * 60 + "\n")

    for distance in sorted(distance_counts):

        f.write(
            f"Distance {distance}: "
            f"{distance_counts[distance]:,}\n"
        )

    f.write(
        "\nTOP CLASS PAIRS\n"
    )

    f.write("-" * 60 + "\n")

    for (class1, class2), count in pair_counts.most_common():

        f.write(
            f"{count:5}  "
            f"{class1} <--> {class2}\n"
        )


print("\nReports created:")

print(
    f"\n1. {exact_report}"
)

print(
    f"\n2. {summary_report}"
)

print("\nIMPORTANT:")
print("No images were deleted or moved.")

print("\nDone.")