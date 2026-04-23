#!/usr/bin/env python3
"""Run database migrations / table creation."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Settings
from app.database import init_db

if __name__ == "__main__":
    settings = Settings()
    init_db(settings)
    print("Database initialized.")
