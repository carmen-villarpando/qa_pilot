"""DeepEval Copilot module for AI-powered evaluation strategy generation."""

from .deepeval_copilot import DeepEvalCopilot
from .models import (
    DeepEvalStrategy,
    ComponentDetection,
    MetricRecommendation,
    EvaluationData,
    NewMetricSuggestion,
    ConversationalTestCase,
    ConversationalTurn,
    PromptInjectionTest,
    CSVTestRow,
    QualityRisk
)

__all__ = [
    "DeepEvalCopilot",
    "DeepEvalStrategy",
    "ComponentDetection",
    "MetricRecommendation",
    "EvaluationData",
    "NewMetricSuggestion",
    "ConversationalTestCase",
    "ConversationalTurn",
    "PromptInjectionTest",
    "CSVTestRow",
    "QualityRisk"
]
