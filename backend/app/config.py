from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_ARTIFACT = PROJECT_ROOT / "ml" / "artifacts" / "zsentinel_pipeline_v1.joblib"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_database: str = "zsentinel"
    mongodb_fallback_mock: bool = True
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"
    model_artifact_path: str = str(DEFAULT_ARTIFACT)
    risk_medium_threshold: float = Field(default=0.25, ge=0.0, le=1.0)
    risk_high_threshold: float = Field(default=0.60, ge=0.0, le=1.0)

    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_webhook_id: str = ""
    paypal_api_base: str = "https://api-m.sandbox.paypal.com"
    paypal_mode: str = "sandbox"

    genai_enabled: bool = False
    genai_api_key: str = ""
    genai_api_url: str = ""
    genai_model: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.frontend_origins.split(",") if item.strip()]

    @property
    def resolved_artifact_path(self) -> Path:
        """Resolve model artifact path regardless of execution directory."""
        raw = Path(self.model_artifact_path)
        if raw.is_absolute() and raw.exists():
            return raw
        # Try relative to current working directory
        if raw.exists():
            return raw.resolve()
        # Try relative to BACKEND_DIR
        candidate1 = (BACKEND_DIR / raw).resolve()
        if candidate1.exists():
            return candidate1
        # Try relative to PROJECT_ROOT
        candidate2 = (PROJECT_ROOT / raw).resolve()
        if candidate2.exists():
            return candidate2
        # Default fallback
        return DEFAULT_ARTIFACT

    @property
    def paypal_configured(self) -> bool:
        return bool(
            self.paypal_client_id
            and self.paypal_client_secret
            and self.paypal_webhook_id
        )

    @property
    def genai_configured(self) -> bool:
        return bool(self.genai_enabled and self.genai_api_key and self.genai_api_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
