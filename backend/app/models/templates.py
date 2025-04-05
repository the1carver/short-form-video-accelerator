from typing import List, Optional
from pydantic import BaseModel

class CaptionStyle(BaseModel):
    font_family: str
    font_size: int
    font_color: str
    background_color: str
    position: str = "bottom"  # "bottom", "top", "middle"
    
class VideoTemplate(BaseModel):
    id: str
    name: str
    description: str
    aspect_ratio: str = "9:16"  # "9:16", "16:9", "1:1"
    suitable_content_types: List[str] = []
    thumbnail_url: str
    caption_style: CaptionStyle
    overlay_color: Optional[str] = None
    intro_animation: Optional[str] = None
    outro_animation: Optional[str] = None
