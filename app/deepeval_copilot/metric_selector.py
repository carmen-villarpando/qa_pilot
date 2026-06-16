"""DeepEval metric selection engine with intelligent reasoning using custom GEval metrics."""

import logging
from typing import List

from .models import ComponentDetection, MetricRecommendation
from metrics_config import get_all_metric_names, get_metric_config

logger = logging.getLogger(__name__)


class MetricSelector:
    """Analyzes which metrics apply to the issue based on component detection and issue context."""

    def analyze_metric_applicability(
        self,
        components: ComponentDetection,
        issue_type: str,
        issue_title: str,
        issue_body: str = ""
    ) -> List[MetricRecommendation]:
        """Analyze which custom GEval metrics apply to the specific issue."""
        recommendations = []
        
        # Get all available metrics
        all_metric_names = get_all_metric_names()
        
        # Analyze issue context
        text = f"{issue_title} {issue_body}".lower()
        
        for metric_name in all_metric_names:
            metric_config = get_metric_config(metric_name)
            if not metric_config:
                continue
            
            # Determine if metric applies based on context
            applies, priority, reason = self._determine_metric_applicability(
                metric_name, metric_config, components, issue_type, text
            )
            
            recommendations.append(MetricRecommendation(
                name=metric_config["name"],
                reason=reason,
                applies=applies,
                priority=priority
            ))
        
        logger.info(f"Analyzed {len(recommendations)} metrics for issue: {issue_title}")
        return recommendations

    def _determine_metric_applicability(
        self,
        metric_name: str,
        metric_config: dict,
        components: ComponentDetection,
        issue_type: str,
        text: str
    ) -> tuple:
        """Determine if a metric applies and its priority."""
        applies = False
        priority = "Low"
        reason = ""
        
        # Core metrics for financial chatbot always apply
        core_metrics = ["correctness_metric", "compliance_metric", "pii_leakage_metric"]
        if metric_name in core_metrics and components.conversational_ai:
            applies = True
            priority = "High"
            reason = f"Core metric for financial chatbot: {metric_config.get('description', '')}"
            return applies, priority, reason
        
        # Check for keywords in issue text
        if "context_keywords" in metric_config:
            for keyword in metric_config["context_keywords"]:
                if keyword in text:
                    applies = True
                    priority = "Medium"
                    reason = f"Keyword '{keyword}' found in issue: {metric_config.get('description', '')}"
                    break
        
        # Check component-specific metrics
        if components.conversational_ai:
            conversational_metrics = ["professionalism_metric", "empathy_metric", "clarity_metric"]
            if metric_name in conversational_metrics:
                applies = True
                priority = "Medium"
                reason = f"Relevant for conversational AI: {metric_config.get('description', '')}"
        
        # Bug-specific metrics
        if issue_type == "Bug":
            if metric_name in ["consistency_metric", "correctness_metric"]:
                applies = True
                priority = "High"
                reason = f"Critical for bug fix: {metric_config.get('description', '')}"
        
        if not applies:
            reason = f"Metric does not apply to this issue context"
        
        return applies, priority, reason
