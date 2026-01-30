"""
Configuration centralisée pour le système TikTok Automation
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
STORAGE_DIR = BASE_DIR / "storage"
PLAYWRIGHT_STATE_DIR = BASE_DIR / "playwright_state"

# Créer les répertoires nécessaires
for directory in [OUTPUT_DIR, LOGS_DIR, STORAGE_DIR, PLAYWRIGHT_STATE_DIR]:
    directory.mkdir(exist_ok=True)

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# TikTok Configuration
TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME")
TIKTOK_PASSWORD = os.getenv("TIKTOK_PASSWORD")

# Cloud Storage
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "tiktok-videos-bucket")

# Thème de contenu
THEME = os.getenv("THEME", "motivation")

# Paramètres de génération
VIDEO_CONFIG = {
    "duration_min": 20,  # secondes
    "duration_max": 40,  # secondes
    "target_duration": 28,  # durée cible optimale
    "resolution": (1080, 1920),  # 9:16 format
    "fps": 30,
    "video_bitrate": "3000k",
    "audio_bitrate": "128k",
}

# Configuration sous-titres
SUBTITLE_CONFIG = {
    "enabled": True,
    "color": (0, 255, 255, 255),  # Cyan RGBA
    "size": 85,  # Taille police
    "font": "Arial Bold",
    "outline_color": (0, 0, 0, 255),  # Noir
    "outline_width": 5,  # Épaisseur bordure
    "position_from_bottom": 300,  # Distance du bas (pixels)
}

# Paramètres Gemini
GEMINI_CONFIG = {
    "idea_model": "gemini-flash-latest",  # Modèle Flash avec quota séparé
    "script_model": "gemini-flash-latest",  # Modèle Flash avec quota séparé
    "subtitle_model": "gemini-flash-latest",  # Modèle Flash avec quota séparé
    "description_model": "gemini-flash-latest",  # Modèle Flash avec quota séparé
    "temperature_creative": 0.9,  # Pour idées
    "temperature_balanced": 0.7,  # Pour scripts
    "temperature_precise": 0.5,   # Pour sous-titres
}

# Paramètres DeepSeek (Alternative gratuite illimitée)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# Paramètres Pexels (Vidéos stock gratuites)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PEXELS_VIDEO_QUALITY = "hd"  # hd ou sd
VIDEO_CACHE_DIR = BASE_DIR / "cache" / "videos"
VIDEO_CACHE_ENABLED = True

# Paramètres TTS GRATUIT
TTS_CONFIG = {
    "backend": "edge",  # "edge" (recommandé), "gtts", ou "pyttsx3"
    "edge_voice": "fr-FR-DeniseNeural",  # Voix féminine Microsoft
    # Alternatives Edge TTS:
    # "fr-FR-HenriNeural" (masculine)
    # "fr-FR-EloiseNeural" (féminine jeune)
    "speaking_rate": "+10%",  # Légèrement plus rapide pour Edge TTS
}

# Paramètres Imagen
IMAGEN_CONFIG = {
    "resolution": (1080, 1920),
    "style": "modern minimalist gradient",
    "format": "PNG",
}

# Paramètres de publication
PUBLICATION_CONFIG = {
    "daily_videos": 2,
    "publication_hours": [(10, 14), (18, 22)],  # Plages horaires
    "randomize_minutes": 30,  # ±30 minutes
    "max_retries": 3,
    "retry_delay": 300,  # 5 minutes
}

# Délais anti-détection (en secondes)
DELAYS = {
    "page_load": (3, 7),
    "upload_wait": (5, 10),
    "processing": (15, 30),
    "typing_char": (0.08, 0.12),
    "between_actions": (2, 5),
    "before_publish": (3, 8),
    "warm_up_scroll": (30, 90),
    "pre_upload_delay": (30, 120),  # Délai avant upload
}

# Hashtags par défaut par thème
DEFAULT_HASHTAGS = {
    "motivation": ["motivation", "mindset", "reussite", "developpementpersonnel", "inspiration"],
    "productivite": ["productivite", "efficacite", "organisation", "conseils", "astuces"],
    "tech": ["tech", "technologie", "innovation", "digital", "futur"],
    "business": ["business", "entrepreneur", "startup", "marketing", "strategie"],
    "sante": ["sante", "bienetre", "fitness", "nutrition", "lifestyle"],
}

# Logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOGS_DIR / "tiktok_automation.log",
    "max_bytes": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5,
}

# Validation
def validate_config():
    """Valider que toutes les configurations essentielles sont présentes"""
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY manquant")
    
    if not TIKTOK_USERNAME or not TIKTOK_PASSWORD:
        errors.append("Identifiants TikTok manquants")
    
    if errors:
        raise ValueError(f"Configuration invalide: {', '.join(errors)}")
    
    return True

if __name__ == "__main__":
    # Test de configuration
    try:
        validate_config()
        print("✅ Configuration valide")
        print(f"📁 Répertoire de sortie: {OUTPUT_DIR}")
        print(f"🎯 Thème: {THEME}")
        print(f"📊 Vidéos par jour: {PUBLICATION_CONFIG['daily_videos']}")
    except ValueError as e:
        print(f"❌ {e}")
