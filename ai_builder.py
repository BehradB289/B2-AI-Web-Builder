import os
import json
import webbrowser
import threading
import time
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app)

# [IMPORTANT] REPLACE WITH YOUR GOOGLE API KEY
MY_API_KEY = "YOUR_API_KEY_HERE"

# Configure AI
genai.configure(api_key=MY_API_KEY)
# Using 'gemini-flash-latest' for stability
model = genai.GenerativeModel('gemini-flash-latest')

def generate_site_json(user_prompt):
    """
    Interacts with Google Gemini to generate website structure.
    """
    system_prompt = f"""
    You are the intelligent engine for 'B2 Studio'.
    USER REQUEST: "{user_prompt}"
    
    REQUIRED JSON STRUCTURE:
    {{
        "meta": {{ "title": "Creative Title", "author": "B2 Studio" }},
        "theme": {{
            "primary": "HexColor", "bg": "HexColor", "text": "HexColor", 
            "card": "HexColor", "font": "String", "radius": "String"
        }},
        "sections": [
            {{
                "id": "unique_id",
                "type": "Choose from: [navbar, hero, features, gallery, cta, footer]",
                "enabled": true,
                "d": {{
                    "title": "String", "sub": "String", "btn": "String",
                    "img_prompt": "Visual description for image generation",
                    "items": [ {{ "title": "String", "sub": "String", "img_prompt": "Desc" }} ]
                }}
            }}
        ]
    }}
    RULES: Output ONLY raw JSON. No markdown.
    """
    try:
        response = model.generate_content(system_prompt)
        # Clean response
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"error": str(e)}

@app.route('/generate', methods=['POST'])
def handle_generation():
    """
    API Endpoint for the HTML frontend.
    """
    try:
        data = request.json
        user_prompt = data.get('prompt', '')
        print(f"[Log] Processing request: {user_prompt}")
        return jsonify(generate_site_json(user_prompt))
    except Exception as e:
        return jsonify({"error": "Server Error"})

def open_ui():
    """
    Automatically opens the HTML interface in the default browser
    once the server starts.
    """
    print("[System] Launching Interface...")
    time.sleep(2) # Wait for server to initialize
    
    # Locate the HTML file (assumed to be in the same folder as the EXE/Script)
    html_path = os.path.join(os.getcwd(), "B2-vs.html")
    
    if os.path.exists(html_path):
        webbrowser.open_new_tab(f'file:///{html_path}')
    else:
        print(f"[Warning] UI file not found at: {html_path}")
        print("Please ensure 'B2-vs.html' is placed next to the executable.")

if __name__ == "__main__":
    # Start the browser opener in a separate thread
    threading.Thread(target=open_ui).start()
    
    print("--- B2 ENGINE STARTED ---")
    print("Listening on port 5000...")
    app.run(port=5000)