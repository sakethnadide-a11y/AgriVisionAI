import os
import json
import sys

import torch
import torch.nn as nn

from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_v2_s
from torchvision.models.segmentation import deeplabv3_resnet50
from ultralytics import YOLO


# ============================================================
# AGRIVISIONAI - COMPLETE AI PIPELINE
# ============================================================
#
# Image
#   ↓
# YOLO26s Leaf Detection
#   ↓
# EfficientNetV2-S Disease Classification
#   ↓
# DeepLabV3 Severity Segmentation
#   ↓
# Diseased Area %
#   ↓
# Severity
#   ↓
# Recommendation Engine
#
# ============================================================


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# MODEL PATHS
# ============================================================

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

IMAGE_PATH = os.path.join(
    BASE_DIR,
    "test_images",
    "test.jpg"
)


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

sys.path.insert(
    0,
    BASE_DIR
)

from recommendation_engine import get_recommendation


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 60)
print("AGRIVISIONAI AI PIPELINE")
print("=" * 60)

print(
    "Device:",
    device
)


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

print("\n" + "=" * 60)
print("CHECKING REQUIRED FILES")
print("=" * 60)


required_files = {

    "YOLO":
        YOLO_PATH,

    "Disease Model":
        DISEASE_PATH,

    "Severity Model":
        SEVERITY_PATH,

    "Class Mapping":
        CLASS_MAPPING_PATH,

    "Test Image":
        IMAGE_PATH
}


for name, path in required_files.items():

    if os.path.exists(path):

        size_mb = (
            os.path.getsize(path)
            / (1024 ** 2)
        )

        print(
            f"{name}: FOUND "
            f"({size_mb:.2f} MB)"
        )

    else:

        print(
            f"{name}: NOT FOUND ❌"
        )

        print(
            "Path:",
            path
        )

        raise SystemExit


# ============================================================
# LOAD YOLO LEAF DETECTOR
# ============================================================

print("\n" + "=" * 60)
print("LOADING YOLO26s LEAF DETECTOR")
print("=" * 60)


try:

    yolo_model = YOLO(
        YOLO_PATH
    )

    print(
        "YOLO model loaded successfully ✅"
    )

except Exception as e:

    print(
        "YOLO loading failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# LOAD EFFICIENTNETV2-S
# ============================================================

print("\n" + "=" * 60)
print("LOADING EFFICIENTNETV2-S DISEASE MODEL")
print("=" * 60)


try:

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


    # Handle both checkpoint formats

    if (
        isinstance(checkpoint, dict)
        and "model_state_dict" in checkpoint
    ):

        disease_state = (
            checkpoint[
                "model_state_dict"
            ]
        )

    else:

        disease_state = checkpoint


    disease_model.load_state_dict(
        disease_state
    )


    disease_model = (
        disease_model.to(device)
    )


    disease_model.eval()


    print(
        "EfficientNetV2-S loaded successfully ✅"
    )

    print(
        "Output classes:",
        98
    )


except Exception as e:

    print(
        "EfficientNet loading failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# LOAD CLASS MAPPING
# ============================================================

print("\n" + "=" * 60)
print("LOADING DISEASE CLASS MAPPING")
print("=" * 60)


try:

    with open(
        CLASS_MAPPING_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        CLASS_NAMES = json.load(f)


    print(
        "Disease classes loaded:",
        len(CLASS_NAMES)
    )


    if len(CLASS_NAMES) != 98:

        print(
            "WARNING: Expected 98 classes!"
        )


except Exception as e:

    print(
        "Class mapping loading failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# LOAD DEEPLABV3
# ============================================================

print("\n" + "=" * 60)
print("LOADING DEEPLABV3 SEVERITY MODEL")
print("=" * 60)


try:

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

        severity_state = (
            checkpoint[
                "model_state_dict"
            ]
        )

    else:

        severity_state = checkpoint


    severity_model.load_state_dict(
        severity_state
    )


    severity_model = (
        severity_model.to(device)
    )


    severity_model.eval()


    print(
        "DeepLabV3 loaded successfully ✅"
    )

    print(
        "Output classes:",
        1
    )


except Exception as e:

    print(
        "DeepLabV3 loading failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# IMAGE TRANSFORMS
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
# SEVERITY CATEGORY
# ============================================================

def severity_category(
    area_percent
):

    if area_percent <= 10:

        return "Mild"

    elif area_percent <= 30:

        return "Moderate"

    else:

        return "Severe"


# ============================================================
# FORMAT CLASS NAME
# ============================================================

def format_class_name(
    class_name
):

    """
    Converts:

        Cucumber__Gummy_Stem_Blight

    into:

        Cucumber
        Gummy Stem Blight
    """

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


    return crop, disease


# ============================================================
# LOAD TEST IMAGE
# ============================================================

print("\n" + "=" * 60)
print("LOADING TEST IMAGE")
print("=" * 60)


try:

    image = Image.open(
        IMAGE_PATH
    ).convert("RGB")


    print(
        "Image:",
        IMAGE_PATH
    )

    print(
        "Image size:",
        image.size
    )


except Exception as e:

    print(
        "Image loading failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# STEP 1 — YOLO LEAF DETECTION
# ============================================================

print("\n" + "=" * 60)
print("STEP 1 — LEAF DETECTION")
print("=" * 60)


try:

    results = yolo_model.predict(

        source=IMAGE_PATH,

        conf=0.25,

        verbose=False
    )


    result = results[0]

    boxes = result.boxes


    number_of_leaves = len(
        boxes
    )


    print(
        "Leaves detected:",
        number_of_leaves
    )


except Exception as e:

    print(
        "YOLO prediction failed ❌"
    )

    print(e)

    raise SystemExit


# ============================================================
# NO LEAVES DETECTED
# ============================================================

if number_of_leaves == 0:

    print(
        "\n❌ No leaves detected."
    )

    print(
        "Please provide a clearer plant image."
    )

    raise SystemExit


# ============================================================
# PROCESS EACH LEAF
# ============================================================

all_results = []


for leaf_number, box in enumerate(
    boxes,
    start=1
):

    print("\n" + "-" * 60)

    print(
        f"LEAF {leaf_number}"
    )

    print("-" * 60)


    # ========================================================
    # BOUNDING BOX
    # ========================================================

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


    print(
        "Bounding box:",
        (x1, y1, x2, y2)
    )


    # ========================================================
    # YOLO CONFIDENCE
    # ========================================================

    yolo_confidence = float(
        box.conf[0]
        .cpu()
        .item()
    )


    print(
        "Leaf detection confidence:",
        f"{yolo_confidence * 100:.2f}%"
    )


    # ========================================================
    # CREATE LEAF CROP
    # ========================================================

    leaf_crop = image.crop(

        (
            x1,
            y1,
            x2,
            y2
        )
    )


    if (
        leaf_crop.width <= 1
        or leaf_crop.height <= 1
    ):

        print(
            "Invalid leaf crop. Skipping."
        )

        continue


    # ========================================================
    # STEP 2 — DISEASE CLASSIFICATION
    # ========================================================

    print(
        "\nDisease classification..."
    )


    disease_input = (
        disease_transform(
            leaf_crop
        )
        .unsqueeze(0)
        .to(device)
    )


    with torch.no_grad():

        disease_output = (
            disease_model(
                disease_input
            )
        )


        probabilities = (
            torch.softmax(
                disease_output,
                dim=1
            )
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


    # ========================================================
    # CLASS NAME
    # ========================================================

    if (
        0 <= class_index
        < len(CLASS_NAMES)
    ):

        full_class_name = (
            CLASS_NAMES[
                class_index
            ]
        )


        crop_name, disease_name = (
            format_class_name(
                full_class_name
            )
        )

    else:

        full_class_name = (
            "Unknown"
        )

        crop_name = (
            "Unknown"
        )

        disease_name = (
            "Unknown"
        )


    print(
        "Predicted class index:",
        class_index
    )

    print(
        "Crop:",
        crop_name
    )

    print(
        "Disease:",
        disease_name
    )

    print(
        "Disease confidence:",
        f"{disease_confidence:.2f}%"
    )


    # ========================================================
    # STEP 3 — SEVERITY SEGMENTATION
    # ========================================================

    print(
        "\nSeverity segmentation..."
    )


    severity_input = (
        severity_transform(
            leaf_crop
        )
        .unsqueeze(0)
        .to(device)
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


    # ========================================================
    # CREATE DISEASE MASK
    # ========================================================

    predicted_mask = (
        probability >= 0.5
    )


    # ========================================================
    # CALCULATE DISEASED AREA
    # ========================================================

    diseased_pixels = (
        predicted_mask
        .float()
        .sum()
        .item()
    )


    total_pixels = (
        predicted_mask.numel()
    )


    if total_pixels > 0:

        diseased_area = (

            diseased_pixels
            / total_pixels
            * 100
        )

    else:

        diseased_area = 0.0


    print(
        "Diseased area:",
        f"{diseased_area:.2f}%"
    )


    # ========================================================
    # SEVERITY
    # ========================================================

    severity = severity_category(
        diseased_area
    )


    print(
        "Severity:",
        severity
    )


    # ========================================================
    # STEP 4 — RECOMMENDATION ENGINE
    # ========================================================

    print(
        "\nGenerating recommendations..."
    )


    recommendation_result = (
        get_recommendation(

            crop=crop_name,

            disease=disease_name,

            severity=severity,

            diseased_area=diseased_area
        )
    )


    recommendations = (
        recommendation_result[
            "recommendations"
        ]
    )


    print(
        "Recommendations generated:",
        len(recommendations)
    )


    # ========================================================
    # DISPLAY RECOMMENDATIONS
    # ========================================================

    for number, recommendation in enumerate(

        recommendations,

        start=1

    ):

        print(
            f"  {number}. "
            f"{recommendation}"
        )


    # ========================================================
    # SAVE LEAF RESULT
    # ========================================================

    leaf_result = {

        "leaf_number":
            leaf_number,

        "bounding_box": [

            x1,
            y1,
            x2,
            y2
        ],

        "leaf_detection_confidence":
            round(
                yolo_confidence * 100,
                2
            ),

        "class_index":
            class_index,

        "crop":
            crop_name,

        "disease":
            disease_name,

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

        "recommendations":
            recommendations
    }


    all_results.append(
        leaf_result
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("FINAL AGRIVISIONAI RESULT")
print("=" * 60)


if len(all_results) == 0:

    print(
        "No valid leaves were processed."
    )

else:

    for result in all_results:

        print("\n" + "-" * 60)

        print(
            "Leaf:",
            result[
                "leaf_number"
            ]
        )

        print(
            "Crop:",
            result[
                "crop"
            ]
        )

        print(
            "Disease:",
            result[
                "disease"
            ]
        )

        print(
            "Disease confidence:",
            f'{result["disease_confidence"]:.2f}%'
        )

        print(
            "Diseased area:",
            f'{result["diseased_area_percent"]:.2f}%'
        )

        print(
            "Severity:",
            result[
                "severity"
            ]
        )


        print(
            "\nRecommendations:"
        )


        for number, recommendation in enumerate(

            result[
                "recommendations"
            ],

            start=1

        ):

            print(
                f"  {number}. "
                f"{recommendation}"
            )


# ============================================================
# SAVE JSON RESULT
# ============================================================

OUTPUT_FILE = os.path.join(

    BASE_DIR,

    "test_images",

    "pipeline_result.json"
)


with open(

    OUTPUT_FILE,

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
# COMPLETE
# ============================================================

print("\n" + "=" * 60)

print(
    "Pipeline result saved:"
)

print(
    OUTPUT_FILE
)

print("=" * 60)

print(
    "\nPIPELINE TEST COMPLETE ✅"
)