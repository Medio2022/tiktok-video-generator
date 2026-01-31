"""
Client DeepSeek pour génération de contenu TikTok
Alternative gratuite et illimitée à Gemini
"""

import json
import logging
import requests
import json_repair
from typing import Dict, Optional
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

logger = logging.getLogger(__name__)


class DeepSeekClient:
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        """Initialiser le client DeepSeek"""
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY manquante dans .env")
        
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_api(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Appeler l'API DeepSeek
        
        Args:
            prompt: Prompt à envoyer
            temperature: Créativité (0-1)
            max_tokens: Tokens maximum
            
        Returns:
            Réponse texte
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API DeepSeek: {e}")
            raise
    
    def generate_idea(self, theme: str) -> Dict:
        """
        Générer une idée virale TikTok
        
        Args:
            theme: Thème (motivation, productivite, etc.)
            
        Returns:
            Dict avec hook, angle, concept, cta, video_keywords
        """
        logger.info(f"🎯 Génération d'idée DeepSeek pour: {theme}")
        
        prompt = f"""Tu es un expert en contenu viral TikTok. Génère UNE idée de vidéo courte (20-30s) sur le thème: {theme}

CONTRAINTES:
- Hook percutant (2 premières secondes)
- Angle unique et contre-intuitif
- Format "faceless" (pas de visage)
- Potentiel viral élevé
- LANGUE: Français PARFAIT (orthographe, grammaire, syntaxe irréprochables). Évite les anglicismes.

IMPORTANT: Ajoute des mots-clés pour rechercher des vidéos stock (Pexels).
Exemples: "workspace", "typing", "coffee", "sunset", "city"

Réponds UNIQUEMENT en JSON valide:
{{
    "hook": "phrase d'accroche choc (max 10 mots)",
    "angle": "angle unique en 2-3 mots",
    "concept": "description du concept (1 phrase)",
    "cta": "call-to-action final",
    "video_keywords": ["mot-clé1", "mot-clé2", "mot-clé3"]
}}

Exemples de hooks viraux:
- "Personne ne parle de ça..."
- "J'ai perdu 10 000€ avant de comprendre..."
- "Cette erreur te coûte 2h par jour"
"""
        
        try:
            response = self._call_api(prompt, temperature=0.9, max_tokens=500)
            
            # Parsing robuste avec json_repair
            idea = json_repair.loads(response)
            
            # Validation
            required = ["hook", "angle", "concept", "cta", "video_keywords"]
            if not all(key in idea for key in required):
                raise ValueError(f"Réponse incomplète. Clés requises: {required}")
            
            logger.info(f"✅ Idée générée: {idea['hook']}")
            return idea
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.error(f"Réponse: {response[:500]}")
            raise
    
    def generate_script(self, idea: Dict) -> Dict:
        """
        Générer un script TikTok optimisé
        
        Args:
            idea: Idée générée par generate_idea
            
        Returns:
            Dict avec script, duration_estimate, segments
        """
        logger.info(f"✍️  Génération script DeepSeek pour: {idea['hook']}")
        
        prompt = f"""Tu es un copywriter expert en scripts TikTok viraux. Écris un script de 20-30 secondes:

IDÉE:
Hook: {idea['hook']}
Angle: {idea['angle']}
Concept: {idea['concept']}
CTA: {idea['cta']}

CONTRAINTES:
- Durée: 20-30 secondes à voix haute
- Phrases ultra-courtes (5-8 mots max)
- Ton naturel et conversationnel (style oral)
- Rythme rapide et dynamique
- LANGUE: Français PARFAIT. Orthographe et syntaxe impeccables. Utilise un langage courant mais correct. Pas de "tournures traduites de l'anglais".

STRUCTURE:
1. Hook (0-3s): Phrase choc
2. Problème (3-10s): Amplifier l'intrigue
3. Solution (10-25s): 3 points concrets
4. CTA (25-30s): Appel à l'action

Réponds UNIQUEMENT en JSON valide:
{{
    "script": "texte complet du script",
    "duration_estimate": 25,
    "word_count": 65,
    "segments": [
        {{"text": "phrase 1", "timing": "0-3s", "emphasis": "high"}},
        {{"text": "phrase 2", "timing": "3-6s", "emphasis": "normal"}}
    ]
}}
"""
        
        try:
            response = self._call_api(prompt, temperature=0.7, max_tokens=1500)
            
            # Parsing robuste avec json_repair
            script = json_repair.loads(response)
            
            # Validation
            required = ["script", "duration_estimate", "segments"]
            if not all(key in script for key in required):
                raise ValueError(f"Script incomplet. Clés requises: {required}")
            
            logger.info(f"✅ Script généré: {len(script['segments'])} segments")
            return script
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.error(f"Réponse: {response[:500]}")
            raise
    
    def generate_subtitles(self, script: Dict) -> Dict:
        """
        Générer des sous-titres synchronisés
        
        Args:
            script: Script généré par generate_script
            
        Returns:
            Dict avec subtitles (liste de {start, end, text})
        """
        logger.info("📝 Génération sous-titres DeepSeek")
        
        prompt = f"""Génère des sous-titres synchronisés pour ce script TikTok:

SCRIPT: {script['script']}
DURÉE: {script['duration_estimate']}s

Découpe en segments courts (2-4 mots max par ligne) pour lisibilité mobile.
Vérifie que les coupures de mots sont logiques (ne pas couper "l' | ami").
ORTHOGRAPHE: Corrige toute faute éventuelle dans le script source.

Réponds UNIQUEMENT en JSON valide:
{{
    "subtitles": [
        {{"start": 0.0, "end": 2.5, "text": "Tu perds 3 heures"}},
        {{"start": 2.5, "end": 4.0, "text": "par jour"}}
    ]
}}
"""
        
        try:
            response = self._call_api(prompt, temperature=0.5, max_tokens=1000)
            
            # Parsing robuste avec json_repair
            subtitles = json_repair.loads(response)
            
            if "subtitles" not in subtitles:
                raise ValueError("Clé 'subtitles' manquante")
            
            logger.info(f"✅ Sous-titres générés: {len(subtitles['subtitles'])} lignes")
            return subtitles
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.error(f"Réponse: {response[:500]}")
            raise
    
    def generate_description(self, script: Dict, idea: Dict, theme: str) -> Dict:
        """
        Générer une description TikTok optimisée SEO
        
        Args:
            script: Script généré
            idea: Idée générée
            theme: Thème
            
        Returns:
            Dict avec description, hashtags
        """
        logger.info("📄 Génération description DeepSeek")
        
        prompt = f"""Génère une description TikTok optimisée SEO:

THÈME: {theme}
HOOK: {idea['hook']}
CONCEPT: {idea['concept']}

CONTRAINTES:
- 150 caractères max
- Intrigant et engageant
- 3-5 hashtags pertinents
- Appel à l'action
- LANGUE: Français naturel et sans faute.

Réponds UNIQUEMENT en JSON valide:
{{
    "description": "description courte et percutante",
    "hashtags": ["#motivation", "#productivite", "#tips"]
}}
"""
        
        try:
            response = self._call_api(prompt, temperature=0.7, max_tokens=300)
            
            # Parsing robuste avec json_repair
            description = json_repair.loads(response)
            
            required = ["description", "hashtags"]
            if not all(key in description for key in required):
                raise ValueError(f"Description incomplète. Clés requises: {required}")
            
            logger.info(f"✅ Description générée")
            return description
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.error(f"Réponse: {response[:500]}")
            raise


if __name__ == "__main__":
    # Test du client DeepSeek
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = DeepSeekClient()
        
        # Test génération d'idée
        idea = client.generate_idea("motivation")
        print("\n" + "="*60)
        print("IDÉE GÉNÉRÉE:")
        print("="*60)
        print(json.dumps(idea, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
