from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Car(Base):
    
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False, index=True)  
    model = Column(String, nullable=False, index=True)  
    year = Column(Integer, nullable=False, index=True)  
    price = Column(Float, nullable=False)  
    color = Column(String, nullable=True)  
    url = Column(String, unique=True, nullable=False, index=True)  
    description = Column(String, nullable=True)  
    source = Column(String, default="carsensor", nullable=False)  
    external_id = Column(String, unique=True, index=True, nullable=True)  
    is_active = Column(Boolean, default=True, index=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_brand_model_year', 'brand', 'model', 'year'),
        Index('idx_active_updated', 'is_active', 'updated_at'),
    )


class ScraperLog(Base):
    
    __tablename__ = "scraper_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)  
    message = Column(String, nullable=True)
    items_scraped = Column(Integer, default=0)
    items_created = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    execution_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
