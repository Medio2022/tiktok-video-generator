"""
Test avec chargement explicite de .env
"""
from dotenv import load_dotenv
load_dotenv()  # Charger .env

import os
import logging

logging.basicConfig(level=logging.INFO)

# Vérifier clé API
api_key = os.getenv('ELEVENLABS_API_KEY')
print(f"🔑 Clé API: {'✅ Trouvée' if api_key else '❌ Non trouvée'}")
if api_key:
    print(f"📏 Longueur: {len(api_key)} caractères")

if api_key:
    from modules.elevenlabs_voice import ElevenLabsVoiceGenerator
    
    print("\n🎤 TEST DE GÉNÉRATION VOCALE\n")
    
    try:
        generator = ElevenLabsVoiceGenerator()
        
        test_text = """
        Hey! This is an amazing test of ElevenLabs premium AI voice.
        The quality is absolutely incredible and sounds completely natural!
        This will make our TikTok videos stand out!
        """
        
        audio_path, duration = generator.generate(
            text=test_text.strip(),
            output_path="final_test_voice.mp3",
            voice="rachel"
        )
        
        print(f"\n✅ SUCCÈS COMPLET!")
        print(f"📁 {audio_path}")
        print(f"⏱️  {duration:.1f}s")
        print(f"\n🎧 Écoutez le fichier pour entendre la qualité premium!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ Ajoutez ELEVENLABS_API_KEY dans .env")
