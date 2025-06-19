"""Configuration management for tiny agent."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class TinyConfig(BaseSettings):
    """Configuration for the tiny agent."""

    # LLM settings
    model: str = Field(
        default="vertex_ai/gemini-2.5-flash",
        description="LLM model to use (any LiteLLM compatible model)",
    )

    # Website settings
    website_path: Path = Field(
        default_factory=lambda: Path("."), description="Path to the website project"
    )
    writings_dir: str = Field(
        default=".", description="Directory containing blog posts"
    )
    writings_index_file: str = Field(
        default="./index.js", description="Writings index file"
    )

    # Git settings
    git_remote: str = Field(default="origin", description="Git remote name")
    git_branch: str = Field(default="main", description="Git branch to push to")

    # Notes settings
    notes_dir: Path = Field(
        default_factory=lambda: Path("notes"), description="Directory containing notes"
    )

    # AI settings
    max_tokens: int = Field(
        default=2000, description="Maximum tokens for AI generation"
    )
    temperature: float = Field(default=0.5, description="Temperature for AI generation")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_config() -> TinyConfig:
    """Get the configuration instance."""
    return TinyConfig()
