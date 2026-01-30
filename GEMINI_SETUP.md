# 🔑 Configuration de la clé Gemini API

## Étapes rapides

### 1. Obtenir une clé API Gemini (GRATUIT)

1. Aller sur [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Se connecter avec votre compte Google
3. Cliquer sur "Create API Key"
4. Copier la clé (commence par `AIza...`)

### 2. Configurer dans .env

Éditer le fichier `.env`:

```bash
nano .env
```

Remplacer:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Par:
```env
GOOGLE_API_KEY=AIzaSy...votre_vraie_clé
```

Sauvegarder (Ctrl+O, Enter, Ctrl+X)

### 3. Tester

```bash
python3 main.py --theme motivation
```

## Quotas gratuits

- **Gemini Pro**: 60 requêtes/minute
- **Coût**: GRATUIT jusqu'à 1500 requêtes/jour
- **Suffisant pour**: 50+ vidéos/jour

## Dépannage

### Erreur "API key not valid"

- Vérifier que la clé est bien copiée (pas d'espaces)
- Vérifier que l'API est activée sur Google AI Studio
- Attendre 1-2 minutes après création de la clé

### Erreur "models/gemini-1.5-flash is not found"

- Les noms de modèles ont changé
- Utiliser `gemini-pro` ou `gemini-1.5-pro-latest`
- Le système a été mis à jour automatiquement

## Liens utiles

- **Obtenir clé**: https://makersuite.google.com/app/apikey
- **Documentation**: https://ai.google.dev/docs
- **Quotas**: https://ai.google.dev/pricing
