import re
import os
from datetime import datetime, timezone

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe_filename(prefix: str, ext: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    safe_prefix = re.sub(r'[^\w-]', '_', prefix)
    return f"{safe_prefix}_{ts}.{ext.lstrip('.')}"

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))
