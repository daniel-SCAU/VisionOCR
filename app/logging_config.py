import logging
import logging.handlers
import os

def setup_logging(log_level: str = "INFO") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    root = logging.getLogger()
    root.setLevel(level)

    if not root.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        root.addHandler(ch)

        fh = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, "vision_ocr.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        fh.setFormatter(formatter)
        root.addHandler(fh)
