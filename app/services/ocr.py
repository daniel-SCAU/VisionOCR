import logging
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
from app.schemas import OCRResult
from app.core.exceptions import OCRExecutionError

logger = logging.getLogger(__name__)


class BaseOCRBackend(ABC):
    @abstractmethod
    def recognize(self, img: np.ndarray) -> OCRResult: ...


class TesseractBackend(BaseOCRBackend):
    def __init__(self, language: str = "eng", psm: int = 6, whitelist: str = ""):
        self._language = language
        self._psm = psm
        self._whitelist = whitelist

    def _build_config(self) -> str:
        config = f"--psm {self._psm}"
        if self._whitelist:
            config += f" -c tessedit_char_whitelist={self._whitelist}"
        return config

    def recognize(self, img: np.ndarray) -> OCRResult:
        try:
            import pytesseract
            from PIL import Image

            if len(img.shape) == 2:
                pil_img = Image.fromarray(img)
            else:
                pil_img = Image.fromarray(img[..., ::-1])

            config = self._build_config()
            data = pytesseract.image_to_data(
                pil_img,
                lang=self._language,
                config=config,
                output_type=pytesseract.Output.DICT,
            )

            words = []
            confs = []
            for text, conf in zip(data["text"], data["conf"]):
                text = text.strip()
                if text and conf != -1:
                    words.append(text)
                    confs.append(float(conf))

            raw_text = " ".join(words)
            confidence = float(np.mean(confs)) if confs else 0.0
            return OCRResult(raw_text=raw_text, confidence=confidence)
        except Exception as exc:
            raise OCRExecutionError(f"Tesseract failed: {exc}") from exc


def get_ocr_backend(settings) -> BaseOCRBackend:
    engine = getattr(settings, "OCR_ENGINE", "TESSERACT").upper()
    if engine == "TESSERACT":
        return TesseractBackend(
            language=settings.OCR_LANGUAGE,
            psm=settings.OCR_PSM,
            whitelist=settings.OCR_WHITELIST,
        )
    raise ValueError(f"Unknown OCR engine: {engine}")
