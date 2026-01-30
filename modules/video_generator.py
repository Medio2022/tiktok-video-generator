"""
Générateur de vidéos avec Pexels API
Télécharge et cache des vidéos HD stock gratuites
"""

import logging
import requests
import hashlib
from pathlib import Path
from typing import Optional, List, Dict
from config import PEXELS_API_KEY, PEXELS_VIDEO_QUALITY, VIDEO_CACHE_DIR, VIDEO_CACHE_ENABLED

logger = logging.getLogger(__name__)


class VideoGenerator:
    def __init__(self, api_key: str = PEXELS_API_KEY):
        """Initialiser le générateur de vidéos"""
        if not api_key:
            logger.warning("⚠️  PEXELS_API_KEY manquante - utilisation de fonds colorés uniquement")
            self.api_key = None
        else:
            self.api_key = api_key
        
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {"Authorization": api_key} if api_key else {}
        self.cache_dir = VIDEO_CACHE_DIR
        self.cache_enabled = VIDEO_CACHE_ENABLED
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, keywords: List[str]) -> Path:
        """Générer le chemin de cache pour des mots-clés"""
        # Hash des mots-clés pour nom de fichier unique
        keywords_str = "_".join(sorted(keywords))
        hash_key = hashlib.md5(keywords_str.encode()).hexdigest()[:12]
        return self.cache_dir / f"pexels_{hash_key}.mp4"
    
    def search_videos(
        self,
        keywords: List[str],
        per_page: int = 10,
        orientation: str = "portrait"
    ) -> List[Dict]:
        """
        Rechercher des vidéos sur Pexels
        
        Args:
            keywords: Liste de mots-clés
            per_page: Nombre de résultats
            orientation: portrait, landscape, square
            
        Returns:
            Liste de vidéos avec URLs
        """
        if not self.api_key:
            logger.warning("⚠️  Pas de clé Pexels - retour vide")
            return []
        
        query = " ".join(keywords)
        logger.info(f"🔍 Recherche Pexels: '{query}'")
        
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": orientation
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("videos", [])
            
            logger.info(f"✅ Trouvé {len(videos)} vidéos")
            return videos
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur recherche Pexels: {e}")
            return []
    
    def download_video(
        self,
        video_url: str,
        output_path: Path
    ) -> bool:
        """
        Télécharger une vidéo
        
        Args:
            video_url: URL de la vidéo
            output_path: Chemin de sortie
            
        Returns:
            True si succès
        """
        try:
            logger.info(f"⬇️  Téléchargement vidéo...")
            
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"✅ Vidéo téléchargée: {file_size:.1f} MB")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur téléchargement: {e}")
            return False
    
    def get_best_video_url(
        self,
        video: Dict,
        quality: str = PEXELS_VIDEO_QUALITY
    ) -> Optional[str]:
        """
        Extraire la meilleure URL de vidéo
        
        Args:
            video: Objet vidéo Pexels
            quality: hd ou sd
            
        Returns:
            URL de la vidéo ou None
        """
        video_files = video.get("video_files", [])
        
        # Filtrer par qualité et format portrait
        candidates = [
            vf for vf in video_files
            if vf.get("quality") == quality
            and vf.get("width", 0) < vf.get("height", 0)  # Portrait
        ]
        
        if not candidates:
            # Fallback: n'importe quelle qualité portrait
            candidates = [
                vf for vf in video_files
                if vf.get("width", 0) < vf.get("height", 0)
            ]
        
        if not candidates:
            logger.warning("⚠️  Aucune vidéo portrait trouvée")
            return None
        
        # Prendre la première
        return candidates[0].get("link")
    
    def generate(
        self,
        keywords: List[str],
        output_path: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Générer/télécharger une vidéo stock
        
        Args:
            keywords: Mots-clés pour recherche
            output_path: Chemin de sortie (optionnel)
            use_cache: Utiliser le cache
            
        Returns:
            Chemin de la vidéo ou None
        """
        if not self.api_key:
            logger.warning("⚠️  Pas de clé Pexels - retour None")
            return None
        
        # Vérifier le cache
        if use_cache and self.cache_enabled:
            cache_path = self._get_cache_path(keywords)
            if cache_path.exists():
                logger.info(f"✅ Vidéo trouvée en cache: {cache_path}")
                return str(cache_path)
        
        # Rechercher des vidéos
        videos = self.search_videos(keywords, per_page=5)
        
        if not videos:
            logger.warning(f"⚠️  Aucune vidéo trouvée pour: {keywords}")
            return None
        
        # Prendre la première vidéo
        video = videos[0]
        video_url = self.get_best_video_url(video)
        
        if not video_url:
            logger.warning("⚠️  Impossible d'extraire l'URL vidéo")
            return None
        
        # Déterminer le chemin de sortie
        if output_path:
            final_path = Path(output_path)
        elif use_cache and self.cache_enabled:
            final_path = self._get_cache_path(keywords)
        else:
            final_path = Path("output") / "temp_video.mp4"
        
        final_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Télécharger
        success = self.download_video(video_url, final_path)
        
        if success:
            logger.info(f"✅ Vidéo générée: {final_path}")
            return str(final_path)
        else:
            return None
    
    def generate_with_fallback(
        self,
        keywords: List[str],
        output_path: Optional[str] = None
    ) -> tuple[Optional[str], str]:
        """
        Générer une vidéo avec fallback sur fond coloré
        
        Args:
            keywords: Mots-clés
            output_path: Chemin de sortie
            
        Returns:
            (chemin_vidéo, type) où type = "pexels" ou "color"
        """
        # Essayer Pexels
        video_path = self.generate(keywords, output_path)
        
        if video_path:
            return video_path, "pexels"
        
        # Fallback: retourner None pour utiliser fond coloré
        logger.info("ℹ️  Fallback sur fond coloré")
        return None, "color"


if __name__ == "__main__":
    # Test du générateur
    logging.basicConfig(level=logging.INFO)
    
    try:
        generator = VideoGenerator()
        
        # Test recherche
        keywords = ["workspace", "typing", "computer"]
        video_path = generator.generate(keywords)
        
        if video_path:
            print(f"\n✅ Vidéo générée: {video_path}")
        else:
            print("\n⚠️  Échec génération (clé API manquante ou aucun résultat)")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
