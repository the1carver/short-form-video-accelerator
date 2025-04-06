"""
Database migration script to create tables in PostgreSQL
"""
import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create database tables"""
    try:
        from app.database_postgres import init_db
        
        init_db()
        
        logger.info("Database tables created successfully")
        return 0
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
