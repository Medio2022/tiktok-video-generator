# Guide de Personnalisation des Sous-titres

## Changer la Couleur

Éditer `/Users/eric/tiktok/config.py`:

```python
SUBTITLE_CONFIG = {
    "enabled": True,
    "color": (0, 255, 255, 255),  # ← Modifier ici
    "size": 85,
    "outline_color": (0, 0, 0, 255),
    "outline_width": 5,
    "position_from_bottom": 300,
}
```

### Couleurs Populaires (RGBA)

| Couleur | Code RGBA | Utilisation |
|---------|-----------|-------------|
| **Cyan** (défaut) | `(0, 255, 255, 255)` | Style TikTok moderne |
| **Jaune** | `(255, 255, 0, 255)` | Très visible, fun |
| **Blanc** | `(255, 255, 255, 255)` | Classique, élégant |
| **Rose** | `(255, 100, 255, 255)` | Féminin, doux |
| **Orange** | `(255, 165, 0, 255)` | Énergique, chaud |
| **Vert** | `(0, 255, 100, 255)` | Frais, nature |

## Changer la Taille

```python
SUBTITLE_CONFIG = {
    "size": 100,  # Plus grand
    # ou
    "size": 70,   # Plus petit
}
```

**Recommandations:**
- Petit appareil: 70-80
- Standard: 85 (défaut)
- Impact visuel: 90-100

## Changer la Bordure

```python
SUBTITLE_CONFIG = {
    "outline_width": 8,  # Bordure épaisse
    "outline_color": (255, 0, 0, 255),  # Bordure rouge
}
```

## Changer la Position

```python
SUBTITLE_CONFIG = {
    "position_from_bottom": 400,  # Plus haut
    # ou
    "position_from_bottom": 200,  # Plus bas
}
```

## Exemples de Styles

### Style TikTok Viral (défaut)
```python
{
    "color": (0, 255, 255, 255),      # Cyan
    "size": 85,
    "outline_width": 5,
    "outline_color": (0, 0, 0, 255),
}
```

### Style YouTube Shorts
```python
{
    "color": (255, 255, 0, 255),      # Jaune
    "size": 90,
    "outline_width": 6,
    "outline_color": (0, 0, 0, 255),
}
```

### Style Minimaliste
```python
{
    "color": (255, 255, 255, 255),    # Blanc
    "size": 75,
    "outline_width": 3,
    "outline_color": (0, 0, 0, 255),
}
```

### Style Énergique
```python
{
    "color": (255, 100, 255, 255),    # Rose/Magenta
    "size": 95,
    "outline_width": 7,
    "outline_color": (255, 255, 0, 255),  # Bordure jaune
}
```

## Changer le Modèle Whisper

Éditer `/Users/eric/tiktok/main.py` ligne ~151:

```python
generate_subtitles_from_audio(
    str(audio_path),
    str(subtitle_path),
    model_size="small"  # Modifier ici
)
```

### Modèles Disponibles

| Modèle | Vitesse | Précision | Taille |
|--------|---------|-----------|--------|
| `tiny` | ⚡⚡⚡ Très rapide | ⭐⭐ | 39 MB |
| `base` | ⚡⚡ Rapide | ⭐⭐⭐ | 139 MB |
| `small` | ⚡ Moyen | ⭐⭐⭐⭐ | 461 MB |
| `medium` | 🐌 Lent | ⭐⭐⭐⭐⭐ | 1.5 GB |
| `large` | 🐌🐌 Très lent | ⭐⭐⭐⭐⭐ | 2.9 GB |

**Recommandation:** `base` (défaut) - excellent équilibre

## Exemples Complets

### Configuration Jaune Vif
```python
# config.py
SUBTITLE_CONFIG = {
    "enabled": True,
    "color": (255, 255, 0, 255),
    "size": 90,
    "outline_color": (0, 0, 0, 255),
    "outline_width": 6,
    "position_from_bottom": 300,
}
```

### Configuration Rose Doux
```python
# config.py
SUBTITLE_CONFIG = {
    "enabled": True,
    "color": (255, 182, 193, 255),  # Rose clair
    "size": 80,
    "outline_color": (255, 255, 255, 255),  # Bordure blanche
    "outline_width": 4,
    "position_from_bottom": 350,
}
```

Après modification, relancez:
```bash
cd /Users/eric/tiktok && source .venv311/bin/activate && python main.py --theme motivation
```
