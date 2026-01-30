"""
Assembleur de vidéo TikTok avec FFmpeg
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional
import ffmpeg
from config import VIDEO_CONFIG, OUTPUT_DIR

logger = logging.getLogger(__name__)


class VideoAssembler:
    def __init__(self):
        """Initialiser l'assembleur vidéo"""
        self.config = VIDEO_CONFIG
        self.width, self.height = self.config["resolution"]
        self.fps = self.config["fps"]
    
    def assemble(
        self,
        audio_path: str,
        background_path: str,
        subtitle_path: str,
        output_path: Optional[str] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        Assembler la vidéo finale
        
        Args:
            audio_path: Chemin vers l'audio (voix off)
            background_path: Chemin vers l'image/vidéo de fond
            subtitle_path: Chemin vers le fichier SRT
            output_path: Chemin de sortie (optionnel)
            duration: Durée de la vidéo (optionnel, déduit de l'audio sinon)
            
        Returns:
            Chemin de la vidéo finale
        """
        logger.info("🎬 Assemblage de la vidéo...")
        
        if output_path is None:
            output_path = OUTPUT_DIR / "final_video.mp4"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Construire la commande FFmpeg
            self._assemble_with_ffmpeg(
                audio_path=audio_path,
                background_path=background_path,
                subtitle_path=subtitle_path,
                output_path=str(output_path),
                duration=duration
            )
            
            logger.info(f"✅ Vidéo assemblée: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'assemblage: {e}")
            raise
    
    def _assemble_with_ffmpeg(
        self,
        audio_path: str,
        background_path: str,
        subtitle_path: str,
        output_path: str,
        duration: Optional[float] = None
    ):
        """Assembler avec FFmpeg (méthode subprocess pour plus de contrôle)"""
        
        # Style des sous-titres
        subtitle_style = (
            "FontName=Arial Bold,"
            "FontSize=32,"
            "PrimaryColour=&HFFFFFF,"  # Blanc
            "OutlineColour=&H000000,"  # Noir
            "BackColour=&H80000000,"   # Fond semi-transparent
            "Outline=3,"
            "Shadow=2,"
            "Alignment=2,"  # Centré en haut
            "MarginV=100"   # Marge verticale
        )
        
        # Construire la commande FFmpeg
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-loop", "1",
            "-i", background_path,  # Image de fond
            "-i", audio_path,  # Audio
            "-vf", (
                f"scale={self.width}:{self.height}:force_original_aspect_ratio=decrease,"
                f"pad={self.width}:{self.height}:(ow-iw)/2:(oh-ih)/2,"
                f"subtitles={subtitle_path}:force_style='{subtitle_style}',"
                "zoompan=z='min(zoom+0.0005,1.05)':d=1:s=1080x1920:fps=30"  # Zoom léger
            ),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", self.config["audio_bitrate"],
            "-shortest",  # Durée = durée de l'audio
            "-movflags", "+faststart",  # Optimisation streaming
            output_path
        ]
        
        if duration:
            cmd.extend(["-t", str(duration)])
        
        logger.info("🔧 Exécution FFmpeg...")
        logger.debug(f"Commande: {' '.join(cmd)}")
        
        # Exécuter FFmpeg
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            logger.error(f"FFmpeg stderr: {process.stderr}")
            raise RuntimeError(f"FFmpeg a échoué avec le code {process.returncode}")
        
        logger.info("✅ FFmpeg terminé")
    
    def assemble_simple(
        self,
        audio_path: str,
        background_color: tuple = (20, 20, 40),
        subtitle_path: str = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Assembler une vidéo simple avec fond de couleur (sans Imagen)
        
        Args:
            audio_path: Chemin vers l'audio
            background_color: Couleur RGB du fond
            subtitle_path: Chemin vers les sous-titres
            output_path: Chemin de sortie
            
        Returns:
            Chemin de la vidéo finale
        """
        logger.info("🎬 Assemblage vidéo simple (fond coloré)...")
        
        if output_path is None:
            output_path = OUTPUT_DIR / "final_video.mp4"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Créer un fond de couleur avec FFmpeg
            r, g, b = background_color
            color_hex = f"0x{r:02x}{g:02x}{b:02x}"
            
            subtitle_style = (
                "FontName=Arial Bold,"
                "FontSize=32,"
                "PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,"
                "BackColour=&H80000000,"
                "Outline=3,"
                "Shadow=2,"
                "Alignment=2,"
                "MarginV=100"
            )
            
            cmd = [
                "ffmpeg",
                "-y",
                "-f", "lavfi",
                "-i", f"color=c={color_hex}:s={self.width}x{self.height}:r={self.fps}",
                "-i", audio_path,
            ]
            
            # Filtres vidéo
            # NOTE: Sous-titres désactivés temporairement (problème d'échappement FFmpeg)
            # Les sous-titres sont générés dans subtitles.srt et peuvent être ajoutés en post-production
            cmd.extend([
                "-vf",
                "zoompan=z='min(zoom+0.0005,1.05)':d=1:s=1080x1920:fps=30"
            ])
            
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", self.config["audio_bitrate"],
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ])
            
            logger.info("🔧 Exécution FFmpeg (fond coloré)...")
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"FFmpeg stderr: {process.stderr}")
                raise RuntimeError(f"FFmpeg a échoué avec le code {process.returncode}")
            
            logger.info(f"✅ Vidéo assemblée: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'assemblage: {e}")
            raise


if __name__ == "__main__":
    # Test de l'assembleur
    logging.basicConfig(level=logging.INFO)
    
    assembler = VideoAssembler()
    
    print("⚠️  Pour tester, vous devez avoir:")
    print("  - output/test_voiceover.mp3")
    print("  - output/background.png (ou utiliser assemble_simple)")
    print("  - output/subtitles.srt")
    print("\nExemple:")
    print('  assembler.assemble_simple("output/test_voiceover.mp3", subtitle_path="output/subtitles.srt")')
