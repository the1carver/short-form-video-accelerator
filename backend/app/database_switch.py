"""
Database switch module to toggle between in-memory and PostgreSQL databases
"""
import os
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() in ("true", "1", "t", "yes")

def get_db_implementation() -> tuple[Callable[[], Any], Callable[[], None]]:
    """
    Returns the appropriate database implementation based on configuration
    
    Returns:
        tuple: (get_db function, init_db function)
    """
    if USE_POSTGRES:
        logger.info("Using PostgreSQL database")
        try:
            from app.database_postgres import get_db, init_db
            return get_db, init_db
        except ImportError as e:
            logger.error(f"Error importing PostgreSQL database module: {e}")
            logger.warning("Falling back to in-memory database")
            from app.database import get_db, init_db
            return get_db, init_db
    else:
        logger.info("Using in-memory database")
        from app.database import get_db, init_db
        return get_db, init_db
