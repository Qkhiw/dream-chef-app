# api/index.py (เวอร์ชันแยก API)
import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import json

# --- Setup ---
load_dotenv()
app = Flask(__name__)
CORS(app)

# --- API Keys & Models Configuration ---
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-pro')

STABILITY_API_HOST = "https://api.stability.ai"
STABILITY_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"


# --- Endpoint 1: สำหรับสร้างรูปภาพเท่านั้น ---
@app.route('/api/generate-image', methods=['POST'])
def generate_image_handler():
    data = request.get_json()
    ingredients = data.get('ingredients')
    style = data.get('style')

    if not ingredients:
        return jsonify({'error': 'Ingredients are required'}), 400

    image_gen_prompt = f"A realistic, appetizing photo of a dish made with '{ingredients}'. The dish is presented in the style of '{style}'. Highly detailed, professional food photography, warm lighting."
    
    try:
        response = requests.post(
            f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE_ID}/text-to-image",
            headers={"Authorization": f"Bearer {STABILITY_API_KEY}", "Accept": "application/json"},
            json={"text_prompts": [{"text": image_gen_prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 25},
            timeout=20 
        )
        response.raise_for_status()
        response_data = response.json()
        image_base64 = response_data["artifacts"][0]["base64"]
        image_data_url = f"data:image/png;base64,{image_base64}"
        return jsonify({"image_url": image_data_url})

    except Exception as e:
        print(f"Stability AI Error: {e}")
        return jsonify({"error": f"Failed to generate image: {e}"}), 500


# --- Endpoint 2: สำหรับสร้างสูตรอาหารเท่านั้น ---
@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe_handler():
    data = request.get_json()
    ingredients = data.get('ingredients')
    quantity = data.get('quantity')
    style = data.get('style')

    if not ingredients:
        return jsonify({'error': 'Ingredients are required'}), 400

    try:
        prompt = f"""
        ในฐานะเชฟมืออาชีพ, จงสร้างสรรค์เมนูอาหารที่ "ทำได้จริง" และน่ารับประทาน
        โดยใช้วัตถุดิบ, ปริมาณ, และสไตล์ที่กำหนดให้ต่อไปนี้
        - วัตถุดิบ: {ingredients}
        - ปริมาณ: {quantity}
        - สไตล์: {style}
        ข้อกำหนด:
        1. คิด "ชื่อเมนู" เป็นภาษาไทยที่สร้างสรรค์และน่าสนใจ
        2. เขียน "วิธีทำ" เป็นภาษาไทยแบบทีละขั้นตอนที่เข้าใจง่ายและทำตามได้จริง
        3. ตอบกลับในรูปแบบ JSON เท่านั้น โดยมีแค่ 2 keys คือ "menu_name" และ "instructions"
        """
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        recipe_data = json.loads(cleaned_response)
        return jsonify(recipe_data)

    except Exception as e:
        error_message = f"Gemini Error: {e}"
        print(error_message)
        return jsonify({"menu_name": "เกิดข้อผิดพลาด", "instructions": error_message}), 500