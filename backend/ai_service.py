# ============================================================
# AGRIVISIONAI - AI SERVICE
# YOLO26s + EfficientNetV2-S + DeepLabV3
# + Disease Recommendations + Fertilizer Recommendation
# ============================================================

import os
import sys
import json

import torch
import torch.nn as nn
from PIL import Image

from torchvision import transforms
from torchvision.models import efficientnet_v2_s
from torchvision.models.segmentation import deeplabv3_resnet50

from ultralytics import YOLO


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Make project root importable
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ============================================================
# IMPORT RECOMMENDATION ENGINE
# ============================================================

from recommendation_engine import get_recommendation


# ============================================================
# MODEL PATHS
# ============================================================

YOLO_MODEL_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "leaf_detector",
    "AgriVisionAI_YOLO26s_PlantDoc_best.pt"
)

DISEASE_MODEL_PATH = os.path.join(
    BASE_DIR,
    "ai_models",
    "disease_models",
    "best_efficientnetv2s.pth"
)

SEVERITY_MODEL_PATH = os.path.join(
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


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("AI Service Device:", DEVICE)


# ============================================================
# GLOBAL MODEL VARIABLES
# ============================================================

_yolo_model = None
_disease_model = None
_severity_model = None
_class_mapping = None


# ============================================================
# LOAD CLASS MAPPING
# ============================================================

def load_class_mapping():

    global _class_mapping

    if _class_mapping is not None:
        return _class_mapping

    if not os.path.exists(CLASS_MAPPING_PATH):

        raise FileNotFoundError(
            f"Class mapping not found:\n"
            f"{CLASS_MAPPING_PATH}"
        )

    with open(
        CLASS_MAPPING_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        _class_mapping = json.load(f)

    return _class_mapping


# ============================================================
# LOAD YOLO MODEL
# ============================================================

def load_yolo_model():

    global _yolo_model

    if _yolo_model is not None:
        return _yolo_model

    if not os.path.exists(YOLO_MODEL_PATH):

        raise FileNotFoundError(
            f"YOLO model not found:\n"
            f"{YOLO_MODEL_PATH}"
        )

    print("Loading YOLO26s...")

    _yolo_model = YOLO(
        YOLO_MODEL_PATH
    )

    print(
        "YOLO26s loaded successfully"
    )

    return _yolo_model


# ============================================================
# LOAD DISEASE MODEL
# ============================================================

def load_disease_model():

    global _disease_model

    if _disease_model is not None:
        return _disease_model

    if not os.path.exists(DISEASE_MODEL_PATH):

        raise FileNotFoundError(
            f"Disease model not found:\n"
            f"{DISEASE_MODEL_PATH}"
        )

    print(
        "Loading EfficientNetV2-S..."
    )

    # 98 disease classes
    model = efficientnet_v2_s(
        weights=None
    )

    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        98
    )

    checkpoint = torch.load(
        DISEASE_MODEL_PATH,
        map_location=DEVICE
    )

    # Handle different checkpoint formats
    if isinstance(
        checkpoint,
        dict
    ) and "model_state_dict" in checkpoint:

        state_dict = checkpoint[
            "model_state_dict"
        ]

    elif isinstance(
        checkpoint,
        dict
    ) and "state_dict" in checkpoint:

        state_dict = checkpoint[
            "state_dict"
        ]

    else:

        state_dict = checkpoint


    model.load_state_dict(
        state_dict
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    _disease_model = model

    print(
        "EfficientNetV2-S loaded successfully"
    )

    print(
        "98 disease classes loaded"
    )

    return _disease_model


# ============================================================
# LOAD SEVERITY MODEL
# ============================================================

def load_severity_model():

    global _severity_model

    if _severity_model is not None:
        return _severity_model

    if not os.path.exists(
        SEVERITY_MODEL_PATH
    ):

        raise FileNotFoundError(
            f"Severity model not found:\n"
            f"{SEVERITY_MODEL_PATH}"
        )

    print(
        "Loading DeepLabV3..."
    )

    model = deeplabv3_resnet50(
        weights=None,
        weights_backbone=None,
        num_classes=1
    )

    checkpoint = torch.load(
        SEVERITY_MODEL_PATH,
        map_location=DEVICE
    )

    # Handle different checkpoint formats
    if isinstance(
        checkpoint,
        dict
    ) and "model_state_dict" in checkpoint:

        state_dict = checkpoint[
            "model_state_dict"
        ]

    elif isinstance(
        checkpoint,
        dict
    ) and "state_dict" in checkpoint:

        state_dict = checkpoint[
            "state_dict"
        ]

    else:

        state_dict = checkpoint


    model.load_state_dict(
        state_dict
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    _severity_model = model

    print(
        "DeepLabV3 loaded successfully"
    )

    print(
        "Output classes: 1"
    )

    return _severity_model


# ============================================================
# LOAD ALL MODELS
# ============================================================

def load_models():

    print("\nLoading all AI models...")

    load_yolo_model()

    load_disease_model()

    load_severity_model()

    load_class_mapping()

    print(
        "All AI models loaded successfully\n"
    )


# ============================================================
# DISEASE IMAGE TRANSFORM
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


# ============================================================
# SEVERITY IMAGE TRANSFORM
# ============================================================

severity_transform = transforms.Compose([

    transforms.Resize(
        (384, 384)
    ),

    transforms.ToTensor()
])


# ============================================================
# FORMAT CLASS NAME
# ============================================================

def format_class_name(
    class_name
):

    """
    Converts:

        Tomato__Late_Blight

    into:

        Tomato
        Late Blight
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
    ).strip()

    disease = disease.replace(
        "_",
        " "
    ).strip()


    return (
        crop.title(),
        disease.title()
    )


# ============================================================
# GET CLASS NAME FROM MAPPING
# ============================================================

def get_class_name(
    class_index
):

    mapping = load_class_mapping()


    # Mapping can be either:
    # {"0": "Tomato__Healthy"}
    # or a list

    if isinstance(
        mapping,
        dict
    ):

        class_name = mapping.get(
            str(class_index)
        )

        if class_name is None:

            class_name = mapping.get(
                class_index
            )

    else:

        class_name = mapping[
            class_index
        ]


    if class_name is None:

        return "Unknown__Unknown"


    return class_name


# ============================================================
# SEVERITY CATEGORY
# ============================================================

def severity_category(
    diseased_area
):

    if diseased_area <= 10:

        return "Mild"

    elif diseased_area <= 30:

        return "Moderate"

    else:

        return "Severe"


# ============================================================
# CALCULATE DISEASED AREA
# ============================================================

def calculate_diseased_area(
    mask
):

    """
    Converts the DeepLabV3 output into a percentage
    of the detected leaf area that is classified as
    diseased.

    Returns:
        percentage
    """

    mask = mask.squeeze()

    if mask.numel() == 0:

        return 0.0


    # Sigmoid because model has one output channel
    probabilities = torch.sigmoid(
        mask
    )


    # Binary segmentation threshold
    binary_mask = (
        probabilities > 0.5
    )


    diseased_pixels = (
        binary_mask.sum().item()
    )

    total_pixels = (
        binary_mask.numel()
    )


    if total_pixels == 0:

        return 0.0


    percentage = (
        diseased_pixels
        /
        total_pixels
        *
        100
    )


    return float(
        percentage
    )


# ============================================================
# ANALYZE IMAGE
# ============================================================

def analyze_image(
    image_path,
    confidence_threshold=0.25
):

    """
    Complete AI pipeline:

        Image
          ↓
        YOLO leaf detection
          ↓
        EfficientNetV2-S disease classification
          ↓
        DeepLabV3 severity segmentation
          ↓
        Recommendation engine
          ↓
        Fertilizer recommendation
          ↓
        Online product link
    """

    try:

        # ====================================================
        # CHECK FILE
        # ====================================================

        if not os.path.exists(
            image_path
        ):

            return {

                "success": False,

                "message":
                    "Image file not found.",

                "leaves_detected": 0,

                "processed_leaves": 0,

                "results": []
            }


        # ====================================================
        # LOAD MODELS
        # ====================================================

        load_models()


        yolo = _yolo_model

        disease_model = (
            _disease_model
        )

        severity_model = (
            _severity_model
        )


        # ====================================================
        # OPEN IMAGE
        # ====================================================

        original_image = Image.open(
            image_path
        ).convert("RGB")


        # ====================================================
        # YOLO LEAF DETECTION
        # ====================================================

        detection_results = yolo.predict(

            source=image_path,

            conf=confidence_threshold,

            verbose=False,

            device=DEVICE
        )


        if not detection_results:

            return {

                "success": True,

                "message":
                    "No leaves detected.",

                "leaves_detected": 0,

                "processed_leaves": 0,

                "results": []
            }


        result = detection_results[0]

        boxes = result.boxes


        if boxes is None or len(boxes) == 0:

            return {

                "success": True,

                "message":
                    "No leaves detected.",

                "leaves_detected": 0,

                "processed_leaves": 0,

                "results": []
            }


        # ====================================================
        # PROCESS EACH LEAF
        # ====================================================

        leaf_results = []


        image_width, image_height = (
            original_image.size
        )


        for leaf_number, box in enumerate(

            boxes,

            start=1

        ):

            try:

                # ==========================================
                # BOUNDING BOX
                # ==========================================

                coordinates = (
                    box.xyxy[0]
                    .detach()
                    .cpu()
                    .tolist()
                )


                x1, y1, x2, y2 = (
                    coordinates
                )


                # Keep coordinates inside image
                x1 = max(
                    0,
                    min(
                        int(x1),
                        image_width - 1
                    )
                )

                y1 = max(
                    0,
                    min(
                        int(y1),
                        image_height - 1
                    )
                )

                x2 = max(
                    1,
                    min(
                        int(x2),
                        image_width
                    )
                )

                y2 = max(
                    1,
                    min(
                        int(y2),
                        image_height
                    )
                )


                # Invalid box
                if x2 <= x1 or y2 <= y1:

                    continue


                # ==========================================
                # LEAF DETECTION CONFIDENCE
                # ==========================================

                leaf_confidence = float(
                    box.conf[0]
                    .detach()
                    .cpu()
                    .item()
                )


                # ==========================================
                # CROP LEAF
                # ==========================================

                leaf_image = (
                    original_image.crop(
                        (
                            x1,
                            y1,
                            x2,
                            y2
                        )
                    )
                )


                if leaf_image.width <= 1 or leaf_image.height <= 1:

                    continue


                # ==========================================
                # DISEASE CLASSIFICATION
                # ==========================================

                disease_tensor = (
                    disease_transform(
                        leaf_image
                    )
                    .unsqueeze(0)
                    .to(DEVICE)
                )


                with torch.no_grad():

                    disease_output = (
                        disease_model(
                            disease_tensor
                        )
                    )


                    disease_probabilities = (
                        torch.softmax(
                            disease_output,
                            dim=1
                        )
                    )


                    disease_confidence, class_index_tensor = (
                        torch.max(
                            disease_probabilities,
                            dim=1
                        )
                    )


                class_index = int(
                    class_index_tensor.item()
                )


                disease_confidence = float(
                    disease_confidence.item()
                    *
                    100
                )


                # ==========================================
                # CLASS NAME
                # ==========================================

                class_name = (
                    get_class_name(
                        class_index
                    )
                )


                crop, disease = (
                    format_class_name(
                        class_name
                    )
                )


                # ==========================================
                # SEVERITY SEGMENTATION
                # ==========================================

                severity_tensor = (
                    severity_transform(
                        leaf_image
                    )
                    .unsqueeze(0)
                    .to(DEVICE)
                )


                with torch.no_grad():

                    severity_output = (
                        severity_model(
                            severity_tensor
                        )
                    )


                    # DeepLabV3 returns:
                    # {"out": tensor}

                    if isinstance(
                        severity_output,
                        dict
                    ):

                        severity_logits = (
                            severity_output[
                                "out"
                            ]
                        )

                    else:

                        severity_logits = (
                            severity_output
                        )


                # ==========================================
                # DISEASED AREA
                # ==========================================

                diseased_area = (
                    calculate_diseased_area(
                        severity_logits[0]
                    )
                )


                diseased_area = round(
                    diseased_area,
                    2
                )


                # ==========================================
                # SEVERITY
                # ==========================================

                severity = (
                    severity_category(
                        diseased_area
                    )
                )


                # ==========================================
                # RECOMMENDATIONS
                # ==========================================

                recommendation_result = (
                    get_recommendation(

                        crop=crop,

                        disease=disease,

                        severity=severity,

                        diseased_area=diseased_area
                    )
                )


                # ==========================================
                # FINAL LEAF RESULT
                # ==========================================

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
                            leaf_confidence * 100,
                            2
                        ),

                    "class_index":
                        class_index,

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
                        diseased_area,

                    "severity":
                        severity,

                    # Disease recommendations
                    "recommendations":
                        recommendation_result[
                            "recommendations"
                        ],

                    # Fertilizer recommendation
                    "fertilizer_recommendation":
                        recommendation_result[
                            "fertilizer"
                        ]
                }


                leaf_results.append(
                    leaf_result
                )


            except Exception as leaf_error:

                print(
                    f"Error processing leaf "
                    f"{leaf_number}: "
                    f"{leaf_error}"
                )

                continue


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return {

            "success": True,

            "message":
                "Image analyzed successfully.",

            "leaves_detected":
                len(boxes),

            "processed_leaves":
                len(leaf_results),

            "results":
                leaf_results
        }


    except Exception as error:

        print(
            "AI pipeline error:",
            error
        )

        return {

            "success": False,

            "message":
                f"AI analysis failed: {str(error)}",

            "leaves_detected": 0,

            "processed_leaves": 0,

            "results": []
        }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "AGRIVISIONAI AI SERVICE TEST"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    try:

        load_models()

        print(
            "\nAll models loaded successfully."
        )

    except Exception as error:

        print(
            "\nModel loading failed:"
        )

        print(error)

        sys.exit(1)


    # --------------------------------------------------------
    # Test image
    # --------------------------------------------------------

    test_image = os.path.join(

        BASE_DIR,

        "test_images",

        "test.jpg"
    )


    if not os.path.exists(
        test_image
    ):

        print(
            "\nTest image not found:"
        )

        print(test_image)

        print(
            "\nAI service model loading test complete."
        )

        sys.exit(0)


    # --------------------------------------------------------
    # Run pipeline
    # --------------------------------------------------------

    print(
        "\nRunning AI pipeline..."
    )

    result = analyze_image(
        test_image
    )


    # --------------------------------------------------------
    # Print result
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "AI PIPELINE RESULT"
    )

    print("=" * 60)


    print(
        "Success:",
        result["success"]
    )

    print(
        "Message:",
        result["message"]
    )

    print(
        "Leaves detected:",
        result["leaves_detected"]
    )

    print(
        "Leaves processed:",
        result["processed_leaves"]
    )


    for leaf in result["results"]:

        print("\n" + "-" * 60)

        print(
            "Leaf:",
            leaf["leaf_number"]
        )

        print(
            "Crop:",
            leaf["crop"]
        )

        print(
            "Disease:",
            leaf["disease"]
        )

        print(
            "Disease confidence:",
            f'{leaf["disease_confidence"]}%'
        )

        print(
            "Diseased area:",
            f'{leaf["diseased_area_percent"]}%'
        )

        print(
            "Severity:",
            leaf["severity"]
        )


        # ----------------------------------------------------
        # Disease recommendations
        # ----------------------------------------------------

        print(
            "\nRecommendations:"
        )

        for recommendation in (
            leaf["recommendations"]
        ):

            print(
                "•",
                recommendation
            )


        # ----------------------------------------------------
        # Fertilizer
        # ----------------------------------------------------

        fertilizer = (
            leaf[
                "fertilizer_recommendation"
            ]
        )


        print(
            "\nFertilizer Recommendation:"
        )

        print(
            "Fertilizer:",
            fertilizer[
                "fertilizer"
            ]
        )

        print(
            "Nutrient focus:",
            fertilizer[
                "nutrient_focus"
            ]
        )

        print(
            "Reason:",
            fertilizer[
                "reason"
            ]
        )

        print(
            "Buy online:",
            fertilizer[
                "buy_online"
            ]
        )

        print(
            "Buy link:",
            fertilizer[
                "buy_url"
            ]
        )


    print("\n" + "=" * 60)

    print(
        "AI SERVICE TEST COMPLETE"
    )

    print("=" * 60)