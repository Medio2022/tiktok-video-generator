"""
ElevenLabs Voice Generator - Premium AI Voices (API v2.33+)
Alternative gratuite/abordable pour voix professionnelles
"""

import os
import logging
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs not installed. Run: pip install elevenlabs")


class ElevenLabsVoiceGenerator:
    """Generate premium AI voices using ElevenLabs API"""
    
    # Voix populaires avec leurs IDs (officiel ElevenLabs)
    PREMIUM_VOICES = {
        # Voix féminines
        "rachel": "21m00Tcm4TlvDq8ikWAM",  # Young, energetic female
        "bella": "EXAVITQu4vr4xnSDxMaL",  # Soft, calm female
        "domi": "AZnzlk1XvdvUeBnXmlld",   # Strong, confident female
        "elli": "MF3mGyEYCl7XYWbV9V6O",   # Emotional, expressive female
        "nicole": "piTKgcLEGmPE4e6mEKli",  # Whisper female
        
        # Voix masculines
        "adam": "pNInz6obpgDQGcFmaJgB",   # Deep, authoritative male
        "antoni": "ErXwobaYiN019PkySvjV", # Well-rounded male
        "josh": "TxGEqnHWrfWFTfGW9XjX",   # Young, casual male
        "arnold": "VR6AewLTigWG4xSOukaG", # Crisp, professional male
        "sam": "yoZ06aMxZJJ28mfd3POQ",    # US Male - Dynamic
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialiser le générateur ElevenLabs
        
        Args:
            api_key: Clé API ElevenLabs (ou depuis env ELEVENLABS_API_KEY)
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("elevenlabs package not installed. Run: pip install elevenlabs")
        
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")
        
        self.client = ElevenLabs(api_key=self.api_key)
        logger.info("✅ ElevenLabs voice generator initialized")
    
    def generate(
        self,
        text: str,
        output_path: str,
        voice: str = "rachel",
        model: str = "eleven_multilingual_v2",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> tuple[str, float]:
        """
        Générer voix avec ElevenLabs
        
        Args:
            text: Texte à synthétiser
            output_path: Chemin de sortie MP3
            voice: Nom de la voix (ou ID)
            model: Modèle ElevenLabs
            stability: Stabilité de la voix (0-1)
            similarity_boost: Boost de similarité (0-1)
        
        Returns:
            tuple: (chemin_audio, durée_secondes)
        """
        try:
            logger.info(f"🎤 Génération voix ElevenLabs ({voice})...")
            start_time = time.time()
            
            # Récupérer l'ID de la voix
            voice_id = self.PREMIUM_VOICES.get(voice.lower(), voice)
            
            # Générer l'audio avec nouvelle API (v2.33+)
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model,
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            )
            
            # Convertir generator en bytes
            audio_bytes = b"".join(audio_generator)
            
            # Sauvegarder
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            
            # Calculer durée réelle
            generation_time = time.time() - start_time
            
            # Estimer durée audio (basé sur taille - ~16KB/sec pour MP3 64kbps)
            duration = len(audio_bytes) / (16 * 1024)  # Approximation
            
            logger.info(f"✅ Voix générée: {output_file} (~{duration:.1f}s) en {generation_time:.1f}s")
            logger.info(f"📊 Taille: {len(audio_bytes):,} bytes ({len(text)} caractères)")
            
            return str(output_file), duration
            
        except Exception as e:
            logger.error(f"❌ Erreur ElevenLabs: {e}")
            raise
    
    def get_available_voices(self) -> list:
        """Récupérer toutes les voix disponibles"""
        try:
            voices_response = self.client.voices.get_all()
            return [
                {
                    "name": v.name,
                    "voice_id": v.voice_id,
                    "category": getattr(v, 'category', 'unknown'),
                    "description": getattr(v, 'description', ''),
                }
                for v in voices_response.voices
            ]
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return []
    
    def get_character_count(self, text: str) -> int:
        """Calculer le nombre de caractères (pour quota)"""
        return len(text)
    
    @staticmethod
    def estimate_monthly_cost(videos_per_month: int, avg_script_length: int = 150) -> dict:
        """
        Estimer le coût mensuel ElevenLabs
        
        Args:
            videos_per_month: Nombre de vidéos par mois
            avg_script_length: Longueur moyenne du script (mots)
        
        Returns:
            dict: Infos de coût
        """
        # ~7 caractères par mot en moyenne (français/anglais)
        chars_per_video = avg_script_length * 7
        total_chars = videos_per_month * chars_per_video
        
        # Plans ElevenLabs (2024)
        if total_chars <= 10000:
            plan = "Free"
            cost = 0
        elif total_chars <= 30000:
            plan = "Starter"
            cost = 5
        elif total_chars <= 100000:
            plan = "Creator"
            cost = 22
        else:
            plan = "Pro"
            cost = 99
        
        return {
            "videos_per_month": videos_per_month,
            "total_characters": total_chars,
            "recommended_plan": plan,
            "monthly_cost": cost,
            "cost_per_video": cost / videos_per_month if videos_per_month > 0 else 0
        }


# Fonction helper pour compatibilité avec VoiceGenerator existant
def generate_elevenlabs_voice(
    text: str,
    output_path: str,
    voice: str = "rachel"
) -> tuple[str, float]:
    """
    Helper function pour générer voix avec ElevenLabs
    
    Args:
        text: Texte à synthétiser
        output_path: Chemin de sortie
        voice: Nom de la voix
    
    Returns:
        tuple: (chemin, durée)
    """
    generator = ElevenLabsVoiceGenerator()
    return generator.generate(text, output_path, voice)


if __name__ == "__main__":
    # Test du module
    logging.basicConfig(level=logging.INFO)
    
    # Estimer coût pour différents scénarios
    print("\n💰 ESTIMATION COÛTS ELEVENLABS\n")
    print("=" * 50)
    
    scenarios = [
        (10, "10 vidéos/mois (test)"),
        (30, "30 vidéos/mois (launch)"),
        (100, "100 vidéos/mois (scaling)"),
        (300, "300 vidéos/mois (agency)")
    ]
    
    for videos, desc in scenarios:
        cost = ElevenLabsVoiceGenerator.estimate_monthly_cost(videos)
        print(f"\n📊 {desc}")
        print(f"  Caractères: {cost['total_characters']:,}")
        print(f"  Plan: {cost['recommended_plan']}")
        print(f"  Coût: ${cost['monthly_cost']}/mois")
        print(f"  Coût/vidéo: ${cost['cost_per_video']:.2f}")
    
    print("\n" + "=" * 50)
    
    # Test génération si API key disponible
    if os.getenv('ELEVENLABS_API_KEY'):
        print("\n🎤 TEST DE GÉNÉRATION VOCALE\n")
        try:
            generator = ElevenLabsVoiceGenerator()
            
            test_text = """
            Hey there! Today I want to share an amazing product with you.
            This has completely changed my daily routine and I think you'll love it too.
            Check the link in my bio to learn more!
            """
            
            audio_path, duration = generator.generate(
                text=test_text.strip(),
                output_path="test_elevenlabs_voice.mp3",
                voice="rachel"
            )
            
            print(f"✅ Test réussi!")
            print(f"📁 Fichier: {audio_path}")
            print(f"⏱️  Durée: {duration:.1f}s")
            
            # Tester d'autres voix
            print("\n🎭 Test de différentes voix...")
            for voice_name in ["bella", "adam", "josh"]:
                try:
                    audio_path, duration = generator.generate(
                        text="This is a test of a different voice.",
                        output_path=f"test_{voice_name}.mp3",
                        voice=voice_name
                    )
                    print(f"  ✅ {voice_name.capitalize()}: {audio_path}")
                except Exception as e:
                    print(f"  ❌ {voice_name}: {e}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            print("💡 Vérifiez ELEVENLABS_API_KEY dans .env")
    else:
        print("\n💡 Pour tester: ajoutez ELEVENLABS_API_KEY dans .env")
