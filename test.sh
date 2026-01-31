#!/bin/bash

# Script de test du système TikTok Automation

echo "🧪 Test du système TikTok Automation"
echo "===================================="
echo ""

# Vérifier Python
echo "1️⃣  Vérification de Python..."
python3 --version || { echo "❌ Python non installé"; exit 1; }
echo ""

# Vérifier FFmpeg
echo "2️⃣  Vérification de FFmpeg..."
ffmpeg -version 2>&1 | head -n1 || { echo "⚠️  FFmpeg non installé (requis pour assemblage vidéo)"; }
echo ""

# Vérifier le fichier .env
echo "3️⃣  Vérification de la configuration..."
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env manquant"
    echo "   Créez-le avec: cp .env.example .env"
    echo "   Puis ajoutez votre clé Gemini API"
    exit 1
fi

# Vérifier la clé API
if grep -q "your_gemini_api_key_here" .env; then
    echo "⚠️  Clé Gemini API non configurée dans .env"
    echo "   Obtenez une clé sur: https://makersuite.google.com/app/apikey"
    echo ""
    echo "   Pour ce test, nous allons tester uniquement les modules TTS gratuits"
    echo ""
fi

# Créer les répertoires
echo "4️⃣  Création des répertoires..."
mkdir -p output logs storage
echo "✅ Répertoires créés"
echo ""

# Test 1: TTS gratuit (Edge TTS)
echo "5️⃣  Test Edge TTS (Microsoft - GRATUIT)..."
python3 << 'EOF'
try:
    import edge_tts
    print("✅ edge-tts installé")
except ImportError:
    print("❌ edge-tts non installé")
    print("   Installez avec: pip install edge-tts")
EOF
echo ""

# Test 2: gTTS
echo "6️⃣  Test gTTS (Google Translate - GRATUIT)..."
python3 << 'EOF'
try:
    from gtts import gTTS
    print("✅ gtts installé")
except ImportError:
    print("❌ gtts non installé")
    print("   Installez avec: pip install gtts")
EOF
echo ""

# Test 3: Gemini
echo "7️⃣  Test Gemini API..."
python3 << 'EOF'
try:
    import google.generativeai as genai
    print("✅ google-generativeai installé")
except ImportError:
    print("❌ google-generativeai non installé")
    print("   Installez avec: pip install google-generativeai")
EOF
echo ""

# Test 4: Autres dépendances
echo "8️⃣  Test des autres dépendances..."
python3 << 'EOF'
import sys
missing = []

try:
    import PIL
except ImportError:
    missing.append("pillow")

try:
    import ffmpeg
except ImportError:
    missing.append("ffmpeg-python")

try:
    from dotenv import load_dotenv
except ImportError:
    missing.append("python-dotenv")

if missing:
    print(f"❌ Modules manquants: {', '.join(missing)}")
    print(f"   Installez avec: pip install {' '.join(missing)}")
else:
    print("✅ Toutes les dépendances de base sont installées")
EOF
echo ""

echo "===================================="
echo "📊 Résumé du test"
echo "===================================="
echo ""
echo "Pour installer toutes les dépendances:"
echo "  pip install -r requirements.txt"
echo ""
echo "Pour tester la génération de voix:"
echo "  python modules/voice_generator.py"
echo ""
echo "Pour générer une vidéo de test (nécessite clé Gemini):"
echo "  python main.py --theme motivation"
echo ""
