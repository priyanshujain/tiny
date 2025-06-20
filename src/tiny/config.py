from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class TinyConfig(BaseSettings):
    model: str = "vertex_ai/gemini-2.5-flash"
    
    posts_dir: Path = Path("posts")
    notes_dir: Path = Path("notes")
    
    max_tokens: int = 2000
    temperature: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

def get_config() -> TinyConfig:
    return TinyConfig()
