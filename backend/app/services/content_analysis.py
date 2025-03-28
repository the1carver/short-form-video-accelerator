import logging
import json
import os
import tempfile
from typing import List, Dict, Any, Optional
import openai
from google.cloud import videointelligence_v1 as videointelligence
from ..config import settings
from ..database import db, create_item, get_item, update_item
from ..models import ContentAnalysisResult, VideoSegment, ContentType
from .storage import storage_service

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class ContentAnalysisService:
    def __init__(self):
        self.openai_client = None
        self.video_intelligence_client = None
        self.initialize_clients()
    
    def initialize_clients(self):
        """Initialize API clients for content analysis"""
        try:
            # Initialize OpenAI client
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not provided, text analysis will be simulated")
            
            # Initialize Google Video Intelligence client
            if settings.enable_google_video_intelligence and os.path.exists(settings.google_application_credentials):
                try:
                    self.video_intelligence_client = videointelligence.VideoIntelligenceServiceClient()
                    logger.info("Google Video Intelligence client initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Google Video Intelligence client: {str(e)}")
            else:
                logger.warning("Google Video Intelligence not enabled or credentials not found, video analysis will be simulated")
        except Exception as e:
            logger.error(f"Error in initialize_clients: {str(e)}")
    
    async def analyze_content(self, content_id: str, s3_key: str) -> Dict[str, Any]:
        """
        Analyze video content to identify segments, keywords, and engagement potential.
        
        Args:
            content_id: ID of the content upload record
            s3_key: S3 key of the uploaded video
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing content: {content_id}")
        
        try:
            # Get content upload record
            content = await get_item(db.content_uploads, content_id)
            if not content:
                logger.error(f"Content not found: {content_id}")
                return {"error": "Content not found"}
            
            # Download video for analysis if needed
            video_path = None
            if self.video_intelligence_client:
                # For Google Video Intelligence, we need the local file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                    video_path = temp_file.name
                
                download_success = await storage_service.download_file(s3_key, video_path)
                if not download_success:
                    logger.warning(f"Failed to download video for analysis, using S3 URL")
                    video_path = None
            
            # Analyze video content
            segments = await self._analyze_video_segments(content, video_path, s3_key)
            
            # Extract keywords and summary
            keywords, summary = await self._extract_keywords_and_summary(segments, content.get("content_type", ""))
            
            # Recommend templates based on content type and segments
            recommended_templates = await self._recommend_templates(content.get("content_type", ""), segments)
            
            # Predict engagement potential
            engagement_prediction = await self._predict_engagement(segments, content.get("content_type", ""))
            
            # Create analysis result
            analysis_result = ContentAnalysisResult(
                content_id=content_id,
                segments=segments,
                keywords=keywords,
                summary=summary,
                recommended_templates=recommended_templates,
                engagement_prediction=engagement_prediction
            )
            
            # Save analysis result
            result_data = await create_item(db.content_analyses, analysis_result)
            
            # Clean up temporary file if created
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
            
            logger.info(f"Content analysis completed for: {content_id}")
            return result_data
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            # Create a minimal analysis result with error information
            try:
                error_result = ContentAnalysisResult(
                    content_id=content_id,
                    segments=[],
                    keywords=[],
                    summary=f"Error analyzing content: {str(e)}",
                    recommended_templates=[],
                    engagement_prediction=0.0
                )
                result_data = await create_item(db.content_analyses, error_result)
                return result_data
            except Exception as inner_e:
                logger.error(f"Error creating error analysis result: {str(inner_e)}")
                return {"error": f"Error analyzing content: {str(e)}"}
    
    async def _analyze_video_segments(self, content: Dict[str, Any], video_path: Optional[str], s3_key: str) -> List[Dict[str, Any]]:
        """
        Analyze video to identify segments.
        
        Args:
            content: Content upload record
            video_path: Local path to video file (if available)
            s3_key: S3 key of the uploaded video
            
        Returns:
            List of video segments
        """
        logger.info(f"Analyzing video segments for content: {content.get('id')}")
        
        segments = []
        
        try:
            if self.video_intelligence_client and video_path and os.path.exists(video_path):
                # Use Google Video Intelligence API for segment detection
                logger.info(f"Using Google Video Intelligence API for segment analysis")
                
                features = [
                    videointelligence.Feature.SPEECH_TRANSCRIPTION,
                    videointelligence.Feature.SHOT_CHANGE_DETECTION,
                    videointelligence.Feature.LABEL_DETECTION
                ]
                
                # Configure speech transcription
                speech_config = videointelligence.SpeechTranscriptionConfig(
                    language_code="en-US",
                    enable_automatic_punctuation=True,
                    enable_speaker_diarization=False,
                    max_alternatives=1
                )
                
                video_context = videointelligence.VideoContext(
                    speech_transcription_config=speech_config
                )
                
                # Start the asynchronous request
                with open(video_path, "rb") as file:
                    input_content = file.read()
                
                operation = self.video_intelligence_client.annotate_video(
                    request={
                        "features": features,
                        "input_content": input_content,
                        "video_context": video_context
                    }
                )
                
                logger.info(f"Waiting for Google Video Intelligence API operation to complete")
                result = operation.result(timeout=300)  # 5-minute timeout
                
                # Process shot changes to identify segments
                shot_changes = result.annotation_results[0].shot_annotations
                
                for i, shot in enumerate(shot_changes):
                    start_time = shot.start_time_offset.seconds + shot.start_time_offset.microseconds / 1000000
                    end_time = shot.end_time_offset.seconds + shot.end_time_offset.microseconds / 1000000
                    
                    # Extract transcript for this segment
                    transcript = ""
                    for speech_transcription in result.annotation_results[0].speech_transcriptions:
                        for alternative in speech_transcription.alternatives:
                            for word_info in alternative.words:
                                word_start = word_info.start_time.seconds + word_info.start_time.microseconds / 1000000
                                word_end = word_info.end_time.seconds + word_info.end_time.microseconds / 1000000
                                
                                if word_start >= start_time and word_end <= end_time:
                                    transcript += word_info.word + " "
                    
                    # Extract keywords from labels
                    keywords = []
                    for label in result.annotation_results[0].segment_label_annotations:
                        for segment in label.segments:
                            segment_start = segment.segment.start_time_offset.seconds + segment.segment.start_time_offset.microseconds / 1000000
                            segment_end = segment.segment.end_time_offset.seconds + segment.segment.end_time_offset.microseconds / 1000000
                            
                            if segment_start >= start_time and segment_end <= end_time:
                                keywords.append(label.entity.description)
                    
                    # Calculate importance score based on labels and duration
                    importance_score = min(len(keywords) * 0.1 + (end_time - start_time) * 0.05, 1.0)
                    
                    # Calculate engagement prediction (placeholder)
                    engagement_prediction = min(importance_score + 0.2, 1.0)
                    
                    segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "transcript": transcript.strip(),
                        "keywords": keywords[:10],  # Limit to top 10 keywords
                        "importance_score": importance_score,
                        "engagement_prediction": engagement_prediction
                    })
            else:
                # Simulate video analysis for development
                logger.info(f"Simulating video segment analysis")
                
                # Create simulated segments based on content type
                content_type = content.get("content_type", "educational")
                
                if content_type == "educational":
                    segments = [
                        {
                            "start_time": 0.0,
                            "end_time": 30.0,
                            "transcript": "Welcome to this educational video about digital marketing strategies.",
                            "keywords": ["introduction", "digital marketing", "overview"],
                            "importance_score": 0.8,
                            "engagement_prediction": 0.75
                        },
                        {
                            "start_time": 30.0,
                            "end_time": 90.0,
                            "transcript": "The first strategy we'll discuss is content marketing and how it drives organic traffic.",
                            "keywords": ["content marketing", "organic traffic", "strategy"],
                            "importance_score": 0.9,
                            "engagement_prediction": 0.85
                        },
                        {
                            "start_time": 90.0,
                            "end_time": 150.0,
                            "transcript": "Social media platforms like TikTok require specific optimization techniques.",
                            "keywords": ["social media", "TikTok", "optimization"],
                            "importance_score": 0.95,
                            "engagement_prediction": 0.9
                        }
                    ]
                elif content_type == "promotional":
                    segments = [
                        {
                            "start_time": 0.0,
                            "end_time": 15.0,
                            "transcript": "Introducing our new product that will revolutionize your workflow.",
                            "keywords": ["product launch", "innovation", "workflow"],
                            "importance_score": 0.9,
                            "engagement_prediction": 0.85
                        },
                        {
                            "start_time": 15.0,
                            "end_time": 45.0,
                            "transcript": "Our customers have reported a 50% increase in productivity after using our solution.",
                            "keywords": ["testimonial", "productivity", "results"],
                            "importance_score": 0.85,
                            "engagement_prediction": 0.8
                        }
                    ]
                else:
                    segments = [
                        {
                            "start_time": 0.0,
                            "end_time": 60.0,
                            "transcript": "This is a simulated transcript for the video content.",
                            "keywords": ["simulated", "content", "analysis"],
                            "importance_score": 0.7,
                            "engagement_prediction": 0.65
                        }
                    ]
        except Exception as e:
            logger.error(f"Error in _analyze_video_segments: {str(e)}")
            # Return a minimal segment as fallback
            segments = [
                {
                    "start_time": 0.0,
                    "end_time": 60.0,
                    "transcript": "Error analyzing video segments.",
                    "keywords": ["error"],
                    "importance_score": 0.5,
                    "engagement_prediction": 0.5
                }
            ]
        
        return segments
    
    async def _extract_keywords_and_summary(self, segments: List[Dict[str, Any]], content_type: str) -> tuple:
        """
        Extract keywords and generate summary from video segments.
        
        Args:
            segments: List of video segments
            content_type: Type of content
            
        Returns:
            Tuple of (keywords, summary)
        """
        logger.info(f"Extracting keywords and summary")
        
        # Combine all transcripts
        combined_transcript = " ".join([segment.get("transcript", "") for segment in segments])
        
        try:
            if self.openai_client and combined_transcript:
                # Use OpenAI for keyword extraction and summarization
                logger.info(f"Using OpenAI for keyword extraction and summarization")
                
                prompt = f"""
                Analyze the following video transcript and:
                1. Extract the top 10 most important keywords or phrases
                2. Create a concise summary (max 100 words)
                
                Content type: {content_type}
                
                Transcript:
                {combined_transcript}
                
                Format your response as JSON with 'keywords' (array) and 'summary' (string) fields.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a content analysis assistant that extracts keywords and creates summaries from video transcripts."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                # Parse the response
                try:
                    content = response.choices[0].message.content
                    result = json.loads(content)
                    keywords = result.get("keywords", [])
                    summary = result.get("summary", "")
                except Exception as parse_error:
                    logger.error(f"Error parsing OpenAI response: {str(parse_error)}")
                    # Extract keywords and summary using fallback method
                    keywords = self._extract_keywords_fallback(combined_transcript)
                    summary = self._generate_summary_fallback(combined_transcript)
            else:
                # Use fallback methods for development
                logger.info(f"Using fallback methods for keyword extraction and summarization")
                keywords = self._extract_keywords_fallback(combined_transcript)
                summary = self._generate_summary_fallback(combined_transcript)
        except Exception as e:
            logger.error(f"Error in _extract_keywords_and_summary: {str(e)}")
            # Use fallback methods
            keywords = self._extract_keywords_fallback(combined_transcript)
            summary = self._generate_summary_fallback(combined_transcript)
        
        return keywords, summary
    
    def _extract_keywords_fallback(self, text: str) -> List[str]:
        """
        Extract keywords from text using a simple fallback method.
        
        Args:
            text: Input text
            
        Returns:
            List of keywords
        """
        if not text:
            return ["no content"]
        
        # Simple keyword extraction based on word frequency
        words = text.lower().split()
        word_freq = {}
        
        # Common stop words to exclude
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "as", "of", "is", "are", "was", "were"}
        
        for word in words:
            # Clean the word
            word = word.strip(".,!?;:\"'()[]{}").lower()
            if word and len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10 keywords
        return [word for word, freq in sorted_words[:10]]
    
    def _generate_summary_fallback(self, text: str) -> str:
        """
        Generate a summary from text using a simple fallback method.
        
        Args:
            text: Input text
            
        Returns:
            Summary text
        """
        if not text:
            return "No content available for summarization."
        
        # Simple summarization by taking the first few sentences
        sentences = text.split(".")
        
        # Take first 3 sentences or fewer if not available
        summary_sentences = sentences[:min(3, len(sentences))]
        
        summary = ". ".join(summary_sentences).strip()
        
        # Limit to 100 words
        words = summary.split()
        if len(words) > 100:
            summary = " ".join(words[:100]) + "..."
        
        return summary
    
    async def _recommend_templates(self, content_type: str, segments: List[Dict[str, Any]]) -> List[str]:
        """
        Recommend video templates based on content type and segments.
        
        Args:
            content_type: Type of content
            segments: List of video segments
            
        Returns:
            List of template IDs
        """
        logger.info(f"Recommending templates for content type: {content_type}")
        
        recommended_templates = []
        
        try:
            # Get all available templates
            templates = list(db.video_templates.values())
            
            # Filter templates by content type
            matching_templates = []
            for template in templates:
                suitable_types = template.get("suitable_content_types", [])
                if content_type in suitable_types:
                    matching_templates.append(template)
            
            # If no matching templates, use all templates
            if not matching_templates:
                matching_templates = templates
            
            # Recommend up to 3 templates
            recommended_templates = [template["id"] for template in matching_templates[:3]]
        except Exception as e:
            logger.error(f"Error in _recommend_templates: {str(e)}")
        
        return recommended_templates
    
    async def _predict_engagement(self, segments: List[Dict[str, Any]], content_type: str) -> float:
        """
        Predict engagement potential for the content.
        
        Args:
            segments: List of video segments
            content_type: Type of content
            
        Returns:
            Engagement prediction score (0.0 to 1.0)
        """
        logger.info(f"Predicting engagement for content type: {content_type}")
        
        try:
            # Calculate average engagement prediction from segments
            if segments:
                segment_predictions = [segment.get("engagement_prediction", 0.0) for segment in segments]
                avg_prediction = sum(segment_predictions) / len(segment_predictions)
                
                # Apply content type modifier
                content_type_modifiers = {
                    "educational": 0.9,
                    "promotional": 1.1,
                    "entertainment": 1.2,
                    "tutorial": 0.95,
                    "interview": 0.85,
                    "presentation": 0.8
                }
                
                modifier = content_type_modifiers.get(content_type, 1.0)
                
                # Calculate final prediction (capped between 0.0 and 1.0)
                prediction = min(max(avg_prediction * modifier, 0.0), 1.0)
                return prediction
            else:
                return 0.5  # Default prediction
        except Exception as e:
            logger.error(f"Error in _predict_engagement: {str(e)}")
            return 0.5  # Default prediction on error
    
    async def get_analysis(self, content_id: str) -> Dict[str, Any]:
        """
        Get content analysis results.
        
        Args:
            content_id: ID of the content
            
        Returns:
            Analysis results
        """
        logger.info(f"Getting analysis for content ID: {content_id}")
        
        try:
            # Find analysis by content ID
            for analysis in db.content_analyses.values():
                if analysis.get("content_id") == content_id:
                    return analysis
            
            return {"error": "Analysis not found"}
        except Exception as e:
            logger.error(f"Error getting analysis: {str(e)}")
            return {"error": f"Error getting analysis: {str(e)}"}

# Create global content analysis service instance
content_analysis_service = ContentAnalysisService()
