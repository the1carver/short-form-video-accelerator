from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class VideoFormat(str, Enum):
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    MKV = "mkv"

class AspectRatio(str, Enum):
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    LANDSCAPE = "16:9"

class ContentType(str, Enum):
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    ENTERTAINMENT = "entertainment"
    TUTORIAL = "tutorial"
    INTERVIEW = "interview"
    PRESENTATION = "presentation"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoSegment(BaseModel):
    start_time: float
    end_time: float
    transcript: str
    keywords: List[str] = []
    importance_score: float = 0.0
    engagement_prediction: float = 0.0

class VideoTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    aspect_ratio: AspectRatio
    suitable_content_types: List[ContentType]
    preview_url: Optional[HttpUrl] = None

class BrandAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    asset_type: str  # logo, font, color, etc.
    s3_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    organization: Optional[str] = None
    subscription_tier: str = "basic"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContentUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    preferred_aspect_ratio: AspectRatio = AspectRatio.PORTRAIT
    preferred_duration: Optional[int] = None  # in seconds
    user_id: str
    template_id: Optional[str] = None
    brand_assets_ids: List[str] = []
    
    @validator('preferred_duration')
    def validate_duration(cls, v):
        if v is not None and (v < 15 or v > 60):
            raise ValueError('Preferred duration must be between 15 and 60 seconds for TikTok videos')
        return v

class ContentAnalysisResult(BaseModel):
    content_id: str
    segments: List[VideoSegment]
    keywords: List[str]
    summary: str
    recommended_templates: List[str] = []
    engagement_prediction: float
    
class VideoProcessingRequest(BaseModel):
    content_id: str
    selected_segments: List[str]
    template_id: str
    brand_assets_ids: List[str] = []
    custom_settings: Dict[str, Any] = {}

class VideoProcessingResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    preview_url: Optional[HttpUrl] = None
    final_url: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    
class PerformanceMetrics(BaseModel):
    video_id: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    average_watch_time: float = 0.0
    completion_rate: float = 0.0
    engagement_rate: float = 0.0
    click_through_rate: Optional[float] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
