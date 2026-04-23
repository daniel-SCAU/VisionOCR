import asyncio
import logging
import threading
from datetime import datetime, timezone
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TriggerService:
    def __init__(self):
        self._interval_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callback: Optional[Callable] = None

    def software_trigger(self) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("Software trigger fired at %s", ts)
        return ts

    def start_interval_mode(self, interval: float, callback: Callable) -> None:
        if self._interval_thread and self._interval_thread.is_alive():
            logger.warning("Interval mode already running.")
            return
        self._stop_event.clear()
        self._callback = callback

        def _loop():
            while not self._stop_event.wait(interval):
                try:
                    self._callback()
                except Exception as exc:
                    logger.error("Interval trigger callback error: %s", exc)

        self._interval_thread = threading.Thread(target=_loop, daemon=True)
        self._interval_thread.start()
        logger.info("Interval trigger started (%.2fs).", interval)

    def stop_interval_mode(self) -> None:
        self._stop_event.set()
        if self._interval_thread:
            self._interval_thread.join(timeout=5)
        logger.info("Interval trigger stopped.")

    def hardware_trigger_stub(self) -> None:
        logger.info("[HW TRIGGER STUB] Hardware trigger pulse received.")
