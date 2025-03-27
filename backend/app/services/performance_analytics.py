import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import json
from ..config import settings
from ..database import db, create_item, get_item, update_item, list_items
from ..models import PerformanceMetrics

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class PerformanceAnalyticsService:
    def __init__(self):
        self.tiktok_api_key = settings.tiktok_api_key
        self.initialized = bool(self.tiktok_api_key)
        
        if not self.initialized:
            logger.warning("TikTok API key not provided, performance analytics will be simulated")
    
    async def get_video_metrics(self, video_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Performance metrics
        """
        logger.info(f"Getting video metrics for video ID: {video_id}")
        
        try:
            # Check if metrics exist in database
            for metrics in db.performance_metrics.values():
                if metrics.get("video_id") == video_id:
                    return metrics
            
            # If not found, generate simulated metrics
            if not self.initialized:
                metrics = await self._generate_simulated_metrics(video_id)
                return metrics
            
            # In a real implementation, we would call the TikTok API here
            # For now, return simulated metrics
            metrics = await self._generate_simulated_metrics(video_id)
            return metrics
        except Exception as e:
            logger.error(f"Error getting video metrics: {str(e)}")
            return {"error": f"Error getting video metrics: {str(e)}"}
    
    async def get_account_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get account-level performance metrics.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Account metrics
        """
        logger.info(f"Getting account metrics for user ID: {user_id}")
        
        try:
            # Get all videos for the user
            videos = []
            for result in db.video_processing_results.values():
                content_id = result.get("content_id")
                if content_id:
                    content = await get_item(db.content_uploads, content_id)
                    if content and content.get("user_id") == user_id:
                        videos.append(result)
            
            # Get metrics for each video
            all_metrics = []
            for video in videos:
                video_id = video.get("id")
                metrics = await self.get_video_metrics(video_id)
                if "error" not in metrics:
                    all_metrics.append(metrics)
            
            # Calculate aggregate metrics
            total_views = sum(metrics.get("views", 0) for metrics in all_metrics)
            total_likes = sum(metrics.get("likes", 0) for metrics in all_metrics)
            total_comments = sum(metrics.get("comments", 0) for metrics in all_metrics)
            total_shares = sum(metrics.get("shares", 0) for metrics in all_metrics)
            
            # Calculate averages
            num_videos = len(all_metrics) or 1  # Avoid division by zero
            avg_views = total_views / num_videos
            avg_likes = total_likes / num_videos
            avg_comments = total_comments / num_videos
            avg_shares = total_shares / num_videos
            avg_engagement = sum(metrics.get("engagement_rate", 0) for metrics in all_metrics) / num_videos
            
            # Calculate growth (simulated)
            growth_rate = random.uniform(0.05, 0.25)
            
            return {
                "user_id": user_id,
                "total_videos": len(videos),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_views": avg_views,
                "avg_likes": avg_likes,
                "avg_comments": avg_comments,
                "avg_shares": avg_shares,
                "avg_engagement_rate": avg_engagement,
                "follower_growth_rate": growth_rate,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting account metrics: {str(e)}")
            return {"error": f"Error getting account metrics: {str(e)}"}
    
    async def get_trend_analysis(self, user_id: str) -> Dict[str, Any]:
        """
        Get trend analysis for TikTok content.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Trend analysis
        """
        logger.info(f"Getting trend analysis for user ID: {user_id}")
        
        try:
            # In a real implementation, we would call the TikTok API to get trending topics
            # For now, return simulated trends
            
            # Simulated trending hashtags
            trending_hashtags = [
                {"tag": "digitalmarketing", "views": 2500000000, "growth": 0.15},
                {"tag": "contentcreator", "views": 1800000000, "growth": 0.12},
                {"tag": "socialmediatips", "views": 950000000, "growth": 0.18},
                {"tag": "businesstips", "views": 750000000, "growth": 0.09},
                {"tag": "entrepreneurlife", "views": 650000000, "growth": 0.11}
            ]
            
            # Simulated trending sounds
            trending_sounds = [
                {"name": "Original Sound - Marketing Expert", "uses": 450000, "growth": 0.22},
                {"name": "Business Growth Tips", "uses": 380000, "growth": 0.17},
                {"name": "Social Media Strategy", "uses": 320000, "growth": 0.14},
                {"name": "Content Creation Hacks", "uses": 290000, "growth": 0.19},
                {"name": "Viral Marketing Sound", "uses": 250000, "growth": 0.21}
            ]
            
            # Simulated trending effects
            trending_effects = [
                {"name": "Professional Overlay", "uses": 180000, "growth": 0.13},
                {"name": "Business Statistics", "uses": 150000, "growth": 0.16},
                {"name": "Split Screen Tutorial", "uses": 130000, "growth": 0.12},
                {"name": "Text Highlight", "uses": 120000, "growth": 0.09},
                {"name": "Zoom Transition", "uses": 100000, "growth": 0.11}
            ]
            
            # Simulated content recommendations
            content_recommendations = [
                "Short educational clips (15-30 seconds) explaining a single concept",
                "Behind-the-scenes of your business or content creation process",
                "Quick tips formatted as lists with text overlays",
                "Response videos to trending topics in your industry",
                "Before/after transformations showing results"
            ]
            
            return {
                "trending_hashtags": trending_hashtags,
                "trending_sounds": trending_sounds,
                "trending_effects": trending_effects,
                "content_recommendations": content_recommendations,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting trend analysis: {str(e)}")
            return {"error": f"Error getting trend analysis: {str(e)}"}
    
    async def generate_performance_report(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report for a date range.
        
        Args:
            user_id: ID of the user
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            Performance report
        """
        logger.info(f"Generating performance report for user ID: {user_id} from {start_date} to {end_date}")
        
        try:
            # Parse dates
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Get account metrics
            account_metrics = await self.get_account_metrics(user_id)
            
            # Get trend analysis
            trend_analysis = await self.get_trend_analysis(user_id)
            
            # Generate daily metrics (simulated)
            daily_metrics = []
            current_date = start_datetime
            
            while current_date <= end_datetime:
                date_str = current_date.date().isoformat()
                
                # Simulate metrics with some randomness but following a trend
                base_views = account_metrics.get("avg_views", 1000) * random.uniform(0.7, 1.3)
                base_likes = account_metrics.get("avg_likes", 100) * random.uniform(0.7, 1.3)
                base_comments = account_metrics.get("avg_comments", 20) * random.uniform(0.7, 1.3)
                base_shares = account_metrics.get("avg_shares", 10) * random.uniform(0.7, 1.3)
                
                # Add some growth over time
                days_from_start = (current_date - start_datetime).days
                growth_factor = 1.0 + (days_from_start * 0.01)
                
                daily_metrics.append({
                    "date": date_str,
                    "views": int(base_views * growth_factor),
                    "likes": int(base_likes * growth_factor),
                    "comments": int(base_comments * growth_factor),
                    "shares": int(base_shares * growth_factor),
                    "new_followers": int(random.uniform(5, 20) * growth_factor)
                })
                
                current_date += timedelta(days=1)
            
            # Generate top performing content
            top_content = []
            for i in range(5):  # Top 5 videos
                engagement_rate = random.uniform(0.05, 0.25)
                completion_rate = random.uniform(0.6, 0.95)
                
                top_content.append({
                    "title": f"Top Performing Video {i+1}",
                    "views": int(account_metrics.get("avg_views", 1000) * random.uniform(1.5, 3.0)),
                    "likes": int(account_metrics.get("avg_likes", 100) * random.uniform(1.5, 3.0)),
                    "comments": int(account_metrics.get("avg_comments", 20) * random.uniform(1.5, 3.0)),
                    "shares": int(account_metrics.get("avg_shares", 10) * random.uniform(1.5, 3.0)),
                    "engagement_rate": engagement_rate,
                    "completion_rate": completion_rate,
                    "key_factors": [
                        "Strong hook in first 3 seconds",
                        "Used trending hashtags",
                        "Posted at optimal time",
                        "Clear call-to-action"
                    ]
                })
            
            # Generate audience demographics (simulated)
            audience_demographics = {
                "age_groups": [
                    {"group": "18-24", "percentage": random.uniform(0.2, 0.4)},
                    {"group": "25-34", "percentage": random.uniform(0.3, 0.5)},
                    {"group": "35-44", "percentage": random.uniform(0.1, 0.3)},
                    {"group": "45+", "percentage": random.uniform(0.05, 0.15)}
                ],
                "gender": [
                    {"group": "Male", "percentage": random.uniform(0.4, 0.6)},
                    {"group": "Female", "percentage": random.uniform(0.4, 0.6)}
                ],
                "top_locations": [
                    {"location": "United States", "percentage": random.uniform(0.3, 0.5)},
                    {"location": "United Kingdom", "percentage": random.uniform(0.1, 0.2)},
                    {"location": "Canada", "percentage": random.uniform(0.05, 0.15)},
                    {"location": "Australia", "percentage": random.uniform(0.05, 0.1)},
                    {"location": "Germany", "percentage": random.uniform(0.03, 0.08)}
                ]
            }
            
            # Generate recommendations based on performance
            recommendations = [
                "Post content between 7-9 PM for maximum engagement",
                "Increase video length to 45-60 seconds for higher completion rates",
                "Use trending sounds to boost discovery",
                "Incorporate more educational content based on audience demographics",
                "Respond to comments within 1 hour to boost engagement"
            ]
            
            return {
                "user_id": user_id,
                "report_period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "account_summary": {
                    "total_videos": account_metrics.get("total_videos", 0),
                    "total_views": account_metrics.get("total_views", 0),
                    "total_likes": account_metrics.get("total_likes", 0),
                    "total_comments": account_metrics.get("total_comments", 0),
                    "total_shares": account_metrics.get("total_shares", 0),
                    "avg_engagement_rate": account_metrics.get("avg_engagement_rate", 0)
                },
                "daily_metrics": daily_metrics,
                "top_performing_content": top_content,
                "audience_demographics": audience_demographics,
                "trending_topics": {
                    "hashtags": trend_analysis.get("trending_hashtags", []),
                    "sounds": trend_analysis.get("trending_sounds", [])
                },
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return {"error": f"Error generating performance report: {str(e)}"}
    
    async def _generate_simulated_metrics(self, video_id: str) -> Dict[str, Any]:
        """
        Generate simulated performance metrics for a video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Simulated metrics
        """
        # Get the video processing result
        video = await get_item(db.video_processing_results, video_id)
        
        # Generate random metrics
        views = random.randint(1000, 10000)
        likes = int(views * random.uniform(0.05, 0.15))
        comments = int(views * random.uniform(0.01, 0.05))
        shares = int(views * random.uniform(0.005, 0.02))
        avg_watch_time = random.uniform(10.0, 45.0)
        completion_rate = random.uniform(0.4, 0.8)
        
        # Calculate engagement rate
        engagement_rate = (likes + comments + shares) / views if views > 0 else 0
        
        # Create metrics object
        metrics = PerformanceMetrics(
            video_id=video_id,
            views=views,
            likes=likes,
            comments=comments,
            shares=shares,
            average_watch_time=avg_watch_time,
            completion_rate=completion_rate,
            engagement_rate=engagement_rate,
            click_through_rate=random.uniform(0.01, 0.05) if random.random() > 0.5 else None
        )
        
        # Save to database
        metrics_data = await create_item(db.performance_metrics, metrics)
        
        return metrics_data

# Create global performance analytics service instance
performance_analytics_service = PerformanceAnalyticsService()
