import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    APPLICATION_ROOT = "/symptomtracker"
    SECRET_KEY = os.environ.get(
        "SECRET_KEY"
    )

    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is required."
        )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / "uploads"

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    TIMEZONE = "Europe/Budapest"
