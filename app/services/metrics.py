import logging
from threading import Lock
from app.schemas import InspectionResult, MetricsResponse
from app.core.types import InspectionStatus

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self):
        self._lock = Lock()
        self._reset()

    def _reset(self):
        self._total = 0
        self._passed = 0
        self._failed = 0
        self._errors = 0
        self._conf_sum = 0.0
        self._conf_count = 0
        self._time_sum = 0.0
        self._time_count = 0

    def record_inspection(self, result: InspectionResult) -> None:
        with self._lock:
            self._total += 1
            if result.status == InspectionStatus.PASS.value:
                self._passed += 1
            elif result.status == InspectionStatus.FAIL.value:
                self._failed += 1
            else:
                self._errors += 1

            if result.confidence is not None:
                self._conf_sum += result.confidence
                self._conf_count += 1

            if result.processing_time_ms is not None:
                self._time_sum += result.processing_time_ms
                self._time_count += 1

    def get_metrics(self) -> dict:
        with self._lock:
            pass_rate = self._passed / self._total if self._total else 0.0
            avg_conf = self._conf_sum / self._conf_count if self._conf_count else 0.0
            avg_time = self._time_sum / self._time_count if self._time_count else 0.0
            return {
                "total": self._total,
                "passed": self._passed,
                "failed": self._failed,
                "errors": self._errors,
                "pass_rate": pass_rate,
                "avg_confidence": avg_conf,
                "avg_processing_time_ms": avg_time,
            }

    def reset(self) -> None:
        with self._lock:
            self._reset()
        logger.info("Metrics reset.")
