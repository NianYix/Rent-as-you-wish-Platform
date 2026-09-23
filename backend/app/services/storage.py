import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import AppError


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024


class LocalStorage:
    def save(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise AppError("仅支持 jpg/png/webp/gif 图片")
        data = file.file.read()
        if len(data) > MAX_SIZE:
            raise AppError("图片不能超过 5MB")
        settings = get_settings()
        ext = Path(file.filename or "img.jpg").suffix.lower() or ".jpg"
        name = f"{uuid.uuid4().hex}{ext}"
        target = settings.upload_dir / name
        target.write_bytes(data)
        return f"{settings.public_base_url.rstrip('/')}/uploads/{name}"


def get_storage() -> LocalStorage:
    return LocalStorage()
