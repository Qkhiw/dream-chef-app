# api/index.py (เวอร์ชันแก้ไขสำหรับ Vercel Timeout)
import os
import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
app = Flask(__name__)
CORS(app)

# --- Configuration (เหมือนเดิม) ---
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-pro')
STABILITY_API_HOST = "https://api.stability.ai"
STABILITY_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

# --- Helper Function (เหมือนเดิม) ---
def generate_recipe_from_ai(ingredients, quantity, style):
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
        # เพิ่มการตั้งค่าเพื่อป้องกันการตอบกลับที่ไม่ปลอดภัย
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        json.loads(cleaned_response) 
        return cleaned_response
    except Exception as e:
        error_message = f"Gemini Error: {e}"
        print(error_message)
        return json.dumps({"menu_name": "เกิดข้อผิดพลาด", "instructions": error_message})

# --- Main Route (ส่วนที่แก้ไข) ---
@app.route('/api/generate-creation', methods=['POST'])
def handler():
    data = request.get_json()
    ingredients = data.get('ingredients')
    quantity = data.get('quantity')
    style = data.get('style')

    # --- Step 1: Generate Image (ปรับลดค่า steps เพื่อให้เร็วขึ้น) ---
    image_gen_prompt = f"A realistic, appetizing photo of a dish made with '{ingredients}'. The dish is presented in the style of '{style}'. Highly detailed, professional food photography, warm lighting."
    try:
        response = requests.post(
            f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE_ID}/text-to-image",
            headers={"Authorization": f"Bearer {STABILITY_API_KEY}", "Accept": "application/json"},
            # ลดจำนวน steps ลงเล็กน้อยเพื่อให้ AI สร้างภาพเร็วขึ้น
            json={"text_prompts": [{"text": image_gen_prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 25},
            timeout=15 # เพิ่ม timeout ให้ request
        )
        response.raise_for_status()
        response_data = response.json()
        image_base64 = response_data["artifacts"][0]["base64"]
        image_data_url = f"data:image/png;base64,{image_base64}"

    except requests.exceptions.RequestException as e:
        print(f"Stability AI Request Error: {e}")
        # ส่ง error กลับไปในรูปแบบ JSON ที่ถูกต้อง
        return jsonify({"error": f"Failed to generate image due to a network issue: {e}"}), 500
    except Exception as e:
        print(f"Stability AI Error: {e}")
        return jsonify({"error": f"Failed to generate image: {e}"}), 500

    # --- Step 2: Generate Recipe ---
    recipe_json_string = generate_recipe_from_ai(ingredients, quantity, style)

    # --- Step 3: Combine and send back ---
    return jsonify({"image_url": image_data_url, "recipe": recipe_json_string})