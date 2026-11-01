import sys
import os


# Add project root
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from recommendation_engine import (
    get_recommendation
)


result = get_recommendation(

    crop="Cabbage",

    disease="Black Rot",

    severity="Moderate",

    diseased_area=25.82
)


print("=" * 60)
print("AGRIVISIONAI RECOMMENDATION TEST")
print("=" * 60)


print(
    "Crop:",
    result["crop"]
)

print(
    "Disease:",
    result["disease"]
)

print(
    "Severity:",
    result["severity"]
)

print(
    "Diseased Area:",
    result["diseased_area_percent"],
    "%"
)


print("\nDisease Recommendations:")

for number, recommendation in enumerate(

    result["recommendations"],

    start=1

):

    print(
        f"{number}. {recommendation}"
    )


# ============================================================
# FERTILIZER
# ============================================================

fertilizer = result[
    "fertilizer"
]


print("\n" + "=" * 60)
print("FERTILIZER RECOMMENDATION")
print("=" * 60)


print(
    "Nutrient focus:",
    fertilizer[
        "nutrient_focus"
    ]
)


print(
    "Fertilizer:",
    fertilizer[
        "fertilizer"
    ]
)


print(
    "Reason:",
    fertilizer[
        "reason"
    ]
)


print(
    "Soil test used:",
    fertilizer[
        "soil_test_used"
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


print(
    "Application note:",
    fertilizer[
        "application_note"
    ]
)


print("=" * 60)