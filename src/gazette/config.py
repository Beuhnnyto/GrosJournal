"""Configuration lue dans l'environnement (voir .env.example)."""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_USER_AGENT = "GrosJournal/0.1 (+https://github.com/Beuhnnyto/GrosJournal)"


@dataclass(frozen=True)
class Settings:
    database_url: str
    sources_path: Path
    data_dir: Path
    user_agent: str
    http_timeout: float

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.environ.get(
                "DATABASE_URL", "postgresql://gazette:gazette@localhost:5432/gazette"
            ),
            sources_path=Path(os.environ.get("SOURCES_PATH", "sources.csv")),
            data_dir=Path(os.environ.get("DATA_DIR", "data")),
            user_agent=os.environ.get("USER_AGENT", DEFAULT_USER_AGENT),
            http_timeout=float(os.environ.get("HTTP_TIMEOUT", "20")),
        )
