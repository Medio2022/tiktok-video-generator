"""
Validateurs pour les outputs du pipeline
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess

logger = logging.getLogger(__name__)


class VideoValidator:
    """Validateur pour les vidéos générées"""
    
    @staticmethod
    def validate_video(video_path: str) -> Tuple[bool, Dict]:
        """
        Valider une vidéo avec FFprobe
        
        Args:
            video_path: Chemin vers la vidéo
            
        Returns:
            Tuple (is_valid, metadata)
        """
        logger.info(f"🔍 Validation de la vidéo: {video_path}")
        
        if not Path(video_path).exists():
            logger.error(f"❌ Fichier introuvable: {video_path}")
            return False, {"error": "File not found"}
        
        try:
            # Utiliser FFprobe pour obtenir les métadonnées
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ FFprobe a échoué: {result.stderr}")
                return False, {"error": "FFprobe failed"}
            
            import json
            metadata = json.loads(result.stdout)
            
            # Extraire les informations importantes
            video_stream = None
            audio_stream = None
            
            for stream in metadata.get("streams", []):
                if stream["codec_type"] == "video":
                    video_stream = stream
                elif stream["codec_type"] == "audio":
                    audio_stream = stream
            
            if not video_stream:
                logger.error("❌ Pas de stream vidéo trouvé")
                return False, {"error": "No video stream"}
            
            if not audio_stream:
                logger.warning("⚠️  Pas de stream audio trouvé")
            
            # Vérifier les propriétés
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))
            duration = float(metadata.get("format", {}).get("duration", 0))
            size_mb = int(metadata.get("format", {}).get("size", 0)) / (1024 * 1024)
            
            info = {
                "width": width,
                "height": height,
                "duration": duration,
                "size_mb": size_mb,
                "has_audio": audio_stream is not None,
                "codec": video_stream.get("codec_name"),
            }
            
            # Validation des contraintes TikTok
            issues = []
            
            if width != 1080 or height != 1920:
                issues.append(f"Résolution incorrecte: {width}x{height} (attendu: 1080x1920)")
            
            if duration < 15:
                issues.append(f"Vidéo trop courte: {duration:.1f}s (min: 15s)")
            
            if duration > 60:
                issues.append(f"Vidéo trop longue: {duration:.1f}s (max: 60s)")
            
            if size_mb > 50:
                issues.append(f"Fichier trop lourd: {size_mb:.1f}MB (max: 50MB)")
            
            if not audio_stream:
                issues.append("Pas d'audio détecté")
            
            if issues:
                logger.warning(f"⚠️  Problèmes détectés:\n" + "\n".join(f"  - {i}" for i in issues))
                info["issues"] = issues
                return False, info
            
            logger.info(f"✅ Vidéo valide: {width}x{height}, {duration:.1f}s, {size_mb:.1f}MB")
            return True, info
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la validation: {e}")
            return False, {"error": str(e)}
    
    @staticmethod
    def validate_duration(duration: float, min_duration: float = 20, max_duration: float = 40) -> bool:
        """Valider la durée d'une vidéo"""
        if duration < min_duration:
            logger.warning(f"⚠️  Durée trop courte: {duration:.1f}s (min: {min_duration}s)")
            return False
        
        if duration > max_duration:
            logger.warning(f"⚠️  Durée trop longue: {duration:.1f}s (max: {max_duration}s)")
            return False
        
        return True
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: float = 50) -> bool:
        """Valider la taille d'un fichier"""
        size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            logger.warning(f"⚠️  Fichier trop lourd: {size_mb:.1f}MB (max: {max_size_mb}MB)")
            return False
        
        return True


if __name__ == "__main__":
    # Test du validateur
    logging.basicConfig(level=logging.INFO)
    
    validator = VideoValidator()
    
    # Tester avec une vidéo (si elle existe)
    test_video = "output/final_video.mp4"
    if Path(test_video).exists():
        is_valid, info = validator.validate_video(test_video)
        print(f"\n{'✅' if is_valid else '❌'} Validation: {is_valid}")
        print(f"📊 Métadonnées: {info}")
    else:
        print(f"⚠️  Fichier de test non trouvé: {test_video}")
