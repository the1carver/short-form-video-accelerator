from typing import Dict, List, Optional, Any, Type, TypeVar
from pydantic import BaseModel
import uuid
from datetime import datetime

# Type variable for generic functions
T = TypeVar('T', bound=BaseModel)

# In-memory database tables
class InMemoryDB:
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.content_uploads: Dict[str, Dict] = {}
        self.content_analyses: Dict[str, Dict] = {}
        self.video_templates: Dict[str, Dict] = {}
        self.brand_assets: Dict[str, Dict] = {}
        self.video_processing_results: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, Dict] = {}

# Create a global database instance
db = InMemoryDB()

# Initialize with some default templates
def initialize_templates():
    templates = [
        {
            "id": "template1",
            "name": "TikTok Explainer",
            "description": "Clean, text-focused template for educational content",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["educational", "tutorial"],
            "thumbnail_url": "https://via.placeholder.com/300x500?text=TikTok+Explainer",
            "caption_style": {
                "font_family": "Inter",
                "font_size": 24,
                "font_color": "#FFFFFF",
                "background_color": "#000000B3",
                "position": "bottom"
            },
            "overlay_color": "#00000033"
        },
        {
            "id": "template2",
            "name": "Dynamic Promo",
            "description": "Fast-paced template with motion graphics for promotional content",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["promotional", "entertainment"],
            "thumbnail_url": "https://via.placeholder.com/300x500?text=Dynamic+Promo",
            "caption_style": {
                "font_family": "Montserrat",
                "font_size": 28,
                "font_color": "#FFFFFF",
                "background_color": "#3B82F6B3",
                "position": "bottom"
            },
            "overlay_color": "#3B82F633",
            "intro_animation": "fade-in",
            "outro_animation": "slide-out"
        },
        {
            "id": "template3",
            "name": "Interview Highlights",
            "description": "Template for showcasing key moments from interviews",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["interview", "educational"],
            "thumbnail_url": "https://via.placeholder.com/300x500?text=Interview+Highlights",
            "caption_style": {
                "font_family": "Roboto",
                "font_size": 22,
                "font_color": "#FFFFFF",
                "background_color": "#000000CC",
                "position": "bottom"
            },
            "overlay_color": "#00000022"
        },
        {
            "id": "template4",
            "name": "Tutorial Steps",
            "description": "Step-by-step format for tutorials with clear instructions",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["tutorial", "educational"],
            "thumbnail_url": "https://via.placeholder.com/300x500?text=Tutorial+Steps",
            "caption_style": {
                "font_family": "Roboto",
                "font_size": 26,
                "font_color": "#333333",
                "background_color": "#FFFFFFCC",
                "position": "middle"
            },
            "overlay_color": "#FFFFFF33"
        },
        {
            "id": "template5",
            "name": "Presentation Clips",
            "description": "Template for converting presentation slides to engaging videos",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["presentation", "educational"],
            "thumbnail_url": "https://via.placeholder.com/300x500?text=Presentation+Clips",
            "caption_style": {
                "font_family": "Open Sans",
                "font_size": 24,
                "font_color": "#FFFFFF",
                "background_color": "#2563EBB3",
                "position": "bottom"
            },
            "overlay_color": "#2563EB22"
        },
        {
            "id": "template6",
            "name": "Product Showcase",
            "description": "Highlight your product features with this dynamic template",
            "aspect_ratio": "1:1",
            "suitable_content_types": ["product", "demo"],
            "thumbnail_url": "https://via.placeholder.com/300x300?text=Product+Showcase",
            "caption_style": {
                "font_family": "Montserrat",
                "font_size": 28,
                "font_color": "#FFFFFF",
                "background_color": "#3B82F6B3",
                "position": "bottom"
            },
            "overlay_color": "#3B82F633"
        }
    ]
    
    for template in templates:
        db.video_templates[template["id"]] = template

# Generic CRUD operations
async def create_item(table: Dict[str, Dict], item: BaseModel) -> Dict:
    """Create a new item in the specified table"""
    item_dict = item.dict()
    if "id" not in item_dict:
        item_dict["id"] = str(uuid.uuid4())
    table[item_dict["id"]] = item_dict
    return item_dict

async def get_item(table: Dict[str, Dict], item_id: str) -> Optional[Dict]:
    """Get an item by ID from the specified table"""
    return table.get(item_id)

async def update_item(table: Dict[str, Dict], item_id: str, item: Dict[str, Any]) -> Optional[Dict]:
    """Update an item in the specified table"""
    if item_id in table:
        current_item = table[item_id]
        updated_item = {**current_item, **item, "updated_at": datetime.utcnow()}
        table[item_id] = updated_item
        return updated_item
    return None

async def delete_item(table: Dict[str, Dict], item_id: str) -> bool:
    """Delete an item from the specified table"""
    if item_id in table:
        del table[item_id]
        return True
    return False

async def list_items(table: Dict[str, Dict], skip: int = 0, limit: int = 100) -> List[Dict]:
    """List items from the specified table with pagination"""
    items = list(table.values())
    return items[skip:skip + limit]

# Initialize the database with default data
initialize_templates()
