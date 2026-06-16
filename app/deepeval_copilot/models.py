"""Data models for DeepEval Copilot analysis."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ComponentDetection:
    """Detection of components involved in the issue."""
    frontend: bool
    backend_api: bool
    conversational_ai: bool
    reasoning: str
    confidence: float


@dataclass
class MetricRecommendation:
    """Recommended metric for the issue."""
    name: str
    reason: str
    applies: bool
    priority: str  # High, Medium, Low


@dataclass
class EvaluationData:
    """Suggested evaluation data (questions and ground truth)."""
    question: str
    ground_truth: str
    metric_name: str
    business_context: str


@dataclass
class NewMetricSuggestion:
    """Suggestion for a new business-specific metric."""
    name: str
    description: str
    evaluation_steps: List[str]
    reason_for_creation: str


@dataclass
class ConversationalTestCase:
    """Specific conversational test case for business scenarios."""
    scenario: str
    expected_behavior: str
    business_value: str


@dataclass
class PromptInjectionTest:
    """Prompt injection test suggestion."""
    attack_scenario: str
    expected_protection: str
    relevance: str


@dataclass
class QualityRisk:
    """Quality risk identified in the issue."""
    level: str  # High, Medium, Low
    description: str
    mitigation: str


@dataclass
class DeepEvalStrategy:
    """Complete DeepEval evaluation strategy for a GitHub Issue."""
    issue_type: str  # Story, Bug, Tech Debt
    issue_title: str
    components: ComponentDetection
    evaluation_focus: List[str]  # What to evaluate
    
    # Metric analysis
    metric_recommendations: List[MetricRecommendation]
    new_metric_suggestions: List[NewMetricSuggestion]
    
    # Evaluation data
    evaluation_data: List[EvaluationData]  # Questions + ground truth for CSV
    
    # Test cases
    conversational_test_cases: List[ConversationalTestCase]
    prompt_injection_tests: List[PromptInjectionTest]
    
    # Risk and recommendations
    quality_risks: List[QualityRisk]
    recommendations: List[str]
    
    # Overall assessment
    provides_evaluation_value: bool  # Whether this issue provides value for evaluation
    value_assessment: str  # Explanation of why/why not
