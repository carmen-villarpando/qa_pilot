"""Value analyzer for determining if a GitHub issue provides evaluation value."""

import logging

from ai_client import AIClient

from .models import ComponentDetection

logger = logging.getLogger(__name__)


class ValueAnalyzer:
    """Analyzes whether a GitHub issue provides value for evaluation purposes."""

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def analyze_evaluation_value(
        self,
        components: ComponentDetection,
        issue_title: str,
        issue_body: str,
        issue_type: str,
    ) -> tuple:
        """Analyze if the issue provides value for evaluation purposes.

        Returns:
            tuple: (provides_value: bool, assessment: str)
        """
        # Quick check for obvious non-valuable issues
        quick_result = self._quick_value_check(
            issue_title, issue_body, issue_type, components
        )
        if quick_result is not None:
            return quick_result

        # Use AI for detailed analysis
        try:
            prompt = self._build_value_analysis_prompt(
                components, issue_title, issue_body, issue_type
            )
            response = self.ai_client.generate_completion_sync(prompt)

            if response:
                return self._parse_value_response(response)
        except Exception as e:
            logger.warning(f"Failed to analyze evaluation value: {e}")

        # Default to valuable if analysis fails
        return True, "Could not determine value, defaulting to valuable"

    def _quick_value_check(
        self,
        issue_title: str,
        issue_body: str,
        issue_type: str,
        components: ComponentDetection,
    ) -> tuple or None:
        """Quick check for obvious non-valuable issues."""
        text = f"{issue_title} {issue_body}".lower()

        # Issues that typically don't provide evaluation value
        non_valuable_keywords = [
            "documentation",
            "readme",
            "typo",
            "spelling",
            "formatting",
            "comment",
            "refactor only",
            "cleanup",
            "style",
            "lint",
        ]

        if any(keyword in text for keyword in non_valuable_keywords):
            return (
                False,
                f"Issue appears to be {non_valuable_keywords[0]}-related, unlikely to provide evaluation value",
            )

        # Issues without AI components typically don't provide evaluation value
        if not components.conversational_ai and not components.backend_api:
            return (
                False,
                "Issue does not involve AI or backend components, unlikely to provide evaluation value",
            )

        # Tech debt and bugs with AI components are typically valuable
        if issue_type in ["Bug", "Tech Debt"] and components.conversational_ai:
            return (
                True,
                f"{issue_type} involving AI components typically provides evaluation value",
            )

        return None  # Need AI analysis

    def _build_value_analysis_prompt(
        self,
        components: ComponentDetection,
        issue_title: str,
        issue_body: str,
        issue_type: str,
    ) -> str:
        """Build prompt for AI to analyze evaluation value."""
        context_parts = []
        context_parts.append(f"Issue: {issue_title}")
        context_parts.append(f"Type: {issue_type}")
        if issue_body:
            context_parts.append(f"Description: {issue_body[:800]}...")

        component_info = []
        if components.frontend:
            component_info.append("Frontend UI")
        if components.backend_api:
            component_info.append("Backend API")
        if components.conversational_ai:
            component_info.append("Conversational AI")
        context_parts.append(f"Components: {', '.join(component_info)}")

        context = "\n".join(context_parts)

        prompt = f"""Analyze the following GitHub issue to determine if it provides value for AI/LLM evaluation purposes.

{context}

Consider whether this issue:
1. Involves AI/LLM functionality that would benefit from evaluation
2. Introduces new features or changes that require quality assessment
3. Affects user-facing AI interactions that should be tested
4. Has business impact that warrants evaluation investment
5. Changes behavior that existing metrics should validate

Respond with:
"Provides value: [yes/no]"
"Reasoning: [your explanation why/why not this issue provides evaluation value]"""

        return prompt

    def _parse_value_response(self, response: str) -> tuple:
        """Parse AI response to determine value assessment."""
        response_lower = response.lower()

        if "provides value: no" in response_lower:
            reasoning = ""
            for line in response.split("\n"):
                if "reasoning:" in line.lower():
                    reasoning = line.split(":", 1)[1].strip()
                    break
            return (
                False,
                reasoning or "AI determined issue does not provide evaluation value",
            )

        # Default to valuable
        reasoning = ""
        for line in response.split("\n"):
            if "reasoning:" in line.lower():
                reasoning = line.split(":", 1)[1].strip()
                break
        return True, reasoning or "AI determined issue provides evaluation value"
