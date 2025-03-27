import logging
import json
import boto3
import uuid
from typing import Dict, Any, Optional, List
from ..config import settings
from ..database import db, create_item, get_item, update_item

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class LambdaService:
    def __init__(self):
        self.lambda_client = None
        self.initialized = False
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize AWS Lambda client"""
        try:
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                self.lambda_client = boto3.client(
                    'lambda',
                    region_name=settings.aws_region,
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key
                )
                self.initialized = True
                logger.info("AWS Lambda client initialized successfully")
            else:
                logger.warning("AWS credentials not provided, Lambda operations will be simulated")
                self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing AWS Lambda client: {str(e)}")
            self.initialized = False
    
    async def predict_engagement(
        self,
        content_id: str,
        segments: List[Dict[str, Any]],
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict engagement potential using AWS Lambda function.
        
        Args:
            content_id: ID of the content
            segments: List of content segments
            content_type: Type of content
            metadata: Additional metadata (optional)
            
        Returns:
            Engagement prediction result
        """
        logger.info(f"Predicting engagement for content ID: {content_id}")
        
        try:
            # Prepare payload for Lambda function
            payload = {
                "content_id": content_id,
                "segments": segments,
                "content_type": content_type,
                "metadata": metadata or {}
            }
            
            if self.initialized and self.lambda_client:
                # Invoke Lambda function
                response = self.lambda_client.invoke(
                    FunctionName=settings.engagement_prediction_lambda,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
                
                # Parse response
                response_payload = json.loads(response['Payload'].read().decode())
                
                logger.info(f"Engagement prediction completed for content ID: {content_id}")
                
                return {
                    "content_id": content_id,
                    "prediction": response_payload.get("prediction", 0.0),
                    "confidence": response_payload.get("confidence", 0.0),
                    "factors": response_payload.get("factors", []),
                    "success": True
                }
            else:
                # Simulate engagement prediction for development
                logger.info(f"Simulating engagement prediction")
                
                # Calculate simulated prediction based on content type and segments
                prediction = self._simulate_engagement_prediction(segments, content_type)
                
                return {
                    "content_id": content_id,
                    "prediction": prediction["score"],
                    "confidence": prediction["confidence"],
                    "factors": prediction["factors"],
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error predicting engagement: {str(e)}")
            return {
                "content_id": content_id,
                "prediction": 0.5,  # Default prediction
                "confidence": 0.0,
                "factors": ["Error occurred during prediction"],
                "success": False,
                "error": str(e)
            }
    
    async def train_model(
        self,
        training_data: List[Dict[str, Any]],
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Train engagement prediction model using AWS Lambda function.
        
        Args:
            training_data: List of training data samples
            model_name: Name of the model (optional)
            
        Returns:
            Training result
        """
        logger.info(f"Training engagement prediction model")
        
        try:
            # Generate model name if not provided
            if not model_name:
                model_name = f"engagement_model_{uuid.uuid4().hex[:8]}"
            
            # Prepare payload for Lambda function
            payload = {
                "action": "train",
                "model_name": model_name,
                "training_data": training_data
            }
            
            if self.initialized and self.lambda_client:
                # Invoke Lambda function
                response = self.lambda_client.invoke(
                    FunctionName=settings.model_training_lambda,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
                
                # Parse response
                response_payload = json.loads(response['Payload'].read().decode())
                
                logger.info(f"Model training completed: {model_name}")
                
                return {
                    "model_name": model_name,
                    "metrics": response_payload.get("metrics", {}),
                    "success": True
                }
            else:
                # Simulate model training for development
                logger.info(f"Simulating model training")
                
                # Simulate training metrics
                metrics = {
                    "accuracy": 0.85,
                    "precision": 0.82,
                    "recall": 0.79,
                    "f1_score": 0.80,
                    "training_time": 120.5  # seconds
                }
                
                return {
                    "model_name": model_name,
                    "metrics": metrics,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                "model_name": model_name,
                "success": False,
                "error": str(e)
            }
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a trained model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information
        """
        logger.info(f"Getting information for model: {model_name}")
        
        try:
            # Prepare payload for Lambda function
            payload = {
                "action": "get_info",
                "model_name": model_name
            }
            
            if self.initialized and self.lambda_client:
                # Invoke Lambda function
                response = self.lambda_client.invoke(
                    FunctionName=settings.model_training_lambda,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(payload)
                )
                
                # Parse response
                response_payload = json.loads(response['Payload'].read().decode())
                
                logger.info(f"Retrieved information for model: {model_name}")
                
                return {
                    "model_name": model_name,
                    "info": response_payload.get("info", {}),
                    "success": True
                }
            else:
                # Simulate model information for development
                logger.info(f"Simulating model information")
                
                # Simulate model info
                info = {
                    "created_at": "2025-03-24T12:34:56Z",
                    "last_updated": "2025-03-24T12:34:56Z",
                    "version": "1.0",
                    "framework": "TensorFlow",
                    "features": ["content_type", "segment_count", "avg_segment_duration", "keywords"],
                    "metrics": {
                        "accuracy": 0.85,
                        "precision": 0.82,
                        "recall": 0.79,
                        "f1_score": 0.80
                    }
                }
                
                return {
                    "model_name": model_name,
                    "info": info,
                    "success": True,
                    "simulated": True
                }
        except Exception as e:
            logger.error(f"Error getting model information: {str(e)}")
            return {
                "model_name": model_name,
                "success": False,
                "error": str(e)
            }
    
    def _simulate_engagement_prediction(
        self,
        segments: List[Dict[str, Any]],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Simulate engagement prediction for development.
        
        Args:
            segments: List of content segments
            content_type: Type of content
            
        Returns:
            Simulated prediction result
        """
        import random
        
        # Base prediction based on content type
        content_type_scores = {
            "educational": 0.7,
            "promotional": 0.6,
            "entertainment": 0.8,
            "tutorial": 0.75,
            "interview": 0.65,
            "presentation": 0.55
        }
        
        # Get base score for content type
        base_score = content_type_scores.get(content_type, 0.5)
        
        # Adjust score based on segments
        segment_count = len(segments)
        
        # More segments generally means more engagement potential
        segment_factor = min(segment_count / 5, 1.0) * 0.1
        
        # Calculate average importance score from segments
        avg_importance = 0.0
        if segments:
            importance_scores = [segment.get("importance_score", 0.0) for segment in segments]
            avg_importance = sum(importance_scores) / len(importance_scores)
        
        # Calculate final score
        final_score = min(base_score + segment_factor + (avg_importance * 0.2), 1.0)
        
        # Add some randomness
        final_score = min(max(final_score + random.uniform(-0.05, 0.05), 0.0), 1.0)
        
        # Generate factors that influenced the prediction
        factors = []
        
        if content_type in content_type_scores:
            factors.append(f"{content_type.capitalize()} content typically performs well")
        
        if segment_count > 3:
            factors.append("Multiple engaging segments detected")
        elif segment_count <= 1:
            factors.append("Limited number of segments may reduce engagement")
        
        if avg_importance > 0.7:
            factors.append("High-quality content segments")
        elif avg_importance < 0.4:
            factors.append("Content segments could be more impactful")
        
        # Add some generic factors
        generic_factors = [
            "Strong visual elements",
            "Clear call-to-action",
            "Trending topic relevance",
            "Optimal video length for platform",
            "Effective use of captions"
        ]
        
        # Add 1-3 generic factors
        factors.extend(random.sample(generic_factors, min(3, len(generic_factors))))
        
        return {
            "score": final_score,
            "confidence": random.uniform(0.7, 0.9),
            "factors": factors[:5]  # Limit to top 5 factors
        }

# Create global lambda service instance
lambda_service = LambdaService()
