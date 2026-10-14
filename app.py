from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from dotenv import load_dotenv
from price_model import predict_price

from PIL import Image
from io import BytesIO

import requests
import os

# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=API_KEY
)


# =========================================================
# KISAN MITRA AI SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are Kisan Mitra AI, an intelligent agriculture assistant
designed especially for Indian farmers.

Your main purpose is to help farmers with:

- Crop selection
- Crop cultivation
- Soil management
- Fertilizer guidance
- Irrigation
- Pest problems
- Crop diseases
- Farming techniques
- Weather-related farming questions
- Agricultural best practices
- Crop yield improvement

RULES:

1. Support Hindi, English and Hinglish.

2. Answer according to the language selected by the farmer.

3. Understand Hinglish naturally.

4. Keep answers simple and practical.

5. Use bullet points when useful.

6. Give step-by-step recommendations when appropriate.

7. Never invent current weather information.

8. Never invent current market prices.

9. For serious crop diseases or pesticide-related issues,
   recommend consulting a local agriculture expert.

10. Be respectful and farmer-friendly.

11. If the question is unrelated to agriculture,
    politely explain that you mainly assist with farming.

12. For crop problems, explain:
    - Possible causes
    - Solutions
    - Prevention

13. Farming conditions can vary according to:
    - Soil
    - Location
    - Season
    - Crop variety

Your name is Kisan Mitra AI.
"""


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# AI CHAT
# =========================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "reply": "Please enter your question."
            }), 400


        user_message = data.get(
            "message",
            ""
        ).strip()


        language = data.get(
            "language",
            "en"
        )


        if not user_message:

            if language == "hi":

                return jsonify({
                    "reply": "कृपया अपना कृषि प्रश्न लिखें।"
                }), 400

            return jsonify({
                "reply": "Please enter your farming question."
            }), 400


        # =================================================
        # LANGUAGE
        # =================================================

        if language == "hi":

            language_instruction = """
Answer completely in Hindi.

Use simple Hindi that an Indian farmer can easily understand.

Avoid difficult technical words.

Common English agricultural terms may be used in brackets
when helpful.
"""

        else:

            language_instruction = """
Answer completely in English.

Use simple and clear language suitable for Indian farmers.
"""


        # =================================================
        # GEMINI PROMPT
        # =================================================

        prompt = f"""
{SYSTEM_PROMPT}

LANGUAGE:

{language_instruction}

FARMER QUESTION:

{user_message}

Give a clear, practical and useful answer.

If this is a crop problem, provide:

1. Possible causes
2. Recommended actions
3. Prevention tips

Do not claim real-time weather or market information.
"""


        # =================================================
        # GEMINI REQUEST
        # =================================================

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )


        if response and response.text:

            return jsonify({
                "reply": response.text
            })


        if language == "hi":

            return jsonify({
                "reply": "माफ कीजिए, अभी उत्तर नहीं मिल पाया।"
            })


        return jsonify({
            "reply": "Sorry, I could not generate a response."
        })


    except Exception as e:

        print("\n========== CHAT ERROR ==========")

        print(e)

        print("===============================\n")


        if language == "hi":

            return jsonify({
                "reply": "AI सेवा में अभी समस्या है। कृपया दोबारा प्रयास करें।"
            }), 500


        return jsonify({
            "reply": "There is a problem with the AI service. Please try again."
        }), 500


# =========================================================
# CROP PRICE PREDICTION
# =========================================================

@app.route(
    "/predict-price",
    methods=["POST"]
)
def predict_crop_price():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "Invalid request."
            }), 400


        crop = data.get(
            "crop",
            ""
        ).strip()


        state = data.get(
            "state",
            ""
        ).strip()


        season = data.get(
            "season",
            ""
        ).strip()


        month = data.get(
            "month",
            ""
        )


        if not crop or not state or not season or not month:

            return jsonify({
                "success": False,
                "message": "Please provide all details."
            }), 400


        month = int(month)


        if month < 1 or month > 12:

            return jsonify({
                "success": False,
                "message": "Invalid month."
            }), 400


        # =================================================
        # ML PREDICTION
        # =================================================

        price = predict_price(

            crop=crop,

            state=state,

            season=season,

            month=month

        )


        return jsonify({

            "success": True,

            "crop": crop,

            "state": state,

            "season": season,

            "month": month,

            "price": price

        })


    except Exception as e:

        print("\n======= PRICE ERROR =======")

        print(e)

        print("===========================\n")


        return jsonify({

            "success": False,

            "message": "Unable to predict crop price."

        }), 500


# =========================================================
# RUN
# =========================================================


# =========================================================
# LIVE WEATHER
# =========================================================

@app.route("/weather", methods=["POST"])
def get_weather():

    try:

        data = request.get_json()

        city = data.get("city", "").strip()

        if not city:
            return jsonify({
                "success": False,
                "message": "Please enter a city."
            }), 400


        # -------------------------------------------------
        # 1. FIND CITY COORDINATES
        # -------------------------------------------------

        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }


        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()


        if not geo_data.get("results"):

            return jsonify({
                "success": False,
                "message": "City not found."
            }), 404


        location = geo_data["results"][0]

        latitude = location["latitude"]

        longitude = location["longitude"]

        city_name = location["name"]

        country = location.get(
            "country",
            ""
        )


        # -------------------------------------------------
        # 2. GET WEATHER
        # -------------------------------------------------

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )


        weather_params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": ",".join([
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "wind_speed_10m"
            ]),

            "hourly": ",".join([
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "relative_humidity_2m"
            ]),

            "forecast_days": 1,

            "timezone": "auto"

        }


        weather_response = requests.get(

            weather_url,

            params=weather_params,

            timeout=10

        )


        weather_response.raise_for_status()

        weather_data = weather_response.json()


        current = weather_data["current"]


        # -------------------------------------------------
        # WEATHER CODE
        # -------------------------------------------------

        weather_code = current.get(
            "weather_code",
            0
        )


        description = get_weather_description(
            weather_code
        )


        return jsonify({

            "success": True,

            "city": city_name,

            "country": country,

            "latitude": latitude,

            "longitude": longitude,

            "temperature": current.get(
                "temperature_2m"
            ),

            "humidity": current.get(
                "relative_humidity_2m"
            ),

            "feels_like": current.get(
                "apparent_temperature"
            ),

            "precipitation": current.get(
                "precipitation"
            ),

            "wind_speed": current.get(
                "wind_speed_10m"
            ),

            "weather_code": weather_code,

            "description": description

        })


    except requests.exceptions.RequestException as e:

        print(
            "Weather API Error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to connect to weather service."

        }), 500


    except Exception as e:

        print(
            "Weather Error:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to get weather information."

        }), 500


# =========================================================
# WEATHER DESCRIPTION
# =========================================================

def get_weather_description(code):

    weather_codes = {

        0: "Clear sky",

        1: "Mainly clear",

        2: "Partly cloudy",

        3: "Overcast",

        45: "Fog",

        48: "Depositing rime fog",

        51: "Light drizzle",

        53: "Moderate drizzle",

        55: "Dense drizzle",

        61: "Slight rain",

        63: "Moderate rain",

        65: "Heavy rain",

        71: "Slight snow",

        73: "Moderate snow",

        75: "Heavy snow",

        80: "Slight rain showers",

        81: "Moderate rain showers",

        82: "Violent rain showers",

        95: "Thunderstorm",

        96: "Thunderstorm with slight hail",

        99: "Thunderstorm with heavy hail"

    }


    return weather_codes.get(
        code,
        "Unknown weather"
    )


    
# =========================================================
# AI CROP DISEASE DETECTION
# =========================================================

@app.route("/detect-disease", methods=["POST"])
def detect_disease():

    try:

        # 1. Check uploaded image
        if "image" not in request.files:

            return jsonify({
                "success": False,
                "message": "Please upload a crop image."
            }), 400

        image_file = request.files["image"]

        if not image_file or not image_file.filename:

            return jsonify({
                "success": False,
                "message": "No image selected."
            }), 400

        # 2. Validate file extension
        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "webp"
        }

        filename = image_file.filename.lower()
        extension = filename.rsplit(".", 1)[-1] if "." in filename else ""

        if extension not in allowed_extensions:

            return jsonify({
                "success": False,
                "message": "Only JPG, JPEG, PNG and WEBP images are allowed."
            }), 400

        # 3. Read image safely
        image_bytes = image_file.read()

        if not image_bytes:

            return jsonify({
                "success": False,
                "message": "The uploaded image is empty."
            }), 400

        # Maximum size: 5 MB
        if len(image_bytes) > 5 * 1024 * 1024:

            return jsonify({
                "success": False,
                "message": "Image size must be less than 5 MB."
            }), 400

        # 4. Open and validate image
        try:

            image = Image.open(BytesIO(image_bytes))

            image.load()

            image_format = image.format

            if image_format not in {
                "JPEG",
                "PNG",
                "WEBP"
            }:

                return jsonify({
                    "success": False,
                    "message": "Unsupported image format."
                }), 400

            # Convert to RGB for consistent processing
            if image.mode not in ("RGB", "RGBA"):

                image = image.convert("RGB")

        except Exception:

            return jsonify({
                "success": False,
                "message": "Invalid or corrupted image."
            }), 400

        # 5. AI prompt
        disease_prompt = """
You are Kisan Mitra AI, an agriculture assistant
for Indian farmers.

Analyze the uploaded crop or plant image.

IMPORTANT:
- Identify the crop if possible.
- Identify possible diseases or visible symptoms.
- Do not claim certainty when the image is unclear.
- Do not invent a disease.
- If the image is not a plant or crop, explain that.
- Do not provide unsafe pesticide dosage.
- Recommend a local agriculture expert for confirmation.

Give your response in the following format:

CROP:
Possible crop name or Unknown

OBSERVATION:
Describe visible symptoms.

POSSIBLE DISEASE:
Possible disease or Unknown

CONFIDENCE:
High, Medium, Low, or Cannot determine

POSSIBLE CAUSES:
Explain likely causes if identifiable.

RECOMMENDED ACTIONS:
Give practical and safe next steps.

PREVENTION:
Provide general prevention advice.

EXPERT GUIDANCE:
Explain when the farmer should consult an agriculture expert.

Answer in simple language suitable for Indian farmers.
"""

        # 6. Send image + prompt to Gemini
        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=[
                disease_prompt,
                image
            ],

            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1200
            )

        )

        # 7. Return AI response
        if response and response.text:

            return jsonify({
                "success": True,
                "reply": response.text
            })

        return jsonify({
            "success": False,
            "message": "AI could not analyze the image."
        }), 500

    except Exception as e:

        print("\n========== DISEASE DETECTION ERROR ==========")
        print(type(e).__name__)
        print(e)
        print("=============================================\n")

        return jsonify({
            "success": False,
            "message": "Unable to analyze the crop image. Please try again."
        }), 500

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )