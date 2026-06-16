"""New metric analyzer for identifying business-specific metric needs."""

import logging

from ai_client import AIClient

from .models import ComponentDetection, NewMetricSuggestion

logger = logging.getLogger(__name__)


class NewMetricAnalyzer:
    """Analyzes issue to identify if new business-specific metrics are needed."""

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def analyze_new_metric_needs(
        self,
        components: ComponentDetection,
        issue_title: str,
        issue_body: str,
        existing_metrics: list,
    ) -> list[NewMetricSuggestion]:
        """Analyze if new business-specific metrics are needed for this issue."""
        suggestions = []

        # Only analyze if this is a significant change or new feature
        if not self._should_analyze_for_new_metrics(issue_title, issue_body):
            logger.info("Issue does not warrant new metric analysis")
            return suggestions

        # Use AI to determine if new metrics are needed
        try:
            prompt = self._build_new_metric_prompt(
                components, issue_title, issue_body, existing_metrics
            )
            response = self.ai_client.generate_completion_sync(prompt)

            if response:
                suggestions = self._parse_new_metric_response(response)
        except Exception as e:
            logger.warning(f"Failed to analyze new metric needs: {e}")

        logger.info(
            f"Identified {len(suggestions)} new metric suggestions for issue: {issue_title}"
        )
        return suggestions

    def _should_analyze_for_new_metrics(
        self, issue_title: str, issue_body: str
    ) -> bool:
        """Determine if the issue warrants analysis for new metrics."""
        # Keywords that might indicate need for new metrics
        new_feature_keywords = [
            "new feature",
            "new functionality",
            "add",
            "implement",
            "create",
        ]
        business_keywords = [
            "business",
            "financial",
            "payment",
            "loan",
            "account",
            "mortgage",
        ]

        text = f"{issue_title} {issue_body}".lower()

        # Check if this is a new feature with business context
        has_new_feature = any(keyword in text for keyword in new_feature_keywords)
        has_business_context = any(keyword in text for keyword in business_keywords)

        return has_new_feature and has_business_context

    def _build_new_metric_prompt(
        self,
        components: ComponentDetection,
        issue_title: str,
        issue_body: str,
        existing_metrics: list,
    ) -> str:
        """Build prompt for AI to analyze new metric needs."""
        context_parts = []
        context_parts.append(f"Issue: {issue_title}")
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

        existing_metric_names = (
            [m.name for m in existing_metrics] if existing_metrics else []
        )
        if existing_metric_names:
            context_parts.append(
                f"Existing Metrics: {', '.join(existing_metric_names)}"
            )

        context = "\n".join(context_parts)

        prompt = f"""Analyze the following GitHub issue to determine if new business-specific evaluation metrics are needed.

{context}

Consider whether:
1. The issue introduces new functionality that existing metrics don't adequately evaluate
2. The change requires domain-specific evaluation criteria
3. Business rules or compliance requirements need specific metric validation
4. The functionality has unique quality characteristics not covered by current metrics

If new metrics are needed, suggest them in Python code format with complete structure like:

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

eval_new_metric = GEval(
    name="[Metric Name]",
    evaluation_steps=(
        "1. [Step 1]",
        "2. [Step 2]",
        "3. [Step 3]",
        "4. [Step 4]",
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        # Add other relevant params
    ],
    threshold=0.85,
    model=local_model,
)
```

Requirements for new metrics:
- Must be specific to mortgage/payment assistance domain
- Include 3-5 detailed evaluation steps
- Specify relevant evaluation parameters
- Include appropriate threshold (0.85-0.90)
- Must address unique business risks or requirements
- Should not duplicate existing metrics: {', '.join(existing_metric_names)}

If no new metrics are needed, respond with: "No new metrics required - existing metrics adequately cover this functionality."

Provide 0-2 new metric suggestions maximum, only if truly necessary."""

        return prompt

    def _parse_new_metric_response(self, response: str) -> list[NewMetricSuggestion]:
        """Parse AI response into NewMetricSuggestion objects."""
        suggestions = []

        if "No new metrics" in response:
            return suggestions

        try:
            # Parse Python code format
            if "GEval(" in response:
                suggestions = self._parse_python_metric_format(response)
            else:
                # Fallback to simple text format
                suggestions = self._parse_text_metric_format(response)

        except Exception as e:
            logger.warning(f"Failed to parse new metric response: {e}")

        return suggestions

    def _parse_python_metric_format(self, response: str) -> list[NewMetricSuggestion]:
        """Parse Python code format for metrics."""
        suggestions = []

        # Extract metric definitions between GEval( and )
        import re

        pattern = r'eval_\w+\s*=\s*GEval\(\s*name="([^"]+)"[^)]*evaluation_steps=\(([^)]+)\)[^)]*\)'
        matches = re.findall(pattern, response, re.DOTALL)

        for name, steps_text in matches:
            # Parse evaluation steps
            steps = []
            for step in steps_text.split("\n"):
                step = step.strip()
                if step and (step.startswith('"') or step.startswith("'")):
                    # Remove quotes and step number
                    clean_step = step.strip("\"'")
                    if ". " in clean_step:
                        clean_step = clean_step.split(". ", 1)[1]
                    steps.append(clean_step)

            # Extract description from context
            description = f"Business-specific metric for {name}"
            reason = "Required for mortgage/payment assistance domain evaluation"

            suggestions.append(
                NewMetricSuggestion(
                    name=name.strip(),
                    description=description,
                    evaluation_steps=steps,
                    reason_for_creation=reason,
                )
            )

        return suggestions

    def _parse_text_metric_format(self, response: str) -> list[NewMetricSuggestion]:
        """Parse simple text format for metrics."""
        suggestions = []
        try:
            lines = response.strip().split("\n")
            current_suggestion = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("Name:"):
                    if current_suggestion:
                        suggestions.append(
                            self._create_new_metric_suggestion(current_suggestion)
                        )
                    current_suggestion = {"name": line[5:].strip()}
                elif line.startswith("Description:"):
                    current_suggestion["description"] = line[12:].strip()
                elif line.startswith("Evaluation Steps:"):
                    current_suggestion["evaluation_steps"] = []
                elif (
                    line.startswith("-")
                    and current_suggestion.get("evaluation_steps") is not None
                ):
                    current_suggestion["evaluation_steps"].append(line[1:].strip())
                elif line.startswith("Reason:"):
                    current_suggestion["reason_for_creation"] = line[7:].strip()

            if current_suggestion:
                suggestions.append(
                    self._create_new_metric_suggestion(current_suggestion)
                )

        except Exception as e:
            logger.warning(f"Failed to parse new metric response: {e}")

        return suggestions

    def _create_new_metric_suggestion(self, data: dict) -> NewMetricSuggestion:
        """Create NewMetricSuggestion object from parsed data."""
        return NewMetricSuggestion(
            name=data.get("name", ""),
            description=data.get("description", ""),
            evaluation_steps=data.get("evaluation_steps", []),
            reason_for_creation=data.get("reason_for_creation", ""),
        )
