"""
Générer une vidéo complète avec ElevenLabs
"""
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from main import TikTokPipeline

print("\n" + "="*70)
print("🎬 GÉNÉRATION VIDÉO COMPLÈTE AVEC ELEVENLABS PREMIUM")
print("="*70 + "\n")

# Créer pipeline avec auto-détection (utilisera ElevenLabs)
pipeline = TikTokPipeline(theme="motivation")

print("📍 Démarrage génération...")
print("⏳ Cela prendra environ 30-60 secondes...\n")

try:
    # Générer vidéo
    metadata = pipeline.generate_video(output_name="test_elevenlabs_video")
    
    print("\n" + "="*70)
    print("✅ VIDÉO GÉNÉRÉE AVEC SUCCÈS!")
    print("="*70)
    print(f"\n📁 Vidéo: {metadata['video_path']}")
    print(f"⏱️  Durée: {metadata.get('audio_duration', 0):.1f}s")
    print(f"🎤 Voix: ElevenLabs Premium (Rachel)")
    print(f"💡 Idée: {metadata['idea']['hook']}")
    print(f"📝 Script: {len(metadata['script']['segments'])} segments")
    
    # Afficher stats
    if 'subtitle_count' in metadata:
        print(f"📊 Sous-titres: {metadata['subtitle_count']}")
    
    print("\n🎧 Écoutez la voix premium dans la vidéo!")
    print("🎉 Produit JVZoo prêt à lancer!\n")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
