"""
Test ElevenLabs - Découverte de l'API
"""
from elevenlabs.client import ElevenLabs

API_KEY = 'sk_6cc337a2ae3f1fb8eb32595caa8b11a7c442cdaf9864e08e'

print("🔍 Exploration de l'API ElevenLabs...")

try:
    client = ElevenLabs(api_key=API_KEY)
    
    # Afficher les méthodes disponibles
    methods = [m for m in dir(client) if not m.startswith('_')]
    print(f"\n📋 Méthodes disponibles: {methods}\n")
    
    # Tester text_to_speech
    if hasattr(client, 'text_to_speech'):
        print("✅ Méthode text_to_speech trouvée! Test en cours...")
        
        audio_generator = client.text_to_speech.convert(
            text="Hello! This is a premium AI voice test.",
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
            model_id="eleven_multilingual_v2"
        )
        
        # Sauvegarder
        audio_bytes = b"".join(audio_generator)
        with open("test_elevenlabs_rachel.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Succès! Fichier créé: test_elevenlabs_rachel.mp3 ({len(audio_bytes)} bytes)")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
