"""
Correction automatique du timing des sous-titres
Basé sur la durée audio réelle vs estimation
"""

import logging
import pysrt
from pathlib import Path

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: str) -> float:
    """
    Obtenir la durée réelle d'un fichier audio
    
    Args:
        audio_path: Chemin vers fichier audio
        
    Returns:
        Durée en secondes
    """
    from moviepy import AudioFileClip
    
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()
    
    return duration


def fix_subtitle_timing(
    srt_path: str,
    audio_duration: float,
    estimated_duration: float,
    output_path: str = None
) -> str:
    """
    Corriger le timing des sous-titres basé sur durée audio réelle
    
    Args:
        srt_path: Chemin vers fichier SRT original
        audio_duration: Durée réelle de l'audio (secondes)
        estimated_duration: Durée estimée du script (secondes)
        output_path: Chemin de sortie (défaut: srt_path avec _fixed)
        
    Returns:
        Chemin du fichier SRT corrigé
    """
    if output_path is None:
        output_path = str(Path(srt_path).with_stem(Path(srt_path).stem + "_fixed"))
    
    logger.info(f"🔧 Correction timing sous-titres")
    logger.info(f"   Audio réel: {audio_duration:.2f}s")
    logger.info(f"   Estimation: {estimated_duration:.2f}s")
    
    # Charger sous-titres
    subs = pysrt.open(srt_path, encoding='utf-8')
    
    # Calculer facteur d'échelle
    scale_factor = audio_duration / estimated_duration
    logger.info(f"   Facteur: {scale_factor:.3f}x")
    
    # Appliquer à chaque sous-titre
    for sub in subs:
        # Convertir en secondes
        start_sec = (sub.start.hours * 3600 + sub.start.minutes * 60 + 
                    sub.start.seconds + sub.start.milliseconds / 1000.0)
        end_sec = (sub.end.hours * 3600 + sub.end.minutes * 60 + 
                  sub.end.seconds + sub.end.milliseconds / 1000.0)
        
        # Appliquer facteur
        new_start = start_sec * scale_factor
        new_end = end_sec * scale_factor
        
        # Reconvertir en format SRT
        sub.start.hours = int(new_start // 3600)
        sub.start.minutes = int((new_start % 3600) // 60)
        sub.start.seconds = int(new_start % 60)
        sub.start.milliseconds = int((new_start % 1) * 1000)
        
        sub.end.hours = int(new_end // 3600)
        sub.end.minutes = int((new_end % 3600) // 60)
        sub.end.seconds = int(new_end % 60)
        sub.end.milliseconds = int((new_end % 1) * 1000)
    
    # Sauvegarder
    subs.save(output_path, encoding='utf-8')
    logger.info(f"✅ Sous-titres corrigés: {output_path}")
    
    return output_path
