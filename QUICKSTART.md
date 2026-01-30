# 🚀 Quick Start Guide - TikTok Automation

Guide rapide pour démarrer avec le système d'automatisation TikTok.

## ⚡ Installation Express (5 minutes)

### 1. Setup automatique

```bash
cd /Users/eric/tiktok
./setup.sh
```

Le script va automatiquement:
- ✅ Vérifier Python et FFmpeg
- ✅ Créer l'environnement virtuel
- ✅ Installer toutes les dépendances
- ✅ Installer Playwright
- ✅ Créer les répertoires nécessaires
- ✅ Générer le fichier .env

### 2. Configuration des API

Éditez le fichier `.env`:

```bash
nano .env
```

**Minimum requis:**

```env
# Gemini API (OBLIGATOIRE - GRATUIT avec quota)
GOOGLE_API_KEY=AIza...votre_clé_ici

# TikTok (OBLIGATOIRE pour auto-publish)
TIKTOK_USERNAME=votre_username
TIKTOK_PASSWORD=votre_password

# Thème
THEME=motivation
```

**Obtenir la clé Gemini (GRATUIT):**

1. **Gemini API**: https://makersuite.google.com/app/apikey
   - Créer une clé API (gratuit)
   - Copier la clé dans .env

**C'est tout!** Plus besoin de Google Cloud Project ni de credentials JSON.

### 3. Premier test

```bash
# Activer l'environnement
source venv/bin/activate

# Générer une vidéo de test
python main.py --theme motivation

# Vérifier la sortie
ls -lh output/tiktok_*/final_video.mp4
```

## 📊 Utilisation

### Générer une vidéo unique

```bash
python main.py --theme productivite
```

**Thèmes disponibles:**
- `motivation` - Contenu motivationnel
- `productivite` - Astuces productivité
- `tech` - Technologie
- `business` - Entrepreneuriat
- `sante` - Santé et bien-être

### Générer plusieurs vidéos

```bash
# Générer 5 vidéos d'un coup
python main.py --theme motivation --count 5
```

### Lancer le scheduler automatique

```bash
# Mode production (publication automatique)
python scheduler.py --theme motivation

# Mode test (génération seule)
python scheduler.py --test
```

## 📁 Structure des fichiers générés

```
output/
└── tiktok_20260128_190000/
    ├── final_video.mp4      # Vidéo finale
    ├── voiceover.mp3        # Audio
    ├── subtitles.srt        # Sous-titres
    └── metadata.json        # Toutes les données
```

## 🎯 Workflow complet

### Option 1: Génération manuelle + Publication manuelle

```bash
# 1. Générer la vidéo
python main.py --theme motivation

# 2. Récupérer la description TikTok
cat output/tiktok_*/metadata.json | grep "tiktok_description" -A 10

# 3. Publier manuellement sur TikTok
# - Uploader output/tiktok_*/final_video.mp4
# - Copier/coller la description
```

### Option 2: Génération + Publication automatique

```bash
# Lancer le scheduler (1-2 vidéos/jour)
python scheduler.py --theme motivation
```

Le scheduler va:
- ✅ Générer des vidéos aux heures optimales
- ✅ Attendre 30-120 min (anti-détection)
- ✅ Publier automatiquement sur TikTok
- ✅ Logger tous les résultats

## 🔧 Personnalisation rapide

### Changer la voix

Dans `config.py`:

```python
TTS_CONFIG = {
    "voice_name": "fr-FR-Neural2-B",  # Voix masculine
    "speaking_rate": 1.15,  # Plus rapide
}
```

### Modifier la fréquence de publication

Dans `config.py`:

```python
PUBLICATION_CONFIG = {
    "daily_videos": 1,  # 1 ou 2 vidéos/jour
    "publication_hours": [(10, 14), (18, 22)],
}
```

### Changer les couleurs de fond

Dans `modules/background_generator.py`, modifier les palettes de couleurs.

## 🐛 Dépannage Express

### Problème: "FFmpeg not found"

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### Problème: "Google API Key invalid"

1. Vérifier que la clé est correcte dans `.env`
2. Activer l'API Gemini: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

### Problème: "No audio in video"

1. Vérifier `GOOGLE_APPLICATION_CREDENTIALS` dans `.env`
2. Activer "Cloud Text-to-Speech API" dans Google Cloud
3. Vérifier que le fichier JSON de credentials existe

### Problème: "TikTok login failed"

1. Vérifier username/password dans `.env`
2. Supprimer les cookies: `rm -rf playwright_state/`
3. Relancer: `python scheduler.py --test`

## 📊 Monitoring

### Voir les logs en temps réel

```bash
tail -f logs/tiktok_automation.log
```

### Vérifier une vidéo

```bash
python -c "from utils.validators import VideoValidator; VideoValidator().validate_video('output/tiktok_*/final_video.mp4')"
```

## 💰 Coûts

Pour 60 vidéos/mois (2/jour):

| Service | Coût |
|---------|------|
| Gemini API | $5-10 |
| **TTS (Edge TTS)** | **$0 🆓** |
| **Total** | **$5-10/mois** |

**🎉 100% GRATUIT pour le TTS!**

Utilise Edge TTS (Microsoft) au lieu de Google Cloud TTS:
- ✅ Qualité identique (voix neurales)
- ✅ Aucun coût
- ✅ Aucune configuration complexe

Voir [`TTS_COMPARISON.md`](file:///Users/eric/tiktok/TTS_COMPARISON.md) pour plus de détails.

## 🛡️ Stratégie Anti-Ban

**IMPORTANT:** Commencer doucement!

**Semaine 1-2:** 1 vidéo/jour
```python
PUBLICATION_CONFIG = {"daily_videos": 1}
```

**Semaine 3+:** 2 vidéos/jour
```python
PUBLICATION_CONFIG = {"daily_videos": 2}
```

**Bonnes pratiques:**
- ✅ Varier les thèmes
- ✅ Monitorer les métriques TikTok
- ✅ Respecter les délais aléatoires
- ❌ Ne jamais publier à heures fixes
- ❌ Ne pas dépasser 2 vidéos/jour

## 📚 Ressources

- **Documentation complète:** `README.md`
- **Plan d'implémentation:** `implementation_plan.md`
- **Script Playwright:** `playwright_script.py`

## ✅ Checklist de démarrage

- [ ] Setup terminé (`./setup.sh`)
- [ ] Clés API configurées dans `.env`
- [ ] Première vidéo générée avec succès
- [ ] Vidéo validée (résolution, durée, audio)
- [ ] Description TikTok récupérée
- [ ] Publication test réussie (manuelle ou auto)
- [ ] Scheduler configuré pour production

---

**🎬 Prêt à générer du contenu viral!**

Pour toute question, consultez `README.md` ou les logs dans `logs/`.
