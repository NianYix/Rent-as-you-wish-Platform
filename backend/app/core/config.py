from pathlib import Path
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    secret_key: str = "dev-secret-key-change-me"
    # 本地默认 SQLite，无需 Docker；上线改为 MySQL 连接串
    database_url: str = "sqlite:///./rent_as_you_wish.db"
    redis_url: str = ""
    wechat_appid: str = ""
    wechat_secret: str = ""
    jwt_expire_minutes: int = 60 * 24 * 7
    admin_seed_username: str = "admin"
    admin_seed_password: str = "Admin@123456"
    storage_backend: str = "local"
    storage_local_dir: str = "./uploads"
    public_base_url: str = "http://127.0.0.1:8000"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"

    @property
    def is_local(self) -> bool:
        return self.app_env.lower() == "local"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def upload_dir(self) -> Path:
        path = Path(self.storage_local_dir)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[2] / path
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
