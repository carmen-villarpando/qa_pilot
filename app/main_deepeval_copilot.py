"""Main entry point for GitHub Actions to run DeepEval Copilot."""

import asyncio
import logging
import os
import sys

from deepeval_copilot.deepeval_copilot import DeepEvalCopilot
from github_client import GitHubClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main function for GitHub Actions."""
    try:
        # Get environment variables
        repo_name = os.getenv("REPO_NAME")
        issue_number = int(os.getenv("ISSUE_NUMBER", "0"))
        comment_body = os.getenv("COMMENT_BODY", "")
        comment_author = os.getenv("COMMENT_AUTHOR", "")

        logger.info(f"Processing issue {issue_number} in {repo_name}")

        if not all([repo_name, issue_number, comment_body, comment_author]):
            logger.error("Missing required environment variables")
            sys.exit(1)

        # Check if comment contains the trigger command
        if "/deepeval-strategy" not in comment_body.lower():
            logger.info("Comment does not contain deepeval-strategy command")
            sys.exit(0)

        # Create GitHub client and get issue
        github_client = GitHubClient.from_env()
        issue = github_client.get_issue(repo_name, issue_number)

        if not issue:
            logger.error(f"Could not find issue {issue_number} in {repo_name}")
            sys.exit(1)

        title = issue.title
        body = issue.body or ""
        labels = [label.name for label in issue.get_labels()]

        logger.info(f"Analyzing issue: '{title}'")

        # Add reaction to indicate processing
        try:
            issue.create_reaction("+1")
        except Exception as e:
            logger.warning(f"Could not add reaction: {e}")

        # Create DeepEval Copilot and analyze issue
        copilot = DeepEvalCopilot.from_env()
        strategy = copilot.analyze_issue(title, body, labels)

        # Format strategy as GitHub comment
        comment = copilot.format_strategy_as_comment(strategy)

        # Add comment to issue
        success = github_client.add_comment(repo_name, issue_number, comment)

        if success:
            logger.info("DeepEval strategy comment added successfully")
            sys.exit(0)
        else:
            logger.error("Failed to add DeepEval strategy comment")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
