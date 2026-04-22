import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}"
}


def extract_preferences_ai(message):

    prompt = f"""
Extract food preferences from this message.

Message: {message}

Return JSON with these fields:
diet (veg / non-veg)
spice (spicy / mild)
meal (breakfast / lunch / dinner)
goal (weight loss / muscle gain / normal)

If something is not mentioned, leave it empty.

Example output:
{{
  "diet": "",
  "spice": "",
  "meal": "",
  "goal": ""
}}
"""

    payload = {
        "inputs": prompt
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    result = response.json()

    
    

    try:
        text = result[0]["generated_text"]
        json_text = re.search(r"\{.*\}", text, re.S).group()
        print("AI RAW RESPONSE:", text)
        return json.loads(json_text)
    except:
        return {}
    