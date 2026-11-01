import os
import json

DATASET_DIR = r"datasets/AgriVisionAI_Split"

TRAIN_DIR = os.path.join(DATASET_DIR, "train")

# Get crop folders
crops = sorted([
    folder for folder in os.listdir(TRAIN_DIR)
    if os.path.isdir(os.path.join(TRAIN_DIR, folder))
])

classes = []

for crop in crops:

    crop_path = os.path.join(TRAIN_DIR, crop)

    diseases = sorted([
        folder for folder in os.listdir(crop_path)
        if os.path.isdir(os.path.join(crop_path, folder))
    ])

    for disease in diseases:
        classes.append(f"{crop}__{disease}")


print("=" * 60)
print("AGRIVISIONAI CLASS MAPPING")
print("=" * 60)

print("Total classes:", len(classes))

for index, class_name in enumerate(classes):
    print(f"{index:02d} -> {class_name}")


# Save mapping
output_file = os.path.join(
    "ai_models",
    "disease_models",
    "class_mapping.json"
)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(
        classes,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\nSaved:")
print(output_file)