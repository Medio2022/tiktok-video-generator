"""
Générateur de sous-titres dynamiques pour TikTok avec Gemini
"""

import json
import logging
from typing import Dict, List
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_CONFIG

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        """Initialiser le générateur de sous-titres"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_CONFIG["subtitle_model"])
        self.temperature = GEMINI_CONFIG["temperature_precise"]
    
    def _build_prompt(self, script_data: Dict) -> str:
        """Construire le prompt pour Gemini"""
        
        # Extraire les segments avec timing
        segments_text = "\n".join([
            f"{seg['timing']}: {seg['text']}"
            for seg in script_data['segments']
        ])
        
        prompt = f"""Tu es un expert en sous-titres TikTok. Crée des sous-titres optimisés pour ce script:

SCRIPT AVEC TIMING:
{segments_text}

RÈGLES STRICTES:
- Max 5-6 mots par ligne de sous-titre
- Découpage rythmique (pas grammatical)
- Emphase sur les mots-clés
- Ajout d'emojis stratégiques (2-3 max dans toute la vidéo)
- Synchronisation précise avec la voix
- Lisibilité maximale sur mobile

STYLE TIKTOK:
- Mots-clés en MAJUSCULES occasionnellement
- Emojis pour renforcer l'émotion (pas sur chaque ligne)
- Pauses naturelles respectées
- Pas de ponctuation excessive
- Découpage qui crée du suspense

FORMAT DE RÉPONSE (JSON):
{{
    "subtitles": [
        {{
            "start": 0.0,
            "end": 3.0,
            "text": "Tu perds 3 heures 😱",
            "style": "emphasis"
        }},
        {{
            "start": 3.0,
            "end": 5.5,
            "text": "par jour",
            "style": "normal"
        }},
        ...
    ]
}}

EXEMPLES DE BON DÉCOUPAGE:
❌ "Tu perds trois heures par jour sans le savoir"
✅ "Tu perds 3 heures 😱" → "par jour" → "Sans le savoir 🤯"

❌ "Voici comment arrêter ça maintenant"
✅ "Voici comment" → "ARRÊTER ça" → "maintenant"

UTILISATION DES EMOJIS:
- Moments émotionnels forts uniquement
- Max 1 emoji par 3-4 lignes
- Emojis pertinents au contexte

UTILISATION DES MAJUSCULES:
- Mots-clés importants
- Moments de révélation
- Appels à l'action
- Pas plus de 2-3 mots en majuscules par vidéo

Réponds UNIQUEMENT en JSON valide, sans texte additionnel.
"""
        return prompt
    
    def generate(self, script_data: Dict) -> Dict:
        """
        Générer des sous-titres optimisés
        
        Args:
            script_data: Script avec segments et timing
            
        Returns:
            Dict avec subtitles et format SRT
        """
        logger.info("📝 Génération des sous-titres...")
        
        try:
            prompt = self._build_prompt(script_data)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=600,
                )
            )
            
            # Extraire le JSON
            response_text = response.text.strip()
            
            # Nettoyer la réponse
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            subtitle_data = json.loads(response_text)
            
            # Validation
            if "subtitles" not in subtitle_data:
                raise ValueError("Clé 'subtitles' manquante")
            
            # Générer le format SRT
            srt_content = self._generate_srt(subtitle_data["subtitles"])
            subtitle_data["srt_format"] = srt_content
            
            logger.info(f"✅ {len(subtitle_data['subtitles'])} sous-titres générés")
            
            return subtitle_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {e}")
            logger.error(f"Réponse brute: {response_text}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            raise
    
    def _generate_srt(self, subtitles: List[Dict]) -> str:
        """
        Générer le format SRT standard
        
        Args:
            subtitles: Liste de sous-titres
            
        Returns:
            Contenu SRT formaté
        """
        srt_lines = []
        
        for i, sub in enumerate(subtitles, 1):
            # Numéro de séquence
            srt_lines.append(str(i))
            
            # Timing au format SRT (00:00:00,000 --> 00:00:03,000)
            start_time = self._seconds_to_srt_time(sub["start"])
            end_time = self._seconds_to_srt_time(sub["end"])
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # Texte
            srt_lines.append(sub["text"])
            
            # Ligne vide
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convertir secondes en format SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def save_srt(self, subtitle_data: Dict, output_path: str):
        """
        Sauvegarder les sous-titres au format SRT
        
        Args:
            subtitle_data: Données de sous-titres
            output_path: Chemin de sortie
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(subtitle_data["srt_format"])
        
        logger.info(f"💾 Sous-titres sauvegardés: {output_path}")


if __name__ == "__main__":
    # Test du générateur de sous-titres
    logging.basicConfig(level=logging.INFO)
    
    # Exemple de script
    test_script = {
        "script": "Tu perds 3 heures par jour. Sans même t'en rendre compte...",
        "duration_estimate": 25,
        "segments": [
            {"text": "Tu perds 3 heures par jour", "timing": "0-3s", "emphasis": "high"},
            {"text": "Sans même t'en rendre compte", "timing": "3-6s", "emphasis": "normal"},
            {"text": "Voici comment arrêter ça", "timing": "6-10s", "emphasis": "normal"},
            {"text": "Première erreur : ton téléphone", "timing": "10-14s", "emphasis": "high"},
            {"text": "Deuxième erreur : les notifications", "timing": "14-18s", "emphasis": "high"},
            {"text": "Troisième erreur : le multitasking", "timing": "18-22s", "emphasis": "high"},
            {"text": "Sauvegarde pour ne pas oublier", "timing": "22-25s", "emphasis": "normal"},
        ]
    }
    
    generator = SubtitleGenerator()
    subtitles = generator.generate(test_script)
    
    print("\n" + "="*60)
    print("SOUS-TITRES GÉNÉRÉS:")
    print("="*60)
    print(json.dumps(subtitles, indent=2, ensure_ascii=False))
    print("\n" + "="*60)
    print("FORMAT SRT:")
    print("="*60)
    print(subtitles["srt_format"])
