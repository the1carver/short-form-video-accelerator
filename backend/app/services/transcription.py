import logging
import os
import tempfile
from typing import Dict, Any, Optional
import openai
from ..config import settings
from .storage import storage_service

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self.openai_client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize OpenAI client for transcription"""
        try:
            # Use the OpenAI API key from settings
            api_key = settings.openai_api_key or settings.openai_whisper_api_key
            
            if api_key:
                openai.api_key = api_key
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully for transcription")
            else:
                logger.warning("OpenAI API key not provided, transcription will be simulated")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: "en")
            
        Returns:
            Transcription result
        """
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        try:
            if self.openai_client and os.path.exists(audio_file_path):
                # Use OpenAI Whisper API for transcription
                with open(audio_file_path, "rb") as audio_file:
                    response = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language
                    )
                
                logger.info(f"Transcription completed successfully")
                return {
                    "text": response.text,
                    "success": True
                }
            else:
                # Simulate transcription for development
                logger.info(f"Simulating audio transcription")
                
                # Generate a simulated transcript based on the filename
                filename = os.path.basename(audio_file_path)
                simulated_transcript = self._generate_simulated_transcript(filename)
                
                return {
                    "text": simulated_transcript,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    async def transcribe_video(self, video_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Extract audio from video and transcribe it.
        
        Args:
            video_file_path: Path to the video file
            language: Language code (default: "en")
            
        Returns:
            Transcription result
        """
        logger.info(f"Transcribing video file: {video_file_path}")
        
        try:
            # Extract audio from video using ffmpeg
            audio_file_path = await self._extract_audio_from_video(video_file_path)
            
            if audio_file_path:
                # Transcribe the extracted audio
                result = await self.transcribe_audio(audio_file_path, language)
                
                # Clean up the temporary audio file
                try:
                    os.remove(audio_file_path)
                except Exception as e:
                    logger.warning(f"Error removing temporary audio file: {str(e)}")
                
                return result
            else:
                # Simulate transcription if audio extraction failed
                logger.info(f"Simulating video transcription (audio extraction failed)")
                
                # Generate a simulated transcript based on the filename
                filename = os.path.basename(video_file_path)
                simulated_transcript = self._generate_simulated_transcript(filename)
                
                return {
                    "text": simulated_transcript,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error transcribing video: {str(e)}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    async def transcribe_from_s3(self, s3_key: str, is_video: bool = True, language: str = "en") -> Dict[str, Any]:
        """
        Download file from S3 and transcribe it.
        
        Args:
            s3_key: S3 key of the file
            is_video: Whether the file is a video (default: True)
            language: Language code (default: "en")
            
        Returns:
            Transcription result
        """
        logger.info(f"Transcribing file from S3: {s3_key}")
        
        try:
            # Create a temporary file
            file_extension = ".mp4" if is_video else ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file_path = temp_file.name
            
            # Download the file from S3
            download_success = await storage_service.download_file(s3_key, temp_file_path)
            
            if download_success:
                # Transcribe the file
                if is_video:
                    result = await self.transcribe_video(temp_file_path, language)
                else:
                    result = await self.transcribe_audio(temp_file_path, language)
                
                # Clean up the temporary file
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    logger.warning(f"Error removing temporary file: {str(e)}")
                
                return result
            else:
                # Simulate transcription if download failed
                logger.info(f"Simulating transcription (S3 download failed)")
                
                # Generate a simulated transcript based on the S3 key
                simulated_transcript = self._generate_simulated_transcript(s3_key)
                
                return {
                    "text": simulated_transcript,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error transcribing from S3: {str(e)}")
            return {
                "text": "",
                "success": False,
                "error": str(e)
            }
    
    async def _extract_audio_from_video(self, video_file_path: str) -> Optional[str]:
        """
        Extract audio from video using ffmpeg.
        
        Args:
            video_file_path: Path to the video file
            
        Returns:
            Path to the extracted audio file or None if failed
        """
        logger.info(f"Extracting audio from video: {video_file_path}")
        
        try:
            # Find ffmpeg
            ffmpeg_path = self._find_ffmpeg()
            
            if not ffmpeg_path:
                logger.warning("FFMPEG not found, audio extraction will be simulated")
                return None
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                audio_file_path = temp_file.name
            
            # Use ffmpeg to extract audio
            import subprocess
            
            command = [
                ffmpeg_path,
                "-i", video_file_path,
                "-q:a", "0",
                "-map", "a",
                "-f", "mp3",
                audio_file_path
            ]
            
            process = subprocess.run(command, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"FFMPEG error: {process.stderr}")
                return None
            
            logger.info(f"Audio extracted successfully to: {audio_file_path}")
            return audio_file_path
        except Exception as e:
            logger.error(f"Error extracting audio from video: {str(e)}")
            return None
    
    def _find_ffmpeg(self) -> Optional[str]:
        """
        Find the FFMPEG binary path.
        
        Returns:
            Path to ffmpeg or None if not found
        """
        try:
            # Try to find ffmpeg in PATH
            import subprocess
            
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
            
            return None
        except Exception as e:
            logger.error(f"Error finding FFMPEG: {str(e)}")
            return None
    
    def _generate_simulated_transcript(self, filename: str) -> str:
        """
        Generate a simulated transcript based on the filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            Simulated transcript
        """
        # Extract the base filename without extension
        base_filename = os.path.splitext(os.path.basename(filename))[0].lower()
        
        # Generate a simulated transcript based on common content types
        if "tutorial" in base_filename or "how" in base_filename:
            return "Welcome to this tutorial. Today I'm going to show you step by step how to optimize your content for TikTok. First, we'll look at the key elements that make TikTok videos successful. Then, we'll explore the best practices for editing and formatting your videos to maximize engagement."
        elif "interview" in base_filename:
            return "Interviewer: Thank you for joining us today. Can you tell us about your experience with short-form video content? Guest: Absolutely. I've been creating content for platforms like TikTok for about three years now. What I've found is that authenticity is key. Viewers can tell when you're being genuine versus when you're just trying to follow trends."
        elif "promo" in base_filename or "ad" in base_filename:
            return "Introducing our new Digital Frontier Short-Form Video Accelerator. Transform your long-form content into engaging TikTok videos in minutes, not hours. Our AI-powered platform analyzes your content, identifies the most engaging segments, and automatically generates optimized videos ready for TikTok. Try it today and see your engagement soar."
        elif "presentation" in base_filename:
            return "Today's presentation covers the latest trends in short-form video marketing. As you can see from this slide, engagement rates for videos under 30 seconds have increased by 45% in the last year. The next slide shows the key elements that contribute to viral content: a strong hook in the first 3 seconds, clear value proposition, and a compelling call to action."
        else:
            return "This is a simulated transcript for demonstration purposes. In a production environment, this would be the actual transcription of your audio or video content. The transcription would capture all spoken words, identify speakers when possible, and include timestamps for longer content."

# Create global transcription service instance
transcription_service = TranscriptionService()
