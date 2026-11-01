from pathlib import Path
import shutil
from collections import defaultdict

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

REPORT = DATASET_DIR / "near_duplicates.txt"

QUARANTINE_DIR = (
    DATASET_DIR / "near_duplicate_quarantine"
)

QUARANTINE_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Union-Find
# ---------------------------------------------------------

class UnionFind:

    def __init__(self):
        self.parent = {}

    def find(self, x):

        if x not in self.parent:
            self.parent[x] = x

        if self.parent[x] != x:
            self.parent[x] = self.find(
                self.parent[x]
            )

        return self.parent[x]

    def union(self, a, b):

        root_a = self.find(a)
        root_b = self.find(b)

        if root_a != root_b:
            self.parent[root_b] = root_a


# ---------------------------------------------------------
# Read report
# ---------------------------------------------------------

print("=" * 60)
print("AGRI VISION AI - STRONG NEAR DUPLICATE CLEANER")
print("=" * 60)

if not REPORT.exists():

    print("\nERROR:")
    print("near_duplicates.txt not found.")

    exit()


same_class_pairs = []

section = None

with open(
    REPORT,
    "r",
    encoding="utf-8"
) as f:

    lines = f.readlines()


current_distance = None

for line in lines:

    line = line.strip()

    if line == "SAME-CLASS NEAR DUPLICATES":

        section = "same"
        continue

    if line == "CROSS-CLASS NEAR DUPLICATES":

        section = "cross"
        continue

    if section != "same":
        continue

    if line.startswith("Distance:"):

        current_distance = int(
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

        if current_distance in {0, 2}:

            same_class_pairs.append(
                (file1, file2, current_distance)
            )


print(
    f"\nStrong same-class pairs "
    f"(distance 0-2): "
    f"{len(same_class_pairs):,}"
)


# ---------------------------------------------------------
# Build clusters
# ---------------------------------------------------------

uf = UnionFind()

for file1, file2, distance in same_class_pairs:

    uf.union(
        str(file1),
        str(file2)
    )


clusters = defaultdict(list)

for file1, file2, distance in same_class_pairs:

    clusters[uf.find(str(file1))].append(
        file1
    )

    clusters[uf.find(str(file2))].append(
        file2
    )


# Remove repeated paths
for root in clusters:

    clusters[root] = list(
        dict.fromkeys(
            clusters[root]
        )
    )


# ---------------------------------------------------------
# Determine files to quarantine
# ---------------------------------------------------------

files_to_move = []
files_to_keep = []

for root, files in clusters.items():

    # Keep one representative
    files = sorted(
        files,
        key=lambda x: str(x)
    )

    keep = files[0]

    files_to_keep.append(keep)

    for file in files[1:]:

        files_to_move.append(
            (file, keep)
        )


print(
    f"Duplicate clusters: "
    f"{len(clusters):,}"
)

print(
    f"Files to quarantine: "
    f"{len(files_to_move):,}"
)


# ---------------------------------------------------------
# Move files
# ---------------------------------------------------------

moved = 0
failed = 0

log_file = (
    DATASET_DIR /
    "strong_near_duplicate_move_log.txt"
)


with open(
    log_file,
    "w",
    encoding="utf-8"
) as log:

    for duplicate, keep in files_to_move:

        if not duplicate.exists():

            continue

        # Preserve crop/class structure
        relative = duplicate.relative_to(
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
                    f"{destination.stem}_duplicate_{counter}"
                    f"{destination.suffix}"
                )

                if not destination.exists():
                    break

                counter += 1

        try:

            shutil.move(
                str(duplicate),
                str(destination)
            )

            moved += 1

            log.write(
                f"MOVED: {duplicate}\n"
                f"KEPT : {keep}\n"
                f"TO   : {destination}\n"
                + "-" * 80
                + "\n"
            )

        except Exception as e:

            failed += 1

            log.write(
                f"FAILED: {duplicate}\n"
                f"ERROR: {e}\n"
                + "-" * 80
                + "\n"
            )


# ---------------------------------------------------------
# Final output
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(
    f"\nFiles moved to quarantine: "
    f"{moved:,}"
)

print(
    f"Move failures: {failed:,}"
)

print("\nQuarantine:")
print(QUARANTINE_DIR)

print("\nLog:")
print(log_file)

print("\nIMPORTANT:")
print("Distance 4 and 6 were NOT touched.")
print("Cross-class duplicates were NOT touched.")
print("Nothing was permanently deleted.")