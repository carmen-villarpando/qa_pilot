"""GitHub API client for issue management."""

import logging
import os

from github import Github, GithubException
from github.Issue import Issue

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str):
        """Initialize GitHub client with token."""
        self.github = Github(token)
        # Store only token hash for logging (security)
        self._token_hash = hash(token) if token else None

    def get_issue(self, repo_name: str, issue_number: int) -> Issue | None:
        """Get issue by repository and number."""
        try:
            repo = self.github.get_repo(repo_name)
            return repo.get_issue(issue_number)
        except GithubException as e:
            logger.error(f"Error getting issue {issue_number} from {repo_name}: {e}")
            return None

    def add_comment(self, repo_name: str, issue_number: int, comment: str) -> bool:
        """Add comment to issue."""
        try:
            issue = self.get_issue(repo_name, issue_number)
            if not issue:
                return False

            issue.create_comment(comment)
            logger.info(f"Successfully added comment to issue {issue_number} in {repo_name}")
            return True
        except GithubException as e:
            logger.error(f"Error adding comment to issue {issue_number} in {repo_name}: {e}")
            return False

    def get_repo_labels(self, repo_name: str) -> list[str]:
        """Get all available labels in repository."""
        try:
            repo = self.github.get_repo(repo_name)
            return [label.name for label in repo.get_labels()]
        except GithubException as e:
            logger.error(f"Error getting labels from {repo_name}: {e}")
            return []

    @staticmethod
    def from_env() -> "GitHubClient":
        """Create GitHub client from environment variables."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        return GitHubClient(token)
