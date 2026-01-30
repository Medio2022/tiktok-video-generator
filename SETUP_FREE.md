# 🚀 Guide de Setup - Solution Gratuite Illimitée

## 📋 Prérequis

- Python 3.11+ ✅ (déjà installé)
- FFmpeg ✅ (déjà installé)
- Edge TTS ✅ (déjà installé)

## 🔑 Obtenir les Clés API (5 minutes)

### 1. DeepSeek API (Gratuit - Illimité)

**Étapes:**
1. Aller sur: https://platform.deepseek.com/
2. Créer un compte (email + mot de passe)
3. Aller dans "API Keys"
4. Cliquer "Create API Key"
5. Copier la clé (commence par `sk-...`)

**Quota gratuit:**
- 50 requêtes/minute
- Pas de limite journalière
- Modèle: `deepseek-chat`

### 2. Pexels API (Gratuit - Illimité)

**Étapes:**
1. Aller sur: https://www.pexels.com/api/
2. Créer un compte
3. Cliquer "Get Started" → "Request API Key"
4. Remplir le formulaire (nom du projet: "TikTok Automation")
5. Copier la clé

**Quota:**
- ♾️ Requêtes illimitées
- ♾️ Téléchargements illimités
- ✅ Pas de watermark
- ✅ Usage commercial OK

## ⚙️ Configuration

### 1. Mettre à jour `.env`

```bash
cd /Users/eric/tiktok

# Éditer .env
nano .env
```

Ajouter vos clés:
```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-votre-cle-deepseek-ici

# Pexels API  
PEXELS_API_KEY=votre-cle-pexels-ici
```

Sauvegarder: `Ctrl+O`, `Enter`, `Ctrl+X`

### 2. Installer dépendances

```bash
source .venv311/bin/activate
pip install requests
```

## ✅ Test Rapide

### Test DeepSeek

```bash
python -c "
from modules.deepseek_client import DeepSeekClient
client = DeepSeekClient()
idea = client.generate_idea('motivation')
print('✅ DeepSeek fonctionne!')
print(f'Idée: {idea[\"hook\"]}')
"
```

### Test Pexels

```bash
python -c "
from modules.video_generator import VideoGenerator
gen = VideoGenerator()
videos = gen.search_videos(['workspace', 'typing'])
print(f'✅ Pexels fonctionne! {len(videos)} vidéos trouvées')
"
```

## 🎬 Génération de Vidéo

```bash
# Activer l'environnement
source .venv311/bin/activate

# Générer 1 vidéo
python main.py --theme motivation

# Générer 10 vidéos
python main.py --theme motivation --count 10
```

## 📊 Résultat Attendu

```
output/tiktok_20260128_230000/
├── final_video.mp4      # Vidéo TikTok 9:16 avec vraie vidéo HD
├── voiceover.mp3        # Audio Edge TTS
├── subtitles.srt        # Sous-titres
└── metadata.json        # Toutes les infos
```

## 🔧 Dépannage

### "DEEPSEEK_API_KEY manquante"
→ Vérifier que la clé est dans `.env` et commence par `sk-`

### "PEXELS_API_KEY manquante"
→ Système utilisera des fonds colorés (fallback automatique)

### "Aucune vidéo trouvée"
→ Normal, système utilisera fond coloré automatiquement

## 💰 Coûts

| Service | Coût |
|---------|------|
| DeepSeek | $0 (tier gratuit) |
| Pexels | $0 (toujours gratuit) |
| Edge TTS | $0 (toujours gratuit) |
| FFmpeg | $0 (open source) |
| **TOTAL** | **$0/mois** |

**Pour 1000 vidéos/mois: $0** 🎉
