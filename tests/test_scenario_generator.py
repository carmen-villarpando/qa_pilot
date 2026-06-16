"""Tests for scenario generator."""

import pytest

from app.deepeval_copilot.scenario_generator import ScenarioGenerator
from app.deepeval_copilot.models import ComponentDetection


class TestScenarioGenerator:
    """Test scenario generation logic."""

    def test_generate_scenarios_for_ai_components(self):
        """Test scenario generation for AI components."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=True,
            backend_api=True,
            conversational_ai=True,
            reasoning="All components detected",
            confidence=0.95
        )
        
        scenarios = generator.generate_scenarios(components, "Add chatbot support")
        
        # Should generate scenarios for AI components
        assert len(scenarios) > 0
        assert all(scenario.scenario is not None for scenario in scenarios)
        assert all(scenario.expected_behavior is not None for scenario in scenarios)

    def test_generate_scenarios_no_ai_components(self):
        """Test scenario generation when no AI components detected."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=True,
            backend_api=False,
            conversational_ai=False,
            reasoning="Only frontend detected",
            confidence=0.7
        )
        
        scenarios = generator.generate_scenarios(components, "Fix button styling")
        
        # Should not generate scenarios for non-AI issues
        assert len(scenarios) == 0

    def test_generate_transaction_scenarios(self):
        """Test scenario generation for transaction-related issues."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7
        )
        
        scenarios = generator.generate_scenarios(components, "Chatbot for transaction disputes")
        
        # Should generate transaction-specific scenarios
        assert len(scenarios) > 0
        assert any("transaction" in scenario.scenario.lower() for scenario in scenarios)

    def test_generate_prompt_injection_scenarios(self):
        """Test prompt injection scenario generation."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7
        )
        
        scenarios = generator.generate_prompt_injection_scenarios(components, "Add chatbot")
        
        # Should generate prompt injection scenarios for AI components
        assert len(scenarios) > 0
        assert any("ignore previous instructions" in scenario.scenario.lower() for scenario in scenarios)

    def test_generate_prompt_injection_no_ai(self):
        """Test prompt injection scenarios when no AI detected."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=True,
            backend_api=False,
            conversational_ai=False,
            reasoning="Only frontend detected",
            confidence=0.7
        )
        
        scenarios = generator.generate_prompt_injection_scenarios(components, "Fix button")
        
        # Should not generate prompt injection scenarios for non-AI issues
        assert len(scenarios) == 0

    def test_scenario_metric_types(self):
        """Test that scenarios have appropriate metric types."""
        generator = ScenarioGenerator()
        components = ComponentDetection(
            frontend=False,
            backend_api=False,
            conversational_ai=True,
            reasoning="AI components detected",
            confidence=0.7
        )
        
        scenarios = generator.generate_scenarios(components, "Add chatbot")
        
        for scenario in scenarios:
            assert scenario.metric_type is not None
            assert len(scenario.metric_type) > 0
