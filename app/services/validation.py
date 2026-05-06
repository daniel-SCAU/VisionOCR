import re
import logging
from typing import Optional
from app.schemas import OCRResult, ValidationResult

logger = logging.getLogger(__name__)


def parse_date_text(raw_text: str, date_regex: str) -> Optional[str]:
    try:
        m = re.search(date_regex, raw_text)
        return m.group(1) if m else None
    except re.error as exc:
        logger.error("Invalid date regex: %s", exc)
        return None


def parse_batch_text(raw_text: str, batch_regex: str) -> Optional[str]:
    try:
        m = re.search(batch_regex, raw_text)
        return m.group(1) if m else None
    except re.error as exc:
        logger.error("Invalid batch regex: %s", exc)
        return None


def validate_result(ocr_result: OCRResult, settings) -> ValidationResult:
    errors: list[str] = []

    date_valid = bool(ocr_result.date_text)
    if not date_valid:
        errors.append("Date not found.")

    batch_valid = bool(ocr_result.batch_text)
    if not batch_valid:
        errors.append("Batch code not found.")

    min_conf = float(getattr(settings, "MIN_CONFIDENCE", 60.0))
    confidence_valid = ocr_result.confidence >= min_conf
    if not confidence_valid:
        errors.append(f"Confidence {ocr_result.confidence:.1f} below threshold {min_conf}.")

    is_pass = date_valid and batch_valid and confidence_valid

    return ValidationResult(
        is_pass=is_pass,
        date_valid=date_valid,
        batch_valid=batch_valid,
        confidence_valid=confidence_valid,
        errors=errors,
    )
