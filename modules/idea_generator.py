"""
Générateur d'idées virales TikTok avec Gemini
"""

import json
import logging
from typing import Dict, Optional
import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_CONFIG

logger = logging.getLogger(__name__)


class IdeaGenerator:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        """Initialiser le générateur d'idées"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_CONFIG["idea_model"])
        self.temperature = GEMINI_CONFIG["temperature_creative"]
    
    def _build_prompt(self, theme: str, trends: Optional[str] = None) -> str:
        """Construire le prompt pour Gemini"""
        prompt = f"""Tu es un expert en contenu viral TikTok. Génère UNE idée de vidéo courte (20-30s) sur le thème: {theme}

CONTRAINTES OBLIGATOIRES:
- Hook percutant dans les 2 premières secondes
- Angle unique et contre-intuitif
- Format "faceless" (pas de visage requis)
- Potentiel viral élevé
- Pas de mention d'IA ou d'automatisation

STRUCTURE DE RÉPONSE (JSON):
{{
    "hook": "phrase d'accroche choc (max 10 mots)",
    "angle": "angle unique en 2-3 mots",
    "concept": "description du concept (1 phrase)",
    "cta": "call-to-action final"
}}

EXEMPLES DE HOOKS VIRAUX:
- "Personne ne parle de ça..."
- "J'ai perdu 10 000€ avant de comprendre..."
- "Cette erreur te coûte 2h par jour"
- "Si tu fais ça, tu as déjà perdu"
- "99% des gens ignorent ce détail"

STYLE:
- Ton conversationnel et naturel
- Phrases courtes et percutantes
- Intrigue sans tout révéler
- Promesse de valeur claire
"""
        
        if trends:
            prompt += f"\n\nTENDANCES ACTUELLES À CONSIDÉRER:\n{trends}"
        
        prompt += "\n\nRéponds UNIQUEMENT en JSON valide, sans texte additionnel."
        
        return prompt
    
    def generate(self, theme: str, trends: Optional[str] = None) -> Dict:
        """
        Générer une idée virale
        
        Args:
            theme: Thème principal (motivation, productivite, etc.)
            trends: Tendances actuelles optionnelles
            
        Returns:
            Dict avec hook, angle, concept, cta
        """
        logger.info(f"🎯 Génération d'idée pour le thème: {theme}")
        
        try:
            prompt = self._build_prompt(theme, trends)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=20000,
                )
            )
            
            # Extraire le JSON de la réponse
            response_text = response.text.strip()
            
            logger.info(f"📝 Réponse Gemini ({len(response_text)} chars)")
            
            # Extraire le JSON si enveloppé dans des code blocks markdown
            if "```json" in response_text:
                # Extraire entre ```json et ```
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Extraire entre ``` et ```
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # Parser le JSON
            idea = json.loads(response_text)
            
            # Validation
            required_keys = ["hook", "angle", "concept", "cta"]
            if not all(key in idea for key in required_keys):
                raise ValueError(f"Réponse incomplète. Clés requises: {required_keys}")
            
            logger.info(f"✅ Idée générée: {idea['hook']}")
            return idea
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur de parsing JSON: {e}")
            logger.error(f"Réponse brute: {response_text[:500]}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            raise
    
    def generate_batch(self, theme: str, count: int = 5) -> list[Dict]:
        """
        Générer plusieurs idées d'un coup
        
        Args:
            theme: Thème principal
            count: Nombre d'idées à générer
            
        Returns:
            Liste d'idées
        """
        logger.info(f"🎯 Génération de {count} idées...")
        ideas = []
        
        for i in range(count):
            try:
                idea = self.generate(theme)
                ideas.append(idea)
                logger.info(f"✅ Idée {i+1}/{count} générée")
            except Exception as e:
                logger.error(f"❌ Échec idée {i+1}: {e}")
                continue
        
        return ideas


if __name__ == "__main__":
    # Test du générateur
    logging.basicConfig(level=logging.INFO)
    
    generator = IdeaGenerator()
    
    # Générer une idée
    idea = generator.generate("productivite")
    
    print("\n" + "="*60)
    print("IDÉE GÉNÉRÉE:")
    print("="*60)
    print(json.dumps(idea, indent=2, ensure_ascii=False))
    print("="*60)
