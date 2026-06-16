"""Tests for component detector."""

from app.deepeval_copilot.component_detector import ComponentDetector


class TestComponentDetector:
    """Test component detection logic."""

    def test_detect_frontend_components(self):
        """Test detection of frontend components."""
        detector = ComponentDetector()

        # Test with frontend keywords
        result = detector.detect_components("Fix button click issue")
        assert result.frontend is True
        assert result.backend_api is False
        assert result.conversational_ai is False

        result = detector.detect_components("UI interface not responsive")
        assert result.frontend is True

        result = detector.detect_components("Chatbot widget not loading")
        assert result.frontend is True

    def test_detect_backend_components(self):
        """Test detection of backend components."""
        detector = ComponentDetector()

        # Test with backend keywords
        result = detector.detect_components("API endpoint timeout")
        assert result.backend_api is True
        assert result.frontend is False

        result = detector.detect_components("Database connection failed")
        assert result.backend_api is True

        result = detector.detect_components("Authentication service error")
        assert result.backend_api is True

    def test_detect_ai_components(self):
        """Test detection of AI components."""
        detector = ComponentDetector()

        # Test with AI keywords
        result = detector.detect_components("Chatbot not responding")
        assert result.conversational_ai is True
        assert result.frontend is False

        result = detector.detect_components("LLM integration issue")
        assert result.conversational_ai is True

        result = detector.detect_components("Conversation context lost")
        assert result.conversational_ai is True

    def test_detect_multiple_components(self):
        """Test detection of multiple components."""
        detector = ComponentDetector()

        # Test with multiple component types
        result = detector.detect_components("Chatbot API endpoint timeout")
        assert result.backend_api is True
        assert result.conversational_ai is True

        result = detector.detect_components("Chatbot widget UI not responsive")
        assert result.frontend is True
        assert result.conversational_ai is True

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        detector = ComponentDetector()

        # No components detected
        result = detector.detect_components("Generic issue")
        assert result.confidence == 0.3

        # Single component
        result = detector.detect_components("Button not working")
        assert result.confidence == 0.7

        # Two components
        result = detector.detect_components("Chatbot API timeout")
        assert result.confidence == 0.85

        # All three components
        result = detector.detect_components("Chatbot widget API integration")
        assert result.confidence == 0.95

    def test_reasoning_generation(self):
        """Test reasoning generation."""
        detector = ComponentDetector()

        result = detector.detect_components("Chatbot widget not working")
        assert "Frontend components" in result.reasoning
        assert "Conversational AI components" in result.reasoning

        result = detector.detect_components("Generic issue")
        assert "no specific components detected" in result.reasoning
