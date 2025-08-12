# api/index.py
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

# ... (ส่วน Configuration API Keys และ Gemini เหมือนเดิม) ...
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
STABILITY_API_HOST = "https://api.stability.ai"
STABILITY_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

def generate_recipe_from_ai(ingredients, quantity, style):
    # ... (ฟังก์ชันนี้เหมือนเดิมทุกประการ) ...
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
        response = gemini_model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        json.loads(cleaned_response)
        return cleaned_response
    except Exception as e:
        error_message = f"Error generating recipe with Gemini: {e}"
        print(error_message)
        return json.dumps({"menu_name": "เกิดข้อผิดพลาด", "instructions": error_message})

# Vercel จะเรียกใช้ "app" นี้โดยตรง ไม่ต้องใช้ if __name__ == '__main__'
# เราจะเปลี่ยนชื่อ Route เป็น /api/generate-creation เพื่อให้ตรงกับโครงสร้าง
@app.route('/api/generate-creation', methods=['POST'])
def handler():
    # ... (โค้ดส่วนต้นของฟังก์ชันเหมือนเดิม) ...
    data = request.get_json()
    ingredients = data.get('ingredients')
    quantity = data.get('quantity')
    style = data.get('style')
    if not ingredients or not quantity:
        return jsonify({'error': 'Ingredients and quantity are required'}), 400

    # --- Step 1: Generate Image (เหมือนเดิม) ---
    image_gen_prompt = f"A realistic, appetizing photo of a dish made with '{ingredients}'. The dish is presented in the style of '{style}'. Highly detailed, professional food photography, warm lighting."
    try:
        response = requests.post(
            f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE_ID}/text-to-image",
            headers={"Authorization": f"Bearer {STABILITY_API_KEY}", "Accept": "application/json"},
            json={
                "text_prompts": [{"text": image_gen_prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 30,
            },
        )
        response.raise_for_status()
        response_data = response.json()
        image_artifact = response_data["artifacts"][0]

        # --- จุดที่แก้ไข: เราจะไม่บันทึกเป็นไฟล์แล้ว ---
        # เราจะเอาข้อมูล Base64 ของรูปภาพมาโดยตรง
        image_base64 = image_artifact["base64"]
        # สร้าง Data URL เพื่อให้ Frontend แสดงผลได้ทันที
        image_data_url = f"data:image/png;base64,{image_base64}"

    except Exception as e:
        print(f"Stability AI Error: {e}")
        return jsonify({"error": f"Failed to generate image: {e}"}), 500

    # --- Step 2: Generate Recipe (เหมือนเดิม) ---
    recipe_json_string = generate_recipe_from_ai(ingredients, quantity, style)

    # --- Step 3: Combine results and send back ---
    return jsonify({
        # ส่ง Data URL ของรูปภาพกลับไปแทน URL ปกติ
        "image_url": image_data_url,
        "recipe": recipe_json_string
    })