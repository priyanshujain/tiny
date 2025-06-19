"""Blog post generator for creating React components."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from tiny.ai.vertex_client import BlogContent
from tiny.config import TinyConfig


logger = logging.getLogger(__name__)


class BlogGenerator:
    """Generator for React blog post components."""
    
    def __init__(self, config: TinyConfig):
        """Initialize the blog generator."""
        self.config = config
    
    def generate(self, blog_content: BlogContent) -> Path:
        """
        Generate a React component file from blog content.
        
        Args:
            blog_content: Blog content with title, content, and date
            
        Returns:
            Path to the generated file
        """
        # Generate filename from title
        filename = self._title_to_filename(blog_content.title)
        
        # Create the full path
        writings_dir = Path(self.config.website_path) / self.config.writings_dir
        file_path = writings_dir / f"{filename}.js"
        
        # Generate React component
        component_code = self._generate_react_component(blog_content)
        
        # Write the file
        file_path.write_text(component_code, encoding="utf-8")
        
        logger.info(f"Generated blog post file: {file_path}")
        return file_path
    
    def _title_to_filename(self, title: str) -> str:
        """
        Convert blog title to a valid filename.
        
        Args:
            title: Blog post title
            
        Returns:
            URL-safe filename
        """
        # Convert to lowercase
        filename = title.lower()
        
        # Replace spaces and special characters with hyphens
        filename = re.sub(r"[^a-z0-9]+", "-", filename)
        
        # Remove leading/trailing hyphens
        filename = filename.strip("-")
        
        # Ensure it's not empty
        if not filename:
            filename = f"post-{datetime.now().strftime('%Y%m%d')}"
        
        return filename
    
    def _generate_react_component(self, blog_content: BlogContent) -> str:
        """
        Generate React component code for the blog post.
        
        Args:
            blog_content: Blog content
            
        Returns:
            React component code as string
        """
        # Format the date for display
        try:
            date_obj = datetime.strptime(blog_content.date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%b %d, %Y")
        except ValueError:
            formatted_date = blog_content.date
        
        # Split content into paragraphs and wrap each in <p> tags
        paragraphs = blog_content.content.split("\n\n")
        paragraph_jsx = "\n              ".join([
            f'<p className="ma0 pa0 pl5 pr5 mt4 f4 f3-ns sig-grey">\n                {self._escape_jsx(para.strip())}\n              </p>'
            for para in paragraphs if para.strip()
        ])
        
        # Generate the component
        component_code = f'''import React, {{ useState }} from "react";
import Layout from "../../components/layout/index";
import SEO from "../../components/seo";
import {{ SectionBox }} from "../../components/home";

const handleScroll = (isModalOpen) => {{
  if (isModalOpen === true) {{
    document.documentElement.style.overflow = "hidden";
  }} else {{
    document.documentElement.style.overflowY = "scroll";
  }}
}};

const Page = (props) => {{
  const [isContactOpen, setContact] = useState(false);
  const handleContact = () => {{
    handleScroll(!isContactOpen);
    setContact(!isContactOpen);
  }};

  return (
    <Layout headerClass="">
      <SEO
        title="{self._escape_jsx(blog_content.title)}"
        description={{`{self._escape_jsx(self._generate_description(blog_content.content))}`}}
      />
      <div
        class="main-content"
        style={{{{
          minHeight: "100vh",
        }}}}
      >
        <SectionBox
          heading="{self._escape_jsx(blog_content.title)}"
          headingClass="ma0 pa0 f2 f-headline-ns sig-blue fw-600"
          bodyClass="col-12 mw-100 center"
          className="pt16"
        />
        <div className=" pt0 pb5 pt10-ns pb20-ns">
          <div className="mw-l center">
            {paragraph_jsx}
          </div>
        </div>
      </div>
    </Layout>
  );
}};

export default Page;
'''
        
        return component_code
    
    def _escape_jsx(self, text: str) -> str:
        """
        Escape text for use in JSX.
        
        Args:
            text: Text to escape
            
        Returns:
            JSX-safe text
        """
        # Escape quotes and backslashes
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        text = text.replace("'", "\\'")
        
        return text
    
    def _generate_description(self, content: str) -> str:
        """
        Generate a description from blog content.
        
        Args:
            content: Full blog content
            
        Returns:
            Short description (first sentence or first 150 chars)
        """
        # Get first paragraph
        first_paragraph = content.split("\n\n")[0].strip()
        
        # Get first sentence or first 150 characters
        sentences = re.split(r"[.!?]+", first_paragraph)
        if sentences and len(sentences[0]) > 10:
            description = sentences[0].strip() + "."
        else:
            description = first_paragraph
        
        # Truncate if too long
        if len(description) > 150:
            description = description[:147] + "..."
        
        return description
    
    def get_url_path(self, blog_content: BlogContent) -> str:
        """
        Get the URL path for the blog post.
        
        Args:
            blog_content: Blog content
            
        Returns:
            URL path (e.g., "/writings/my-blog-post")
        """
        filename = self._title_to_filename(blog_content.title)
        return f"/writings/{filename}"