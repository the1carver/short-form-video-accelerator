from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from typing import List, Optional
import uuid
import os
import logging
from ..config import settings
from ..models import ContentUploadRequest, ContentAnalysisResult, VideoProcessingRequest, VideoProcessingResult, ProcessingStatus
from ..database import db, create_item, get_item, update_item, list_items
from ..services.storage import storage_service
from ..services.content_analysis import content_analysis_service
from ..services.video_processing import video_processing_service
from ..services.auth import get_current_user

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/content",
    tags=["content"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/upload")
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: str = Form(...),
    preferred_aspect_ratio: str = Form("9:16"),
    preferred_duration: Optional[int] = Form(None),
    user_id: str = Form(...),
    template_id: Optional[str] = Form(None),
    brand_assets_ids: str = Form("")
):
    """
    Upload a video file for processing
    """
    logger.info(f"Uploading content: {title} for user {user_id}")
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower().replace(".", "")
    if file_extension not in settings.supported_video_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(settings.supported_video_formats)}"
        )
    
    try:
        # Create a unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        s3_key = f"uploads/{user_id}/{unique_filename}"
        
        # Save file temporarily
        temp_file_path = f"/tmp/{unique_filename}"
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Upload to S3
        file_url = await storage_service.upload_file(
            temp_file_path, 
            s3_key,
            content_type=f"video/{file_extension}"
        )
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        # Parse brand assets IDs
        brand_assets_ids_list = brand_assets_ids.split(",") if brand_assets_ids else []
        
        # Create content upload record
        content_request = ContentUploadRequest(
            title=title,
            description=description,
            content_type=content_type,
            preferred_aspect_ratio=preferred_aspect_ratio,
            preferred_duration=preferred_duration,
            user_id=user_id,
            template_id=template_id,
            brand_assets_ids=brand_assets_ids_list
        )
        
        content_data = await create_item(db.content_uploads, content_request)
        content_data["file_url"] = file_url
        content_data["original_filename"] = file.filename
        content_data["s3_key"] = s3_key
        
        # Update the record with file info
        await update_item(db.content_uploads, content_data["id"], content_data)
        
        # Start content analysis in background
        # In a production environment, this would be a background task or queue
        try:
            await content_analysis_service.analyze_content(content_data["id"], s3_key)
        except Exception as analysis_error:
            logger.error(f"Error starting content analysis: {str(analysis_error)}")
            # We don't want to fail the upload if analysis fails to start
        
        return {
            "message": "Content uploaded successfully",
            "content_id": content_data["id"],
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading content: {str(e)}"
        )

@router.get("/analysis/{content_id}")
async def get_content_analysis(content_id: str):
    """
    Get the analysis results for uploaded content
    """
    logger.info(f"Getting content analysis for content ID: {content_id}")
    
    # Check if content exists
    content = await get_item(db.content_uploads, content_id)
    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"Content not found: {content_id}"
        )
    
    # Check if analysis exists
    analysis = None
    for analysis_item in db.content_analyses.values():
        if analysis_item.get("content_id") == content_id:
            analysis = analysis_item
            break
    
    if not analysis:
        # Check if analysis is in progress
        return {
            "status": "processing",
            "message": "Content analysis is in progress"
        }
    
    return analysis

@router.post("/process")
async def process_video(request: VideoProcessingRequest):
    """
    Process a video based on content analysis and template
    """
    logger.info(f"Processing video for content ID: {request.content_id}")
    
    # Check if content exists
    content = await get_item(db.content_uploads, request.content_id)
    if not content:
        raise HTTPException(
            status_code=404,
            detail=f"Content not found: {request.content_id}"
        )
    
    # Check if template exists
    template = await get_item(db.video_templates, request.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {request.template_id}"
        )
    
    try:
        # Create processing record
        processing_result = VideoProcessingResult(
            content_id=request.content_id,
            status=ProcessingStatus.PENDING
        )
        
        result_data = await create_item(db.video_processing_results, processing_result)
        
        # Start video processing in background
        # In a production environment, this would be a background task or queue
        try:
            await video_processing_service.process_video(
                result_data["id"],
                request.content_id,
                request.template_id,
                request.selected_segments,
                request.brand_assets_ids,
                request.custom_settings
            )
        except Exception as processing_error:
            logger.error(f"Error starting video processing: {str(processing_error)}")
            # Update status to failed
            await update_item(
                db.video_processing_results,
                result_data["id"],
                {"status": ProcessingStatus.FAILED, "error_message": str(processing_error)}
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error processing video: {str(processing_error)}"
            )
        
        return {
            "message": "Video processing started",
            "processing_id": result_data["id"],
            "status": result_data["status"]
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )

@router.get("/processing/{processing_id}")
async def get_processing_status(processing_id: str):
    """
    Get the status of video processing
    """
    logger.info(f"Getting processing status for ID: {processing_id}")
    
    # Check if processing record exists
    result = await get_item(db.video_processing_results, processing_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Processing record not found: {processing_id}"
        )
    
    return result

@router.get("/templates")
async def get_templates(
    content_type: Optional[str] = Query(None),
    aspect_ratio: Optional[str] = Query(None)
):
    """
    Get available video templates, optionally filtered by content type and aspect ratio
    """
    logger.info("Getting video templates")
    
    templates = list(db.video_templates.values())
    
    # Filter by content type if provided
    if content_type:
        templates = [t for t in templates if content_type in t.get("suitable_content_types", [])]
    
    # Filter by aspect ratio if provided
    if aspect_ratio:
        templates = [t for t in templates if t.get("aspect_ratio") == aspect_ratio]
    
    return {"templates": templates}

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get a specific video template
    """
    logger.info(f"Getting template ID: {template_id}")
    
    template = await get_item(db.video_templates, template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {template_id}"
        )
    
    return template
