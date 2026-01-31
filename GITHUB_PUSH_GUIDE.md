# 🚀 Instructions pour Pousser sur GitHub

## Étape 1: Créer le Repository sur GitHub

1. **Aller sur GitHub:**
   - Ouvrir https://github.com/new
   - Ou: GitHub.com → Cliquer sur le `+` en haut à droite → "New repository"

2. **Configuration du Repository:**
   - **Repository name:** `tiktok-video-generator`
   - **Description (optionnel):** "AI-powered TikTok video generator with Whisper, DeepSeek, and Edge TTS"
   - **Visibilité:** ✅ **Private** (cocher "Private")
   - ⚠️ **NE PAS** cocher "Add a README file"
   - ⚠️ **NE PAS** cocher "Add .gitignore"
   - ⚠️ **NE PAS** cocher "Choose a license"
   - Cliquer sur **"Create repository"**

## Étape 2: Pousser le Code

Une fois le repository créé sur GitHub, exécuter ces commandes dans le terminal:

```bash
cd /Users/eric/tiktok
git push -u origin main
```

**Si demande de credentials:**

### Option A: Token GitHub (Recommandé)
```bash
# Entrer:
Username: Medio2022
Password: <VOTRE_GITHUB_TOKEN>  # Pas votre mot de passe !
```

**Créer un token:**
1. GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → Select scopes: `repo` (tout cocher)
3. Copier le token (vous ne le reverrez plus !)

### Option B: SSH (Alternative)
```bash
# Changer le remote en SSH
cd /Users/eric/tiktok
git remote set-url origin git@github.com:Medio2022/tiktok-video-generator.git
git push -u origin main
```

## Étape 3: Vérification

Après le push, aller sur:
```
https://github.com/Medio2022/tiktok-video-generator
```

Vous devriez voir:
- ✅ 29 fichiers poussés
- ✅ README.md affiché
- ✅ Repository privé (🔒 icône cadenas)

## Fichiers Inclus

**Code principal:**
- `main.py` - Pipeline principal
- `config.py` - Configuration
- `requirements.txt` - Dépendances

**Modules (modules/):**
- `whisper_subtitles.py` - Transcription Whisper
- `deepseek_client.py` - Génération contenu AI
- `voice_generator.py` - Edge TTS
- `video_generator.py` - Pexels downloader
- `complete_video_assembler.py` - Assemblage final
- ... et 19 autres modules

**Documentation:**
- `README.md` - Guide principal
- `SUBTITLE_CUSTOMIZATION.md` - Guide personnalisation
- `TTS_COMPARISON.md` - Comparaison TTS
- `QUICKSTART.md` - Démarrage rapide
- `.env.example` - Template environnement

**Sécurité:**
- `.gitignore` - Exclut `.env`, `output/`, `venv/`
- ⚠️ Vos clés API restent locales (non poussées)

## Commandes Git Utiles

```bash
# Voir l'état
git status

# Voir l'historique
git log --oneline

# Voir les fichiers trackés
git ls-files

# Ajouter de nouveaux changements
git add .
git commit -m "Description des changements"
git push

# Cloner ailleurs
git clone https://github.com/Medio2022/tiktok-video-generator.git
```

## Troubleshooting

### Erreur "repository not found"
→ Le repo n'est pas encore créé sur GitHub, suivre Étape 1

### Erreur "authentication failed"
→ Utiliser un token GitHub, pas votre mot de passe

### Erreur "rejected (non-fast-forward)"
```bash
git pull origin main --rebase
git push -u origin main
```

---

**Une fois poussé, le code sera sauvegardé et versionné sur GitHub ! 🎉**
