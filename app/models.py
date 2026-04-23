from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(16), nullable=False)
    raw_text = Column(Text, nullable=True)
    date_text = Column(String(64), nullable=True)
    batch_text = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=True)
    camera_name = Column(String(128), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    image_path = Column(String(512), nullable=True)
    processed_image_path = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)

    artifacts = relationship("ImageArtifact", back_populates="inspection")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    type = Column(String(64), nullable=False)
    message = Column(Text, nullable=True)
    details_json = Column(Text, nullable=True)


class ImageArtifact(Base):
    __tablename__ = "image_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    kind = Column(String(64), nullable=False)
    path = Column(String(512), nullable=False)

    inspection = relationship("Inspection", back_populates="artifacts")
