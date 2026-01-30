"""
Générateur de voix off avec alternatives GRATUITES
Remplace Google Cloud TTS par des solutions sans coût
"""

import logging
from pathlib import Path
from typing import Optional, Literal
import asyncio

from config import OUTPUT_DIR

logger = logging.getLogger(__name__)


class VoiceGenerator:
    """Générateur de voix avec plusieurs backends gratuits"""
    
    def __init__(self, backend: Literal["edge", "gtts", "pyttsx3"] = "edge"):
        """
        Initialiser le générateur de voix
        
        Args:
            backend: Backend à utiliser
                - "edge": Edge TTS (Microsoft) - GRATUIT, meilleure qualité
                - "gtts": Google Translate TTS - GRATUIT, qualité moyenne
                - "pyttsx3": TTS offline - GRATUIT, qualité basique
        """
        self.backend = backend
        logger.info(f"🎤 Initialisation du générateur de voix: {backend}")
    
    def generate(self, text: str, output_path: Optional[str] = None) -> tuple[str, float]:
        """
        Générer une voix off à partir du texte
        
        Args:
            text: Texte du script
            output_path: Chemin de sortie (optionnel)
            
        Returns:
            Tuple (chemin_fichier, durée_secondes)
        """
        if output_path is None:
            output_path = OUTPUT_DIR / "voiceover.mp3"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.backend == "edge":
            return self._generate_edge_tts(text, str(output_path))
        elif self.backend == "gtts":
            return self._generate_gtts(text, str(output_path))
        elif self.backend == "pyttsx3":
            return self._generate_pyttsx3(text, str(output_path))
        else:
            raise ValueError(f"Backend inconnu: {self.backend}")
    
    def _generate_edge_tts(self, text: str, output_path: str) -> tuple[str, float]:
        """
        Générer avec Edge TTS (Microsoft) - GRATUIT
        Meilleure qualité, voix naturelles
        """
        logger.info("🎤 Génération avec Edge TTS (Microsoft)...")
        
        try:
            import edge_tts
        except ImportError:
            raise ImportError(
                "edge-tts non installé. Installez avec: pip install edge-tts"
            )
        
        # Voix françaises disponibles (gratuites)
        # Femme: fr-FR-DeniseNeural (naturelle)
        # Homme: fr-FR-HenriNeural (naturel)
        voice = "fr-FR-DeniseNeural"
        
        # Edge TTS est async, donc on utilise asyncio
        async def _generate():
            communicate = edge_tts.Communicate(text, voice, rate="+10%")
            await communicate.save(output_path)
        
        # Exécuter la génération
        asyncio.run(_generate())
        
        # Estimer la durée
        word_count = len(text.split())
        words_per_minute = 165  # Rate +10%
        duration = (word_count / words_per_minute) * 60
        
        logger.info(f"✅ Voix générée avec Edge TTS: {output_path} (~{duration:.1f}s)")
        
        return output_path, duration
    
    def _generate_gtts(self, text: str, output_path: str) -> tuple[str, float]:
        """
        Générer avec gTTS (Google Translate) - GRATUIT
        Qualité correcte, voix Google Translate
        """
        logger.info("🎤 Génération avec gTTS (Google Translate)...")
        
        try:
            from gtts import gTTS
        except ImportError:
            raise ImportError(
                "gTTS non installé. Installez avec: pip install gtts"
            )
        
        # Générer l'audio
        tts = gTTS(text=text, lang='fr', slow=False)
        tts.save(output_path)
        
        # Estimer la durée
        word_count = len(text.split())
        words_per_minute = 150
        duration = (word_count / words_per_minute) * 60
        
        logger.info(f"✅ Voix générée avec gTTS: {output_path} (~{duration:.1f}s)")
        
        return output_path, duration
    
    def _generate_pyttsx3(self, text: str, output_path: str) -> tuple[str, float]:
        """
        Générer avec pyttsx3 (TTS offline) - GRATUIT
        Qualité basique, fonctionne hors ligne
        """
        logger.info("🎤 Génération avec pyttsx3 (offline)...")
        
        try:
            import pyttsx3
        except ImportError:
            raise ImportError(
                "pyttsx3 non installé. Installez avec: pip install pyttsx3"
            )
        
        # Initialiser le moteur
        engine = pyttsx3.init()
        
        # Configurer la voix (chercher une voix française si disponible)
        voices = engine.getProperty('voices')
        french_voice = None
        
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.languages:
                french_voice = voice.id
                break
        
        if french_voice:
            engine.setProperty('voice', french_voice)
        
        # Configurer la vitesse (légèrement plus rapide)
        engine.setProperty('rate', 165)
        
        # Sauvegarder
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        # Estimer la durée
        word_count = len(text.split())
        words_per_minute = 165
        duration = (word_count / words_per_minute) * 60
        
        logger.info(f"✅ Voix générée avec pyttsx3: {output_path} (~{duration:.1f}s)")
        
        return output_path, duration
    
    @staticmethod
    def list_edge_voices():
        """Lister toutes les voix Edge TTS disponibles en français"""
        try:
            import edge_tts
            import asyncio
            
            async def _list():
                voices = await edge_tts.list_voices()
                french_voices = [v for v in voices if v['Locale'].startswith('fr-')]
                
                print("\n🎤 Voix françaises disponibles (Edge TTS - GRATUIT):\n")
                for voice in french_voices:
                    gender = voice['Gender']
                    name = voice['ShortName']
                    locale = voice['Locale']
                    print(f"  - {name} ({gender}, {locale})")
                
                return french_voices
            
            return asyncio.run(_list())
            
        except ImportError:
            print("❌ edge-tts non installé")
            return []


# Fonction helper pour compatibilité avec l'ancien code
def generate_voice(text: str, output_path: str = None, backend: str = "edge") -> tuple[str, float]:
    """
    Fonction helper pour générer une voix
    
    Args:
        text: Texte à synthétiser
        output_path: Chemin de sortie
        backend: Backend à utiliser (edge, gtts, pyttsx3)
        
    Returns:
        Tuple (chemin, durée)
    """
    generator = VoiceGenerator(backend=backend)
    return generator.generate(text, output_path)


if __name__ == "__main__":
    # Test des différents backends
    logging.basicConfig(level=logging.INFO)
    
    test_text = """Tu perds 3 heures par jour.
Sans même t'en rendre compte.
Voici comment arrêter ça.
Première erreur : ton téléphone.
Deuxième erreur : les notifications.
Troisième erreur : le multitasking.
Sauvegarde pour ne pas oublier."""
    
    print("\n" + "="*60)
    print("TEST DES BACKENDS TTS GRATUITS")
    print("="*60)
    
    # Test Edge TTS (recommandé)
    print("\n1️⃣  Test Edge TTS (Microsoft - GRATUIT)...")
    try:
        generator = VoiceGenerator(backend="edge")
        audio_path, duration = generator.generate(test_text, "output/test_edge.mp3")
        print(f"✅ Edge TTS: {audio_path} ({duration:.1f}s)")
    except Exception as e:
        print(f"❌ Edge TTS échoué: {e}")
    
    # Test gTTS
    print("\n2️⃣  Test gTTS (Google Translate - GRATUIT)...")
    try:
        generator = VoiceGenerator(backend="gtts")
        audio_path, duration = generator.generate(test_text, "output/test_gtts.mp3")
        print(f"✅ gTTS: {audio_path} ({duration:.1f}s)")
    except Exception as e:
        print(f"❌ gTTS échoué: {e}")
    
    # Test pyttsx3
    print("\n3️⃣  Test pyttsx3 (Offline - GRATUIT)...")
    try:
        generator = VoiceGenerator(backend="pyttsx3")
        audio_path, duration = generator.generate(test_text, "output/test_pyttsx3.mp3")
        print(f"✅ pyttsx3: {audio_path} ({duration:.1f}s)")
    except Exception as e:
        print(f"❌ pyttsx3 échoué: {e}")
    
    print("\n" + "="*60)
    print("RECOMMANDATION: Utilisez Edge TTS (meilleure qualité)")
    print("="*60)
    
    # Lister les voix Edge TTS
    print("\n")
    VoiceGenerator.list_edge_voices()
