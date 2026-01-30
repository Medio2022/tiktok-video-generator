# 🎬 TikTok Video Generator - AI-Powered Automation

Système complet de génération automatique de vidéos TikTok avec intelligence artificielle. Génère des vidéos virales de qualité professionnelle en une seule commande.

## ✨ Fonctionnalités

- 🤖 **Génération de contenu AI** - DeepSeek pour idées, scripts et descriptions (gratuit illimité)
- 🎤 **Voix off automatique** - Edge TTS (Microsoft) gratuit et illimité
- 📝 **Sous-titres synchronisés** - Whisper AI pour transcription parfaite mot par mot
- 🎨 **Sous-titres stylés** - Cyan personnalisable, retour à la ligne automatique
- 🎥 **Vidéos HD Pexels** - Téléchargement automatique de backgrounds professionnels
- ✅ Assemblage vidéo automatique (FFmpeg)
- ✅ Publication automatique sur TikTok (Playwright)
- ✅ Stratégies anti-détection avancées
- ✅ Scheduler pour publication programmée

## 📋 Prérequis

- Python 3.10+
- FFmpeg installé
- Compte Google Cloud (Gemini API, Text-to-Speech)
- Compte TikTok

## 🚀 Installation

### 1. Cloner et installer les dépendances

```bash
cd /Users/eric/tiktok
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Installer FFmpeg

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Vérifier l'installation
ffmpeg -version
```

### 3. Installer Playwright

```bash
playwright install chromium
```

### 4. Configuration Google Gemini

1. Obtenir une clé API Gemini (GRATUIT):
   - Aller sur [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Créer une clé API
   - Copier la clé

### 5. Variables d'environnement

Copier `.env.example` vers `.env` et remplir:

```bash
cp .env.example .env
nano .env
```

```env
# Seule la clé Gemini est requise (GRATUIT)
GOOGLE_API_KEY=your_gemini_api_key

TIKTOK_USERNAME=your_username
TIKTOK_PASSWORD=your_password

THEME=motivation
```

## 📖 Utilisation

### Génération d'une vidéo unique

```bash
python main.py --theme motivation
```

### Génération en batch

```bash
python main.py --theme productivite --count 5
```

### Lancer le scheduler automatique

```bash
python scheduler.py --theme motivation
```

### Test du scheduler (exécution immédiate)

```bash
python scheduler.py --test
```

## 📁 Structure du projet

```
tiktok/
├── config.py                 # Configuration centralisée
├── main.py                   # Orchestrateur principal
├── scheduler.py              # Scheduler automatique
├── requirements.txt          # Dépendances Python
├── .env                      # Variables d'environnement
│
├── modules/
│   ├── idea_generator.py     # Génération d'idées (Gemini)
│   ├── script_writer.py      # Écriture de scripts (Gemini)
│   ├── subtitle_generator.py # Génération de sous-titres (Gemini)
│   ├── voice_generator.py    # Synthèse vocale (Google TTS)
│   ├── description_generator.py # Descriptions TikTok (Gemini)
│   └── video_assembler.py    # Assemblage vidéo (FFmpeg)
│
├── output/                   # Vidéos générées
├── logs/                     # Logs du système
└── playwright_state/         # Sessions TikTok
```

## 🎨 Thèmes disponibles

- `motivation` - Contenu motivationnel
- `productivite` - Astuces de productivité
- `tech` - Technologie et innovation
- `business` - Entrepreneuriat et business
- `sante` - Santé et bien-être

## 🔧 Configuration avancée

### Modifier la fréquence de publication

Dans `config.py`:

```python
PUBLICATION_CONFIG = {
    "daily_videos": 2,  # 1 ou 2 vidéos/jour
    "publication_hours": [(10, 14), (18, 22)],
    "randomize_minutes": 30,  # ±30 minutes
}
```

### Changer la voix TTS

Dans `config.py`:

```python
TTS_CONFIG = {
    "backend": "edge",  # "edge", "gtts", ou "pyttsx3"
    "edge_voice": "fr-FR-HenriNeural",  # Voix masculine
    "speaking_rate": "+15%",  # Plus rapide
}
```

**Voix Edge TTS disponibles (GRATUITES):**
- `fr-FR-DeniseNeural` - Féminine naturelle (recommandé)
- `fr-FR-HenriNeural` - Masculine naturelle
- `fr-FR-EloiseNeural` - Féminine jeune

Voir [`TTS_COMPARISON.md`](file:///Users/eric/tiktok/TTS_COMPARISON.md) pour plus de détails.

## 🛡️ Stratégie anti-ban

Le système implémente plusieurs mécanismes anti-détection:

1. **Délais aléatoires** entre toutes les actions
2. **Typing humain** (80-120ms par caractère)
3. **Warm-up de session** (scroll, likes avant upload)
4. **Randomisation des heures** de publication
5. **Variation de contenu** (durée, style, hashtags)
6. **Montée en charge progressive** (1→2 vidéos/jour sur 2 semaines)

### Recommandations

- ✅ Commencer avec 1 vidéo/jour pendant 2 semaines
- ✅ Monitorer les métriques TikTok quotidiennement
- ✅ Varier les thèmes et styles
- ❌ Ne jamais publier à heures fixes
- ❌ Ne pas dépasser 2 vidéos/jour

## 📊 Monitoring

Les logs sont sauvegardés dans `logs/tiktok_automation.log`:

```bash
tail -f logs/tiktok_automation.log
```

## 🐛 Dépannage

### Erreur "FFmpeg not found"

```bash
which ffmpeg
# Si vide, installer FFmpeg
brew install ffmpeg
```

### Erreur "Google API Key invalid"

Vérifier que la clé API est correcte dans `.env` et que l'API Gemini est activée sur [Google AI Studio](https://makersuite.google.com/app/apikey).

### Erreur TikTok "Session expired"

Supprimer les cookies et se reconnecter:

```bash
rm -rf playwright_state/
python scheduler.py --test
```

### Vidéo sans son / Erreur TTS

```bash
# Vérifier l'installation Edge TTS
pip install --upgrade edge-tts

# Tester la génération
python modules/voice_generator.py

# Si Edge TTS échoue, utiliser gTTS
# Dans config.py: TTS_CONFIG = {"backend": "gtts"}
```

## 💰 Coûts estimés

Pour 60 vidéos/mois:

| Service | Coût mensuel |
|---------|--------------|
| Gemini API | $5-10 |
| **TTS (Edge TTS)** | **$0 🆓** |
| Cloud Storage (optionnel) | $0-1 |
| **Total** | **$5-10** |

### 🎉 Économies avec TTS gratuit

- ❌ Avant (Google Cloud TTS): $7-15/mois
- ✅ Maintenant (Edge TTS): **$5-10/mois**
- 💰 **Économie: $24-60/an**

**Alternatives TTS:**
- **Edge TTS** (Microsoft) - Gratuit, qualité excellente ⭐⭐⭐⭐⭐
- **gTTS** (Google Translate) - Gratuit, qualité bonne ⭐⭐⭐
- **pyttsx3** (Offline) - Gratuit, qualité basique ⭐⭐

Voir [`TTS_COMPARISON.md`](file:///Users/eric/tiktok/TTS_COMPARISON.md) pour comparer.

## 📝 Exemples de prompts

Les prompts Gemini sont optimisés pour TikTok. Voir:

- `modules/idea_generator.py` - Prompts d'idées virales
- `modules/script_writer.py` - Prompts de scripts
- `modules/subtitle_generator.py` - Prompts de sous-titres

## 🔐 Sécurité

- ⚠️ Ne jamais commiter le fichier `.env`
- ⚠️ Garder les credentials Google en sécurité
- ⚠️ Utiliser un compte TikTok dédié pour les tests

## 📚 Ressources

- [Documentation Gemini](https://ai.google.dev/docs)
- [Google Text-to-Speech](https://cloud.google.com/text-to-speech)
- [Playwright Python](https://playwright.dev/python/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

## 🤝 Support

Pour toute question ou problème, consulter:

1. Les logs dans `logs/`
2. La documentation dans `implementation_plan.md`
3. Les exemples de code dans chaque module

## ⚖️ Licence et Avertissement

Ce système est fourni à des fins éducatives. L'utilisation d'automatisation sur TikTok peut violer les conditions d'utilisation de la plateforme. Utilisez à vos propres risques.

**Recommandations légales:**
- Respecter les droits d'auteur
- Ne pas publier de contenu trompeur
- Suivre les guidelines TikTok
- Utiliser sur un compte de test d'abord

---

**Développé avec ❤️ et Google IA**
