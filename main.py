"""
Orchestrateur principal du système TikTok Automation
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json

import config
from config import (
    THEME, OUTPUT_DIR, LOGS_DIR, VIDEO_CONFIG, DEFAULT_HASHTAGS, TTS_CONFIG,
    DEEPSEEK_API_KEY, PEXELS_API_KEY, SUBTITLE_CONFIG
)
from modules.config_schemas import SubtitleConfig # Import schema
from modules.idea_generator import IdeaGenerator
from modules.script_writer import ScriptWriter
from modules.subtitle_generator import SubtitleGenerator
from modules.voice_generator import VoiceGenerator
from modules.description_generator import DescriptionGenerator
from modules.video_assembler import VideoAssembler
from modules.avatar_generator import AvatarVideoGenerator

# Modules gratuits illimités
try:
    from modules.deepseek_client import DeepSeekClient
    DEEPSEEK_AVAILABLE = bool(DEEPSEEK_API_KEY)
except ImportError:
    DEEPSEEK_AVAILABLE = False

try:
    from modules.video_generator import VideoGenerator
    PEXELS_AVAILABLE = bool(PEXELS_API_KEY)
except ImportError:
    PEXELS_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "tiktok_automation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TikTokPipeline:
    """Pipeline complet de génération de vidéos TikTok"""
    
    def __init__(
        self,
        theme: str = THEME,
        use_avatar: bool = False,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        aspect_ratio: str = "9:16",
        elevenlabs_voice: str = "rachel",  # NOUVEAU: Choix de voix ElevenLabs
        subtitle_config: Optional[SubtitleConfig] = None # Config avancée sous-titres
    ):
        """
        Initialiser le pipeline
        
        Args:
            theme: Thème du contenu (motivation, productivite, etc.)
            use_avatar: Utiliser un avatar AI au lieu de vidéo Pexels
            avatar_id: ID de l'avatar HeyGen (si use_avatar=True)
            voice_id: ID de la voix HeyGen (si use_avatar=True)
            aspect_ratio: Ratio de la vidéo (9:16, 16:9, 1:1)
            elevenlabs_voice: Voix ElevenLabs (rachel, bella, adam, josh, etc.)
        """
        self.theme = theme
        self.use_avatar = use_avatar
        self.avatar_id = avatar_id or "anna_casual_v2"
        self.voice_id = voice_id or "en-US-JennyNeural"
        self.aspect_ratio = aspect_ratio
        self.elevenlabs_voice = elevenlabs_voice
        self.subtitle_config = subtitle_config or SubtitleConfig() # Utiliser défaut si None
        
        # Initialiser les modules
        logger.info("🚀 Initialisation du pipeline TikTok...")
        
        # Utiliser DeepSeek si disponible, sinon Gemini
        if DEEPSEEK_AVAILABLE:
            logger.info("✅ Utilisation de DeepSeek (gratuit illimité)")
            self.content_generator = DeepSeekClient()
            self.use_deepseek = True
        else:
            logger.info("⚠️  Utilisation de Gemini (quota limité)")
            self.idea_generator = IdeaGenerator()
            self.script_writer = ScriptWriter()
            self.subtitle_generator = SubtitleGenerator()
            self.use_deepseek = False
        
        # Générateur d'avatars AI (HeyGen)
        if self.use_avatar:
            try:
                logger.info("🎭 Activation du mode Avatar AI (HeyGen)")
                self.avatar_generator = AvatarVideoGenerator()
                logger.info(f"✅ Avatar: {self.avatar_id}, Voix: {self.voice_id}")
            except Exception as e:
                logger.error(f"❌ Erreur avatar: {e}")
                logger.info("⚠️  Retour au mode Pexels")
                self.use_avatar = False
                self.avatar_generator = None
        else:
            self.avatar_generator = None
        
        # Générateur de vidéos Pexels (utilisé si avatar désactivé)
        if not self.use_avatar and PEXELS_AVAILABLE:
            logger.info("✅ Générateur vidéo Pexels activé")
            self.video_generator = VideoGenerator()
        else:
            logger.info("ℹ️  Pexels non configuré - utilisation de fonds colorés")
            self.video_generator = None
        
        self.voice_generator = VoiceGenerator(
            backend=TTS_CONFIG.get("backend", "auto"),
            elevenlabs_voice=self.elevenlabs_voice
        )
        self.description_generator = DescriptionGenerator()
        self.video_assembler = VideoAssembler()
        
        logger.info("✅ Pipeline initialisé")
    
    def generate_video(
        self,
        output_name: Optional[str] = None,
        save_metadata: bool = True
    ) -> Dict:
        """
        Générer une vidéo TikTok complète
        
        Args:
            output_name: Nom du fichier de sortie (optionnel)
            save_metadata: Sauvegarder les métadonnées
            
        Returns:
            Dict avec tous les chemins et métadonnées
        """
        logger.info("="*60)
        logger.info("🎬 DÉBUT DE LA GÉNÉRATION VIDÉO")
        logger.info("="*60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_name is None:
            output_name = f"tiktok_{timestamp}"
        
        # Créer le répertoire de sortie pour cette vidéo
        video_dir = OUTPUT_DIR / output_name
        video_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Générer l'idée
            logger.info("\n📍 ÉTAPE 1/7: Génération de l'idée")
            if self.use_deepseek:
                idea = self.content_generator.generate_idea(self.theme)
            else:
                idea = self.idea_generator.generate(self.theme)
            logger.info(f"💡 Idée: {idea['hook']}")
            
            # 2. Écrire le script
            logger.info("\n📍 ÉTAPE 2/7: Écriture du script")
            if self.use_deepseek:
                script = self.content_generator.generate_script(idea)
            else:
                script = self.script_writer.write(idea)
            logger.info(f"📝 Script: {len(script['segments'])} segments, ~{script['duration_estimate']}s")
            
            # 3. Générer la voix off
            logger.info("\n📍 ÉTAPE 3/7: Génération de la voix off")
            audio_path, audio_duration = self.voice_generator.generate(
                text=script["script"],
                output_path=str(video_dir / "voiceover.mp3")
            )
            logger.info(f"🎤 Audio: {audio_path} ({audio_duration:.1f}s)")
            
            # 4. Générer les sous-titres avec Whisper (synchronisation parfaite)
            logger.info("\n📍 ÉTAPE 4/7: Génération des sous-titres")
            from modules.whisper_subtitles import generate_subtitles_from_audio
            
            subtitle_path = video_dir / "subtitles.srt"
            _, subtitle_segments = generate_subtitles_from_audio(
                str(audio_path),
                str(subtitle_path),
                model_size="base"  # Bon équilibre rapidité/précision
            )
            
            # Compter lignes pour log
            import pysrt
            subs = pysrt.open(str(subtitle_path), encoding='utf-8')
            logger.info(f"📝 Sous-titres: {len(subs)} lignes (synchronisés Whisper)")
            
            # 5. Générer la description
            logger.info("\n📍 ÉTAPE 5/7: Génération de la description")
            if self.use_deepseek:
                description = self.content_generator.generate_description(script, idea, self.theme)
            else:
                description = self.description_generator.generate(script, idea, self.theme)
            logger.info(f"📄 Description: {description['description'][:50]}...")
            
            # 6. Assembler la vidéo
            logger.info("\n📍 ÉTAPE 6/7: Assemblage de la vidéo")
            
            # NOUVEAU: Option Avatar AI
            if self.use_avatar:
                logger.info(f"🎭 Génération vidéo avec avatar AI ({self.avatar_id})")
                
                try:
                    # Générer vidéo avec avatar
                    avatar_video_url = self.avatar_generator.create_avatar_video(
                        script=script["script"],
                        avatar_id=self.avatar_id,
                        voice_id=self.voice_id,
                        aspect_ratio=self.aspect_ratio
                    )
                    
                    # Télécharger la vidéo
                    background_video = self.avatar_generator.download_video(
                        avatar_video_url,
                        str(video_dir / "avatar_video.mp4")
                    )
                    
                    logger.info("✅ Vidéo avatar générée avec succès")
                    
                    # Utiliser directement la vidéo avatar (déjà avec voix + lip-sync)
                    # On peut ajouter juste les sous-titres si besoin
                    from modules.complete_video_assembler import assemble_complete_video
                    
                    video_path = assemble_complete_video(
                        pexels_video_path=str(background_video),
                        audio_path=str(audio_path),
                        srt_path=str(subtitle_path),
                        output_path=str(video_dir / "final_video.mp4"),
                        subtitle_color=config.SUBTITLE_CONFIG['color'],
                        subtitle_size=config.SUBTITLE_CONFIG['size'],
                        outline_width=config.SUBTITLE_CONFIG['outline_width'],
                        position_from_bottom=config.SUBTITLE_CONFIG['position_from_bottom']
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Erreur génération avatar: {e}")
                    logger.info("⚠️  Fallback: utilisation Pexels/fond coloré")
                    self.use_avatar = False  # Fallback pour cette génération
            
            # Fallback ou mode Pexels normal
            if not self.use_avatar:
                # Essayer de générer une vidéo Pexels si disponible
                background_video = None
                if self.video_generator and 'video_keywords' in idea:
                    logger.info(f"🎬 Recherche vidéo Pexels: {idea['video_keywords']}")
                    background_video, video_type = self.video_generator.generate_with_fallback(
                        keywords=idea['video_keywords'],
                        output_path=str(video_dir / "background_video.mp4")
                    )
                    if video_type == "pexels":
                        logger.info("✅ Vidéo Pexels téléchargée")
            
            # Assembler avec vidéo Pexels ou fond coloré
                if background_video and os.path.exists(background_video):
                    logger.info("🎬 Assemblage vidéo complète (Pexels + sous-titres Whisper)")
                
                    # Importer module d'assemblage complet
                    from modules.complete_video_assembler import assemble_complete_video
                
                    # Assembler vidéo complète (Whisper génère déjà timestamps parfaits)
                    video_path = assemble_complete_video(
                        pexels_video_path=background_video,
                        audio_path=str(audio_path),
                        srt_path=str(subtitle_path),  # Whisper SRT déjà synchronisé
                        output_path=str(video_dir / "final_video.mp4"),
                        subtitle_config=self.subtitle_config,
                        subtitle_segments=subtitle_segments # Segments bruts pour animation avancée
                    )
                else:
                    # Fallback: assemblage simple avec fond coloré
                    logger.info("ℹ️  Assemblage avec fond coloré (vidéo Pexels en développement)")
                
                    # Couleurs selon le thème
                    background_colors = {
                        "motivation": (20, 30, 60),      # Bleu foncé
                        "productivite": (30, 20, 40),    # Violet foncé
                        "tech": (10, 20, 30),            # Bleu très foncé
                        "business": (30, 30, 30),        # Gris foncé
                        "sante": (20, 40, 30),           # Vert foncé
                    }
                
                    bg_color = background_colors.get(self.theme, (20, 20, 40))
                
                    video_path = self.video_assembler.assemble_simple(
                        audio_path=audio_path,
                        background_color=bg_color,
                        subtitle_path=str(subtitle_path),
                        output_path=str(video_dir / "final_video.mp4")
                    )
            
            logger.info(f"🎬 Vidéo: {video_path}")
            
            # 7. Sauvegarder les métadonnées
            logger.info("\n📍 ÉTAPE 7/7: Sauvegarde des métadonnées")
            
            metadata = {
                "timestamp": timestamp,
                "theme": self.theme,
                "idea": idea,
                "script": script,
                "description": description,
                "audio_path": audio_path,
                "audio_duration": audio_duration,
                "subtitle_path": str(subtitle_path),
                "video_path": video_path,
                "tiktok_description": self.description_generator.format_for_tiktok(description)
            }
            
            if save_metadata:
                metadata_path = video_dir / "metadata.json"
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Métadonnées: {metadata_path}")
            
            logger.info("\n" + "="*60)
            logger.info("✅ VIDÉO GÉNÉRÉE AVEC SUCCÈS!")
            logger.info("="*60)
            logger.info(f"📁 Répertoire: {video_dir}")
            logger.info(f"🎬 Vidéo: {video_path}")
            logger.info(f"📝 Description TikTok:\n{metadata['tiktok_description']}")
            logger.info("="*60)
            
            return metadata
            
        except Exception as e:
            logger.error(f"\n❌ ERREUR LORS DE LA GÉNÉRATION: {e}")
            raise
    
    def _format_time(self, seconds: float) -> str:
        """
        Formater le temps pour SRT (HH:MM:SS,mmm)
        
        Args:
            seconds: Temps en secondes
            
        Returns:
            Temps formaté
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_batch(self, count: int = 5) -> list[Dict]:
        """
        Générer plusieurs vidéos d'un coup
        
        Args:
            count: Nombre de vidéos à générer
            
        Returns:
            Liste de métadonnées
        """
        logger.info(f"🎬 Génération de {count} vidéos...")
        
        results = []
        for i in range(count):
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"VIDÉO {i+1}/{count}")
                logger.info(f"{'='*60}")
                
                metadata = self.generate_video(
                    output_name=f"batch_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
                )
                results.append(metadata)
                
                logger.info(f"✅ Vidéo {i+1}/{count} terminée")
                
            except Exception as e:
                logger.error(f"❌ Échec vidéo {i+1}/{count}: {e}")
                continue
        
        logger.info(f"\n✅ Batch terminé: {len(results)}/{count} vidéos générées")
        return results


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TikTok Video Automation Pipeline")
    parser.add_argument(
        "--theme",
        type=str,
        default=THEME,
        choices=list(DEFAULT_HASHTAGS.keys()),
        help="Thème du contenu"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Nombre de vidéos à générer"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Nom du fichier de sortie (pour une seule vidéo)"
    )
    
    args = parser.parse_args()
    
    # Créer le pipeline
    pipeline = TikTokPipeline(theme=args.theme)
    
    # Générer les vidéos
    if args.count == 1:
        pipeline.generate_video(output_name=args.output)
    else:
        pipeline.generate_batch(count=args.count)


if __name__ == "__main__":
    main()
