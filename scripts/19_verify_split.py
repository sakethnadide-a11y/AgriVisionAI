from pathlib import Path

SPLIT_DIR = Path(
    r"datasets/AgriVisionAI_Split"
)

SPLITS = ["train", "val", "test"]

print("=" * 70)
print("AGRI VISION AI - SPLIT VERIFICATION")
print("=" * 70)

all_classes = {}

for split in SPLITS:

    split_dir = SPLIT_DIR / split

    classes = set()

    for crop_dir in split_dir.iterdir():

        if not crop_dir.is_dir():
            continue

        for class_dir in crop_dir.iterdir():

            if class_dir.is_dir():
                classes.add(
                    f"{crop_dir.name}/{class_dir.name}"
                )

    all_classes[split] = classes

    print(
        f"\n{split.upper()} classes: "
        f"{len(classes)}"
    )


train_classes = all_classes["train"]
val_classes = all_classes["val"]
test_classes = all_classes["test"]

print("\n" + "-" * 70)
print("CLASS CONSISTENCY")
print("-" * 70)

missing_from_val = train_classes - val_classes
missing_from_test = train_classes - test_classes

print(
    f"\nMissing from validation: "
    f"{len(missing_from_val)}"
)

if missing_from_val:
    for c in sorted(missing_from_val):
        print("  ", c)

print(
    f"\nMissing from test: "
    f"{len(missing_from_test)}"
)

if missing_from_test:
    for c in sorted(missing_from_test):
        print("  ", c)


# ---------------------------------------------------------
# Count images
# ---------------------------------------------------------

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
}

print("\n" + "-" * 70)
print("IMAGE COUNTS")
print("-" * 70)

totals = {}

for split in SPLITS:

    count = 0

    for file in (SPLIT_DIR / split).rglob("*"):

        if (
            file.is_file()
            and file.suffix.lower()
            in IMAGE_EXTENSIONS
        ):
            count += 1

    totals[split] = count

    print(
        f"{split.capitalize():15}: "
        f"{count:,}"
    )


print("\n" + "=" * 70)
print("VERIFICATION RESULT")
print("=" * 70)

if (
    len(train_classes) == 98
    and len(val_classes) == 98
    and len(test_classes) == 98
    and not missing_from_val
    and not missing_from_test
):

    print("\n✅ ALL 98 CLASSES ARE PRESENT IN ALL SPLITS")

else:

    print("\n⚠️ CHECK THE RESULTS ABOVE")


print("\nNo files were changed.")
print("Done.")