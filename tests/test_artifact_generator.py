"""Tests for artifact generator."""

from app.deepeval_copilot.artifact_generator import ArtifactGenerator
from app.deepeval_copilot.models import (
    ComponentDetection,
    DeepEvalMetric,
    DeepEvalStrategy,
    EvaluationScenario,
    QualityRisk,
)


class TestArtifactGenerator:
    """Test artifact generation logic."""

    def test_generate_deepeval_code(self):
        """Test complete DeepEval code generation."""
        generator = ArtifactGenerator()

        # Create a sample strategy
        components = ComponentDetection(
            frontend=True,
            backend_api=True,
            conversational_ai=True,
            reasoning="All components detected",
            confidence=0.95,
        )

        metrics = [
            DeepEvalMetric(
                name="Answer Relevancy",
                reason="Ensures responses are relevant",
                code_snippet="from deepeval.metrics import AnswerRelevancyMetric\nanswer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)",
                threshold=0.7,
            )
        ]

        scenarios = [
            EvaluationScenario(
                scenario="User asks about transaction",
                expected_behavior="Assistant provides accurate information",
                metric_type="Answer Relevancy",
            )
        ]

        risks = [
            QualityRisk(
                level="High",
                description="Context may be lost",
                mitigation="Implement context management",
            )
        ]

        strategy = DeepEvalStrategy(
            issue_type="Story",
            issue_title="Add chatbot support",
            components=components,
            evaluation_focus=["Frontend", "Backend", "AI"],
            deepeval_metrics=metrics,
            conversational_scenarios=scenarios,
            prompt_injection_scenarios=[],
            deepeval_code="",
            quality_risks=risks,
            recommendations=["Implement metrics"],
        )

        code = generator.generate_deepeval_code(strategy)

        # Verify code structure
        assert code is not None
        assert len(code) > 0
        assert "from deepeval import evaluate" in code
        assert "from deepeval.test_case import ConversationalTestCase" in code
        assert "Answer Relevancy" in code
        assert "User asks about transaction" in code

    def test_generate_imports(self):
        """Test import generation."""
        generator = ArtifactGenerator()

        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI detected",
            confidence=0.7,
        )

        metrics = [
            DeepEvalMetric(
                name="Answer Relevancy",
                reason="Test",
                code_snippet="test",
                threshold=0.7,
            )
        ]

        strategy = DeepEvalStrategy(
            issue_type="Story",
            issue_title="Test",
            components=components,
            evaluation_focus=["AI"],
            deepeval_metrics=metrics,
            conversational_scenarios=[],
            prompt_injection_scenarios=[],
            deepeval_code="",
            quality_risks=[],
            recommendations=[],
        )

        imports = generator._generate_imports(strategy)

        assert "from deepeval import evaluate" in imports
        assert "from deepeval.test_case import ConversationalTestCase" in imports
        assert "from deepeval.metrics import AnswerRelevancyMetric" in imports

    def test_generate_metrics(self):
        """Test metric code generation."""
        generator = ArtifactGenerator()

        metrics = [
            DeepEvalMetric(
                name="Answer Relevancy",
                reason="Ensures relevance",
                code_snippet="answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)",
                threshold=0.7,
            )
        ]

        metrics_code = generator._generate_metrics(metrics)

        assert "Answer Relevancy" in metrics_code
        assert "Ensures relevance" in metrics_code
        assert "AnswerRelevancyMetric" in metrics_code

    def test_generate_test_cases(self):
        """Test test case generation."""
        generator = ArtifactGenerator()

        scenarios = [
            EvaluationScenario(
                scenario="User asks question",
                expected_behavior="Assistant answers",
                metric_type="Answer Relevancy",
            )
        ]

        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI detected",
            confidence=0.7,
        )

        strategy = DeepEvalStrategy(
            issue_type="Story",
            issue_title="Test",
            components=components,
            evaluation_focus=["AI"],
            deepeval_metrics=[],
            conversational_scenarios=scenarios,
            prompt_injection_scenarios=[],
            deepeval_code="",
            quality_risks=[],
            recommendations=[],
        )

        test_cases_code = generator._generate_test_cases(strategy)

        assert "User asks question" in test_cases_code
        assert "Assistant answers" in test_cases_code
        assert "ConversationalTestCase" in test_cases_code

    def test_generate_empty_strategy(self):
        """Test generation with empty strategy."""
        generator = ArtifactGenerator()

        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=False,
            reasoning="No components",
            confidence=0.3,
        )

        strategy = DeepEvalStrategy(
            issue_type="Story",
            issue_title="Test",
            components=components,
            evaluation_focus=[],
            deepeval_metrics=[],
            conversational_scenarios=[],
            prompt_injection_scenarios=[],
            deepeval_code="",
            quality_risks=[],
            recommendations=[],
        )

        code = generator.generate_deepeval_code(strategy)

        # Should still generate valid code structure
        assert code is not None
        assert len(code) > 0
