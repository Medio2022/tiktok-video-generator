#!/bin/bash

# Script de setup pour le système TikTok Automation

set -e  # Arrêter en cas d'erreur

echo "🚀 Setup TikTok Automation System"
echo "=================================="
echo ""

# Vérifier Python
echo "📍 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "   Installez Python 3.10+ depuis https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION détecté"
echo ""

# Vérifier FFmpeg
echo "📍 Vérification de FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg n'est pas installé"
    echo "   Installation de FFmpeg..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew n'est pas installé"
            echo "   Installez Homebrew: https://brew.sh/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    else
        echo "❌ Système d'exploitation non supporté pour l'installation automatique"
        echo "   Installez FFmpeg manuellement: https://ffmpeg.org/"
        exit 1
    fi
fi

FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
echo "✅ FFmpeg $FFMPEG_VERSION détecté"
echo ""

# Créer l'environnement virtuel
echo "📍 Création de l'environnement virtuel..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
else
    echo "✅ Environnement virtuel existant"
fi
echo ""

# Activer l'environnement virtuel
echo "📍 Activation de l'environnement virtuel..."
source venv/bin/activate
echo "✅ Environnement virtuel activé"
echo ""

# Installer les dépendances
echo "📍 Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dépendances installées"
echo ""

# Installer Playwright
echo "📍 Installation de Playwright..."
playwright install chromium
echo "✅ Playwright installé"
echo ""

# Créer les répertoires nécessaires
echo "📍 Création des répertoires..."
mkdir -p output
mkdir -p logs
mkdir -p storage
mkdir -p playwright_state
echo "✅ Répertoires créés"
echo ""

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "📍 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
    echo ""
    echo "⚠️  IMPORTANT: Configurez vos clés API dans .env"
    echo "   Éditez le fichier .env et ajoutez:"
    echo "   - GOOGLE_API_KEY"
    echo "   - GOOGLE_CLOUD_PROJECT"
    echo "   - GOOGLE_APPLICATION_CREDENTIALS"
    echo "   - TIKTOK_USERNAME"
    echo "   - TIKTOK_PASSWORD"
    echo ""
else
    echo "✅ Fichier .env existant"
    echo ""
fi

# Créer .gitignore
if [ ! -f ".gitignore" ]; then
    echo "📍 Création du .gitignore..."
    cat > .gitignore << 'EOF'
# Environment
venv/
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Output
output/
logs/
storage/
playwright_state/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo "✅ .gitignore créé"
    echo ""
fi

echo "=================================="
echo "✅ Setup terminé avec succès!"
echo "=================================="
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Configurez vos clés API dans .env"
echo "   2. Testez la génération: python main.py --theme motivation"
echo "   3. Lancez le scheduler: python scheduler.py --test"
echo ""
echo "📚 Documentation complète dans README.md"
echo ""
