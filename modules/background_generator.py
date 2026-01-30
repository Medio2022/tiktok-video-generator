"""
Générateur de fonds visuels pour TikTok
Alternative simple à Imagen pour réduire les coûts
"""

import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random
from typing import Tuple, Optional

from config import VIDEO_CONFIG, OUTPUT_DIR

logger = logging.getLogger(__name__)


class BackgroundGenerator:
    """Générateur de fonds visuels pour vidéos TikTok"""
    
    def __init__(self):
        """Initialiser le générateur"""
        self.width, self.height = VIDEO_CONFIG["resolution"]
    
    def generate_gradient(
        self,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        output_path: Optional[str] = None,
        direction: str = "vertical"
    ) -> str:
        """
        Générer un fond avec dégradé
        
        Args:
            color1: Couleur de départ (RGB)
            color2: Couleur de fin (RGB)
            output_path: Chemin de sortie
            direction: 'vertical', 'horizontal', 'diagonal'
            
        Returns:
            Chemin du fichier généré
        """
        logger.info(f"🎨 Génération d'un fond dégradé {direction}...")
        
        if output_path is None:
            output_path = OUTPUT_DIR / "background.png"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer l'image
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        if direction == "vertical":
            for y in range(self.height):
                ratio = y / self.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        elif direction == "horizontal":
            for x in range(self.width):
                ratio = x / self.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, self.height)], fill=(r, g, b))
        
        elif direction == "diagonal":
            for y in range(self.height):
                for x in range(self.width):
                    ratio = (x + y) / (self.width + self.height)
                    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                    draw.point((x, y), fill=(r, g, b))
        
        # Sauvegarder
        img.save(output_path, 'PNG')
        logger.info(f"✅ Fond généré: {output_path}")
        
        return str(output_path)
    
    def generate_themed(
        self,
        theme: str,
        output_path: Optional[str] = None,
        style: str = "gradient"
    ) -> str:
        """
        Générer un fond selon le thème
        
        Args:
            theme: Thème du contenu
            output_path: Chemin de sortie
            style: Style visuel ('gradient', 'solid', 'noise')
            
        Returns:
            Chemin du fichier généré
        """
        logger.info(f"🎨 Génération d'un fond pour le thème '{theme}'...")
        
        # Palettes de couleurs par thème
        palettes = {
            "motivation": [
                ((20, 30, 60), (60, 40, 100)),    # Bleu-violet
                ((30, 20, 50), (80, 50, 120)),    # Violet profond
                ((10, 30, 70), (40, 60, 140)),    # Bleu nuit
            ],
            "productivite": [
                ((30, 20, 40), (70, 50, 90)),     # Violet foncé
                ((20, 40, 50), (50, 80, 100)),    # Bleu-vert
                ((40, 30, 60), (90, 70, 120)),    # Violet-rose
            ],
            "tech": [
                ((10, 20, 30), (30, 50, 80)),     # Bleu tech
                ((20, 20, 40), (40, 40, 90)),     # Bleu électrique
                ((15, 25, 35), (35, 55, 85)),     # Bleu cyber
            ],
            "business": [
                ((30, 30, 30), (60, 60, 60)),     # Gris professionnel
                ((20, 25, 35), (50, 55, 70)),     # Gris-bleu
                ((35, 30, 25), (70, 60, 50)),     # Gris-brun
            ],
            "sante": [
                ((20, 40, 30), (50, 90, 70)),     # Vert nature
                ((30, 50, 40), (60, 100, 80)),    # Vert frais
                ((25, 45, 35), (55, 95, 75)),     # Vert santé
            ],
        }
        
        # Choisir une palette aléatoire pour le thème
        theme_palettes = palettes.get(theme, palettes["motivation"])
        color1, color2 = random.choice(theme_palettes)
        
        if style == "gradient":
            direction = random.choice(["vertical", "diagonal"])
            return self.generate_gradient(color1, color2, output_path, direction)
        
        elif style == "solid":
            return self.generate_solid(color1, output_path)
        
        elif style == "noise":
            return self.generate_noise(color1, color2, output_path)
        
        else:
            logger.warning(f"⚠️  Style '{style}' non reconnu, utilisation de 'gradient'")
            return self.generate_gradient(color1, color2, output_path)
    
    def generate_solid(
        self,
        color: Tuple[int, int, int],
        output_path: Optional[str] = None
    ) -> str:
        """Générer un fond de couleur unie"""
        logger.info(f"🎨 Génération d'un fond uni...")
        
        if output_path is None:
            output_path = OUTPUT_DIR / "background.png"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGB', (self.width, self.height), color)
        img.save(output_path, 'PNG')
        
        logger.info(f"✅ Fond généré: {output_path}")
        return str(output_path)
    
    def generate_noise(
        self,
        color1: Tuple[int, int, int],
        color2: Tuple[int, int, int],
        output_path: Optional[str] = None
    ) -> str:
        """Générer un fond avec texture de bruit"""
        logger.info(f"🎨 Génération d'un fond avec texture...")
        
        if output_path is None:
            output_path = OUTPUT_DIR / "background.png"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Créer un dégradé de base
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Ajouter du bruit
        pixels = img.load()
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:  # 10% de pixels avec bruit
                    r, g, b = pixels[x, y]
                    noise = random.randint(-20, 20)
                    r = max(0, min(255, r + noise))
                    g = max(0, min(255, g + noise))
                    b = max(0, min(255, b + noise))
                    pixels[x, y] = (r, g, b)
        
        # Appliquer un léger flou pour adoucir
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
        
        img.save(output_path, 'PNG')
        logger.info(f"✅ Fond généré: {output_path}")
        
        return str(output_path)


if __name__ == "__main__":
    # Test du générateur
    logging.basicConfig(level=logging.INFO)
    
    generator = BackgroundGenerator()
    
    # Tester différents styles
    print("\n🎨 Génération de fonds de test...\n")
    
    # Gradient
    generator.generate_themed("motivation", "output/bg_motivation.png", "gradient")
    
    # Solid
    generator.generate_themed("tech", "output/bg_tech.png", "solid")
    
    # Noise
    generator.generate_themed("productivite", "output/bg_productivite.png", "noise")
    
    print("\n✅ Fonds générés dans output/")
