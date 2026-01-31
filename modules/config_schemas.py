from pydantic import BaseModel
from typing import Optional, List

# Models for Subtitle Configuration
class SubtitleStyle(BaseModel):
    font_family: str = "Montserrat-Bold" # Nom de la police (devra être installée/disponible)
    font_size: int = 70
    text_color: str = "#FFFFFF"
    stroke_color: str = "#000000"
    stroke_width: int = 4
    shadow_color: str = "rgba(0,0,0,0.5)"
    shadow_offset: List[int] = [3, 3] # [x, y]

class SubtitleAnimation(BaseModel):
    type: str = "karaoke"  # "static", "karaoke", "pop-in"
    highlight_color: str = "#00FF00" # Couleur du mot actif (karaoke)
    word_by_word: bool = True

class SubtitlePosition(BaseModel):
    alignment: str = "center" # "left", "center", "right"
    vertical_align: str = "center" # "top", "center", "bottom"
    margin_bottom: int = 150 # Marge du bas en pixels

class SubtitleBackground(BaseModel):
    enabled: bool = False
    color: str = "#000000"
    opacity: float = 0.6
    padding: int = 20
    corner_radius: int = 10

class SubtitleConfig(BaseModel):
    style: SubtitleStyle = SubtitleStyle()
    animation: SubtitleAnimation = SubtitleAnimation()
    position: SubtitlePosition = SubtitlePosition()
    background: SubtitleBackground = SubtitleBackground()
