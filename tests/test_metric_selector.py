"""Tests for metric selector."""

from app.deepeval_copilot.metric_selector import MetricSelector
from app.deepeval_copilot.models import ComponentDetection


class TestMetricSelector:
    """Test metric selection logic."""

    def test_select_metrics_for_ai_components(self):
        """Test metric selection for AI components."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=True,
            backend_api=True,
            conversational_ai=True,
            reasoning="All components detected",
            confidence=0.95,
        )

        metrics = selector.select_metrics(components, "Story", "Add chatbot support")

        # Should select at least Answer Relevancy for AI
        assert len(metrics) > 0
        assert any("Answer Relevancy" in m.name for m in metrics)

    def test_select_metrics_for_conversation(self):
        """Test metric selection for conversation-focused issues."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7,
        )

        metrics = selector.select_metrics(
            components, "Story", "Improve conversation context management"
        )

        # Should select Conversation Relevancy for conversation issues
        assert len(metrics) > 0
        assert any("Conversation Relevancy" in m.name for m in metrics)

    def test_select_metrics_for_rag(self):
        """Test metric selection for RAG applications."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7,
        )

        metrics = selector.select_metrics(
            components, "Story", "Implement RAG for document retrieval"
        )

        # Should select Faithfulness for RAG
        assert len(metrics) > 0
        assert any("Faithfulness" in m.name for m in metrics)

    def test_select_metrics_no_ai_components(self):
        """Test metric selection when no AI components detected."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=True,
            backend_api=False,
            conversational_ai=False,
            reasoning="Only frontend detected",
            confidence=0.7,
        )

        metrics = selector.select_metrics(components, "Story", "Fix button styling")

        # Should not select any metrics for non-AI issues
        assert len(metrics) == 0

    def test_metric_code_snippets(self):
        """Test that metric code snippets are valid."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7,
        )

        metrics = selector.select_metrics(components, "Story", "Add chatbot")

        for metric in metrics:
            assert metric.code_snippet is not None
            assert len(metric.code_snippet) > 0
            assert "from deepeval" in metric.code_snippet
            assert metric.threshold > 0

    def test_metric_reasoning(self):
        """Test that metric reasoning is generated."""
        selector = MetricSelector()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7,
        )

        metrics = selector.select_metrics(components, "Story", "Add chatbot")

        for metric in metrics:
            assert metric.reason is not None
            assert len(metric.reason) > 0
