"""
Correcteur de timing de sous-titres
Aligne les sous-titres avec la durée réelle de l'audio
"""

import json
import pysrt
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def fix_subtitle_timing(metadata_path: str, srt_path: str, output_srt: str):
    """
    Corriger le timing des sous-titres basé sur la vraie durée audio
    
    Args:
        metadata_path: Chemin vers metadata.json
        srt_path: Chemin vers le fichier SRT original
        output_srt: Chemin de sortie pour le SRT corrigé
    """
    # Charger les métadonnées
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Récupérer la durée audio réelle
    audio_duration = metadata['audio_duration']
    
    # Charger les sous-titres
    subs = pysrt.open(srt_path, encoding='utf-8')
    
    logger.info(f"📊 Durée audio: {audio_duration}s")
    logger.info(f"📝 Nombre de sous-titres: {len(subs)}")
    
    # Trouver la durée totale des sous-titres originaux
    if subs:
        last_sub = subs[-1]
        original_duration = (last_sub.end.hours * 3600 + 
                            last_sub.end.minutes * 60 + 
                            last_sub.end.seconds + 
                            last_sub.end.milliseconds / 1000.0)
        
        logger.info(f"⏱️  Durée sous-titres originale: {original_duration}s")
        
        # Calculer le facteur d'échelle
        scale_factor = audio_duration / original_duration
        logger.info(f"🔧 Facteur d'échelle: {scale_factor:.3f}")
        
        # Ajuster chaque sous-titre
        for sub in subs:
            # Convertir en secondes
            start_sec = (sub.start.hours * 3600 + 
                        sub.start.minutes * 60 + 
                        sub.start.seconds + 
                        sub.start.milliseconds / 1000.0)
            
            end_sec = (sub.end.hours * 3600 + 
                      sub.end.minutes * 60 + 
                      sub.end.seconds + 
                      sub.end.milliseconds / 1000.0)
            
            # Appliquer le facteur d'échelle
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
        
        # Sauvegarder avec encodage UTF-8
        subs.save(output_srt, encoding='utf-8')
        logger.info(f"✅ Sous-titres corrigés sauvegardés: {output_srt}")
        
        # Afficher un aperçu
        logger.info("\n📋 Aperçu des premiers sous-titres:")
        for i, sub in enumerate(subs[:3], 1):
            logger.info(f"  {i}. {sub.start} --> {sub.end}")
            logger.info(f"     {sub.text}")
    
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Chemins
    metadata_path = "output/tiktok_20260128_225344/metadata.json"
    srt_path = "output/tiktok_20260128_225344/subtitles.srt"
    output_srt = "output/tiktok_20260128_225344/subtitles_fixed.srt"
    
    fix_subtitle_timing(metadata_path, srt_path, output_srt)
    
    print(f"\n✅ Timing corrigé! Utilisez {output_srt} pour la vidéo finale")
