import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.ocr import TesseractBackend, get_ocr_backend
from app.schemas import OCRResult
from app.config import Settings


def make_mock_tess_data(text="AB1234 25.06.2025", conf=85):
    words = text.split()
    return {
        "text": words + [""],
        "conf": [conf] * len(words) + [-1],
    }


def test_tesseract_recognize():
    backend = TesseractBackend(language="eng", psm=6)
    img = np.ones((100, 300), dtype=np.uint8) * 255
    mock_data = make_mock_tess_data("AB1234 25.06.2025", conf=85)
    with patch("pytesseract.image_to_data", return_value=mock_data):
        result = backend.recognize(img)
    assert isinstance(result, OCRResult)
    assert "AB1234" in result.raw_text
    assert result.confidence == pytest.approx(85.0)


def test_tesseract_empty_result():
    backend = TesseractBackend()
    img = np.ones((100, 300), dtype=np.uint8) * 255
    mock_data = {"text": ["", ""], "conf": [-1, -1]}
    with patch("pytesseract.image_to_data", return_value=mock_data):
        result = backend.recognize(img)
    assert result.raw_text == ""
    assert result.confidence == 0.0


def test_tesseract_config_whitelist():
    backend = TesseractBackend(psm=7, whitelist="0123456789")
    config = backend._build_config()
    assert "--psm 7" in config
    assert "tessedit_char_whitelist=0123456789" in config


def test_get_ocr_backend():
    settings = Settings(OCR_ENGINE="TESSERACT")
    backend = get_ocr_backend(settings)
    assert isinstance(backend, TesseractBackend)


def test_tesseract_raises_on_failure():
    from app.core.exceptions import OCRExecutionError
    backend = TesseractBackend()
    img = np.ones((10, 10), dtype=np.uint8)
    with patch("pytesseract.image_to_data", side_effect=Exception("tess error")):
        with pytest.raises(OCRExecutionError):
            backend.recognize(img)
