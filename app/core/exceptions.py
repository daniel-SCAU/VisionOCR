class VisionOCRException(Exception): pass
class CameraInitError(VisionOCRException): pass
class CaptureError(VisionOCRException): pass
class InvalidConfigError(VisionOCRException): pass
class OCRExecutionError(VisionOCRException): pass
class StorageError(VisionOCRException): pass
class InvalidROIError(VisionOCRException): pass
