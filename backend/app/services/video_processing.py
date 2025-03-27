import logging
import os
import tempfile
import subprocess
import json
import uuid
from typing import List, Dict, Any, Optional
from ..config import settings
from ..database import db, create_item, get_item, update_item
from ..models import VideoProcessingResult, ProcessingStatus
from .storage import storage_service
from .content_analysis import content_analysis_service

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class VideoProcessingService:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.temp_dir = tempfile.gettempdir()
        logger.info(f"Video processing service initialized with FFMPEG: {self.ffmpeg_path}")
    
    def _find_ffmpeg(self) -> str:
        """Find the FFMPEG binary path"""
        try:
            # Try to find ffmpeg in PATH
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            
            # Check common locations
            common_paths = [
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "/opt/homebrew/bin/ffmpeg"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
            
            logger.warning("FFMPEG not found, video processing will be simulated")
            return "ffmpeg"  # Default fallback
        except Exception as e:
            logger.error(f"Error finding FFMPEG: {str(e)}")
            return "ffmpeg"  # Default fallback
    
    async def process_video(
        self,
        processing_id: str,
        content_id: str,
        template_id: str,
        selected_segments: List[str],
        brand_assets_ids: List[str],
        custom_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a video based on content analysis and template.
        
        Args:
            processing_id: ID of the processing record
            content_id: ID of the content upload record
            template_id: ID of the template to use
            selected_segments: List of segment IDs to include
            brand_assets_ids: List of brand asset IDs to include
            custom_settings: Custom settings for processing
            
        Returns:
            Processing result
        """
        logger.info(f"Processing video for content ID: {content_id} with template ID: {template_id}")
        
        try:
            # Update processing status to analyzing
            await update_item(
                db.video_processing_results,
                processing_id,
                {"status": ProcessingStatus.ANALYZING}
            )
            
            # Get content upload record
            content = await get_item(db.content_uploads, content_id)
            if not content:
                logger.error(f"Content not found: {content_id}")
                await self._update_processing_failed(processing_id, "Content not found")
                return {"error": "Content not found"}
            
            # Get template
            template = await get_item(db.video_templates, template_id)
            if not template:
                logger.error(f"Template not found: {template_id}")
                await self._update_processing_failed(processing_id, "Template not found")
                return {"error": "Template not found"}
            
            # Get content analysis
            analysis = None
            for analysis_item in db.content_analyses.values():
                if analysis_item.get("content_id") == content_id:
                    analysis = analysis_item
                    break
            
            if not analysis:
                logger.error(f"Content analysis not found for content ID: {content_id}")
                await self._update_processing_failed(processing_id, "Content analysis not found")
                return {"error": "Content analysis not found"}
            
            # Update processing status to processing
            await update_item(
                db.video_processing_results,
                processing_id,
                {"status": ProcessingStatus.PROCESSING}
            )
            
            # Get brand assets
            brand_assets = []
            for asset_id in brand_assets_ids:
                asset = await get_item(db.brand_assets, asset_id)
                if asset:
                    brand_assets.append(asset)
            
            # Process the video
            result = await self._process_video_with_template(
                content,
                template,
                analysis,
                selected_segments,
                brand_assets,
                custom_settings
            )
            
            if result.get("error"):
                logger.error(f"Error processing video: {result.get('error')}")
                await self._update_processing_failed(processing_id, result.get("error"))
                return result
            
            # Update processing record with result
            await update_item(
                db.video_processing_results,
                processing_id,
                {
                    "status": ProcessingStatus.COMPLETED,
                    "preview_url": result.get("preview_url"),
                    "final_url": result.get("final_url")
                }
            )
            
            logger.info(f"Video processing completed for content ID: {content_id}")
            
            # Get updated processing record
            updated_record = await get_item(db.video_processing_results, processing_id)
            return updated_record
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            await self._update_processing_failed(processing_id, str(e))
            return {"error": f"Error processing video: {str(e)}"}
    
    async def _update_processing_failed(self, processing_id: str, error_message: str) -> None:
        """
        Update processing record with failed status.
        
        Args:
            processing_id: ID of the processing record
            error_message: Error message
        """
        await update_item(
            db.video_processing_results,
            processing_id,
            {
                "status": ProcessingStatus.FAILED,
                "error_message": error_message
            }
        )
    
    async def _process_video_with_template(
        self,
        content: Dict[str, Any],
        template: Dict[str, Any],
        analysis: Dict[str, Any],
        selected_segments: List[str],
        brand_assets: List[Dict[str, Any]],
        custom_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a video with a template.
        
        Args:
            content: Content upload record
            template: Template record
            analysis: Content analysis record
            selected_segments: List of segment IDs to include
            brand_assets: List of brand assets
            custom_settings: Custom settings for processing
            
        Returns:
            Processing result
        """
        logger.info(f"Processing video with template: {template.get('name')}")
        
        try:
            # Create a unique output filename
            output_filename = f"{uuid.uuid4()}.{settings.output_video_format}"
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # Get the original video file
            original_file_path = None
            s3_key = content.get("s3_key")
            
            if s3_key:
                # Download the original video
                temp_input_file = os.path.join(self.temp_dir, f"input_{uuid.uuid4()}.mp4")
                download_success = await storage_service.download_file(s3_key, temp_input_file)
                
                if download_success:
                    original_file_path = temp_input_file
                else:
                    logger.warning(f"Failed to download original video, using simulated processing")
            
            # Check if we have FFMPEG and the original file
            if self.ffmpeg_path and original_file_path and os.path.exists(original_file_path):
                logger.info(f"Using FFMPEG to process video")
                
                # Get segments from analysis
                segments = analysis.get("segments", [])
                
                # Filter segments if selected_segments is provided
                if selected_segments and len(selected_segments) > 0:
                    # In a real implementation, we would filter by segment ID
                    # For this simulation, we'll just take the first few segments
                    segments = segments[:len(selected_segments)]
                
                # Create a temporary file for the segment list
                segments_file = os.path.join(self.temp_dir, f"segments_{uuid.uuid4()}.txt")
                
                with open(segments_file, "w") as f:
                    for i, segment in enumerate(segments):
                        start_time = segment.get("start_time", 0)
                        end_time = segment.get("end_time", 0)
                        f.write(f"file '{original_file_path}'\n")
                        f.write(f"inpoint {start_time}\n")
                        f.write(f"outpoint {end_time}\n")
                
                # Use FFMPEG to concatenate segments
                concat_output = os.path.join(self.temp_dir, f"concat_{uuid.uuid4()}.mp4")
                
                ffmpeg_concat_cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", segments_file,
                    "-c", "copy",
                    concat_output
                ]
                
                logger.info(f"Running FFMPEG concat command: {' '.join(ffmpeg_concat_cmd)}")
                
                try:
                    subprocess.run(ffmpeg_concat_cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"FFMPEG concat error: {e.stderr.decode() if e.stderr else str(e)}")
                    return {"error": "Error concatenating video segments"}
                
                # Apply template effects
                aspect_ratio = template.get("aspect_ratio", "9:16")
                
                # Parse aspect ratio
                if aspect_ratio == "9:16":
                    width, height = 1080, 1920
                elif aspect_ratio == "1:1":
                    width, height = 1080, 1080
                elif aspect_ratio == "16:9":
                    width, height = 1920, 1080
                else:
                    width, height = 1080, 1920  # Default to 9:16
                
                # Apply template effects with FFMPEG
                ffmpeg_template_cmd = [
                    self.ffmpeg_path,
                    "-i", concat_output,
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    output_path
                ]
                
                logger.info(f"Running FFMPEG template command: {' '.join(ffmpeg_template_cmd)}")
                
                try:
                    subprocess.run(ffmpeg_template_cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    logger.error(f"FFMPEG template error: {e.stderr.decode() if e.stderr else str(e)}")
                    return {"error": "Error applying template to video"}
                
                # Clean up temporary files
                if os.path.exists(segments_file):
                    os.remove(segments_file)
                
                if os.path.exists(concat_output):
                    os.remove(concat_output)
                
                # Upload the processed video to S3
                output_s3_key = f"processed/{content.get('user_id')}/{output_filename}"
                
                output_url = await storage_service.upload_file(
                    output_path,
                    output_s3_key,
                    content_type=f"video/{settings.output_video_format}"
                )
                
                # Clean up the output file
                if os.path.exists(output_path):
                    os.remove(output_path)
                
                # Clean up the input file
                if os.path.exists(original_file_path):
                    os.remove(original_file_path)
                
                return {
                    "preview_url": output_url,
                    "final_url": output_url
                }
            else:
                # Simulate video processing for development
                logger.info(f"Simulating video processing")
                
                # Create a simulated output URL
                output_s3_key = f"processed/{content.get('user_id')}/{output_filename}"
                output_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{output_s3_key}"
                
                # Simulate processing delay
                await self._simulate_processing_delay()
                
                return {
                    "preview_url": output_url,
                    "final_url": output_url
                }
        except Exception as e:
            logger.error(f"Error in _process_video_with_template: {str(e)}")
            return {"error": f"Error processing video: {str(e)}"}
    
    async def _simulate_processing_delay(self) -> None:
        """Simulate a processing delay for development"""
        import asyncio
        await asyncio.sleep(2)  # Simulate a 2-second processing delay
    
    async def get_processing_status(self, processing_id: str) -> Dict[str, Any]:
        """
        Get the status of video processing.
        
        Args:
            processing_id: ID of the processing record
            
        Returns:
            Processing status
        """
        logger.info(f"Getting processing status for ID: {processing_id}")
        
        try:
            # Get processing record
            result = await get_item(db.video_processing_results, processing_id)
            if not result:
                return {"error": "Processing record not found"}
            
            return result
        except Exception as e:
            logger.error(f"Error getting processing status: {str(e)}")
            return {"error": f"Error getting processing status: {str(e)}"}

# Create global video processing service instance
video_processing_service = VideoProcessingService()
