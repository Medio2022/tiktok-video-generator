import logging
from typing import List, Tuple, Optional
from moviepy import ImageClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from modules.config_schemas import SubtitleConfig

logger = logging.getLogger(__name__)

def hex_to_rgba(hex_color: str, opacity: float = 1.0) -> Tuple[int, int, int, int]:
    """Convertit hex (#RRGGBB) en tuple RGBA (R, G, B, A)"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(opacity * 255)
    
    return (r, g, b, a)
    
def create_word_image(text: str, font_size: int, font_path: str, color: Tuple[int, int, int, int], stroke_color: Tuple[int, int, int, int], stroke_width: int, video_width: int, scale: float = 1.0) -> np.ndarray:
    """Crée une image PIL pour un mot ou texte centré avec support scale (pop effect)"""
    
    # Créer image transparente large
    # Create temporary font to measure size
    try:
        current_font_size = int(font_size * scale)
        font = ImageFont.truetype(font_path, current_font_size)
    except:
        font = ImageFont.load_default()
        
    # Create distinct image for this word
    height = int(current_font_size * 2.0)  # More vertical space for pop effect
    img = Image.new('RGBA', (video_width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Font already loaded above
        
    # Calculer taille texte
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Centrer
    x = (video_width - text_width) // 2
    y = (height - text_height) // 2
    
    # Bordure
    if stroke_width > 0:
        for offset_x in range(-stroke_width, stroke_width + 1):
            for offset_y in range(-stroke_width, stroke_width + 1):
                if offset_x**2 + offset_y**2 <= stroke_width**2:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=stroke_color)

    # Texte principal
    draw.text((x, y), text, font=font, fill=color)
    
    return np.array(img)

def create_karaoke_clips(
    segments: list, 
    video_size: Tuple[int, int], 
    config: SubtitleConfig
) -> List[ImageClip]:
    """
    Génère des clips de sous-titres animés style Karaoke (PIL + ImageClip)
    """
    width, height = video_size
    clips = []
    
    # Fonts logic
    font_family = config.style.font_family or "Arial-Bold"
    font_map = {
        "Montserrat-Bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf", 
        "Arial-Bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    }
    font_path = font_map.get(font_family, "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    
    # Colors
    text_color_rgba = hex_to_rgba(config.style.text_color)
    highlight_color_rgba = hex_to_rgba(config.animation.highlight_color)
    stroke_color_rgba = hex_to_rgba(config.style.stroke_color)
    
    margin_bottom = config.position.margin_bottom
    
    logger.info(f"✨ Génération Karaoke (PIL Mode) - Font: {config.style.font_size}px")
    
    for segment in segments:
        words = segment.get('words', [])
        segment_text = segment['text'].strip()
        
        # Fallback static if no words
        if not words or not config.animation.word_by_word:
            arr = create_word_image(
                segment_text, config.style.font_size, font_path, 
                text_color_rgba, stroke_color_rgba, config.style.stroke_width, 
                width
            )
            clip = ImageClip(arr)
            clip = clip.with_position(('center', height - margin_bottom))
            clip = clip.with_start(segment['start'])
            clip = clip.with_duration(segment['end'] - segment['start'])
            clips.append(clip)
            continue
            
        # SAFE MODE: Static Rendering (No Karaoke) to fix "Double Vision"
        # We simply draw the full segment text once.
        # This guarantees legibility and removes any artifact.
        
        segment_text = segment['text'].strip()
        arr = create_word_image(
            segment_text, config.style.font_size, font_path, 
            text_color_rgba, stroke_color_rgba, config.style.stroke_width, 
            width
        )
        clip = ImageClip(arr)
        clip = clip.with_position(('center', height - margin_bottom))
        clip = clip.with_start(segment['start'])
        clip = clip.with_duration(segment['end'] - segment['start'])
        clips.append(clip)

    return clips
