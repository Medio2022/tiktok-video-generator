"""
Scheduler pour publication automatique TikTok
"""

import logging
import random
from datetime import datetime, time, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from config import PUBLICATION_CONFIG, DELAYS
from main import TikTokPipeline

logger = logging.getLogger(__name__)


class TikTokScheduler:
    """Scheduler pour automatiser la génération et publication"""
    
    def __init__(self, theme: str = "motivation"):
        """
        Initialiser le scheduler
        
        Args:
            theme: Thème du contenu
        """
        self.theme = theme
        self.pipeline = TikTokPipeline(theme=theme)
        self.scheduler = BlockingScheduler()
        self.config = PUBLICATION_CONFIG
        
        # Importer le publisher (optionnel)
        try:
            import sys
            sys.path.append(str(Path(__file__).parent))
            from playwright_script import TikTokPublisher
            self.publisher = TikTokPublisher(
                username=os.getenv("TIKTOK_USERNAME"),
                password=os.getenv("TIKTOK_PASSWORD"),
                headless=True
            )
            self.auto_publish = True
            logger.info("✅ Publisher TikTok activé")
        except ImportError:
            self.publisher = None
            self.auto_publish = False
            logger.warning("⚠️  Publisher TikTok non disponible (mode génération seule)")
    
    def _randomize_time(self, hour: int) -> tuple[int, int]:
        """
        Randomiser l'heure de publication
        
        Args:
            hour: Heure de base
            
        Returns:
            Tuple (heure, minute) randomisé
        """
        # Ajouter une variation aléatoire
        minutes = random.randint(0, 59)
        
        # Appliquer la randomisation configurée
        total_minutes = hour * 60 + minutes
        variation = random.randint(
            -self.config["randomize_minutes"],
            self.config["randomize_minutes"]
        )
        total_minutes += variation
        
        # Normaliser
        final_hour = (total_minutes // 60) % 24
        final_minute = total_minutes % 60
        
        return final_hour, final_minute
    
    def generate_and_publish_job(self):
        """Job de génération et publication"""
        logger.info("🎬 Démarrage du job de génération...")
        
        try:
            # Générer la vidéo
            metadata = self.pipeline.generate_video()
            
            if self.auto_publish and self.publisher:
                # Délai avant publication (anti-détection)
                delay = random.uniform(*DELAYS["pre_upload_delay"])
                logger.info(f"⏸️  Pause de {delay:.0f}s avant publication...")
                time.sleep(delay)
                
                # Publier sur TikTok
                logger.info("📤 Publication sur TikTok...")
                
                # Utiliser asyncio pour le publisher
                result = asyncio.run(self._publish_video(metadata))
                
                if result["status"] == "success":
                    logger.info(f"✅ Vidéo publiée: {result.get('video_url', 'URL non disponible')}")
                else:
                    logger.error(f"❌ Échec de la publication: {result.get('message')}")
            else:
                logger.info("📁 Vidéo générée (publication manuelle requise)")
                logger.info(f"📝 Description TikTok:\n{metadata['tiktok_description']}")
            
        except Exception as e:
            logger.error(f"❌ Erreur dans le job: {e}")
            # Retry logic pourrait être ajouté ici
    
    async def _publish_video(self, metadata: dict) -> dict:
        """
        Publier la vidéo sur TikTok (async)
        
        Args:
            metadata: Métadonnées de la vidéo
            
        Returns:
            Résultat de la publication
        """
        try:
            await self.publisher.init_browser()
            await self.publisher.login()
            
            result = await self.publisher.upload_video(
                video_path=metadata["video_path"],
                description=metadata["description"]["description"],
                hashtags=metadata["description"]["hashtags"],
                dry_run=False
            )
            
            await self.publisher.close()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la publication: {e}")
            return {"status": "error", "message": str(e)}
    
    def setup_schedule(self):
        """Configurer le planning de publication"""
        logger.info("📅 Configuration du planning...")
        
        daily_videos = self.config["daily_videos"]
        pub_hours = self.config["publication_hours"]
        
        # Calculer les heures de publication
        if daily_videos == 1:
            # 1 vidéo/jour: choisir aléatoirement dans la première plage
            hour = random.randint(*pub_hours[0])
            final_hour, final_minute = self._randomize_time(hour)
            
            self.scheduler.add_job(
                self.generate_and_publish_job,
                CronTrigger(hour=final_hour, minute=final_minute),
                id="daily_video",
                name="Publication quotidienne"
            )
            
            logger.info(f"✅ Planifié: 1 vidéo/jour à {final_hour:02d}:{final_minute:02d}")
            
        elif daily_videos == 2:
            # 2 vidéos/jour: une dans chaque plage
            for i, (start_hour, end_hour) in enumerate(pub_hours[:2]):
                hour = random.randint(start_hour, end_hour)
                final_hour, final_minute = self._randomize_time(hour)
                
                self.scheduler.add_job(
                    self.generate_and_publish_job,
                    CronTrigger(hour=final_hour, minute=final_minute),
                    id=f"daily_video_{i+1}",
                    name=f"Publication quotidienne #{i+1}"
                )
                
                logger.info(f"✅ Planifié: Vidéo #{i+1} à {final_hour:02d}:{final_minute:02d}")
        
        else:
            logger.warning(f"⚠️  {daily_videos} vidéos/jour non supporté (max 2)")
    
    def start(self):
        """Démarrer le scheduler"""
        logger.info("🚀 Démarrage du scheduler TikTok...")
        logger.info(f"🎯 Thème: {self.theme}")
        logger.info(f"📊 Vidéos par jour: {self.config['daily_videos']}")
        
        self.setup_schedule()
        
        # Afficher les jobs planifiés
        logger.info("\n📋 Jobs planifiés:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name}: {job.next_run_time}")
        
        logger.info("\n✅ Scheduler actif. Ctrl+C pour arrêter.\n")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\n🛑 Arrêt du scheduler...")
            self.scheduler.shutdown()


def main():
    """Point d'entrée"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="TikTok Automation Scheduler")
    parser.add_argument(
        "--theme",
        type=str,
        default=os.getenv("THEME", "motivation"),
        help="Thème du contenu"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Exécuter un job de test immédiatement"
    )
    
    args = parser.parse_args()
    
    scheduler = TikTokScheduler(theme=args.theme)
    
    if args.test:
        logger.info("🧪 Mode test: exécution immédiate d'un job")
        scheduler.generate_and_publish_job()
    else:
        scheduler.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()
