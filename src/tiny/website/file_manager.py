"""File manager for website operations."""

import logging
import shutil
from pathlib import Path
from typing import Optional

from ..config import TinyConfig


logger = logging.getLogger(__name__)


class FileManager:
    """Manager for website file operations."""
    
    def __init__(self, config: TinyConfig):
        """Initialize the file manager."""
        self.config = config
        self.website_path = Path(config.website_path).resolve()
        self.writings_dir = self.website_path / config.writings_dir
    
    def validate_website_path(self) -> bool:
        """
        Validate that the website path exists and has the expected structure.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.website_path.exists():
            logger.error(f"Website path does not exist: {self.website_path}")
            return False
        
        # Check for key files/directories
        required_paths = [
            self.website_path / "package.json",
            self.website_path / "src",
            self.writings_dir,
        ]
        
        for path in required_paths:
            if not path.exists():
                logger.error(f"Required path missing: {path}")
                return False
        
        logger.info("Website path validation successful")
        return True
    
    def backup_file(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of a file before modifying it.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file, or None if backup failed
        """
        if not file_path.exists():
            return None
        
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path}: {e}")
            return None
    
    def restore_backup(self, original_path: Path, backup_path: Path) -> bool:
        """
        Restore a file from backup.
        
        Args:
            original_path: Path where file should be restored
            backup_path: Path to backup file
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                logger.info(f"Restored file from backup: {original_path}")
                return True
            else:
                logger.error(f"Backup file not found: {backup_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def cleanup_backup(self, backup_path: Path) -> None:
        """
        Remove a backup file.
        
        Args:
            backup_path: Path to backup file to remove
        """
        try:
            if backup_path.exists():
                backup_path.unlink()
                logger.info(f"Removed backup file: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to remove backup file {backup_path}: {e}")
    
    def validate_react_component(self, file_path: Path) -> bool:
        """
        Validate that a React component file has valid syntax.
        
        Args:
            file_path: Path to React component file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Basic syntax checks
            checks = [
                "import React" in content,
                "export default" in content,
                content.count("{") == content.count("}"),
                content.count("(") == content.count(")"),
                content.count("[") == content.count("]"),
            ]
            
            if not all(checks):
                logger.error(f"React component validation failed: {file_path}")
                return False
            
            logger.info(f"React component validation successful: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating React component {file_path}: {e}")
            return False
    
    def ensure_directory_exists(self, directory: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path to ensure exists
            
        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    def get_writings_files(self) -> list[Path]:
        """
        Get list of all writing files in the writings directory.
        
        Returns:
            List of paths to writing files
        """
        try:
            writings_files = list(self.writings_dir.glob("*.js"))
            # Filter out index.js
            writings_files = [f for f in writings_files if f.name != "index.js"]
            return sorted(writings_files)
        except Exception as e:
            logger.error(f"Error getting writings files: {e}")
            return []