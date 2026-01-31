"""
Test complet pipeline avec ElevenLabs
"""
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

from modules.voice_generator import VoiceGenerator

print("🎬 TEST DU GÉNÉRATEUR DE VOIX AVEC AUTO-DÉTECTION\n")
print("=" * 60)

test_text = """
Voici un secret que personne ne vous dit.
Vous perdez trois heures par jour à scroller.
Sans même vous en rendre compte.
Première étape : désactiver toutes les notifications.
Deuxième étape : supprimer les apps inutiles.
Troisième étape : installer un bloqueur de distractions.
Sauvegardez cette vidéo pour ne pas oublier.
"""

# Test 1: Auto-détection (devrait utiliser ElevenLabs)
print("\n1️⃣  Test AUTO-DÉTECTION...")
try:
    generator = VoiceGenerator(backend="auto")
    audio_path, duration = generator.generate(test_text.strip(), "test_auto_voice.mp3")
    print(f"✅ Succès: {audio_path} ({duration:.1f}s)")
    print(f"   Backend utilisé: {generator.backend}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: ElevenLabs explicite
print("\n2️⃣  Test ELEVENLABS EXPLICITE...")
try:
    generator = VoiceGenerator(backend="elevenlabs", elevenlabs_voice="rachel")
    audio_path, duration = generator.generate(test_text.strip(), "test_elevenlabs_explicit.mp3")
    print(f"✅ Succès: {audio_path} ({duration:.1f}s)")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Edge TTS (fallback)
print("\n3️⃣  Test EDGE TTS (fallback)...")
try:
    generator = VoiceGenerator(backend="edge")
    audio_path, duration = generator.generate(test_text.strip(), "test_edge_fallback.mp3")
    print(f"✅ Succès: {audio_path} ({duration:.1f}s)")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS!")
print("=" * 60)
