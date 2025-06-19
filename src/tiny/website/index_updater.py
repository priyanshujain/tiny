"""Index updater for managing the writings index."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from ..ai.vertex_client import BlogContent
from ..config import TinyConfig
from ..processors.blog_generator import BlogGenerator
from .file_manager import FileManager


logger = logging.getLogger(__name__)


class IndexUpdater:
    """Updates the writings index file with new blog posts."""
    
    def __init__(self, config: TinyConfig):
        """Initialize the index updater."""
        self.config = config
        self.file_manager = FileManager(config)
        self.blog_generator = BlogGenerator(config)
        self.index_path = Path(config.website_path) / config.writings_index_file
    
    def add_entry(self, blog_content: BlogContent) -> bool:
        """
        Add a new entry to the writings index.
        
        Args:
            blog_content: Blog content to add
            
        Returns:
            True if successfully added, False otherwise
        """
        try:
            # Validate index file exists
            if not self.index_path.exists():
                logger.error(f"Index file not found: {self.index_path}")
                return False
            
            # Create backup
            backup_path = self.file_manager.backup_file(self.index_path)
            
            try:
                # Read current index
                current_content = self.index_path.read_text(encoding="utf-8")
                
                # Generate new entry
                new_entry = self._generate_entry(blog_content)
                
                # Insert new entry
                updated_content = self._insert_entry(current_content, new_entry, blog_content.date)
                
                # Write updated content
                self.index_path.write_text(updated_content, encoding="utf-8")
                
                # Validate the updated file
                if self.file_manager.validate_react_component(self.index_path):
                    # Success, cleanup backup
                    if backup_path:
                        self.file_manager.cleanup_backup(backup_path)
                    logger.info(f"Successfully added entry to index: {blog_content.title}")
                    return True
                else:
                    # Validation failed, restore backup
                    if backup_path:
                        self.file_manager.restore_backup(self.index_path, backup_path)
                    logger.error("Updated index file failed validation, restored backup")
                    return False
                    
            except Exception as e:
                # Error occurred, restore backup
                if backup_path:
                    self.file_manager.restore_backup(self.index_path, backup_path)
                logger.error(f"Error updating index, restored backup: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding entry to index: {e}")
            return False
    
    def _generate_entry(self, blog_content: BlogContent) -> str:
        """
        Generate the JSX entry for a blog post.
        
        Args:
            blog_content: Blog content
            
        Returns:
            JSX entry string
        """
        # Format date for display
        try:
            date_obj = datetime.strptime(blog_content.date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%b %d, %Y")
        except ValueError:
            formatted_date = blog_content.date
        
        # Get URL path
        url_path = self.blog_generator.get_url_path(blog_content)
        
        # Escape title for JSX
        escaped_title = blog_content.title.replace('"', '\\"').replace("'", "\\'")
        
        entry = f'''                <a
                  className="primary-text-color ma0 pa0 f5 mr6 fw-bold"
                  href="{url_path}"
                >
                  <h4 className="f3 ma0 flex-l justify-between">
                    <p className="left fit-content">{escaped_title}</p>
                    <p className="tertiary-text-color tl">{formatted_date}</p>
                  </h4>
                </a>'''
        
        return entry
    
    def _insert_entry(self, content: str, new_entry: str, entry_date: str) -> str:
        """
        Insert a new entry into the index content in chronological order.
        
        Args:
            content: Current index file content
            new_entry: New entry to insert
            entry_date: Date of the new entry (YYYY-MM-DD format)
            
        Returns:
            Updated content with new entry inserted
        """
        # Find the writings section where entries are listed
        # Look for the pattern with multiple <a> tags
        writings_section_pattern = r'(<div className="mt10 ma20-l">)(.*?)(\s*</div>\s*</div>\s*</div>)'
        
        match = re.search(writings_section_pattern, content, re.DOTALL)
        if not match:
            logger.error("Could not find writings section in index file")
            # Fallback: append at the end before closing divs
            return self._fallback_insert(content, new_entry)
        
        before_entries = match.group(1)
        entries_section = match.group(2)
        after_entries = match.group(3)
        
        # Parse existing entries and their dates
        existing_entries = self._parse_existing_entries(entries_section)
        
        # Convert entry date to datetime for comparison
        try:
            new_date = datetime.strptime(entry_date, "%Y-%m-%d")
        except ValueError:
            # If date parsing fails, add to the top
            new_date = datetime.now()
        
        # Find the right position to insert (newest first)
        insert_position = 0
        for i, (entry, entry_datetime) in enumerate(existing_entries):
            if entry_datetime and new_date > entry_datetime:
                insert_position = i
                break
            insert_position = i + 1
        
        # Insert the new entry
        entries_list = [entry for entry, _ in existing_entries]
        entries_list.insert(insert_position, new_entry)
        
        # Reconstruct the content
        new_entries_section = "\\n".join(entries_list)
        updated_content = content.replace(
            before_entries + entries_section + after_entries,
            before_entries + "\\n" + new_entries_section + "\\n" + after_entries
        )
        
        return updated_content
    
    def _parse_existing_entries(self, entries_section: str) -> List[Tuple[str, datetime]]:
        """
        Parse existing entries and extract their dates.
        
        Args:
            entries_section: The entries section of the index file
            
        Returns:
            List of tuples (entry_text, entry_date)
        """
        entries = []
        
        # Split by <a> tags to get individual entries
        entry_pattern = r'(<a[^>]*>.*?</a>)'
        entry_matches = re.findall(entry_pattern, entries_section, re.DOTALL)
        
        for entry in entry_matches:
            # Extract date from the entry
            date_pattern = r'<p className="tertiary-text-color tl">([^<]+)</p>'
            date_match = re.search(date_pattern, entry)
            
            entry_date = None
            if date_match:
                date_str = date_match.group(1).strip()
                # Try to parse various date formats
                for fmt in ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]:
                    try:
                        entry_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            
            entries.append((entry.strip(), entry_date))
        
        return entries
    
    def _fallback_insert(self, content: str, new_entry: str) -> str:
        """
        Fallback method to insert entry at the beginning of the writings section.
        
        Args:
            content: Current index file content
            new_entry: New entry to insert
            
        Returns:
            Updated content
        """
        logger.warning("Using fallback insertion method")
        
        # Look for the first <a> tag in the writings section
        first_entry_pattern = r'(<div className="mt10 ma20-l">\s*)(.*?<a[^>]*>.*?</a>)'
        
        match = re.search(first_entry_pattern, content, re.DOTALL)
        if match:
            before = match.group(1)
            first_entry = match.group(2)
            
            # Insert new entry before the first existing entry
            replacement = before + new_entry + "\\n                " + first_entry
            return content.replace(match.group(0), replacement)
        
        # Ultimate fallback: just add a note that manual intervention is needed
        logger.error("Could not automatically insert entry, manual intervention required")
        return content