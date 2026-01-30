"""
Animateur de sous-titres pour vidéos TikTok
Ajoute des sous-titres animés style TikTok avec effets
"""

import logging
from pathlib import Path
from typing import List, Dict, Tuple
import re

logger = logging.getLogger(__name__)


class SubtitleAnimator:
    """Gère l'ajout de sous-titres animés aux vidéos"""
    
    def __init__(self):
        """Initialiser l'animateur"""
        self.font = None  # Utiliser la police système par défaut
        self.fontsize = 70
        self.color = "white"
        self.stroke_color = "black"
        self.stroke_width = 3
    
    def parse_srt(self, srt_path: str) -> List[Dict]:
        """
        Parser un fichier SRT
        
        Args:
            srt_path: Chemin vers le fichier SRT
            
        Returns:
            Liste de dictionnaires avec timing et texte
        """
        import pysrt
        
        subtitles = []
        subs = pysrt.open(srt_path)
        
        for sub in subs:
            # Convertir le timing en secondes
            start = (sub.start.hours * 3600 + 
                    sub.start.minutes * 60 + 
                    sub.start.seconds + 
                    sub.start.milliseconds / 1000.0)
            
            end = (sub.end.hours * 3600 + 
                  sub.end.minutes * 60 + 
                  sub.end.seconds + 
                  sub.end.milliseconds / 1000.0)
            
            subtitles.append({
                'start': start,
                'end': end,
                'text': sub.text.replace('\n', ' ')
            })
        
        return subtitles
    
    def create_subtitle_clip(self, text: str, start: float, end: float, 
                            video_size: Tuple[int, int]):
        """
        Créer un clip de sous-titre avec animations
        
        Args:
            text: Texte du sous-titre
            start: Temps de début (secondes)
            end: Temps de fin (secondes)
            video_size: Taille de la vidéo (width, height)
            
        Returns:
            Clip de texte animé
        """
        from moviepy import TextClip
        
        # Créer le clip de texte avec la nouvelle API
        txt_clip = TextClip(
            text=text,
            font_size=self.fontsize,
            font=self.font,
            color=self.color,
            stroke_color=self.stroke_color,
            stroke_width=self.stroke_width
        )
        
        # Position en bas de l'écran
        txt_clip = txt_clip.with_position(('center', video_size[1] - 300))
        
        # Timing
        txt_clip = txt_clip.with_start(start)
        txt_clip = txt_clip.with_duration(end - start)
        
        # Note: animations fade in/out non supportées dans moviepy 2.2.1
        # Les sous-titres apparaissent instantanément (style TikTok classique)
        
        return txt_clip
    
    def add_subtitles_to_video(self, video_path: str, srt_path: str, 
                               output_path: str) -> bool:
        """
        Ajouter des sous-titres animés à une vidéo
        
        Args:
            video_path: Chemin de la vidéo source
            srt_path: Chemin du fichier SRT
            output_path: Chemin de la vidéo de sortie
            
        Returns:
            True si succès
        """
        try:
            from moviepy import VideoFileClip, CompositeVideoClip
            
            logger.info(f"🎬 Chargement vidéo: {video_path}")
            video = VideoFileClip(video_path)
            
            logger.info(f"📝 Parsing sous-titres: {srt_path}")
            subtitles = self.parse_srt(srt_path)
            
            logger.info(f"✨ Création de {len(subtitles)} clips de sous-titres animés")
            subtitle_clips = []
            
            for i, sub in enumerate(subtitles, 1):
                logger.info(f"  {i}/{len(subtitles)}: {sub['text'][:30]}...")
                clip = self.create_subtitle_clip(
                    sub['text'],
                    sub['start'],
                    sub['end'],
                    video.size
                )
                subtitle_clips.append(clip)
            
            logger.info("🎨 Composition de la vidéo finale")
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            logger.info(f"💾 Exportation: {output_path}")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                preset='medium',
                bitrate='2000k',
                logger=None  # Désactiver les logs verbeux de moviepy
            )
            
            # Nettoyer
            video.close()
            final_video.close()
            
            logger.info("✅ Sous-titres ajoutés avec succès!")
            return True
            
        except ImportError as e:
            logger.error(f"❌ Librairie manquante: {e}")
            logger.error("Installez avec: pip install moviepy pysrt")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    animator = SubtitleAnimator()
    
    # Chemins de test
    video_path = "output/tiktok_20260128_225344/temp_no_subs.mp4"
    srt_path = "output/tiktok_20260128_225344/subtitles.srt"
    output_path = "output/tiktok_20260128_225344/final_with_subs.mp4"
    
    success = animator.add_subtitles_to_video(video_path, srt_path, output_path)
    
    if success:
        print(f"\n✅ Vidéo créée: {output_path}")
    else:
        print("\n❌ Échec")
