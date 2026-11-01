# ============================================================
# AGRIVISIONAI RECOMMENDATION ENGINE
# ============================================================

def get_fertilizer_recommendation(
    crop,
    disease,
    severity,
    diseased_area,
    soil_n=None,
    soil_p=None,
    soil_k=None,
    soil_ph=None
):
    """
    Generate a general fertilizer recommendation.

    Soil values are optional.

    We intentionally do NOT calculate an exact fertilizer
    dose from the image alone.
    """

    crop_lower = crop.lower().strip()

    recommendation = {
        "nutrient_focus": "Balanced NPK",
        "fertilizer": "NPK 19:19:19",
        "reason": (
            "A balanced NPK formulation can be considered "
            "when a soil test is not available. Exact "
            "nutrient requirements should be based on "
            "soil conditions, crop stage and local "
            "agricultural recommendations."
        ),
        "soil_test_used": False,
        "buy_online": True,
        "buy_url": (
            "https://www.kisanshop.in/product/"
            "nfl-kisan-triple-effect-npk-191919-water-soluble-fertilizer"
        ),
        "buy_label": "Buy NPK 19:19:19 Online"
    }


    # ========================================================
    # IF SOIL DATA IS AVAILABLE
    # ========================================================

    soil_values_available = all(
        value is not None
        for value in [
            soil_n,
            soil_p,
            soil_k,
            soil_ph
        ]
    )


    if soil_values_available:

        recommendation["soil_test_used"] = True

        nutrient_focus = []


        # ----------------------------------------------------
        # Simple relative interpretation
        #
        # These are NOT laboratory diagnostic thresholds.
        # They are only used to indicate which nutrient
        # deserves attention relative to the others.
        # ----------------------------------------------------

        values = {
            "Nitrogen": float(soil_n),
            "Phosphorus": float(soil_p),
            "Potassium": float(soil_k)
        }


        lowest_nutrient = min(
            values,
            key=values.get
        )


        nutrient_focus.append(
            lowest_nutrient
        )


        recommendation["nutrient_focus"] = (
            f"Pay attention to {lowest_nutrient}"
        )


        recommendation["reason"] = (
            f"The supplied soil values indicate "
            f"{lowest_nutrient} is the lowest of the "
            f"three supplied N-P-K values. This is only "
            f"a screening-level indication; actual "
            f"fertilizer selection and application rate "
            f"should follow a soil-test interpretation "
            f"and crop-specific recommendation."
        )


    # ========================================================
    # CROP-SPECIFIC GENERAL INFORMATION
    # ========================================================

    if crop_lower in [
        "tomato",
        "chilli",
        "capsicum",
        "cucumber",
        "cabbage",
        "cauliflower"
    ]:

        recommendation["crop_note"] = (
            "For vegetable crops, nutrient requirements "
            "vary with crop stage and production system. "
            "Use a crop-specific nutrient recommendation "
            "where available."
        )


    elif crop_lower in [
        "wheat",
        "rice",
        "maize"
    ]:

        recommendation["crop_note"] = (
            "For field crops, fertilizer requirements "
            "should be based on soil-test results, crop "
            "stage and the locally recommended nutrient "
            "schedule."
        )


    elif crop_lower in [
        "mango",
        "banana",
        "apple"
    ]:

        recommendation["crop_note"] = (
            "For fruit crops, nutrient requirements vary "
            "with plant age, growth stage, soil condition "
            "and production system."
        )


    else:

        recommendation["crop_note"] = (
            "Use crop-specific fertilizer guidance "
            "together with soil-test information where "
            "available."
        )


    # ========================================================
    # APPLICATION SAFETY
    # ========================================================

    recommendation["application_note"] = (
        "Do not apply fertilizer solely because a disease "
        "was detected. Follow the product label and "
        "crop-specific/local agricultural guidance. "
        "Avoid over-application."
    )


    return recommendation


# ============================================================
# DISEASE RECOMMENDATIONS
# ============================================================

def get_recommendation(
    crop,
    disease,
    severity,
    diseased_area,
    soil_n=None,
    soil_p=None,
    soil_k=None,
    soil_ph=None
):

    crop = crop.lower().strip()

    disease = disease.lower().strip()

    severity = severity.lower().strip()


    recommendations = []


    # ========================================================
    # SEVERITY
    # ========================================================

    if severity == "mild":

        recommendations.append(
            "Monitor the affected plant regularly "
            "for progression of symptoms."
        )

        recommendations.append(
            "Remove visibly affected plant material "
            "where practical."
        )


    elif severity == "moderate":

        recommendations.append(
            "Remove heavily affected plant material "
            "where practical."
        )

        recommendations.append(
            "Increase monitoring of nearby plants "
            "for similar symptoms."
        )

        recommendations.append(
            "Improve field sanitation and avoid "
            "conditions that favor disease spread."
        )


    elif severity == "severe":

        recommendations.append(
            "Isolate heavily affected plants where "
            "practical to reduce disease spread."
        )

        recommendations.append(
            "Remove severely affected plant material "
            "using appropriate sanitation practices."
        )

        recommendations.append(
            "Inspect surrounding plants immediately "
            "for similar symptoms."
        )


    # ========================================================
    # BACTERIAL DISEASE
    # ========================================================

    if "bacterial" in disease:

        recommendations.append(
            "Avoid unnecessary overhead irrigation "
            "and prolonged leaf wetness."
        )

        recommendations.append(
            "Sanitize tools after handling infected "
            "plant material."
        )


    # ========================================================
    # BLIGHT
    # ========================================================

    if "blight" in disease:

        recommendations.append(
            "Remove affected leaves where practical "
            "and maintain good field sanitation."
        )

        recommendations.append(
            "Avoid prolonged leaf wetness and improve "
            "air circulation around plants."
        )


    # ========================================================
    # RUST
    # ========================================================

    if "rust" in disease:

        recommendations.append(
            "Remove heavily infected leaves where "
            "practical."
        )

        recommendations.append(
            "Improve air circulation and avoid "
            "excessive leaf moisture."
        )


    # ========================================================
    # MILDEW
    # ========================================================

    if "mildew" in disease:

        recommendations.append(
            "Improve air circulation around plants."
        )

        recommendations.append(
            "Avoid excessive humidity and prolonged "
            "leaf wetness where possible."
        )


    # ========================================================
    # VIRAL DISEASE
    # ========================================================

    if (
        "mosaic" in disease
        or "virus" in disease
    ):

        recommendations.append(
            "Inspect the plant and surrounding plants "
            "for similar viral symptoms."
        )

        recommendations.append(
            "Control known insect vectors according "
            "to locally approved agricultural practices."
        )

        recommendations.append(
            "Remove severely affected plants where "
            "appropriate to limit disease spread."
        )


    # ========================================================
    # ANTHRACNOSE
    # ========================================================

    if "anthracnose" in disease:

        recommendations.append(
            "Remove infected plant material and "
            "maintain good field sanitation."
        )

        recommendations.append(
            "Avoid prolonged moisture on plant surfaces."
        )


    # ========================================================
    # LEAF SPOT
    # ========================================================

    if "leaf spot" in disease:

        recommendations.append(
            "Remove severely affected leaves where "
            "practical."
        )

        recommendations.append(
            "Maintain field sanitation and avoid "
            "unnecessary leaf wetness."
        )


    # ========================================================
    # CROP-SPECIFIC BASIC ADVICE
    # ========================================================

    if crop == "tomato":

        recommendations.append(
            "Maintain adequate spacing and inspect "
            "nearby tomato plants regularly."
        )


    elif crop == "potato":

        recommendations.append(
            "Monitor surrounding potato plants "
            "for disease progression."
        )


    elif crop == "rice":

        recommendations.append(
            "Monitor neighboring rice plants and "
            "maintain appropriate field management."
        )


    elif crop == "wheat":

        recommendations.append(
            "Inspect nearby wheat plants for "
            "similar symptoms."
        )


    elif crop == "banana":

        recommendations.append(
            "Inspect surrounding banana plants "
            "and maintain plantation sanitation."
        )


    # ========================================================
    # DISEASED AREA
    # ========================================================

    recommendations.append(
        f"Estimated diseased area: "
        f"{diseased_area:.2f}%."
    )


    # ========================================================
    # FERTILIZER
    # ========================================================

    fertilizer = get_fertilizer_recommendation(

        crop=crop,

        disease=disease,

        severity=severity,

        diseased_area=diseased_area,

        soil_n=soil_n,

        soil_p=soil_p,

        soil_k=soil_k,

        soil_ph=soil_ph
    )


    # ========================================================
    # GENERAL DISCLAIMER
    # ========================================================

    recommendations.append(
        "Use locally approved agricultural products "
        "and follow their label instructions. For severe "
        "or uncertain cases, consult a qualified "
        "agricultural expert."
    )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_recommendations = []


    for recommendation in recommendations:

        if recommendation not in unique_recommendations:

            unique_recommendations.append(
                recommendation
            )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "crop":
            crop.title(),

        "disease":
            disease.title(),

        "severity":
            severity.title(),

        "diseased_area_percent":
            round(
                diseased_area,
                2
            ),

        "recommendations":
            unique_recommendations,

        "fertilizer":
            fertilizer
    }