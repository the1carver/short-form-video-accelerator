from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timedelta
import logging
from ..config import settings
from ..services.performance_analytics import performance_analytics_service

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

from ..services.auth import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/video/{video_id}")
async def get_video_metrics(video_id: str):
    """
    Get performance metrics for a specific video
    """
    logger.info(f"Getting video metrics for video ID: {video_id}")
    
    try:
        metrics = await performance_analytics_service.get_video_metrics(video_id)
        return metrics
    except Exception as e:
        logger.error(f"Error getting video metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting video metrics: {str(e)}"
        )

@router.get("/account/{user_id}")
async def get_account_metrics(user_id: str):
    """
    Get account-level performance metrics
    """
    logger.info(f"Getting account metrics for user ID: {user_id}")
    
    try:
        metrics = await performance_analytics_service.get_account_metrics(user_id)
        return metrics
    except Exception as e:
        logger.error(f"Error getting account metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting account metrics: {str(e)}"
        )

@router.get("/trends/{user_id}")
async def get_trend_analysis(user_id: str):
    """
    Get trend analysis for TikTok content
    """
    logger.info(f"Getting trend analysis for user ID: {user_id}")
    
    try:
        trends = await performance_analytics_service.get_trend_analysis(user_id)
        return trends
    except Exception as e:
        logger.error(f"Error getting trend analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting trend analysis: {str(e)}"
        )

@router.get("/report/{user_id}")
async def generate_performance_report(
    user_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Generate a comprehensive performance report for a date range
    """
    logger.info(f"Generating performance report for user ID: {user_id}")
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
    
    if not end_date:
        end_date = datetime.utcnow().isoformat()
    
    try:
        report = await performance_analytics_service.generate_performance_report(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        return report
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating performance report: {str(e)}"
        )
