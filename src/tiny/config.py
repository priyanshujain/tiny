from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TinyConfig(BaseSettings):
    model: str = "vertex_ai/gemini-2.5-flash"

    max_tokens: int = 2000
    temperature: float = 0.5

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = v.upper()
        if level not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return level


def get_config() -> TinyConfig:
    return TinyConfig()
