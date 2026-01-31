#!/usr/bin/env python3
"""
Lister les modèles Gemini disponibles
"""

import os
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Modèles Gemini disponibles:\n")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Description: {model.display_name}")
        print()
