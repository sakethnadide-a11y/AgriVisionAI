from pathlib import Path
import shutil
import random

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

OUTPUT_DIR = Path(
    r"datasets/AgriVisionAI_Split"
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

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

SEED = 42

random.seed(SEED)


print("=" * 70)
print("AGRI VISION AI - TRAIN / VAL / TEST SPLIT")
print("=" * 70)

print("\nSource:")
print(DATASET_DIR)

print("\nDestination:")
print(OUTPUT_DIR)

print("\nSplit:")
print("Train: 80%")
print("Val  : 10%")
print("Test : 10%")


# ---------------------------------------------------------
# Check output directory
# ---------------------------------------------------------

if OUTPUT_DIR.exists():

    print("\nERROR:")
    print("Output directory already exists:")
    print(OUTPUT_DIR)

    print(
        "\nDelete/rename the existing split folder "
        "before running this script again."
    )

    exit()


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Collect classes
# ---------------------------------------------------------

classes = []

for crop_dir in sorted(DATASET_DIR.iterdir()):

    if not crop_dir.is_dir():
        continue

    if crop_dir.name in IGNORED_FOLDERS:
        continue

    for class_dir in sorted(crop_dir.iterdir()):

        if not class_dir.is_dir():
            continue

        images = [
            f for f in class_dir.iterdir()
            if (
                f.is_file()
                and f.suffix.lower()
                in IMAGE_EXTENSIONS
            )
        ]

        if images:
            classes.append(
                (
                    crop_dir.name,
                    class_dir.name,
                    images
                )
            )


print(
    f"\nClasses found: {len(classes)}"
)


# ---------------------------------------------------------
# Split each class
# ---------------------------------------------------------

total_train = 0
total_val = 0
total_test = 0

print("\nCreating split...\n")


for crop, class_name, images in classes:

    random.shuffle(images)

    total = len(images)

    train_count = int(
        total * TRAIN_RATIO
    )

    val_count = int(
        total * VAL_RATIO
    )

    train_images = images[
        :train_count
    ]

    val_images = images[
        train_count:
        train_count + val_count
    ]

    test_images = images[
        train_count + val_count:
    ]


    splits = {
        "train": train_images,
        "val": val_images,
        "test": test_images
    }


    for split_name, split_images in splits.items():

        destination = (
            OUTPUT_DIR
            / split_name
            / crop
            / class_name
        )

        destination.mkdir(
            parents=True,
            exist_ok=True
        )

        for image in split_images:

            shutil.copy2(
                image,
                destination / image.name
            )


    total_train += len(train_images)
    total_val += len(val_images)
    total_test += len(test_images)


    print(
        f"{crop:15} "
        f"{class_name:35} "
        f"{total:6,} -> "
        f"{len(train_images):5,} / "
        f"{len(val_images):5,} / "
        f"{len(test_images):5,}"
    )


# ---------------------------------------------------------
# Final statistics
# ---------------------------------------------------------

total = (
    total_train
    + total_val
    + total_test
)


print("\n" + "=" * 70)
print("SPLIT COMPLETE")
print("=" * 70)

print(
    f"\nTrain images: {total_train:,}"
)

print(
    f"Validation images: {total_val:,}"
)

print(
    f"Test images: {total_test:,}"
)

print(
    f"Total images: {total:,}"
)

print(
    f"\nOutput:"
)

print(OUTPUT_DIR)

print("\nOriginal dataset was NOT modified.")

print("\nDone.")