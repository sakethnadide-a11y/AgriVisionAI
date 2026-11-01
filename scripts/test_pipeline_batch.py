import os
import json
import random
import torch
import torch.nn as nn

from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_v2_s
from torchvision.models.segmentation import deeplabv3_resnet50
from ultralytics import YOLO


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YOLO_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "leaf_detector",
    "AgriVisionAI_YOLO26s_PlantDoc_best.pt"
)

DISEASE_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "disease_models",
    "best_efficientnetv2s.pth"
)

SEVERITY_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "severity_model",
    "best_severity_model.pth"
)

CLASS_MAPPING_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "disease_models",
    "class_mapping.json"
)

TEST_DIR = os.path.join(
    BASE_DIR,
    "test_images"
)


# ============================================================
# DEVICE
# ============================================================

device = torch.device("cpu")

print("=" * 60)
print("AGRIVISIONAI BATCH PIPELINE TEST")
print("=" * 60)

print("Device:", device)


# ============================================================
# LOAD CLASS MAPPING
# ============================================================

with open(
    CLASS_MAPPING_PATH,
    "r",
    encoding="utf-8"
) as f:

    CLASS_NAMES = json.load(f)

print(
    "Disease classes:",
    len(CLASS_NAMES)
)


# ============================================================
# LOAD YOLO
# ============================================================

print("\nLoading YOLO...")

yolo_model = YOLO(
    YOLO_PATH
)

print("YOLO loaded ✅")


# ============================================================
# LOAD EFFICIENTNET
# ============================================================

print("\nLoading EfficientNet...")

disease_model = efficientnet_v2_s(
    weights=None
)

disease_model.classifier[1] = nn.Linear(
    disease_model.classifier[1].in_features,
    98
)

checkpoint = torch.load(
    DISEASE_PATH,
    map_location="cpu"
)

if (
    isinstance(checkpoint, dict)
    and "model_state_dict" in checkpoint
):

    disease_state = checkpoint[
        "model_state_dict"
    ]

else:

    disease_state = checkpoint

disease_model.load_state_dict(
    disease_state
)

disease_model.eval()

print("EfficientNet loaded ✅")


# ============================================================
# LOAD DEEPLAB
# ============================================================

print("\nLoading DeepLabV3...")

severity_model = deeplabv3_resnet50(
    weights=None,
    weights_backbone=None,
    num_classes=1
)

checkpoint = torch.load(
    SEVERITY_PATH,
    map_location="cpu"
)

if (
    isinstance(checkpoint, dict)
    and "model_state_dict" in checkpoint
):

    severity_state = checkpoint[
        "model_state_dict"
    ]

else:

    severity_state = checkpoint

severity_model.load_state_dict(
    severity_state
)

severity_model.eval()

print("DeepLabV3 loaded ✅")


# ============================================================
# TRANSFORMS
# ============================================================

disease_transform = transforms.Compose([

    transforms.Resize(
        (384, 384)
    ),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[
            0.485,
            0.456,
            0.406
        ],

        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


severity_transform = transforms.Compose([

    transforms.Resize(
        (384, 384)
    ),

    transforms.ToTensor()
])


# ============================================================
# SEVERITY FUNCTION
# ============================================================

def get_severity(area):

    if area <= 10:
        return "Mild"

    elif area <= 30:
        return "Moderate"

    else:
        return "Severe"


# ============================================================
# GET TEST IMAGES
# ============================================================

extensions = (
    ".jpg",
    ".jpeg",
    ".png",
    ".JPG",
    ".JPEG",
    ".PNG"
)

image_files = [

    f for f in os.listdir(TEST_DIR)

    if f.endswith(extensions)

    and f != "pipeline_result.json"
]


if len(image_files) == 0:

    print(
        "\nNo test images found."
    )

    raise SystemExit


# Select up to 10 images

random.seed(42)

random.shuffle(
    image_files
)

selected_images = image_files[:5]

print(
    "\nImages selected:",
    len(selected_images)
)


# ============================================================
# RESULTS
# ============================================================

all_results = []


# ============================================================
# PROCESS IMAGES
# ============================================================

for image_number, filename in enumerate(
    selected_images,
    start=1
):

    image_path = os.path.join(
        TEST_DIR,
        filename
    )

    print("\n" + "=" * 60)

    print(
        f"IMAGE {image_number}/"
        f"{len(selected_images)}"
    )

    print(
        "File:",
        filename
    )

    print("=" * 60)


    # --------------------------------------------------------
    # LOAD IMAGE
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")


    # --------------------------------------------------------
    # YOLO
    # --------------------------------------------------------

    results = yolo_model.predict(

        source=image_path,

        conf=0.25,

        verbose=False
    )

    result = results[0]

    boxes = result.boxes

    print(
        "Leaves detected:",
        len(boxes)
    )


    if len(boxes) == 0:

        print(
            "No leaves detected ❌"
        )

        all_results.append({

            "image":
                filename,

            "leaves_detected":
                0

        })

        continue


    # --------------------------------------------------------
    # PROCESS LEAVES
    # --------------------------------------------------------

    image_results = []


    for leaf_number, box in enumerate(
        boxes,
        start=1
    ):

        coordinates = (
            box.xyxy[0]
            .cpu()
            .numpy()
        )

        x1, y1, x2, y2 = coordinates

        x1 = max(
            0,
            int(x1)
        )

        y1 = max(
            0,
            int(y1)
        )

        x2 = min(
            image.width,
            int(x2)
        )

        y2 = min(
            image.height,
            int(y2)
        )


        leaf_crop = image.crop(
            (
                x1,
                y1,
                x2,
                y2
            )
        )


        # ----------------------------------------------------
        # DISEASE
        # ----------------------------------------------------

        disease_input = (
            disease_transform(
                leaf_crop
            )
            .unsqueeze(0)
        )


        with torch.no_grad():

            output = disease_model(
                disease_input
            )

            probabilities = torch.softmax(
                output,
                dim=1
            )

            confidence, predicted_class = (
                probabilities.max(
                    dim=1
                )
            )


        class_index = (
            predicted_class.item()
        )

        disease_confidence = (
            confidence.item()
            * 100
        )


        class_name = CLASS_NAMES[
            class_index
        ]


        if "__" in class_name:

            crop, disease = (
                class_name.split(
                    "__",
                    1
                )
            )

        else:

            crop = "Unknown"
            disease = class_name


        crop = crop.replace(
            "_",
            " "
        )

        disease = disease.replace(
            "_",
            " "
        )


        # ----------------------------------------------------
        # SEVERITY
        # ----------------------------------------------------

        severity_input = (
            severity_transform(
                leaf_crop
            )
            .unsqueeze(0)
        )


        with torch.no_grad():

            severity_output = (
                severity_model(
                    severity_input
                )["out"]
            )

            probability = torch.sigmoid(
                severity_output
            )[0, 0]


        predicted_mask = (
            probability >= 0.5
        )


        diseased_area = (

            predicted_mask
            .float()
            .mean()
            .item()

            * 100
        )


        severity = get_severity(
            diseased_area
        )


        leaf_result = {

            "leaf":
                leaf_number,

            "crop":
                crop,

            "disease":
                disease,

            "disease_confidence":
                round(
                    disease_confidence,
                    2
                ),

            "diseased_area_percent":
                round(
                    diseased_area,
                    2
                ),

            "severity":
                severity,

            "yolo_confidence":
                round(
                    float(
                        box.conf[0]
                        .cpu()
                        .item()
                        * 100
                    ),
                    2
                )
        }


        image_results.append(
            leaf_result
        )


        print(
            f"Leaf {leaf_number}: "
            f"{crop} | "
            f"{disease} | "
            f"{disease_confidence:.2f}% | "
            f"{diseased_area:.2f}% | "
            f"{severity}"
        )


    all_results.append({

        "image":
            filename,

        "leaves_detected":
            len(boxes),

        "results":
            image_results

    })


# ============================================================
# SAVE RESULTS
# ============================================================

output_file = os.path.join(
    TEST_DIR,
    "batch_pipeline_results.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# SUMMARY
# ============================================================

total_images = len(
    all_results
)

images_with_detection = sum(

    1

    for r in all_results

    if r.get(
        "leaves_detected",
        0
    ) > 0
)

total_leaves = sum(

    r.get(
        "leaves_detected",
        0
    )

    for r in all_results
)


print("\n" + "=" * 60)
print("BATCH TEST SUMMARY")
print("=" * 60)

print(
    "Images tested:",
    total_images
)

print(
    "Images with leaf detection:",
    images_with_detection
)

print(
    "Images without detection:",
    total_images -
    images_with_detection
)

print(
    "Total leaves detected:",
    total_leaves
)

print("\nResults saved to:")

print(
    output_file
)

print("=" * 60)