import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-before-exposing-the-app")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'restoration.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_MB", "20")) * 1024 * 1024
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        str(BASE_DIR / "instance" / "uploads"),
    )
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
