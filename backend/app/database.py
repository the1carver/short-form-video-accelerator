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
            "id": str(uuid.uuid4()),
            "name": "TikTok Explainer",
            "description": "Clean, text-focused template for educational content",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["educational", "tutorial"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Dynamic Promo",
            "description": "Fast-paced template with motion graphics for promotional content",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["promotional", "entertainment"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Interview Highlights",
            "description": "Template for showcasing key moments from interviews",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["interview", "educational"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Tutorial Steps",
            "description": "Step-by-step format for tutorials with clear instructions",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["tutorial", "educational"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Presentation Clips",
            "description": "Template for converting presentation slides to engaging videos",
            "aspect_ratio": "9:16",
            "suitable_content_types": ["presentation", "educational"]
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
