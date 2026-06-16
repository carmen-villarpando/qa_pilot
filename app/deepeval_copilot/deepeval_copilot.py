"""Main orchestrator for DeepEval Copilot analysis."""

import logging
from typing import List, Optional

from deepeval_copilot.models import DeepEvalStrategy, ComponentDetection
from deepeval_copilot.component_detector import ComponentDetector
from deepeval_copilot.metric_selector import MetricSelector
from deepeval_copilot.risk_analyzer import RiskAnalyzer
from deepeval_copilot.scenario_generator import ScenarioGenerator
from deepeval_copilot.artifact_generator import ArtifactGenerator
from ai_client import AIClient

logger = logging.getLogger(__name__)


class DeepEvalCopilot:
    """Main orchestrator for DeepEval strategy generation."""

    def __init__(self, ai_client: Optional[AIClient] = None):
        """Initialize DeepEval Copilot with all components.
        
        Args:
            ai_client: Optional AI client for enhanced scenario generation
        """
        self.component_detector = ComponentDetector()
        self.metric_selector = MetricSelector()
        self.risk_analyzer = RiskAnalyzer()
        self.scenario_generator = ScenarioGenerator()
        self.artifact_generator = ArtifactGenerator()
        self.ai_client = ai_client
        
        logger.info("DeepEval Copilot initialized")

    def analyze_issue(
        self,
        title: str,
        body: str = "",
        labels: List[str] = None
    ) -> DeepEvalStrategy:
        """Analyze a GitHub issue and generate DeepEval strategy.
        
        Args:
            title: Issue title
            body: Issue body/description
            labels: Issue labels
            
        Returns:
            Complete DeepEval strategy
        """
        logger.info(f"Analyzing issue: {title}")
        
        # Step 1: Component Detection
        components = self.component_detector.detect_components(title, body)
        logger.info(f"Components detected: {components}")
        
        # Determine issue type
        issue_type = self.risk_analyzer.determine_issue_type(title, labels)
        logger.info(f"Issue type: {issue_type}")
        
        # Step 2: Metric Selection
        metrics = self.metric_selector.select_metrics(components, issue_type, title)
        logger.info(f"Metrics selected: {len(metrics)}")
        
        # Step 3: Risk Analysis
        risks = self.risk_analyzer.analyze_risks(components, issue_type, title)
        logger.info(f"Risks identified: {len(risks)}")
        
        # Steps 7-8: Scenario Generation
        conversational_scenarios = self.scenario_generator.generate_scenarios(
            components, title, body
        )
        logger.info(f"Conversational scenarios: {len(conversational_scenarios)}")
        
        prompt_injection_scenarios = self.scenario_generator.generate_prompt_injection_scenarios(
            components, title
        )
        logger.info(f"Prompt injection scenarios: {len(prompt_injection_scenarios)}")
        
        # Determine evaluation focus
        evaluation_focus = self._determine_evaluation_focus(components)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            components, metrics, risks, issue_type
        )
        
        # Step 9: Generate DeepEval Code Artifact
        strategy = DeepEvalStrategy(
            issue_type=issue_type,
            issue_title=title,
            components=components,
            evaluation_focus=evaluation_focus,
            deepeval_metrics=metrics,
            conversational_scenarios=conversational_scenarios,
            prompt_injection_scenarios=prompt_injection_scenarios,
            deepeval_code="",  # Will be generated next
            quality_risks=risks,
            recommendations=recommendations
        )
        
        # Generate the actual code artifact
        strategy.deepeval_code = self.artifact_generator.generate_deepeval_code(strategy)
        
        logger.info("DeepEval strategy analysis complete")
        return strategy

    def _determine_evaluation_focus(self, components: ComponentDetection) -> List[str]:
        """Determine what should be evaluated based on components."""
        focus = []
        
        if components.frontend:
            focus.append("Chatbot interface usability and user interaction flow")
        if components.backend_api:
            focus.append("API integration reliability and data processing accuracy")
        if components.conversational_ai:
            focus.append("AI response quality and accuracy for financial queries")
            focus.append("Context retention across multi-turn conversations")
            focus.append("Safety and compliance in financial advice delivery")
        
        if not focus:
            focus.append("General functionality and user experience")
        
        return focus

    def _generate_recommendations(
        self,
        components: ComponentDetection,
        metrics: List,
        risks: List,
        issue_type: str
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if components.conversational_ai:
            recommendations.append(
                "Implement DeepEval metrics for continuous monitoring of AI responses"
            )
            recommendations.append(
                "Set up automated evaluation pipeline for conversational scenarios"
            )
            
            if any("High" in risk.level for risk in risks):
                recommendations.append(
                    "Prioritize high-risk scenarios in testing and monitoring"
                )
        
        if components.frontend:
            recommendations.append(
                "Test AI integration across different frontend devices and browsers"
            )
        
        if components.backend_api:
            recommendations.append(
                "Monitor API response times and error rates for AI endpoints"
            )
        
        if issue_type == "Bug":
            recommendations.append(
                "Add regression tests to prevent similar issues in the future"
            )
        elif issue_type == "Tech Debt":
            recommendations.append(
                "Maintain evaluation baseline before and after refactoring"
            )
        
        if metrics:
            metric_names = [metric.name for metric in metrics]
            recommendations.append(
                f"Focus on these key metrics: {', '.join(metric_names)}"
            )
        
        return recommendations

    def format_strategy_as_comment(self, strategy: DeepEvalStrategy) -> str:
        """Format strategy as a GitHub comment."""
        lines = []
        
        lines.append("## 🤖 DeepEval Strategy Analysis")
        lines.append("")
        lines.append(f"**Issue Type:** {strategy.issue_type}")
        lines.append(f"**Issue:** {strategy.issue_title}")
        lines.append("")
        
        # Detected Components
        lines.append("### 🔍 Detected Components")
        if strategy.components.frontend:
            lines.append("✓ **Frontend UI** (chatbot interface, user interaction elements, client-side display)")
        if strategy.components.backend_api:
            lines.append("✓ **Backend API** (data processing, service endpoints, system integration)")
        if strategy.components.conversational_ai:
            lines.append("✓ **Conversational AI** (chatbot logic, NLP, AI response generation)")
        lines.append("")
        lines.append(f"*{strategy.components.reasoning}*")
        lines.append("")
        
        # Evaluation Focus
        lines.append("### 🎯 Evaluation Focus")
        for focus in strategy.evaluation_focus:
            lines.append(f"- {focus}")
        lines.append("")
        
        # DeepEval Metrics
        lines.append("### 📊 Recommended DeepEval Metrics")
        for metric in strategy.deepeval_metrics:
            lines.append(f"**{metric.name}** (threshold: {metric.threshold})")
            lines.append(f"- {metric.reason}")
            lines.append("")
        
        # Quality Risks
        lines.append("### ⚠️ Quality Risks")
        for risk in strategy.quality_risks:
            lines.append(f"**{risk.level}** - {risk.description}")
            lines.append(f"- *Mitigation: {risk.mitigation}*")
            lines.append("")
        
        # Conversational Scenarios
        if strategy.conversational_scenarios:
            lines.append("### 💬 Conversational Scenarios")
            for i, scenario in enumerate(strategy.conversational_scenarios, 1):
                lines.append(f"**Scenario {i}:** {scenario.scenario}")
                lines.append(f"- Expected: {scenario.expected_behavior}")
                lines.append(f"- Metric: {scenario.metric_type}")
                lines.append("")
        
        # Prompt Injection Scenarios
        if strategy.prompt_injection_scenarios:
            lines.append("### 🔐 Prompt Injection Scenarios")
            for i, scenario in enumerate(strategy.prompt_injection_scenarios, 1):
                lines.append(f"**Scenario {i}:** {scenario.scenario}")
                lines.append(f"- Expected: {scenario.expected_behavior}")
                lines.append("")
        
        # Recommendations
        lines.append("### 💡 Recommendations")
        for rec in strategy.recommendations:
            lines.append(f"- {rec}")
        lines.append("")
        
        # DeepEval Code
        lines.append("### 🐍 DeepEval Code")
        lines.append("")
        lines.append("```python")
        lines.append(strategy.deepeval_code)
        lines.append("```")
        lines.append("")
        
        lines.append("---")
        lines.append("*Generated by QA Pilot*")
        
        return "\n".join(lines)

    @staticmethod
    def from_env() -> "DeepEvalCopilot":
        """Create DeepEval Copilot from environment variables."""
        ai_client = AIClient.from_env()
        return DeepEvalCopilot(ai_client=ai_client)
