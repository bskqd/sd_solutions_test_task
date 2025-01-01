import os
from pathlib import Path, PosixPath

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    HOST_DOMAIN: str = os.getenv("HOST_DOMAIN", 'http://127.0.0.1:8000')

    BASE_DIR: PosixPath = Path(__file__).resolve().parent

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    REDIS_HOST_URL: str = os.getenv("REDIS_HOST_URL")
    REDIS_SHARED_CONTEXT_DB: int = os.getenv("REDIS_SHARED_CONTEXT_DB", 1)

    MINIO_URL: str = os.getenv("MINIO_URL")
    MINIO_SECURE: bool = bool(os.getenv("MINIO_SECURE", ""))
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY")
    MINIO_PUBLIC_HOST: str = os.getenv("MINIO_PUBLIC_HOST", "http://127.0.0.1:9000")

    PERSISTENT_DATA_BUCKET_NAME: str = os.getenv("PERSISTENT_DATA_BUCKET_NAME", "candidates-info")
    LOGS_BUCKET_NAME: str = os.getenv("LOGS_BUCKET_NAME", "logs")

    class Config:
        frozen = True
