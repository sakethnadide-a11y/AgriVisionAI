import os
import torch
import torch.nn as nn
from torchvision.models.segmentation import deeplabv3_resnet50
from torchvision.models import efficientnet_v2_s
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


# ============================================================
# CHECK FILES
# ============================================================

print("=" * 60)
print("CHECKING MODEL FILES")
print("=" * 60)

for name, path in [
    ("YOLO", YOLO_PATH),
    ("Disease Model", DISEASE_PATH),
    ("Severity Model", SEVERITY_PATH)
]:

    print(f"{name}: ", end="")

    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024 ** 2)
        print(f"FOUND ({size_mb:.2f} MB)")
    else:
        print("NOT FOUND ❌")


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("\n" + "=" * 60)
print("DEVICE")
print("=" * 60)

print("PyTorch:", torch.__version__)
print("Device:", device)


# ============================================================
# 1. YOLO LEAF DETECTOR
# ============================================================

print("\n" + "=" * 60)
print("1. LOADING YOLO LEAF DETECTOR")
print("=" * 60)

try:

    yolo_model = YOLO(YOLO_PATH)

    print("YOLO model loaded successfully ✅")

except Exception as e:

    print("YOLO loading failed ❌")
    print(e)


# ============================================================
# 2. EFFICIENTNET DISEASE MODEL
# ============================================================

print("\n" + "=" * 60)
print("2. LOADING EFFICIENTNET DISEASE MODEL")
print("=" * 60)

try:

    disease_checkpoint = torch.load(
        DISEASE_PATH,
        map_location="cpu"
    )

    # Our model was trained with 98 combined crop+disease classes
    disease_model = efficientnet_v2_s(
        weights=None
    )

    disease_model.classifier[1] = nn.Linear(
        disease_model.classifier[1].in_features,
        98
    )

    # Handle either a raw state_dict or checkpoint dictionary
    if "model_state_dict" in disease_checkpoint:

        disease_state = disease_checkpoint[
            "model_state_dict"
        ]

    else:

        disease_state = disease_checkpoint

    disease_model.load_state_dict(
        disease_state
    )

    disease_model = disease_model.to(device)
    disease_model.eval()

    print("EfficientNetV2-S loaded successfully ✅")
    print("Output classes:", 98)


except Exception as e:

    print("EfficientNet loading failed ❌")
    print(e)


# ============================================================
# 3. DEEPLABV3 SEVERITY MODEL
# ============================================================

print("\n" + "=" * 60)
print("3. LOADING DEEPLABV3 SEVERITY MODEL")
print("=" * 60)

try:

    severity_checkpoint = torch.load(
        SEVERITY_PATH,
        map_location="cpu"
    )

    severity_model = deeplabv3_resnet50(
        weights=None,
        weights_backbone=None,
        num_classes=1
    )

    if "model_state_dict" in severity_checkpoint:

        severity_state = severity_checkpoint[
            "model_state_dict"
        ]

    else:

        severity_state = severity_checkpoint

    severity_model.load_state_dict(
        severity_state
    )

    severity_model = severity_model.to(device)
    severity_model.eval()

    print("DeepLabV3 loaded successfully ✅")
    print("Output classes:", 1)


except Exception as e:

    print("DeepLabV3 loading failed ❌")
    print(e)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("MODEL LOADING TEST COMPLETE")
print("=" * 60)