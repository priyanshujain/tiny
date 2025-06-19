"""Note parser for processing various note formats."""

import logging
import re
from pathlib import Path
from typing import Dict, Optional

import yaml


logger = logging.getLogger(__name__)


class NoteParser:
    """Parser for various note formats."""
    
    def parse(self, note_file: Path) -> str:
        """
        Parse a note file and extract content.
        
        Args:
            note_file: Path to the note file
            
        Returns:
            Cleaned note content as string
        """
        if not note_file.exists():
            raise FileNotFoundError(f"Note file not found: {note_file}")
        
        logger.info(f"Parsing note file: {note_file}")
        
        # Read the file
        content = note_file.read_text(encoding="utf-8")
        
        # Parse based on file extension
        if note_file.suffix.lower() == ".md":
            return self._parse_markdown(content)
        elif note_file.suffix.lower() in [".txt", ".text"]:
            return self._parse_text(content)
        elif note_file.suffix.lower() in [".yml", ".yaml"]:
            return self._parse_yaml(content)
        else:
            # Default to text parsing
            logger.warning(f"Unknown file extension {note_file.suffix}, treating as text")
            return self._parse_text(content)
    
    def _parse_markdown(self, content: str) -> str:
        """
        Parse markdown content and extract the main text.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Cleaned content without frontmatter and excessive formatting
        """
        # Remove YAML frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Remove markdown headers (keep the text but remove # symbols)
        content = re.sub(r"^#{1,6}\s+", "", content, flags=re.MULTILINE)
        
        # Remove emphasis markers but keep the text
        content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)  # Bold
        content = re.sub(r"\*([^*]+)\*", r"\1", content)      # Italic
        content = re.sub(r"`([^`]+)`", r"\1", content)        # Inline code
        
        # Remove link formatting but keep the text
        content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
        
        # Clean up excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
        content = content.strip()
        
        return content
    
    def _parse_text(self, content: str) -> str:
        """
        Parse plain text content.
        
        Args:
            content: Raw text content
            
        Returns:
            Cleaned content
        """
        # Simple text cleaning
        content = content.strip()
        
        # Normalize line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)
        
        return content
    
    def _parse_yaml(self, content: str) -> str:
        """
        Parse YAML content and extract relevant text fields.
        
        Args:
            content: Raw YAML content
            
        Returns:
            Extracted text content
        """
        try:
            data = yaml.safe_load(content)
            
            # Extract text from common fields
            text_parts = []
            
            # Common fields that might contain content
            for field in ["content", "text", "notes", "body", "description"]:
                if field in data and isinstance(data[field], str):
                    text_parts.append(data[field])
            
            # If we have a title, include it
            if "title" in data:
                text_parts.insert(0, f"Title: {data['title']}")
            
            # If no text fields found, convert the whole thing to string
            if not text_parts:
                text_parts.append(str(data))
            
            return "\n\n".join(text_parts)
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            # Fallback to text parsing
            return self._parse_text(content)
    
    def extract_metadata(self, note_file: Path) -> Dict[str, Optional[str]]:
        """
        Extract metadata from note file.
        
        Args:
            note_file: Path to the note file
            
        Returns:
            Dictionary with metadata (title, date, tags, etc.)
        """
        metadata = {
            "title": None,
            "date": None,
            "tags": None,
        }
        
        if not note_file.exists():
            return metadata
        
        content = note_file.read_text(encoding="utf-8")
        
        # Try to extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        metadata.update({
                            "title": frontmatter.get("title"),
                            "date": frontmatter.get("date"),
                            "tags": frontmatter.get("tags"),
                        })
                except yaml.YAMLError:
                    pass
        
        # Try to extract title from first heading
        if not metadata["title"]:
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()
        
        # Try to extract date from filename
        if not metadata["date"]:
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", note_file.name)
            if date_match:
                metadata["date"] = date_match.group(1)
        
        return metadata