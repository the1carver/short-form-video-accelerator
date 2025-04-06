"""
PostgreSQL database configuration for Railway deployment
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/short_form_video_accelerator")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    videos = relationship("Video", back_populates="user")
    clips = relationship("Clip", back_populates="user")
    
    preferences = Column(JSON, default={})

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    url = Column(String)
    thumbnail_url = Column(String, nullable=True)
    duration = Column(Float)
    status = Column(String)  # uploaded, processing, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    scenes = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="videos")
    clips = relationship("Clip", back_populates="video")

class Clip(Base):
    __tablename__ = "clips"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    video_id = Column(String, ForeignKey("videos.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    start_time = Column(Float)
    end_time = Column(Float)
    url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String)  # processing, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    aspect_ratio = Column(String, default="9:16")
    template_id = Column(String, ForeignKey("templates.id"), nullable=True)
    settings = Column(JSON, default={})
    
    user = relationship("User", back_populates="clips")
    video = relationship("Video", back_populates="clips")
    template = relationship("Template", back_populates="clips")

class Template(Base):
    __tablename__ = "templates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    settings = Column(JSON, default={})
    
    clips = relationship("Clip", back_populates="template")

def init_db():
    """Initialize the database by creating all tables"""
    try:
        logger.info("Creating PostgreSQL database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating PostgreSQL database tables: {e}")
        raise

def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
