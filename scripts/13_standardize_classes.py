from pathlib import Path

DATASET_DIR = Path(
    r"datasets/AgriVisionAI_Dataset"
)

# Current class name -> standardized class name
# Crop folder remains unchanged.

RENAMES = {
    # Apple
    ("Apple", "Apple___Black_rot"): "Black_Rot",
    ("Apple", "Apple_Cedar_Rust"): "Cedar_Apple_Rust",
    ("Apple", "Apple_Healthy"): "Healthy",
    ("Apple", "Apple_Scab"): "Apple_Scab",

    # Banana
    ("Banana", "Banana_Black_Sigatoka"): "Black_Sigatoka",
    ("Banana", "Banana_Bract_Mosaic_Virus"): "Bract_Mosaic_Virus",
    ("Banana", "Banana_Cordana_Leaf_Spot"): "Cordana_Leaf_Spot",
    ("Banana", "Banana_Healthy"): "Healthy",
    ("Banana", "Banana_Moko_Disease"): "Moko_Disease",
    ("Banana", "Banana_Panama_Disease"): "Panama_Disease",
    ("Banana", "Banana_Pestalotiopsis_Leaf_Spot"): "Pestalotiopsis_Leaf_Spot",
    ("Banana", "Banana_Yellow_Sigatoka"): "Yellow_Sigatoka",

    # Blueberry
    ("Blueberry", "Blueberry_Healthy"): "Healthy",

    # Bottle Gourd
    ("Bottle_Gourd", "Bottlegourd_Anthracnose"): "Anthracnose",
    ("Bottle_Gourd", "Bottlegourd_DownyMildew"): "Downy_Mildew",
    ("Bottle_Gourd", "Bottlegourd_Healthy(3)"): "Healthy",

    # Cabbage
    ("Cabbage", "Cabbage_Alternaria_Leaf_Spot"): "Alternaria_Leaf_Spot",
    ("Cabbage", "Cabbage_Bacterial_Spot_Rot"): "Bacterial_Spot_Rot",
    ("Cabbage", "Cabbage_Black_Rot"): "Black_Rot",
    ("Cabbage", "Cabbage_Downy_Mildew"): "Downy_Mildew",
    ("Cabbage", "Cabbage_Healthy"): "Healthy",
    ("Cabbage", "Cabbage_Ring_Spot"): "Ring_Spot",

    # Capsicum
    ("Capsicum", "Capsicum_Bacterial_Spot"): "Bacterial_Spot",
    ("Capsicum", "Capsicum_Healthy(2)"): "Healthy",

    # Cauliflower
    ("Cauliflower", "Cauliflower_Bacterial_Spot_Rot"): "Bacterial_Spot_Rot",
    ("Cauliflower", "Cauliflower_Black_Rot"): "Black_Rot",
    ("Cauliflower", "Cauliflower_Downy_Mildew"): "Downy_Mildew",
    ("Cauliflower", "Cauliflower_Healthy(4)"): "Healthy",

    # Chilli
    ("Chilli", "Chili_Healthy"): "Healthy",
    ("Chilli", "Chili_Leaf_Curl_Virus"): "Leaf_Curl_Virus",
    ("Chilli", "Chili_Leaf_Spot"): "Leaf_Spot",
    ("Chilli", "Chilli_Anthracnose"): "Anthracnose",

    # Cotton
    ("Cotton", "Cotton_Bacterial_Blight"): "Bacterial_Blight",
    ("Cotton", "Cotton_Curl_Virus"): "Curl_Virus",
    ("Cotton", "Cotton_Fusarium_Wilt"): "Fusarium_Wilt",
    ("Cotton", "Cotton_Healthy"): "Healthy",
    ("Cotton", "Cotton_Powdery_Mildew"): "Powdery_Mildew",
    ("Cotton", "Cotton_Target_Spot"): "Target_Spot",

    # Cucumber
    ("Cucumber", "Cucumber_Anthracnose"): "Anthracnose",
    ("Cucumber", "Cucumber_Bacterial_Wilt"): "Bacterial_Wilt",
    ("Cucumber", "Cucumber_Gummy_Stem_Blight"): "Gummy_Stem_Blight",
    ("Cucumber", "Cucumber_Healthy"): "Healthy",

    # Groundnut
    ("Groundnut", "Groundnut_Alternaria_Leaf_Spot"): "Alternaria_Leaf_Spot",
    ("Groundnut", "Groundnut_Healthy"): "Healthy",
    ("Groundnut", "Groundnut_Leaf_Spot"): "Leaf_Spot",
    ("Groundnut", "Groundnut_Rosette_Disease"): "Rosette_Disease",
    ("Groundnut", "Groundnut_Rust(5)"): "Rust",

    # Maize
    ("Maize", "Maize_Common_Rust"): "Common_Rust",
    ("Maize", "Maize_Gray_Leaf_Spot"): "Gray_Leaf_Spot",
    ("Maize", "Maize_Healthy"): "Healthy",
    ("Maize", "Maize_Northern_Leaf_Blight"): "Northern_Leaf_Blight",

    # Mango
    ("Mango", "Mango_Anthracnose"): "Anthracnose",
    ("Mango", "Mango_Bacterial_Canker"): "Bacterial_Canker",
    ("Mango", "Mango_Die_Back"): "Die_Back",
    ("Mango", "Mango_Healthy"): "Healthy",
    ("Mango", "Mango_Powdery_Mildew"): "Powdery_Mildew",
    ("Mango", "Mango_Sooty_Mould"): "Sooty_Mould",

    # Onion
    ("Onion", "Onion_Alternaria_Leaf_Blight"): "Alternaria_Leaf_Blight",
    ("Onion", "Onion_Botrytis_Leaf_Blight"): "Botrytis_Leaf_Blight",
    ("Onion", "Onion_Healthy"): "Healthy",
    ("Onion", "Onion_Purple_Blotch"): "Purple_Blotch",
    ("Onion", "Onion_Viral_Disease"): "Viral_Disease",

    # Pea
    ("Pea", "Pea_Downy_Mildew"): "Downy_Mildew",
    ("Pea", "Pea_Healthy"): "Healthy",
    ("Pea", "Pea_Powder_Mildew"): "Powdery_Mildew",

    # Peach
    ("Peach", "Peach_Healthy"): "Healthy",

    # Potato
    ("Potato", "Potato___Early_blight"): "Early_Blight",
    ("Potato", "Potato___healthy"): "Healthy",
    ("Potato", "Potato___Late_blight"): "Late_Blight",

    # Raspberry
    ("Raspberry", "Raspberry_Healthy"): "Healthy",

    # Rice
    ("Rice", "Rice_Bacterial_Leaf_Blight"): "Bacterial_Leaf_Blight",
    ("Rice", "Rice_Brown_Spot"): "Brown_Spot",
    ("Rice", "Rice_Healthy"): "Healthy",
    ("Rice", "Rice_Leaf_Blast"): "Leaf_Blast",
    ("Rice", "Rice_Leaf_Scald"): "Leaf_Scald",
    ("Rice", "Rice_Leaf_Smut"): "Leaf_Smut",
    ("Rice", "Rice_Sheath_Blight"): "Sheath_Blight",
    ("Rice", "Rice_Tungro"): "Tungro",

    # Soybean
    ("Soyabean", "Soyabean_Frogeye_Leaf_Spot"): "Frogeye_Leaf_Spot",
    ("Soyabean", "Soyabean_Healthy"): "Healthy",
    ("Soyabean", "Soyabean_Mosaic_Virus"): "Mosaic_Virus",
    ("Soyabean", "Soyabean_Septoria_Brown_Spot"): "Septoria_Brown_Spot",

    # Sugarcane
    ("Sugarcane", "Sugarcane_Healthy"): "Healthy",
    ("Sugarcane", "Sugarcane_Mosaic_Virus"): "Mosaic_Virus",
    ("Sugarcane", "Sugarcane_Red_Rot"): "Red_Rot",
    ("Sugarcane", "Sugarcane_Rust"): "Rust",
    ("Sugarcane", "Sugarcane_Yellow_Leaf_Disease"): "Yellow_Leaf_Disease",

    # Tomato
    ("Tomato", "Tomato_Bacterial_Spot"): "Bacterial_Spot",
    ("Tomato", "Tomato_Early_Blight"): "Early_Blight",
    ("Tomato", "Tomato_Healthy"): "Healthy",
    ("Tomato", "Tomato_Late_Blight"): "Late_Blight",
    ("Tomato", "Tomato_Leaf_Mold"): "Leaf_Mold",
    ("Tomato", "Tomato_Mosaic_Virus"): "Mosaic_Virus",
    ("Tomato", "Tomato_Septoria_Leaf_Spot"): "Septoria_Leaf_Spot",
    ("Tomato", "Tomato_Target_Spot"): "Target_Spot",
    ("Tomato", "Tomato_Yellow_Leaf_Curl_Virus"): "Yellow_Leaf_Curl_Virus",

    # Wheat
    ("Wheat", "Wheat_Blast"): "Blast",
    ("Wheat", "Wheat_Common_Root_Rot"): "Common_Root_Rot",
    ("Wheat", "Wheat_Fusarium_Head_Blight"): "Fusarium_Head_Blight",
    ("Wheat", "Wheat_Healthy"): "Healthy",
    ("Wheat", "Wheat_Helminthosporium_Leaf_Blight"): "Helminthosporium_Leaf_Blight",
    ("Wheat", "Wheat_Leaf_Rust"): "Leaf_Rust",
    ("Wheat", "Wheat_Powdery_Mildew"): "Powdery_Mildew",
    ("Wheat", "Wheat_Septoria_Leaf_Blotch"): "Septoria_Leaf_Blotch",
    ("Wheat", "Wheat_Smut"): "Smut",
    ("Wheat", "Wheat_Stem_Rust"): "Stem_Rust",
    ("Wheat", "Wheat_Stripe_Rust"): "Stripe_Rust",
    ("Wheat", "Wheat_Tan_Spot(12)"): "Tan_Spot",
}


print("=" * 60)
print("AGRI VISION AI - CLASS NAME STANDARDIZATION PREVIEW")
print("=" * 60)

found = 0
missing = 0

for (crop, old_name), new_name in RENAMES.items():

    old_path = DATASET_DIR / crop / old_name
    new_path = DATASET_DIR / crop / new_name

    if old_path.exists():

        found += 1

        print(
            f"{crop:15} "
            f"{old_name:45} "
            f"-> {new_name}"
        )

        if new_path.exists() and old_path != new_path:

            print(
                "   WARNING: destination already exists!"
            )

    else:
        missing += 1


print("\n" + "=" * 60)
print("PREVIEW COMPLETE")
print("=" * 60)

print(f"\nFolders found : {found}")
print(f"Folders missing: {missing}")

print("\nNO folders were renamed.")
print("NO images were moved.")
print("\nReview the output before we perform the rename.")