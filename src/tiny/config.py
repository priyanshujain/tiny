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

    # Google Cloud / Vertex AI settings
    google_cloud_project: str = Field(default="", description="Google Cloud project ID")
    vertex_ai_location: str = Field(
        default="us-east1", description="Vertex AI location"
    )

    # Output settings
    posts_dir: str = Field(default="./posts", description="Directory to write posts to")

    # Website settings
    website_path: str = Field(default="", description="Path to website directory")
    writings_dir: str = Field(
        default="src/pages/writings", description="Directory for blog posts"
    )
    writings_index_file: str = Field(
        default="src/pages/writings/index.js", description="Index file to update"
    )

    # Git settings
    git_remote: str = Field(default="origin", description="Git remote name")
    git_branch: str = Field(default="main", description="Git branch to use")

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
