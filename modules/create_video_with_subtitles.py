"""
Générateur de vidéo avec sous-titres via drawtext FFmpeg
Solution robuste sans problèmes d'échappement
"""

import subprocess
import pysrt
import json
from pathlib import Path


def create_video_with_subtitles(video_path, srt_path, output_path):
    """
    Créer une vidéo avec sous-titres en utilisant FFmpeg drawtext
    
    Args:
        video_path: Chemin de la vidéo source
        srt_path: Chemin du fichier SRT
        output_path: Chemin de sortie
    """
    # Charger les sous-titres
    subs = pysrt.open(srt_path, encoding='utf-8')
    
    # Créer les filtres drawtext pour chaque sous-titre
    drawtext_filters = []
    
    for sub in subs:
        # Convertir timing en secondes
        start = (sub.start.hours * 3600 + sub.start.minutes * 60 + 
                sub.start.seconds + sub.start.milliseconds / 1000.0)
        end = (sub.end.hours * 3600 + sub.end.minutes * 60 + 
              sub.end.seconds + sub.end.milliseconds / 1000.0)
        
        # Échapper le texte pour FFmpeg
        text = sub.text.replace('\\', '\\\\').replace("'", "'\\\\''").replace(':', '\\:')
        
        # Créer le filtre drawtext pour ce sous-titre
        filter_str = (
            f"drawtext="
            f"text='{text}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:"
            f"fontsize=60:"
            f"fontcolor=white:"
            f"borderw=3:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h-200:"
            f"enable='between(t,{start},{end})'"
        )
        
        drawtext_filters.append(filter_str)
    
    # Combiner tous les filtres
    filter_complex = ','.join(drawtext_filters)
    
    # Construire la commande FFmpeg
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', filter_complex,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'copy',
        output_path
    ]
    
    print(f"🎬 Création de la vidéo avec {len(subs)} sous-titres...")
    
    # Exécuter
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Vidéo créée: {output_path}")
        return True
    else:
        print(f"❌ Erreur FFmpeg:")
        print(result.stderr[-500:])
        return False


if __name__ == "__main__":
    video_path = "output/tiktok_20260128_225344/temp_no_subs.mp4"
    srt_path = "output/tiktok_20260128_225344/subtitles_fixed.srt"
    output_path = "output/tiktok_20260128_225344/final_ultimate.mp4"
    
    success = create_video_with_subtitles(video_path, srt_path, output_path)
    
    if success:
        print(f"\n🎉 SUCCÈS! Vidéo finale: {output_path}")
    else:
        print("\n❌ Échec")
