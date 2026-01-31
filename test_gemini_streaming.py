#!/usr/bin/env python3
"""
Test de génération Gemini avec streaming
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = """Génère UNE idée de vidéo TikTok sur le thème: motivation

Réponds en JSON:
{
    "hook": "phrase choc",
    "angle": "angle unique",
    "concept": "description",
    "cta": "call to action"
}
"""

print("🧪 Test génération Gemini avec streaming\n")

# Test 1: Sans streaming
print("1️⃣  Sans streaming:")
response = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        temperature=0.9,
        max_output_tokens=2000,
    )
)
print(f"Longueur: {len(response.text)} chars")
print(f"Texte: {response.text[:200]}...")
print()

# Test 2: Avec streaming
print("2️⃣  Avec streaming:")
response_stream = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        temperature=0.9,
        max_output_tokens=2000,
    ),
    stream=True
)

full_text = ""
for chunk in response_stream:
    if chunk.text:
        full_text += chunk.text

print(f"Longueur: {len(full_text)} chars")
print(f"Texte complet:\n{full_text}")
print()

# Parser le JSON
try:
    # Nettoyer
    clean_text = full_text.strip()
    if "```json" in clean_text:
        start = clean_text.find("```json") + 7
        end = clean_text.find("```", start)
        clean_text = clean_text[start:end].strip()
    
    idea = json.loads(clean_text)
    print("✅ JSON parsé avec succès!")
    print(json.dumps(idea, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Erreur: {e}")
