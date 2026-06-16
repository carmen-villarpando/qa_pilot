"""QA Pilot for analyzing GitHub issues and generating test strategies."""

import logging
import os
from typing import Dict, List, Any

from .ai_client import AIClient

logger = logging.getLogger(__name__)


class QAPilot:
    """QA Pilot for analyzing issues and generating test strategies."""

    def __init__(self, ai_client: AIClient):
        """Initialize QA Pilot with AI client."""
        self.ai_client = ai_client

    @classmethod
    def from_env(cls) -> "QAPilot":
        """Create QA Pilot from environment variables."""
        ai_client = AIClient.from_env()
        return cls(ai_client)

    def analyze_issue(self, title: str, body: str, labels: List[str]) -> Dict[str, Any]:
        """Analyze a GitHub issue and generate QA analysis."""
        prompt = self._build_analysis_prompt(title, body, labels)
        
        try:
            response = self.ai_client.generate_response(prompt)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Error analyzing issue: {e}")
            raise

    def _build_analysis_prompt(self, title: str, body: str, labels: List[str]) -> str:
        """Build the analysis prompt for the AI."""
        return f"""Analyze this GitHub Issue as a Senior QA Engineer specialized in AI Testing.

Issue Title: {title}
Issue Description: {body}
Labels: {', '.join(labels) if labels else 'None'}

Generate:
- Quality Risks
- Recommended DeepEval Metrics
- Evaluation Questions
- Ground Truths
- Prompt Injection Scenarios

Return markdown in this exact format:

## QA_Pilot Analysis

### Quality Risks

1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

---

### Recommended DeepEval Metrics

- [Metric 1]
- [Metric 2]
- [Metric 3]

---

### Evaluation Dataset

#### [Metric 1 Name]

Question: [Question 1]
Ground Truth: [Ground truth 1]

Question: [Question 2]
Ground Truth: [Ground truth 2]

#### [Metric 2 Name]

Question: [Question 1]
Ground Truth: [Ground truth 1]

---

### Prompt Injection

Question: [Injection scenario 1]
Ground Truth: [Expected response 1]

Question: [Injection scenario 2]
Ground Truth: [Expected response 2]

Focus on mortgage payment assistant scenarios if relevant, otherwise provide general AI testing patterns."""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        return {
            "raw_response": response,
            "formatted": True
        }

    def format_analysis_as_comment(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis as a GitHub comment."""
        return analysis["raw_response"]
