# backend/app.py (เวอร์ชันอัปเกรด)
import os
import requests
import base64
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import json

# --- Setup ---
load_dotenv()
app = Flask(__name__)
CORS(app)

# --- API Keys Configuration ---
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not STABILITY_API_KEY or not GEMINI_API_KEY:
    raise ValueError("API keys for Stability AI and Gemini are required!")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-pro')

# Configure Stability AI
STABILITY_API_HOST = "https://api.stability.ai"
STABILITY_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

# --- Helper Functions ---
def generate_recipe_from_ai(ingredients, quantity, style):
    """Uses Gemini to generate a practical, Thai-language recipe."""
    try:
        # สร้าง Prompt ใหม่ที่ละเอียดและตรงเป้าหมายมากขึ้น
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

        ตัวอย่างผลลัพธ์ที่ต้องการ:
        {{
          "menu_name": "หมูสามชั้นทอดน้ำปลาตะไคร้กรอบ",
          "instructions": "1. หั่นหมูสามชั้นเป็นชิ้นพอดีคำ แล้วนำไปหมักกับน้ำปลาและพริกไทย 15 นาที\\n2. ซอยตะไคร้แล้วนำไปทอดในน้ำมันร้อนจัดจนเหลืองกรอบ แล้วตักขึ้นพักไว้\\n3. นำหมูที่หมักไว้ลงทอดในน้ำมันเดิมจนสุกเหลืองน่ารับประทาน\\n4. จัดหมูทอดใส่จานแล้วโรยด้วยตะไคร้กรอบ"
        }}
        """
        response = gemini_model.generate_content(prompt)
        # ทำความสะอาด response ที่อาจจะมี markdown ติดมา
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        # ตรวจสอบว่าผลลัพธ์เป็น JSON ที่ถูกต้องหรือไม่
        json.loads(cleaned_response)
        return cleaned_response
    except Exception as e:
        error_message = f"Error generating recipe with Gemini: {e}"
        print(error_message)
        # ส่ง JSON ที่มีข้อความ Error กลับไป
        return json.dumps({"menu_name": "เกิดข้อผิดพลาด", "instructions": error_message})


# --- Flask Routes ---
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('generated_images', filename)

@app.route('/api/generate-creation', methods=['POST'])
def generate_creation_route():
    data = request.get_json()
    ingredients = data.get('ingredients')
    quantity = data.get('quantity')
    style = data.get('style')

    if not ingredients or not quantity:
        return jsonify({'error': 'Ingredients and quantity are required'}), 400

    # --- Step 1: Generate Image with Stability AI ---
    # สร้าง Prompt ใหม่ที่เน้นความสมจริงและสอดคล้องกับสไตล์
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
        filename = f"{int(time.time())}.png"
        output_path = os.path.join("generated_images", filename)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_artifact["base64"]))
        
        image_url = f"http://127.0.0.1:5000/images/{filename}"

    except Exception as e:
        print(f"Stability AI Error: {e}")
        return jsonify({"error": f"Failed to generate image: {e}"}), 500

    # --- Step 2: Generate Recipe with Gemini ---
    recipe_json_string = generate_recipe_from_ai(ingredients, quantity, style)

    # --- Step 3: Combine results and send back ---
    return jsonify({
        "image_url": image_url,
        "recipe": recipe_json_string
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)