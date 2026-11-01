from datetime import datetime

from database.db import db


# ============================================================
# USER
# ============================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    state = db.Column(
        db.String(80)
    )

    preferred_language = db.Column(
        db.String(30),
        default="English"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    profile = db.relationship(
        "FarmerProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    predictions = db.relationship(
        "Prediction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ============================================================
# FARMER PROFILE
# ============================================================

class FarmerProfile(db.Model):

    __tablename__ = "farmer_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        unique=True,
        nullable=False
    )


    # ========================================================
    # PERSONAL INFORMATION
    # ========================================================

    phone = db.Column(
        db.String(20)
    )

    district = db.Column(
        db.String(100)
    )

    village = db.Column(
        db.String(100)
    )


    # ========================================================
    # FARM INFORMATION
    # ========================================================

    farm_size = db.Column(
        db.Float
    )

    farm_size_unit = db.Column(
        db.String(20),
        default="acres"
    )

    primary_crop = db.Column(
        db.String(100)
    )


    # ========================================================
    # SOIL INFORMATION
    # ========================================================

    soil_type = db.Column(
        db.String(100)
    )

    soil_ph = db.Column(
        db.Float
    )


    # ========================================================
    # TIMESTAMPS
    # ========================================================

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# ============================================================
# PREDICTION HISTORY
# ============================================================

class Prediction(db.Model):

    __tablename__ = "predictions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # ========================================================
    # USER
    # ========================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=False
    )


    # ========================================================
    # IMAGE
    # ========================================================

    image_filename = db.Column(
        db.String(255)
    )


    # ========================================================
    # AI RESULT
    # ========================================================

    leaf_number = db.Column(
        db.Integer
    )

    crop = db.Column(
        db.String(100)
    )

    disease = db.Column(
        db.String(150)
    )

    disease_confidence = db.Column(
        db.Float
    )

    leaf_detection_confidence = db.Column(
        db.Float
    )

    diseased_area_percent = db.Column(
        db.Float
    )

    severity = db.Column(
        db.String(30)
    )


    # ========================================================
    # FERTILIZER
    # ========================================================

    fertilizer = db.Column(
        db.String(150)
    )

    nutrient_focus = db.Column(
        db.String(150)
    )

    fertilizer_reason = db.Column(
        db.Text
    )

    fertilizer_buy_url = db.Column(
        db.Text
    )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    recommendations = db.Column(
        db.Text
    )


    # ========================================================
    # TIMESTAMP
    # ========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )