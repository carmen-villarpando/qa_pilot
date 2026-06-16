"""Evaluation data analyzer for suggesting questions and ground truth for CSV files."""

import logging

from ai_client import AIClient

from .models import ComponentDetection, EvaluationData, MetricRecommendation

logger = logging.getLogger(__name__)


class EvaluationDataAnalyzer:
    """Analyzes issue and suggests evaluation data (questions + ground truth) for CSV files."""

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def suggest_evaluation_data(
        self,
        components: ComponentDetection,
        metric_recommendations: list[MetricRecommendation],
        issue_title: str,
        issue_body: str,
    ) -> list[EvaluationData]:
        """Suggest evaluation data (questions and ground truth) for applicable metrics."""
        evaluation_data = []

        # Get applicable metrics
        applicable_metrics = [m for m in metric_recommendations if m.applies]

        if not applicable_metrics:
            logger.info("No applicable metrics, no evaluation data suggested")
            return evaluation_data

        # Use AI to generate specific evaluation data
        try:
            prompt = self._build_evaluation_data_prompt(
                components, applicable_metrics, issue_title, issue_body
            )
            response = self.ai_client.generate_completion_sync(prompt)

            if response:
                evaluation_data = self._parse_evaluation_data_response(
                    response, applicable_metrics
                )
        except Exception as e:
            logger.warning(f"Failed to generate evaluation data suggestions: {e}")

        logger.info(
            f"Suggested {len(evaluation_data)} evaluation data entries for issue: {issue_title}"
        )
        return evaluation_data

    def _build_evaluation_data_prompt(
        self,
        components: ComponentDetection,
        applicable_metrics: list[MetricRecommendation],
        issue_title: str,
        issue_body: str,
    ) -> str:
        """Build prompt for AI to generate evaluation data suggestions."""
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

        metric_info = []
        for metric in applicable_metrics:
            metric_info.append(f"- {metric.name} ({metric.priority} priority)")
        context_parts.append("Applicable Metrics:\n" + "\n".join(metric_info))

        context = "\n".join(context_parts)

        prompt = f"""Based on the following GitHub issue context, suggest 3-5 specific evaluation data entries (questions and ground truth) that would be valuable to add to a CSV file for testing the applicable metrics.

{context}

For each evaluation data entry, provide:
1. A specific question or scenario relevant to the issue
2. The expected ground truth or correct response
3. Which metric this data should evaluate
4. The business context (why this specific test is valuable)

Format each entry as CSV-ready data:
question,ground_truth,metric_name,business_context
"[specific question]","[expected answer]","[metric name]","[why valuable]"

Requirements:
- Questions must be specific to the functionality described in the issue
- Cover important business scenarios and edge cases for mortgage/payment assistance
- Test actual user interactions mentioned in the issue
- Ground truth answers must be accurate and complete
- Use proper CSV escaping for quotes and commas
- Align with the applicable metrics: {', '.join([m.name for m in applicable_metrics])}

Example format:
"Can I set up automatic transfers between my savings and checking accounts?","Yes, you can set up automatic transfers between your savings and checking accounts through online banking or by visiting a branch.","Correctness","Tests basic transfer functionality"

Generate exactly 3-5 entries in CSV format."""

        return prompt

    def _parse_evaluation_data_response(
        self, response: str, applicable_metrics: list[MetricRecommendation]
    ) -> list[EvaluationData]:
        """Parse AI CSV response into EvaluationData objects."""
        evaluation_data = []

        try:
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()
                if not line or line.startswith("question,ground_truth"):
                    continue  # Skip header and empty lines

                # Parse CSV line
                if line.startswith('"') and '","' in line:
                    parts = line.split('","')
                    if len(parts) >= 4:
                        question = parts[0].strip('"')
                        ground_truth = parts[1].strip('"')
                        metric_name = parts[2].strip('"')
                        business_context = parts[3].strip('"')

                        # Clean up any remaining quotes
                        ground_truth = ground_truth.replace('""', '"')
                        business_context = business_context.replace('""', '"')

                        evaluation_data.append(
                            EvaluationData(
                                question=question,
                                ground_truth=ground_truth,
                                metric_name=metric_name,
                                business_context=business_context,
                            )
                        )

        except Exception as e:
            logger.warning(f"Failed to parse evaluation data response: {e}")
            # Fallback: try to parse as regular format
            return self._parse_fallback_format(response, applicable_metrics)

        return evaluation_data

    def _parse_fallback_format(
        self, response: str, applicable_metrics: list[MetricRecommendation]
    ) -> list[EvaluationData]:
        """Fallback parser for non-CSV format."""
        evaluation_data = []
        try:
            lines = response.strip().split("\n")
            current_data = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("Question:"):
                    if current_data:
                        evaluation_data.append(
                            self._create_evaluation_data(
                                current_data, applicable_metrics
                            )
                        )
                    current_data = {"question": line[9:].strip()}
                elif line.startswith("Ground Truth:"):
                    current_data["ground_truth"] = line[13:].strip()
                elif line.startswith("Metric:"):
                    current_data["metric_name"] = line[7:].strip()
                elif line.startswith("Business Context:"):
                    current_data["business_context"] = line[17:].strip()

            if current_data:
                evaluation_data.append(
                    self._create_evaluation_data(current_data, applicable_metrics)
                )

        except Exception as e:
            logger.warning(f"Fallback parsing also failed: {e}")

        return evaluation_data

    def _create_evaluation_data(
        self, data: dict, applicable_metrics: list[MetricRecommendation]
    ) -> EvaluationData:
        """Create EvaluationData object from parsed data."""
        # Find matching metric name
        metric_name = data.get("metric_name", "")
        if not metric_name and applicable_metrics:
            # Use first applicable metric as default
            metric_name = applicable_metrics[0].name

        return EvaluationData(
            question=data.get("question", ""),
            ground_truth=data.get("ground_truth", ""),
            metric_name=metric_name,
            business_context=data.get("business_context", ""),
        )
