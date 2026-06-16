"""DeepEval Copilot module for AI-powered evaluation strategy generation."""

from .deepeval_copilot import DeepEvalCopilot
from .models import (
    ComponentDetection,
    ConversationalTestCase,
    ConversationalTurn,
    CSVTestRow,
    DeepEvalStrategy,
    EvaluationData,
    MetricRecommendation,
    NewMetricSuggestion,
    PromptInjectionTest,
    QualityRisk,
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
    "QualityRisk",
]
