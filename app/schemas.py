from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class OCRResult(BaseModel):
    raw_text: str = ""
    date_text: Optional[str] = None
    batch_text: Optional[str] = None
    confidence: float = 0.0


class ValidationResult(BaseModel):
    is_pass: bool = False
    date_valid: bool = False
    batch_valid: bool = False
    confidence_valid: bool = False
    errors: list[str] = []


class CaptureResult(BaseModel):
    frame: bytes
    timestamp: str


class InspectionResult(BaseModel):
    id: Optional[int] = None
    timestamp: str
    status: str
    raw_text: Optional[str] = None
    date_text: Optional[str] = None
    batch_text: Optional[str] = None
    confidence: Optional[float] = None
    camera_name: Optional[str] = None
    processing_time_ms: Optional[int] = None
    image_path: Optional[str] = None
    processed_image_path: Optional[str] = None
    error_message: Optional[str] = None


class InspectionCreate(BaseModel):
    status: str
    raw_text: Optional[str] = None
    date_text: Optional[str] = None
    batch_text: Optional[str] = None
    confidence: Optional[float] = None
    camera_name: Optional[str] = None
    processing_time_ms: Optional[int] = None
    image_path: Optional[str] = None
    processed_image_path: Optional[str] = None
    error_message: Optional[str] = None


class InspectionResponse(BaseModel):
    id: int
    timestamp: datetime
    status: str
    raw_text: Optional[str] = None
    date_text: Optional[str] = None
    batch_text: Optional[str] = None
    confidence: Optional[float] = None
    camera_name: Optional[str] = None
    processing_time_ms: Optional[int] = None
    image_path: Optional[str] = None
    processed_image_path: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class SettingItem(BaseModel):
    key: str
    value: Optional[str] = None


class SettingsResponse(BaseModel):
    settings: list[SettingItem]


class SettingsUpdate(BaseModel):
    settings: list[SettingItem]


class TriggerRequest(BaseModel):
    mode: Optional[str] = None


class TriggerResponse(BaseModel):
    triggered: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str


class MetricsResponse(BaseModel):
    total: int
    passed: int
    failed: int
    errors: int
    pass_rate: float
    avg_confidence: float
    avg_processing_time_ms: float


class CameraTestResult(BaseModel):
    success: bool
    message: str
    width: Optional[int] = None
    height: Optional[int] = None
    snapshot_path: Optional[str] = None
