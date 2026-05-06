from enum import Enum

class InspectionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

class CaptureMode(str, Enum):
    SINGLE = "SINGLE"
    BEST_OF_N = "BEST_OF_N"
    MEDIAN_FUSION = "MEDIAN_FUSION"

class ThresholdMode(str, Enum):
    GLOBAL = "GLOBAL"
    ADAPTIVE = "ADAPTIVE"
    OTSU = "OTSU"

class OCREngine(str, Enum):
    TESSERACT = "TESSERACT"
    PADDLEOCR = "PADDLEOCR"
