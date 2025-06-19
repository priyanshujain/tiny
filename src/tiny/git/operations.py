"""Git operations for automated commits and deployment."""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional

import git
from git import Repo

from ..config import TinyConfig


logger = logging.getLogger(__name__)


class GitOperations:
    """Handles git operations for the website."""
    
    def __init__(self, config: TinyConfig):
        """Initialize git operations."""
        self.config = config
        self.website_path = Path(config.website_path).resolve()
        self.repo: Optional[Repo] = None
        self._initialize_repo()
    
    def _initialize_repo(self) -> None:
        """Initialize the git repository."""
        try:
            self.repo = Repo(self.website_path)
            logger.info(f"Initialized git repo at: {self.website_path}")
        except git.exc.InvalidGitRepositoryError:
            logger.error(f"Not a git repository: {self.website_path}")
            raise
        except Exception as e:
            logger.error(f"Error initializing git repo: {e}")
            raise
    
    def check_status(self) -> dict:
        """
        Check the git status of the repository.
        
        Returns:
            Dictionary with status information
        """
        if not self.repo:
            return {"error": "Repository not initialized"}
        
        try:
            status = {
                "branch": self.repo.active_branch.name,
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
                "modified_files": [item.a_path for item in self.repo.index.diff(None)],
                "staged_files": [item.a_path for item in self.repo.index.diff("HEAD")],
            }
            return status
        except Exception as e:
            logger.error(f"Error checking git status: {e}")
            return {"error": str(e)}
    
    def add_files(self, file_paths: List[str]) -> bool:
        """
        Add files to git staging area.
        
        Args:
            file_paths: List of file paths to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        try:
            self.repo.index.add(file_paths)
            logger.info(f"Added files to staging: {file_paths}")
            return True
        except Exception as e:
            logger.error(f"Error adding files to git: {e}")
            return False
    
    def commit_changes(self, message: str, author: Optional[str] = None) -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            author: Optional author string (format: "Name <email>")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        try:
            # Check if there are changes to commit
            if not self.repo.is_dirty() and not self.repo.untracked_files:
                logger.warning("No changes to commit")
                return True
            
            # Add all changed files
            self.repo.git.add(A=True)
            
            # Create commit
            if author:
                commit = self.repo.index.commit(message, author=author)
            else:
                commit = self.repo.index.commit(message)
            
            logger.info(f"Created commit: {commit.hexsha} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    def push_changes(self, remote: Optional[str] = None, branch: Optional[str] = None) -> bool:
        """
        Push changes to remote repository.
        
        Args:
            remote: Remote name (defaults to config.git_remote)
            branch: Branch name (defaults to config.git_branch)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        remote_name = remote or self.config.git_remote
        branch_name = branch or self.config.git_branch
        
        try:
            origin = self.repo.remote(remote_name)
            push_info = origin.push(refspec=f"{branch_name}:{branch_name}")
            
            # Check if push was successful
            if push_info and push_info[0].flags & push_info[0].ERROR:
                logger.error(f"Push failed: {push_info[0].summary}")
                return False
            
            logger.info(f"Successfully pushed to {remote_name}/{branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error pushing changes: {e}")
            return False
    
    def deploy(self) -> bool:
        """
        Deploy the website (commit + push + trigger Netlify build).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check status
            status = self.check_status()
            if "error" in status:
                return False
            
            # Commit changes if there are any
            if status["is_dirty"] or status["untracked_files"]:
                commit_message = f"Deploy: Update blog posts - {status['modified_files'] + status['untracked_files']}"
                if not self.commit_changes(commit_message):
                    return False
            
            # Push changes
            if not self.push_changes():
                return False
            
            # Trigger Netlify deployment (if configured)
            self._trigger_netlify_deploy()
            
            logger.info("Deployment completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during deployment: {e}")
            return False
    
    def _trigger_netlify_deploy(self) -> None:
        """
        Trigger Netlify deployment using the deploy script.
        """
        try:
            # Look for deployment script
            deploy_script = self.website_path / "deployment" / "deploy.sh"
            
            if deploy_script.exists():
                logger.info("Triggering Netlify deployment...")
                result = subprocess.run(
                    ["bash", str(deploy_script)],
                    cwd=self.website_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    logger.info("Netlify deployment triggered successfully")
                else:
                    logger.error(f"Netlify deployment failed: {result.stderr}")
            else:
                logger.warning("No deployment script found, skipping Netlify deployment")
                
        except subprocess.TimeoutExpired:
            logger.error("Netlify deployment timed out")
        except Exception as e:
            logger.error(f"Error triggering Netlify deployment: {e}")
    
    def create_branch(self, branch_name: str) -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            
        Returns:
            True if successful, False otherwise
        """
        if not self.repo:
            logger.error("Repository not initialized")
            return False
        
        try:
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            logger.info(f"Created and checked out branch: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating branch {branch_name}: {e}")
            return False
    
    def get_recent_commits(self, count: int = 5) -> List[dict]:
        """
        Get recent commits.
        
        Args:
            count: Number of recent commits to retrieve
            
        Returns:
            List of commit information dictionaries
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits(max_count=count):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                })
            return commits
        except Exception as e:
            logger.error(f"Error getting recent commits: {e}")
            return []