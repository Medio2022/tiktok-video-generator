"""
Assembleur Vidéo Complet pour TikTok
Combine vidéo Pexels HD + audio + sous-titres cyan synchronisés
"""

import logging
import os
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip
import pysrt

logger = logging.getLogger(__name__)


def wrap_text(text: str, font, max_width: int) -> list:
    """
    Couper le texte en plusieurs lignes si trop long
    
    Args:
        text: Texte à couper
        font: Police PIL
        max_width: Largeur maximale en pixels
        
    Returns:
        Liste de lignes
    """
    from PIL import ImageDraw
    
    # Créer un draw temporaire pour mesurer
    temp_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    
    # Si le texte tient sur une ligne
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    
    if text_width <= max_width:
        return [text]
    
    # Couper par mots
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Tester avec le mot ajouté
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        
        if test_width <= max_width:
            current_line.append(word)
        else:
            # Ligne pleine, commencer nouvelle ligne
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Ajouter dernière ligne
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def create_subtitle_image(
    text: str,
    width: int = 1080,
    height: int = 250,
    font_size: int = 85,
    text_color: Tuple[int, int, int, int] = (0, 255, 255, 255),
    outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    outline_width: int = 5
) -> np.ndarray:
    """
    Créer une image de sous-titre avec PIL (avec retour à la ligne automatique)
    
    Args:
        text: Texte du sous-titre
        width: Largeur de l'image
        height: Hauteur de l'image
        font_size: Taille de la police
        text_color: Couleur du texte RGBA
        outline_color: Couleur de la bordure RGBA
        outline_width: Épaisseur de la bordure
        
    Returns:
        Image numpy array RGBA
    """
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Couper texte si trop long (80% de la largeur max)
    max_text_width = int(width * 0.8)
    lines = wrap_text(text, font, max_text_width)
    
    # Calculer hauteur totale pour centrage vertical
    line_height = font_size + 10  # Espacement entre lignes
    total_height = len(lines) * line_height
    start_y = (height - total_height) // 2
    
    # Dessiner chaque ligne centrée
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        
        # Centrer horizontalement
        x = (width - line_width) // 2
        y = start_y + i * line_height
        
        # Dessiner bordure
        for offset_x in range(-outline_width, outline_width + 1):
            for offset_y in range(-outline_width, outline_width + 1):
                if offset_x**2 + offset_y**2 <= outline_width**2:
                    draw.text((x + offset_x, y + offset_y), line, font=font, fill=outline_color)
        
        # Dessiner texte
        draw.text((x, y), line, font=font, fill=text_color)
    
    return np.array(img)


def assemble_complete_video(
    pexels_video_path: str,
    audio_path: str,
    srt_path: str,
    output_path: str,
    subtitle_color: Tuple[int, int, int, int] = (0, 255, 255, 255),
    subtitle_size: int = 85,
    outline_width: int = 5,
    position_from_bottom: int = 300
) -> str:
    """
    Assembler vidéo complète: vidéo Pexels + audio + sous-titres
    
    Args:
        pexels_video_path: Chemin vers vidéo Pexels téléchargée
        audio_path: Chemin vers fichier audio (voix off)
        srt_path: Chemin vers fichier SRT (sous-titres synchronisés)
        output_path: Chemin de sortie pour vidéo finale
        subtitle_color: Couleur RGBA des sous-titres (défaut cyan)
        subtitle_size: Taille de police des sous-titres
        outline_width: Épaisseur bordure sous-titres
        position_from_bottom: Position sous-titres depuis le bas
        
    Returns:
        Chemin de la vidéo finale
    """
    logger.info("🎬 Assemblage vidéo complète avec Pexels + sous-titres")
    
    # Charger vidéo Pexels
    logger.info(f"📹 Chargement vidéo Pexels: {pexels_video_path}")
    video = VideoFileClip(pexels_video_path)
    
    # Charger audio
    logger.info(f"🎵 Chargement audio: {audio_path}")
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration
    
    logger.info(f"⏱️  Durée audio: {audio_duration:.2f}s")
    
    # Boucler la vidéo si nécessaire
    if video.duration < audio_duration:
        loops_needed = int(np.ceil(audio_duration / video.duration))
        logger.info(f"🔁 Bouclage vidéo x{loops_needed} ({video.duration:.2f}s -> ~{audio_duration:.2f}s)")
        
        # Créer une liste de clips répétés
        video_clips = [video] * loops_needed
        video = CompositeVideoClip([c.with_start(i * video.duration) for i, c in enumerate(video_clips)]).with_duration(audio_duration)
    
    # Couper à la durée exacte de l'audio
    video = video.subclipped(0, audio_duration)
    
    # Redimensionner pour format TikTok 9:16 (1080x1920)
    logger.info("📐 Redimensionnement format TikTok 1080x1920")
    video = video.resized(height=1920)
    
    # Crop au centre si nécessaire
    if video.w > 1080:
        video = video.cropped(x_center=video.w/2, width=1080)
    
    # Ajouter audio
    video = video.with_audio(audio)
    
    # Charger et ajouter sous-titres
    logger.info(f"📝 Chargement sous-titres: {srt_path}")
    subs = pysrt.open(srt_path, encoding='utf-8')
    
    logger.info(f"✨ Création de {len(subs)} sous-titres")
    subtitle_clips = []
    
    for i, sub in enumerate(subs, 1):
        start = (sub.start.hours * 3600 + sub.start.minutes * 60 + 
                sub.start.seconds + sub.start.milliseconds / 1000.0)
        end = (sub.end.hours * 3600 + sub.end.minutes * 60 + 
              sub.end.seconds + sub.end.milliseconds / 1000.0)
        
        # Créer image sous-titre
        img_array = create_subtitle_image(
            sub.text,
            font_size=subtitle_size,
            text_color=subtitle_color,
            outline_width=outline_width
        )
        
        # Créer clip
        clip = ImageClip(img_array)
        clip = clip.with_position(('center', video.size[1] - position_from_bottom))
        clip = clip.with_start(start)
        clip = clip.with_duration(end - start)
        
        subtitle_clips.append(clip)
    
    # Composer vidéo finale
    logger.info("🎨 Composition vidéo + sous-titres")
    final = CompositeVideoClip([video] + subtitle_clips)
    
    # Exporter
    logger.info(f"💾 Exportation: {output_path}")
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        preset='medium',
        bitrate='2500k',
        logger=None
    )
    
    # Nettoyer
    video.close()
    audio.close()
    final.close()
    
    logger.info("✅ Vidéo complète assemblée avec succès!")
    return output_path


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    test_video = "output/tiktok_20260128_232446/background_video.mp4"
    test_audio = "output/tiktok_20260128_232446/voiceover.mp3"
    test_srt = "output/tiktok_20260128_232446/subtitles_fixed.srt"
    test_output = "output/tiktok_20260128_232446/ASSEMBLED_TEST.mp4"
    
    if os.path.exists(test_video):
        result = assemble_complete_video(
            test_video,
            test_audio,
            test_srt,
            test_output,
            subtitle_color=(0, 255, 255, 255)  # Cyan
        )
        print(f"\n✅ Test réussi: {result}")
