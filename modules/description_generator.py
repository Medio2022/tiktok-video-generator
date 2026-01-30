"""
Générateur de description TikTok avec Gemini
"""

import json
import logging
from typing import Dict, List
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_CONFIG, DEFAULT_HASHTAGS

logger = logging.getLogger(__name__)


class DescriptionGenerator:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        """Initialiser le générateur de descriptions"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_CONFIG["description_model"])
        self.temperature = GEMINI_CONFIG["temperature_balanced"]
    
    def _build_prompt(self, script: str, concept: str, theme: str) -> str:
        """Construire le prompt pour Gemini"""
        
        default_tags = DEFAULT_HASHTAGS.get(theme, ["tiktok", "viral", "pourtoi"])
        
        prompt = f"""Crée une description TikTok optimisée pour cette vidéo:

SCRIPT: {script}
CONCEPT: {concept}
THÈME: {theme}

CONTRAINTES:
- Max 150 caractères pour la description
- 2-3 emojis stratégiques
- Intrigue sans tout révéler
- Incitation au visionnage complet
- Pas de spam de hashtags dans la description

HASHTAGS (5-8):
- Mix de populaires et niche
- Pertinents au contenu
- Éviter les hashtags trop génériques (#fyp, #pourtoi)
- Suggestions par défaut pour {theme}: {', '.join(default_tags)}

CTA:
- Incitation à sauvegarder/partager/commenter
- Naturel et non forcé
- Pas de "like et abonne-toi"

FORMAT JSON:
{{
    "description": "texte accrocheur avec emojis",
    "hashtags": ["tag1", "tag2", "tag3", ...],
    "cta": "call-to-action final"
}}

EXEMPLES DE BONNES DESCRIPTIONS:
✅ "Tu perds 3h par jour sans le savoir 😱 Découvre les micro-distractions invisibles 🎯"
✅ "Cette erreur te coûte 2h quotidiennes ⏰ La solution va te surprendre 💡"
✅ "99% des gens ignorent ce détail 🤯 Pourtant c'est si simple ✨"

EXEMPLES À ÉVITER:
❌ "Salut ! Aujourd'hui je vais te montrer..."
❌ "N'oublie pas de liker et de t'abonner !"
❌ "Clique sur le lien dans ma bio"

Réponds UNIQUEMENT en JSON valide, sans texte additionnel.
"""
        return prompt
    
    def generate(self, script_data: Dict, idea: Dict, theme: str) -> Dict:
        """
        Générer une description optimisée
        
        Args:
            script_data: Données du script
            idea: Idée originale
            theme: Thème du contenu
            
        Returns:
            Dict avec description, hashtags, cta
        """
        logger.info("📝 Génération de la description...")
        
        try:
            prompt = self._build_prompt(
                script=script_data["script"],
                concept=idea["concept"],
                theme=theme
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2000,
                )
            )
            
            # Extraire le JSON
            response_text = response.text.strip()
            
            # Nettoyer la réponse
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            description_data = json.loads(response_text)
            
            # Validation
            required_keys = ["description", "hashtags"]
            if not all(key in description_data for key in required_keys):
                raise ValueError(f"Description incomplète. Clés requises: {required_keys}")
            
            # Vérifier la longueur
            if len(description_data["description"]) > 150:
                logger.warning(f"⚠️  Description trop longue: {len(description_data['description'])} caractères")
            
            logger.info(f"✅ Description générée avec {len(description_data['hashtags'])} hashtags")
            
            return description_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {e}")
            logger.error(f"Réponse brute: {response_text}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            raise
    
    def format_for_tiktok(self, description_data: Dict) -> str:
        """
        Formater la description pour TikTok
        
        Args:
            description_data: Données de description
            
        Returns:
            Texte formaté pour TikTok
        """
        parts = [description_data["description"]]
        
        # Ajouter le CTA si présent
        if "cta" in description_data and description_data["cta"]:
            parts.append(f"\n\n{description_data['cta']}")
        
        # Ajouter les hashtags
        hashtags = " ".join([f"#{tag}" for tag in description_data["hashtags"]])
        parts.append(f"\n\n{hashtags}")
        
        return "".join(parts)


if __name__ == "__main__":
    # Test du générateur de descriptions
    logging.basicConfig(level=logging.INFO)
    
    test_script = {
        "script": "Tu perds 3 heures par jour. Sans même t'en rendre compte...",
        "duration_estimate": 25
    }
    
    test_idea = {
        "hook": "Tu perds 3 heures par jour sans le savoir",
        "angle": "productivité invisible",
        "concept": "Les micro-distractions qui tuent ta productivité",
        "cta": "Sauvegarde pour ne pas oublier"
    }
    
    generator = DescriptionGenerator()
    description = generator.generate(test_script, test_idea, "productivite")
    
    print("\n" + "="*60)
    print("DESCRIPTION GÉNÉRÉE:")
    print("="*60)
    print(json.dumps(description, indent=2, ensure_ascii=False))
    print("\n" + "="*60)
    print("FORMAT TIKTOK:")
    print("="*60)
    print(generator.format_for_tiktok(description))
