"""
Générateur de sous-titres avec PIL + moviepy
Render parfait avec contrôle total
"""

from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip
import numpy as np
import pysrt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_subtitle_image(text, width=1080, height=250, font_size=85, 
                          text_color=(255, 255, 255, 255),  # Blanc par défaut
                          outline_color=(0, 0, 0, 255),      # Noir par défaut
                          outline_width=5):
    """
    Créer une image de sous-titre avec PIL
    
    Args:
        text: Texte du sous-titre
        width: Largeur de l'image
        height: Hauteur de l'image
        font_size: Taille de la police (défaut 85)
        text_color: Couleur du texte RGBA (défaut blanc)
        outline_color: Couleur de la bordure RGBA (défaut noir)
        outline_width: Épaisseur de la bordure (défaut 5)
    """
    # Créer une image transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Charger la police
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Mesurer le texte
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position centrée
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Dessiner bordure (outline)
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x**2 + offset_y**2 <= outline_width**2:  # Cercle
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)
    
    # Dessiner texte principal
    draw.text((x, y), text, font=font, fill=text_color)
    
    # Convertir en numpy array
    return np.array(img)


def create_video_with_subs(video_path, srt_path, output_path,
                          font_size=85,
                          text_color=(255, 255, 255, 255),      # Blanc
                          outline_color=(0, 0, 0, 255),          # Noir
                          outline_width=5):
    """
    Créer vidéo avec sous-titres PIL personnalisables
    
    Args:
        font_size: Taille de police (85 par défaut, plus grand)
        text_color: Couleur texte RGBA - exemples:
                   (255, 255, 255, 255) = Blanc
                   (255, 255, 0, 255) = Jaune
                   (255, 100, 255, 255) = Rose/Magenta
        outline_color: Couleur bordure RGBA
        outline_width: Épaisseur bordure (5 par défaut)
    """
    logger.info(f"🎬 Chargement: {video_path}")
    video = VideoFileClip(video_path)
    
    logger.info(f"📝 Parsing: {srt_path}")
    subs = pysrt.open(srt_path, encoding='utf-8')
    
    logger.info(f"✨ Création de {len(subs)} sous-titres")
    subtitle_clips = []
    
    for i, sub in enumerate(subs, 1):
        start = (sub.start.hours * 3600 + sub.start.minutes * 60 + 
                sub.start.seconds + sub.start.milliseconds / 1000.0)
        end = (sub.end.hours * 3600 + sub.end.minutes * 60 + 
              sub.end.seconds + sub.end.milliseconds / 1000.0)
        
        logger.info(f"  {i}/{len(subs)}: {start:.2f}-{end:.2f}s '{sub.text}'")
        
        # Créer image avec les paramètres personnalisés
        img_array = create_subtitle_image(
            sub.text,
            font_size=font_size,
            text_color=text_color,
            outline_color=outline_color,
            outline_width=outline_width
        )
        
        # Créer clip à partir du numpy array
        clip = ImageClip(img_array)
        clip = clip.with_position(('center', video.size[1] - 300))
        clip = clip.with_start(start)
        clip = clip.with_duration(end - start)
        
        subtitle_clips.append(clip)
    
    logger.info("🎨 Composition")
    final = CompositeVideoClip([video] + subtitle_clips)
    
    logger.info("💾 Exportation")
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps,
        preset='medium',
        bitrate='2500k',
        logger=None
    )
    
    video.close()
    final.close()
    
    logger.info("✅ TERMINÉ!")
    return True


if __name__ == "__main__":
    video_path = "output/tiktok_20260128_225344/temp_no_subs.mp4"
    srt_path = "output/tiktok_20260128_225344/subtitles_fixed.srt"
    output_path = "output/tiktok_20260128_225344/FINAL_PERFECT.mp4"
    
    # OPTIONS DE COULEUR:
    # Blanc (défaut): (255, 255, 255, 255)
    # Jaune vif: (255, 255, 0, 255)
    # Rose/Magenta: (255, 100, 255, 255)
    # Cyan: (0, 255, 255, 255)
    # Orange: (255, 165, 0, 255)
    
    create_video_with_subs(
        video_path, 
        srt_path, 
        output_path,
        font_size=85,                      # Plus grand qu'avant (était 70)
        text_color=(0, 255, 255, 255),     # CYAN - couleur tendance !
        outline_color=(0, 0, 0, 255),      # Bordure noire
        outline_width=5                    # Bordure épaisse
    )
    print(f"\n🎉 Vidéo finale: {output_path}")
