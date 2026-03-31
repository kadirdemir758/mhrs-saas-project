"""
MHRS SaaS — Application Configuration
Loads all settings from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ── Application ─────────────────────────────
    app_name: str = "MHRS SaaS"
    app_env: str = "development"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── Security ─────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    encryption_key: str = "change-me-in-production"
    char_substitution_seed: str = "mhrs_saas_substitution_v1_secret"

    # ── Database ──────────────────────────────────
    database_url: str = "mysql+pymysql://mhrs_user:mhrs_password@localhost:3306/mhrs_db"

    # ── RabbitMQ ──────────────────────────────────
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "mhrs_rabbit"
    rabbitmq_pass: str = "rabbitpass"
    rabbitmq_vhost: str = "mhrs_vhost"
    rabbitmq_url: str = "amqp://mhrs_rabbit:rabbitpass@localhost:5672/mhrs_vhost"

    # ── Elasticsearch ─────────────────────────────
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index_doctors: str = "doctors"

    # ── SMTP ──────────────────────────────────────
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "your_email@gmail.com"
    smtp_password: str = "your_app_password"
    smtp_from_name: str = "MHRS Sistem"
    smtp_from_email: str = "your_email@gmail.com"

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings — created once per process."""
    return Settings()
