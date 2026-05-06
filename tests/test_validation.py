import pytest
from app.services.validation import parse_date_text, parse_batch_text, validate_result
from app.schemas import OCRResult


DATE_REGEX = r"(\d{2}[./]\d{2}[./]\d{4}|\d{6}|\d{4}-\d{2}-\d{2})"
BATCH_REGEX = r"([A-Z]{1,3}\d{4,8})"


def test_parse_date_ddmmyyyy():
    result = parse_date_text("LOT: AB1234 EXP 25.06.2025", DATE_REGEX)
    assert result == "25.06.2025"


def test_parse_date_yymmdd():
    result = parse_date_text("250612 batch AB1234", DATE_REGEX)
    assert result == "250612"


def test_parse_date_iso():
    result = parse_date_text("Date 2025-06-12 code AB1234", DATE_REGEX)
    assert result == "2025-06-12"


def test_parse_date_without_capture_group():
    result = parse_date_text("EXP 2025-06-12", r"\b\d{4}-\d{2}-\d{2}\b")
    assert result == "2025-06-12"


def test_parse_date_none():
    result = parse_date_text("no date here", DATE_REGEX)
    assert result is None


def test_parse_batch_valid():
    result = parse_batch_text("AB123456 25.06.2025", BATCH_REGEX)
    assert result == "AB123456"


def test_parse_batch_none():
    result = parse_batch_text("no batch here 123", BATCH_REGEX)
    assert result is None


def test_parse_date_invalid_regex():
    result = parse_date_text("some text", "[invalid")
    assert result is None


def test_validate_pass():
    class FakeSettings:
        MIN_CONFIDENCE = 60.0
    ocr = OCRResult(raw_text="AB1234 25.06.2025", date_text="25.06.2025", batch_text="AB1234", confidence=80.0)
    result = validate_result(ocr, FakeSettings())
    assert result.is_pass is True
    assert result.confidence_valid is True


def test_validate_fail_no_date():
    class FakeSettings:
        MIN_CONFIDENCE = 60.0
    ocr = OCRResult(raw_text="AB1234", date_text=None, batch_text="AB1234", confidence=80.0)
    result = validate_result(ocr, FakeSettings())
    assert result.is_pass is False
    assert result.date_valid is False
    assert "Date not found." in result.errors


def test_validate_fail_low_confidence():
    class FakeSettings:
        MIN_CONFIDENCE = 60.0
    ocr = OCRResult(raw_text="AB1234 25.06.2025", date_text="25.06.2025", batch_text="AB1234", confidence=30.0)
    result = validate_result(ocr, FakeSettings())
    assert result.is_pass is False
    assert result.confidence_valid is False


def test_validate_fail_no_batch():
    class FakeSettings:
        MIN_CONFIDENCE = 60.0
    ocr = OCRResult(raw_text="25.06.2025", date_text="25.06.2025", batch_text=None, confidence=80.0)
    result = validate_result(ocr, FakeSettings())
    assert result.is_pass is False
    assert result.batch_valid is False
