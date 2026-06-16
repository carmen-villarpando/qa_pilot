"""DeepEval metric selection engine with intelligent reasoning using custom GEval metrics."""

import logging
from typing import List

from .models import ComponentDetection, DeepEvalMetric
from metrics_config import get_relevant_metrics, get_metric_config

logger = logging.getLogger(__name__)


class MetricSelector:
    """Selects appropriate custom GEval metrics based on component detection and issue context."""

    def select_metrics(
        self,
        components: ComponentDetection,
        issue_type: str,
        issue_title: str,
        issue_body: str = ""
    ) -> List[DeepEvalMetric]:
        """Select appropriate custom GEval metrics based on components and issue context."""
        selected_metrics = []
        
        # Get relevant metrics from user's custom GEval metrics
        relevant_metric_names = get_relevant_metrics(issue_title, issue_body)
        
        for metric_name in relevant_metric_names:
            metric_config = get_metric_config(metric_name)
            if metric_config:
                selected_metrics.append(self._create_custom_metric(metric_name, metric_config, issue_title))
        
        logger.info(f"Selected {len(selected_metrics)} custom GEval metrics for issue: {issue_title}")
        return selected_metrics

    def _create_custom_metric(self, metric_name: str, metric_config: dict, issue_title: str) -> DeepEvalMetric:
        """Create a DeepEvalMetric from custom GEval metric configuration."""
        # Generate GEval code snippet
        code_snippet = self._generate_geval_code(metric_name, metric_config)
        
        return DeepEvalMetric(
            name=metric_config["name"],
            reason=f"{metric_config['description']}. Selected based on issue context: '{issue_title}'",
            code_snippet=code_snippet,
            threshold=metric_config["threshold"]
        )

    def _generate_geval_code(self, metric_name: str, metric_config: dict) -> str:
        """Generate GEval metric code snippet."""
        evaluation_steps_str = "\n        ".join([
            f'"{step}"' for step in metric_config["evaluation_steps"]
        ])
        
        # Handle different evaluation_params
        evaluation_params = metric_config.get("evaluation_params", ["ACTUAL_OUTPUT"])
        if "EXPECTED_OUTPUT" in evaluation_params:
            params_str = "[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT]"
        else:
            params_str = "[LLMTestCaseParams.ACTUAL_OUTPUT]"
        
        code = f"""{metric_name} = GEval(
    name="{metric_config['name']}",
    evaluation_steps=[
        {evaluation_steps_str}
    ],
    evaluation_params={params_str},
    threshold={metric_config['threshold']},
    model=local_model,
)"""
        return code
