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
class DeepEvalMetric:
    """DeepEval metric recommendation with reasoning."""
    name: str
    reason: str
    code_snippet: str
    threshold: float


@dataclass
class EvaluationScenario:
    """Evaluation scenario for testing."""
    scenario: str
    expected_behavior: str
    metric_type: str


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
    deepeval_metrics: List[DeepEvalMetric]
    conversational_scenarios: List[EvaluationScenario]
    prompt_injection_scenarios: List[EvaluationScenario]
    deepeval_code: str  # Ready-to-use Python code
    quality_risks: List[QualityRisk]
    recommendations: List[str]
