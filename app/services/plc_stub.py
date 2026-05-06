import logging
import time

logger = logging.getLogger(__name__)


class PLCStub:
    def set_busy(self) -> None:
        logger.info("[PLC] Signal: BUSY")

    def set_pass(self) -> None:
        logger.info("[PLC] Signal: PASS")

    def set_fail(self) -> None:
        logger.info("[PLC] Signal: FAIL")

    def pulse_reject(self, duration_ms: int = 200) -> None:
        logger.info("[PLC] Pulse REJECT for %d ms", duration_ms)

    def heartbeat(self) -> None:
        logger.debug("[PLC] Heartbeat at %s", time.strftime("%H:%M:%S"))
