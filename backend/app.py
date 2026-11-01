from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

import os
import uuid
import json
import requests
from datetime import datetime, timedelta

from extensions import bcrypt, mail
from flask_mail import Message

from config import Config

from database.db import db
from database.models import (
    User,
    FarmerProfile,
    Prediction
)

from otp_utils import generate_otp
from email_service import send_otp_email

from ai_service import analyze_image


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# JINJA FILTERS
# ============================================================

@app.template_filter("from_json")
def from_json_filter(value):

    if not value:
        return []

    try:
        return json.loads(value)

    except (
        TypeError,
        json.JSONDecodeError
    ):
        return []


# ============================================================
# USER HELPERS
# ============================================================

def get_current_user():

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        return None

    return User.query.get(
        user_id
    )


def ensure_farmer_profile(user):

    if not user:
        return None

    profile = FarmerProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:

        profile = FarmerProfile(
            user_id=user.id
        )

        db.session.add(
            profile
        )

        db.session.commit()

    return profile


# ============================================================
# DATABASE
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name"
        )

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )

        state = request.form.get(
            "state"
        )

        preferred_language = request.form.get(
            "preferred_language"
        ) or "English"


        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not full_name:
            return "Full name is required."

        if not email:
            return "Email is required."

        if not password:
            return "Password is required."


        # ----------------------------------------------------
        # Existing user
        # ----------------------------------------------------

        existing_user = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )

        if existing_user:

            return "Email already exists."


        # ----------------------------------------------------
        # Password hash
        # ----------------------------------------------------

        hashed_password = (
            bcrypt
            .generate_password_hash(
                password
            )
            .decode("utf-8")
        )


        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_password,
            state=state,
            preferred_language=preferred_language
        )

        db.session.add(
            user
        )

        db.session.commit()


        # ----------------------------------------------------
        # Create farmer profile
        # ----------------------------------------------------

        profile = FarmerProfile(
            user_id=user.id
        )

        db.session.add(
            profile
        )

        db.session.commit()


        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email"
        )

        password = request.form.get(
            "password"
        )


        user = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )


        if user and bcrypt.check_password_hash(
            user.password_hash,
            password
        ):

            otp = generate_otp()


            session["pending_user"] = (
                user.id
            )

            session["pending_name"] = (
                user.full_name
            )

            session["pending_email"] = (
                user.email
            )

            session["otp"] = otp


            send_otp_email(
                user.email,
                otp
            )


            return redirect(
                url_for(
                    "verify_otp"
                )
            )


        return (
            "Invalid Email or Password"
        )


    return render_template(
        "login.html"
    )


# ============================================================
# VERIFY OTP
# ============================================================

@app.route(
    "/verify-otp",
    methods=["GET", "POST"]
)
def verify_otp():

    if "otp" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        entered_otp = request.form.get(
            "otp"
        )


        if (
            entered_otp
            == session["otp"]
        ):

            session["user_id"] = (
                session["pending_user"]
            )

            session["user_name"] = (
                session["pending_name"]
            )


            session.pop(
                "otp",
                None
            )

            session.pop(
                "pending_user",
                None
            )

            session.pop(
                "pending_name",
                None
            )

            session.pop(
                "pending_email",
                None
            )


            return redirect(
                url_for(
                    "dashboard"
                )
            )


        return "Invalid OTP"


    return render_template(
        "verify_otp.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    user = get_current_user()

    if not user:

        session.clear()

        return redirect(
            url_for("login")
        )


    predictions = (
        Prediction.query
        .filter_by(
            user_id=user.id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .all()
    )


    total_scans = len(
        predictions
    )


    healthy_count = sum(
        1
        for p in predictions
        if p.disease
        and p.disease.lower()
        in [
            "healthy",
            "healthy crop",
            "healthy leaf"
        ]
    )


    disease_count = (
        total_scans
        - healthy_count
    )


    healthy_percentage = (

        round(
            (
                healthy_count
                / total_scans
            ) * 100
        )
        if total_scans
        else 0
    )


    recent_predictions = predictions[:5]


    return render_template(
        "dashboard.html",

        username=session[
            "user_name"
        ],

        total_scans=total_scans,

        healthy_percentage=(
            healthy_percentage
        ),

        diseases_detected=(
            disease_count
        ),

        model_accuracy=97.63,

        recent_predictions=(
            recent_predictions
        )
    )


# ============================================================
# SCAN PAGE
# ============================================================

@app.route("/scan")
def scan():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "scan.html",

        username=session[
            "user_name"
        ]
    )


# ============================================================
# AI IMAGE ANALYSIS
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    # --------------------------------------------------------
    # Login check
    # --------------------------------------------------------

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "message": "No image was uploaded."
        }), 400


    file = request.files[
        "image"
    ]


    if file.filename == "":

        return jsonify({
            "success": False,
            "message": "No image selected."
        }), 400


    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not allowed_file(
        file.filename
    ):

        return jsonify({
            "success": False,
            "message": (
                "Unsupported image format. "
                "Use JPG, JPEG, PNG or WEBP."
            )
        }), 400


    # --------------------------------------------------------
    # Create unique filename
    # --------------------------------------------------------

    extension = (
        file.filename
        .rsplit(
            ".",
            1
        )[1]
        .lower()
    )


    unique_filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )


    image_path = os.path.join(
        app.config[
            "UPLOAD_FOLDER"
        ],
        unique_filename
    )


    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    file.save(
        image_path
    )


    # --------------------------------------------------------
    # Run AI
    # --------------------------------------------------------

    try:

        result = analyze_image(
            image_path
        )


        # ----------------------------------------------------
        # Save predictions to database
        # ----------------------------------------------------

        user = get_current_user()


        if user:

            results = result.get(
                "results",
                []
            )


            # Some pipelines return a single
            # result instead of results[]
            if not results:

                if (
                    "crop" in result
                    or "disease" in result
                ):

                    results = [
                        result
                    ]


            for index, item in enumerate(
                results,
                start=1
            ):

                if not isinstance(
                    item,
                    dict
                ):
                    continue


                crop = item.get(
                    "crop",
                    "Unknown"
                )

                disease = item.get(
                    "disease",
                    "Unknown"
                )


                disease_confidence = (
                    item.get(
                        "disease_confidence"
                    )
                    or item.get(
                        "confidence"
                    )
                    or 0
                )


                leaf_detection_confidence = (
                    item.get(
                        "leaf_detection_confidence"
                    )
                    or item.get(
                        "leaf_confidence"
                    )
                    or 0
                )


                diseased_area = (
                    item.get(
                        "diseased_area_percent"
                    )
                    or item.get(
                        "diseased_area"
                    )
                    or 0
                )


                severity = item.get(
                    "severity",
                    "Unknown"
                )


                fertilizer_data = (
                    item.get(
                        "fertilizer",
                        {}
                    )
                )


                if not isinstance(
                    fertilizer_data,
                    dict
                ):

                    fertilizer_data = {}


                fertilizer = (
                    fertilizer_data.get(
                        "fertilizer"
                    )
                    or item.get(
                        "fertilizer"
                    )
                    or ""
                )


                nutrient_focus = (
                    fertilizer_data.get(
                        "nutrient_focus"
                    )
                    or ""
                )


                fertilizer_reason = (
                    fertilizer_data.get(
                        "reason"
                    )
                    or fertilizer_data.get(
                        "fertilizer_reason"
                    )
                    or ""
                )


                fertilizer_buy_url = (
                    fertilizer_data.get(
                        "buy_url"
                    )
                    or ""
                )


                recommendations = (
                    item.get(
                        "recommendations",
                        []
                    )
                )


                if isinstance(
                    recommendations,
                    list
                ):

                    recommendations_json = (
                        json.dumps(
                            recommendations
                        )
                    )

                elif isinstance(
                    recommendations,
                    str
                ):

                    recommendations_json = (
                        json.dumps([
                            recommendations
                        ])
                    )

                else:

                    recommendations_json = (
                        json.dumps([])
                    )


                prediction = Prediction(

                    user_id=user.id,

                    image_filename=(
                        unique_filename
                    ),

                    leaf_number=index,

                    crop=crop,

                    disease=disease,

                    disease_confidence=float(
                        disease_confidence
                        or 0
                    ),

                    leaf_detection_confidence=float(
                        leaf_detection_confidence
                        or 0
                    ),

                    diseased_area_percent=float(
                        diseased_area
                        or 0
                    ),

                    severity=severity,

                    fertilizer=fertilizer,

                    nutrient_focus=(
                        nutrient_focus
                    ),

                    fertilizer_reason=(
                        fertilizer_reason
                    ),

                    fertilizer_buy_url=(
                        fertilizer_buy_url
                    ),

                    recommendations=(
                        recommendations_json
                    )
                )


                db.session.add(
                    prediction
                )


            db.session.commit()


        return jsonify(
            result
        )


    except Exception as e:

        db.session.rollback()

        print(
            "AI analysis error:",
            str(e)
        )


        return jsonify({

            "success": False,

            "message": (
                "AI analysis failed."
            ),

            "error": str(e)

        }), 500


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    predictions = (
        Prediction.query
        .filter_by(
            user_id=session[
                "user_id"
            ]
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .all()
    )


    return render_template(
        "history.html",

        username=session[
            "user_name"
        ],

        predictions=predictions
    )


# ============================================================
# WEATHER - CURRENT BROWSER LOCATION
# ============================================================

def get_weather_by_coordinates(lat, lon, api_key):
    if not api_key:
        raise ValueError("OpenWeather API key is not configured.")
    base_url = app.config.get("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
    response = requests.get(f"{base_url}/weather", params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}, timeout=10)
    print("OPENWEATHER GPS STATUS:", response.status_code)
    if response.status_code != 200:
        print("OPENWEATHER RESPONSE:", response.text[:1000])
        response.raise_for_status()
    raw = response.json()
    main = raw.get("main", {})
    wind = raw.get("wind", {})
    condition = (raw.get("weather") or [{}])[0]
    rain = raw.get("rain", {})
    return {"city": raw.get("name", "Current Location"), "country": raw.get("sys", {}).get("country", "IN"), "latitude": lat, "longitude": lon, "temperature": main.get("temp"), "feels_like": main.get("feels_like"), "humidity": main.get("humidity"), "pressure": main.get("pressure"), "wind_speed": wind.get("speed"), "description": condition.get("description", ""), "icon": condition.get("icon", ""), "rain": rain.get("1h", 0)}


def get_profile_weather(profile, user, api_key):
    location = (profile.district if profile and profile.district else None) or (user.state if user and user.state else None) or "Vijayawada"
    geo = requests.get("https://api.openweathermap.org/geo/1.0/direct", params={"q": f"{location},IN", "limit": 1, "appid": api_key}, timeout=10)
    if geo.status_code != 200:
        geo.raise_for_status()
    locations = geo.json()
    if not locations:
        raise ValueError(f"Could not find weather location: {location}")
    return get_weather_by_coordinates(locations[0]["lat"], locations[0]["lon"], api_key)


@app.route("/weather")
def weather():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = get_current_user()
    profile = ensure_farmer_profile(user)
    api_key = app.config.get("OPENWEATHER_API_KEY")
    weather_data = None
    weather_error = None
    weather_source = "profile"
    weather_lat = None
    weather_lon = None
    try:
        lat_raw = request.args.get("lat")
        lon_raw = request.args.get("lon")
        if lat_raw is not None and lon_raw is not None:
            lat, lon = float(lat_raw), float(lon_raw)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("Invalid GPS coordinates.")
            weather_data = get_weather_by_coordinates(lat, lon, api_key)
            weather_lat, weather_lon = lat, lon
            weather_source = "current"
        else:
            weather_data = get_profile_weather(profile, user, api_key)
    except requests.exceptions.Timeout:
        weather_error = "Weather service timed out. Please try again."
    except requests.exceptions.HTTPError:
        weather_error = "Unable to retrieve weather data."
    except ValueError as e:
        weather_error = str(e)
    except Exception as e:
        print("Weather error:", e)
        weather_error = "Weather service is temporarily unavailable."
    return render_template("weather.html", username=session["user_name"], weather=weather_data, weather_error=weather_error, city=weather_data.get("city") if weather_data else "Current Location", weather_source=weather_source, weather_lat=weather_lat, weather_lon=weather_lon)


# ============================================================
# CEDA AGMARKNET MARKET PRICES
# ============================================================

CEDA_BASE_URL = "https://api.ceda.ashoka.edu.in/v1"


def ceda_request(method, endpoint, payload=None):
    api_key = app.config.get("CEDA_API_KEY") or os.environ.get("CEDA_API_KEY")
    if not api_key:
        raise ValueError("CEDA_API_KEY is not configured in config.py.")
    base_url = (app.config.get("CEDA_BASE_URL") or os.environ.get("CEDA_BASE_URL") or CEDA_BASE_URL).rstrip("/")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.request(method, f"{base_url}/{endpoint.lstrip('/')}", headers=headers, json=payload if method.upper() != "GET" else None, timeout=20)
    print("CEDA", method, endpoint, response.status_code)
    if response.status_code != 200:
        print("CEDA RESPONSE:", response.text[:2000])
        if response.status_code == 401:
            raise ValueError("CEDA rejected the API key. Check CEDA_API_KEY.")
        if response.status_code == 429:
            raise ValueError("CEDA rate limit reached. Please wait and try again.")
        response.raise_for_status()
    return response.json()


def ceda_list(data, keys):
    if isinstance(data, list): return data
    if not isinstance(data, dict): return []
    for key in keys:
        if isinstance(data.get(key), list): return data[key]
    output = data.get("output")
    if isinstance(output, dict):
        for key in keys:
            if isinstance(output.get(key), list): return output[key]
        if isinstance(output.get("data"), list): return output["data"]
    return []


def get_ceda_commodities():
    raw = ceda_list(ceda_request("GET", "/agmarknet/commodities"), ["commodities", "data", "records"])
    result=[]
    for x in raw:
        if not isinstance(x, dict): continue
        cid=x.get("commodity_id", x.get("id")); name=x.get("commodity_name") or x.get("name") or x.get("commodity")
        if cid is not None and name: result.append({"id": int(cid), "name": str(name)})
    return sorted(result, key=lambda x:x["name"].lower())


def get_ceda_geographies():
    data=ceda_request("GET", "/agmarknet/geographies")
    raw=ceda_list(data, ["geographies", "data", "records"])
    result=[]
    for x in raw:
        if not isinstance(x, dict): continue
        sid=x.get("state_id", x.get("census_state_id")); sname=x.get("state_name") or x.get("state")
        did=x.get("district_id", x.get("census_district_id")); dname=x.get("district_name") or x.get("district")
        if sid is not None and sname and did is not None and dname:
            result.append({"state_id":int(sid),"state_name":str(sname),"district_id":int(did),"district_name":str(dname)})
        for d in x.get("districts", []) if isinstance(x.get("districts"), list) else []:
            if isinstance(d,dict):
                dd=d.get("district_id", d.get("census_district_id")); dn=d.get("district_name") or d.get("district") or d.get("name")
                if sid is not None and sname and dd is not None and dn: result.append({"state_id":int(sid),"state_name":str(sname),"district_id":int(dd),"district_name":str(dn)})
    unique={(x["state_id"],x["district_id"]):x for x in result}
    return list(unique.values())


def get_ceda_markets(commodity_id, state_id, district_id):
    payload={"commodity_id":int(commodity_id),"state_id":int(state_id),"district_id":int(district_id),"indicator":"price"}
    raw=ceda_list(ceda_request("POST", "/agmarknet/markets", payload), ["data", "markets", "records"])
    result=[]
    for x in raw:
        if not isinstance(x,dict): continue
        mid=x.get("market_id", x.get("id")); name=x.get("market_name") or x.get("name") or x.get("market")
        if mid is not None and name: result.append({"id":int(mid),"name":str(name)})
    return sorted(result,key=lambda x:x["name"].lower())


def get_ceda_prices(commodity_id, state_id, district_id, market_id=None):
    today=date.today()
    payload={"commodity_id":int(commodity_id),"state_id":int(state_id),"district_id":[int(district_id)],"market_id":[int(market_id)] if market_id else [],"from_date":(today-timedelta(days=30)).isoformat(),"to_date":today.isoformat()}
    data=ceda_request("POST", "/agmarknet/prices", payload)
    if isinstance(data,dict):
        output=data.get("output")
        if isinstance(output,dict) and isinstance(output.get("data"),list): return output["data"]
        if isinstance(data.get("data"),list): return data["data"]
    return []


@app.route("/market")
def market():
    if "user_id" not in session: return redirect(url_for("login"))
    user=get_current_user(); profile=ensure_farmer_profile(user)
    try:
        commodities=get_ceda_commodities(); geographies=get_ceda_geographies(); error=None
    except Exception as e:
        print("CEDA MARKET PAGE ERROR:",e); commodities=[]; geographies=[]; error=str(e)
    return render_template("market.html", username=session["user_name"], commodities=commodities, geographies=geographies, market_error=error, default_state=user.state if user else "", default_district=profile.district if profile else "")


@app.route("/api/market/commodities")
def market_commodities_api():
    if "user_id" not in session: return jsonify({"success":False,"message":"Please login first."}),401
    try: return jsonify({"success":True,"commodities":get_ceda_commodities()})
    except Exception as e: return jsonify({"success":False,"message":str(e)}),500


@app.route("/api/market/geographies")
def market_geographies_api():
    if "user_id" not in session: return jsonify({"success":False,"message":"Please login first."}),401
    try: return jsonify({"success":True,"geographies":get_ceda_geographies()})
    except Exception as e: return jsonify({"success":False,"message":str(e)}),500


@app.route("/api/market/markets", methods=["POST"])
def market_markets_api():
    if "user_id" not in session: return jsonify({"success":False,"message":"Please login first."}),401
    data=request.get_json(silent=True) or {}
    try:
        markets=get_ceda_markets(int(data["commodity_id"]),int(data["state_id"]),int(data["district_id"]))
        return jsonify({"success":True,"markets":markets})
    except KeyError: return jsonify({"success":False,"message":"Commodity, state and district are required."}),400
    except Exception as e: return jsonify({"success":False,"message":str(e)}),500


@app.route("/api/market/prices", methods=["POST"])
def market_prices_api():
    if "user_id" not in session: return jsonify({"success":False,"message":"Please login first."}),401
    data=request.get_json(silent=True) or {}
    try:
        market_id=data.get("market_id")
        market_id=int(market_id) if market_id not in (None,"","all") else None
        prices=get_ceda_prices(int(data["commodity_id"]),int(data["state_id"]),int(data["district_id"]),market_id)
        return jsonify({"success":True,"prices":prices})
    except KeyError: return jsonify({"success":False,"message":"Commodity, state and district are required."}),400
    except Exception as e: return jsonify({"success":False,"message":str(e)}),500


# ============================================================
# GOVERNMENT SCHEMES
# ============================================================

@app.route("/schemes")
def schemes():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(

        "schemes.html",

        username=session[
            "user_name"
        ]
    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    user = get_current_user()

    profile = ensure_farmer_profile(
        user
    )


    # --------------------------------------------------------
    # Update profile
    # --------------------------------------------------------

    if request.method == "POST":

        user.full_name = (
            request.form.get(
                "full_name"
            )
            or user.full_name
        )


        user.state = (
            request.form.get(
                "state"
            )
            or user.state
        )


        profile.phone = (
            request.form.get(
                "phone"
            )
            or profile.phone
        )


        profile.district = (
            request.form.get(
                "district"
            )
            or profile.district
        )


        profile.village = (
            request.form.get(
                "village"
            )
            or profile.village
        )


        farm_size = request.form.get(
            "farm_size"
        )


        if farm_size:

            try:

                profile.farm_size = float(
                    farm_size
                )

            except ValueError:

                pass


        profile.farm_size_unit = (
            request.form.get(
                "farm_size_unit"
            )
            or profile.farm_size_unit
            or "acres"
        )


        profile.primary_crop = (
            request.form.get(
                "primary_crop"
            )
            or profile.primary_crop
        )


        profile.soil_type = (
            request.form.get(
                "soil_type"
            )
            or profile.soil_type
        )


        soil_ph = request.form.get(
            "soil_ph"
        )


        if soil_ph:

            try:

                profile.soil_ph = float(
                    soil_ph
                )

            except ValueError:

                pass


        db.session.commit()


        session["user_name"] = (
            user.full_name
        )


        return redirect(
            url_for("profile")
        )


    return render_template(

        "profile.html",

        username=session[
            "user_name"
        ],

        user=user,

        profile=profile
    )


# ============================================================
# SETTINGS
# ============================================================

@app.route(
    "/settings",
    methods=["GET", "POST"]
)
def settings():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    user = get_current_user()


    if request.method == "POST":

        language = (
            request.form.get(
                "preferred_language"
            )
        )


        if language:

            user.preferred_language = (
                language
            )

            db.session.commit()


        return redirect(
            url_for("settings")
        )


    return render_template(

        "settings.html",

        username=session[
            "user_name"
        ],

        user=user
    )


# ============================================================
# AI CHATBOT
# ============================================================

@app.route("/chatbot")
def chatbot():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(

        "chatbot.html",

        username=session[
            "user_name"
        ]
    )


# ============================================================
# CONTACT FORM
# ============================================================

@app.route(
    "/contact",
    methods=["POST"]
)
def contact():

    name = request.form.get(
        "name"
    )

    email = request.form.get(
        "email"
    )

    subject = request.form.get(
        "subject"
    )

    message = request.form.get(
        "message"
    )


    msg = Message(

        subject=(
            f"New Contact Message - "
            f"{subject}"
        ),

        sender=app.config[
            "MAIL_USERNAME"
        ],

        recipients=[
            app.config[
                "MAIL_USERNAME"
            ]
        ]
    )


    msg.body = f"""
New Contact Message

-----------------------------------------

Name : {name}

Email : {email}

Subject : {subject}

Message :

{message}

-----------------------------------------
"""


    try:

        mail.send(
            msg
        )

    except Exception as e:

        print(
            "Contact email error:",
            e
        )


    return redirect(
        url_for("home")
        + "#contact"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )