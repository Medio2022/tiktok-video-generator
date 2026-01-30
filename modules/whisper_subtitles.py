"""
Générateur de sous-titres avec Whisper
Transcription précise depuis l'audio pour synchronisation parfaite
"""

import logging
import whisper
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_subtitles_from_audio(audio_path: str, output_srt: str, model_size: str = "base") -> str:
    """
    Générer sous-titres parfaitement synchronisés avec Whisper
    
    Args:
        audio_path: Chemin vers fichier audio
        output_srt: Chemin de sortie pour fichier SRT
        model_size: Taille du modèle Whisper (tiny, base, small, medium, large)
                   - tiny: très rapide, moins précis
                   - base: bon équilibre (recommandé)
                   - small/medium/large: plus précis mais plus lent
    
    Returns:
        Chemin du fichier SRT généré
    """
    logger.info(f"🎤 Transcription Whisper (modèle: {model_size})")
    
    # Charger modèle Whisper
    model = whisper.load_model(model_size)
    
    # Transcrire avec timestamps au niveau des mots
    logger.info(f"🔍 Analyse audio: {audio_path}")
    result = model.transcribe(
        audio_path,
        language="fr",  # Français
        word_timestamps=True,  # Timestamps précis par mot
        verbose=False
    )
    
    # Créer fichier SRT
    logger.info(f"✍️  Génération SRT avec {len(result['segments'])} segments")
    
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result['segments'], 1):
            # Format timestamp SRT: HH:MM:SS,mmm
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
    
    logger.info(f"✅ Sous-titres synchronisés générés: {output_srt}")
    return output_srt


def format_timestamp(seconds: float) -> str:
    """
    Convertir secondes en format SRT (HH:MM:SS,mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    test_audio = "output/tiktok_20260128_234737/voiceover.mp3"
    test_output = "output/tiktok_20260128_234737/subtitles_whisper.srt"
    
    if Path(test_audio).exists():
        generate_subtitles_from_audio(test_audio, test_output, model_size="base")
        print(f"\n✅ Test réussi: {test_output}")
