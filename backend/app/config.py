"""Environment-backed application settings."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _csv(value: str) -> list[str]:
    """Return a comma-separated environment value as trimmed, non-empty items."""
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Runtime settings with safe local-development defaults."""

    app_name: str
    api_v1_prefix: str
    frontend_origins: list[str]
    database_url: str | None

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            app_name=os.getenv("SPECS_APP_NAME", "SPECS API"),
            api_v1_prefix=os.getenv("SPECS_API_V1_PREFIX", "/api/v1"),
            frontend_origins=_csv(
                os.getenv(
                    "SPECS_FRONTEND_ORIGINS",
                    "http://localhost:5173,http://127.0.0.1:5173",
                )
            ),
            database_url=os.getenv("DATABASE_URL"),
        )
