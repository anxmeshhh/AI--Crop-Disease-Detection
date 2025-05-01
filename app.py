from flask import Flask, render_template, request, redirect, url_for
import base64
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)

# Get Gemini API key from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return {'error': 'No file part'}, 400

    image_file = request.files['image']
    language = request.form.get('language', 'English')

    if image_file.filename == '':
        return {'error': 'No selected file'}, 400

    image_bytes = image_file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    prompt = (
    "You are an experienced agricultural expert with deep knowledge of crop diseases, and you are capable of delivering a detailed, "
    "well-researched, and scientifically grounded report. Analyze the uploaded crop image and generate a comprehensive and easy-to-understand report "
    "based on the following criteria:\n\n"
    
    "1. **Disease Identification**:\n"
    "- Provide the exact name of the disease affecting the crop (e.g., blight, mildew, rust) based on visual clues and scientific classification.\n"
    "- Specify the type of plant affected (e.g., tomato, wheat, corn), mentioning the botanical or varietal differences if relevant.\n"
    "- Cite research or case studies where the disease has been prevalent, including known causes and its impact on the plant type.\n\n"
    
    "2. **Disease Severity**:\n"
    "- Assess the severity of the disease on the crop (e.g., mild, moderate, severe) based on common criteria used in agricultural research.\n"
    "- Provide a health score (e.g., percentage of affected crop area) and explain how this score was derived from recognized standards.\n"
    "- Reference studies or methodologies that assess disease severity and its implications for crop management.\n\n"
    
    "3. **Cause of Disease**:\n"
    "- Identify the pathogen causing the disease (e.g., fungus, bacteria, virus) with detailed scientific information on the pathogen's behavior and lifecycle.\n"
    "- Describe how the disease spreads (e.g., wind, insects, water) and explain the mechanisms behind this spread in both natural and controlled environments.\n"
    "- List environmental factors (e.g., temperature, humidity) that encourage the growth and spread of the disease, citing specific studies or research papers.\n\n"
    
    "4. **Impact on the Crop**:\n"
    "- Detail the effects of the disease on crop growth (e.g., discoloration, wilting, reduced yield) based on field observations and research data.\n"
    "- Estimate the potential economic loss if the disease is left untreated, citing statistics from studies or historical data (e.g., yield loss percentage, financial impact).\n"
    "- Provide real-world examples of similar crop diseases and their impact on local or global agriculture.\n\n"
    
    "5. **Treatment Suggestions**:\n"
    "- Recommend chemical treatments (e.g., fungicides, pesticides) with specific dosage instructions and application methods, based on scientific studies and industry standards.\n"
    "- Suggest organic solutions (e.g., neem oil, biocontrol agents) supported by research on their effectiveness in controlling the disease.\n"
    "- Provide cultural practices (e.g., crop rotation, proper spacing, pruning) and explain their research-backed effectiveness in disease management.\n"
    "- Include any recent advancements in treatment methods or innovative technologies used to combat crop diseases.\n\n"
    
    "6. **Preventive Measures**:\n"
    "- Offer scientific advice on future disease prevention, including disease-resistant varieties, irrigation adjustments, and soil management.\n"
    "- Recommend early detection techniques (e.g., sensor-based systems, visual detection) supported by recent research in precision agriculture.\n"
    "- Discuss sanitation practices that can prevent re-infection, referencing studies on effective crop sanitation protocols.\n\n"
    
    "7. **Additional Research and References**:\n"
    "- Provide research papers, case studies, or expert opinions related to the disease, its treatments, and prevention strategies.\n"
    "- Include links to scientific journals, research articles, or agricultural resources that offer more detailed information.\n\n"
    
    "Please ensure that the response is well-researched, clear, and approachable for a farmer while being backed by relevant studies and examples. "
    "The report should be written in **{language}**, keeping in mind the farmer's understanding of agricultural concepts.\n"
    ).format(language=language)

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': GEMINI_API_KEY
    }
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/jpeg", "data": image_base64}}
            ]
        }]
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        diagnosis = result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Error:", e)
        return {'error': f"Error contacting Gemini API: {e}"}, 500

    return {'diagnosis': diagnosis, 'language': language}

@app.route('/result')
def result():
    diagnosis = request.args.get('diagnosis', '')
    language = request.args.get('language', 'English')
    return render_template('result.html', diagnosis=diagnosis, language=language)

if __name__ == '__main__':
    app.run(debug=True)