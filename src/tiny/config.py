"""Configuration management for tiny agent."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class TinyConfig(BaseSettings):
    """Configuration for the tiny agent."""
    
    # Vertex AI settings
    google_application_credentials: Optional[str] = Field(
        default=None,
        description="Path to Google Cloud service account key file (optional if using ADC)"
    )
    google_cloud_project: Optional[str] = Field(
        default=None,
        description="Google Cloud project ID (optional if using ADC)"
    )
    vertex_ai_location: str = Field(
        default="us-east5",
        description="Vertex AI location"
    )
    vertex_ai_model: str = Field(
        default="gemini-2.5-flash",
        description="Vertex AI model to use"
    )
    
    # Website settings
    website_path: Path = Field(
        default_factory=lambda: Path("."),
        description="Path to the website project"
    )
    writings_dir: str = Field(
        default=".",
        description="Directory containing blog posts"
    )
    writings_index_file: str = Field(
        default="./index.js",
        description="Writings index file"
    )
    
    # Git settings
    git_remote: str = Field(
        default="origin",
        description="Git remote name"
    )
    git_branch: str = Field(
        default="main",
        description="Git branch to push to"
    )
    
    # Notes settings
    notes_dir: Path = Field(
        default_factory=lambda: Path("notes"),
        description="Directory containing notes"
    )
    
    # AI settings
    max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for AI generation"
    )
    temperature: float = Field(
        default=0.5,
        description="Temperature for AI generation"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_config() -> TinyConfig:
    """Get the configuration instance."""
    return TinyConfig()