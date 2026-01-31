#!/usr/bin/env python3
"""
Test simple des backends TTS gratuits
"""

import sys
import os
import asyncio
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Test des backends TTS GRATUITS")
print("="*60)
print()

# Créer le répertoire output
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

test_text = """Tu perds 3 heures par jour.
Sans même t'en rendre compte.
Voici comment arrêter ça.
Sauvegarde pour ne pas oublier."""

# Test 1: Edge TTS (recommandé)
print("1️⃣  Test Edge TTS (Microsoft - GRATUIT)...")
try:
    import edge_tts
    
    async def test_edge():
        voice = "fr-FR-DeniseNeural"
        output_file = "output/test_edge.mp3"
        
        communicate = edge_tts.Communicate(test_text, voice, rate="+10%")
        await communicate.save(output_file)
        
        file_size = Path(output_file).stat().st_size / 1024
        print(f"✅ Edge TTS: {output_file} ({file_size:.1f} KB)")
        print(f"   Voix: {voice}")
        print(f"   Qualité: ⭐⭐⭐⭐⭐ Excellente")
    
    asyncio.run(test_edge())
    
except ImportError:
    print("❌ edge-tts non installé")
    print("   Installez avec: pip3 install edge-tts --user")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 2: gTTS
print("2️⃣  Test gTTS (Google Translate - GRATUIT)...")
try:
    from gtts import gTTS
    
    output_file = "output/test_gtts.mp3"
    tts = gTTS(text=test_text, lang='fr', slow=False)
    tts.save(output_file)
    
    file_size = Path(output_file).stat().st_size / 1024
    print(f"✅ gTTS: {output_file} ({file_size:.1f} KB)")
    print(f"   Qualité: ⭐⭐⭐ Bonne")
    
except ImportError:
    print("❌ gtts non installé")
    print("   Installez avec: pip3 install gtts --user")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 3: pyttsx3 (optionnel, offline)
print("3️⃣  Test pyttsx3 (Offline - GRATUIT)...")
try:
    import pyttsx3
    
    output_file = "output/test_pyttsx3.mp3"
    engine = pyttsx3.init()
    
    # Chercher une voix française
    voices = engine.getProperty('voices')
    french_voice = None
    for voice in voices:
        if 'french' in voice.name.lower() or 'fr' in str(voice.languages).lower():
            french_voice = voice.id
            break
    
    if french_voice:
        engine.setProperty('voice', french_voice)
    
    engine.setProperty('rate', 165)
    engine.save_to_file(test_text, output_file)
    engine.runAndWait()
    
    if Path(output_file).exists():
        file_size = Path(output_file).stat().st_size / 1024
        print(f"✅ pyttsx3: {output_file} ({file_size:.1f} KB)")
        print(f"   Qualité: ⭐⭐ Basique")
    else:
        print("⚠️  Fichier non généré")
    
except ImportError:
    print("⚠️  pyttsx3 non installé (optionnel)")
    print("   Installez avec: pip3 install pyttsx3 --user")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()
print("="*60)
print("📊 Résumé")
print("="*60)
print()
print("Fichiers générés dans output/:")
for f in sorted(output_dir.glob("test_*.mp3")):
    size = f.stat().st_size / 1024
    print(f"  - {f.name} ({size:.1f} KB)")

print()
print("🎧 Écoutez les fichiers pour comparer la qualité!")
print()
print("🏆 RECOMMANDATION: Edge TTS (meilleure qualité)")
print()
