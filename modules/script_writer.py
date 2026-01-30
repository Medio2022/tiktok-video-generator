"""
Générateur de scripts TikTok optimisés avec Gemini
"""

import json
import logging
from typing import Dict
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_CONFIG, VIDEO_CONFIG

logger = logging.getLogger(__name__)


class ScriptWriter:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        """Initialiser le générateur de scripts"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_CONFIG["script_model"])
        self.temperature = GEMINI_CONFIG["temperature_balanced"]
        self.target_duration = VIDEO_CONFIG["target_duration"]
    
    def _build_prompt(self, idea: Dict) -> str:
        """Construire le prompt pour Gemini"""
        prompt = f"""Tu es un copywriter expert en scripts TikTok viraux. Écris un script de 20-30 secondes basé sur cette idée:

IDÉE:
Hook: {idea['hook']}
Angle: {idea['angle']}
Concept: {idea['concept']}
CTA: {idea['cta']}

CONTRAINTES STRICTES:
- Durée: 20-30 secondes à voix haute
- Phrases ultra-courtes (5-8 mots max par phrase)
- Ton naturel et conversationnel
- Pas de jargon technique
- Rythme rapide et dynamique
- Optimisé pour la voix off
- Pas de mention d'IA ou d'automatisation

STRUCTURE OBLIGATOIRE:
1. Hook (0-3s): Phrase choc qui arrête le scroll
2. Problème (3-10s): Amplifier la douleur ou l'intrigue
3. Solution (10-25s): 3 points concrets et actionnables
4. CTA (25-30s): Appel à l'action engageant

FORMAT DE RÉPONSE (JSON):
{{
    "script": "texte complet du script, phrase par phrase",
    "duration_estimate": 25,
    "word_count": 65,
    "segments": [
        {{"text": "phrase 1", "timing": "0-3s", "emphasis": "high"}},
        {{"text": "phrase 2", "timing": "3-6s", "emphasis": "normal"}},
        ...
    ]
}}

STYLE D'ÉCRITURE:
- Utilise "tu" (tutoiement)
- Phrases déclaratives courtes
- Pas de questions rhétoriques excessives
- Vocabulaire simple et direct
- Transitions fluides entre les segments
- Rythme varié (alternance rapide/pause)

EXEMPLES DE BONNES PHRASES:
✅ "Tu perds 3 heures par jour"
✅ "Sans même t'en rendre compte"
✅ "Voici comment arrêter ça"
✅ "Première erreur : ton téléphone"

EXEMPLES À ÉVITER:
❌ "Salut c'est [nom], aujourd'hui on va parler de..."
❌ "Dans cette vidéo je vais vous montrer..."
❌ "N'oubliez pas de liker et de vous abonner"

Réponds UNIQUEMENT en JSON valide, sans texte additionnel.
"""
        return prompt
    
    def write(self, idea: Dict) -> Dict:
        """
        Écrire un script TikTok optimisé
        
        Args:
            idea: Idée générée par IdeaGenerator
            
        Returns:
            Dict avec script, durée, segments
        """
        logger.info(f"✍️  Écriture du script pour: {idea['hook']}")
        
        try:
            prompt = self._build_prompt(idea)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=800,
                )
            )
            
            # Extraire le JSON
            response_text = response.text.strip()
            
            # DEBUG: Afficher la réponse complète
            logger.info(f"📝 Réponse complète ({len(response_text)} chars):")
            logger.info(response_text)
            
            # Nettoyer la réponse
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            script_data = json.loads(response_text)
            
            # Validation
            required_keys = ["script", "duration_estimate", "segments"]
            if not all(key in script_data for key in required_keys):
                raise ValueError(f"Script incomplet. Clés requises: {required_keys}")
            
            # Vérifier la durée
            duration = script_data["duration_estimate"]
            if duration < VIDEO_CONFIG["duration_min"] or duration > VIDEO_CONFIG["duration_max"]:
                logger.warning(f"⚠️  Durée hors limites: {duration}s (cible: {self.target_duration}s)")
            
            logger.info(f"✅ Script généré: {len(script_data['segments'])} segments, ~{duration}s")
            
            return script_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {e}")
            logger.error(f"Réponse brute (500 chars): {response_text[:500]}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'écriture: {e}")
            raise
    
    def refine_script(self, script_data: Dict, feedback: str) -> Dict:
        """
        Affiner un script existant avec du feedback
        
        Args:
            script_data: Script existant
            feedback: Feedback pour amélioration
            
        Returns:
            Script amélioré
        """
        logger.info("🔄 Affinage du script...")
        
        prompt = f"""Améliore ce script TikTok en tenant compte du feedback:

SCRIPT ACTUEL:
{script_data['script']}

FEEDBACK:
{feedback}

Réponds avec le même format JSON que précédemment, en intégrant les améliorations demandées.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=800,
                )
            )
            
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            refined_script = json.loads(response_text)
            logger.info("✅ Script affiné")
            
            return refined_script
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'affinage: {e}")
            raise


if __name__ == "__main__":
    # Test du générateur de scripts
    logging.basicConfig(level=logging.INFO)
    
    # Exemple d'idée
    test_idea = {
        "hook": "Tu perds 3 heures par jour sans le savoir",
        "angle": "productivité invisible",
        "concept": "Les micro-distractions qui tuent ta productivité",
        "cta": "Sauvegarde pour ne pas oublier"
    }
    
    writer = ScriptWriter()
    script = writer.write(test_idea)
    
    print("\n" + "="*60)
    print("SCRIPT GÉNÉRÉ:")
    print("="*60)
    print(json.dumps(script, indent=2, ensure_ascii=False))
    print("="*60)
