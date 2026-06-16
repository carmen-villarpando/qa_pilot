"""Main orchestrator for DeepEval Copilot analysis."""

import logging
from typing import List, Optional

from deepeval_copilot.models import DeepEvalStrategy, ComponentDetection
from deepeval_copilot.component_detector import ComponentDetector
from deepeval_copilot.metric_selector import MetricSelector
from deepeval_copilot.risk_analyzer import RiskAnalyzer
from deepeval_copilot.scenario_generator import ScenarioGenerator
from deepeval_copilot.evaluation_data_analyzer import EvaluationDataAnalyzer
from deepeval_copilot.new_metric_analyzer import NewMetricAnalyzer
from deepeval_copilot.value_analyzer import ValueAnalyzer
from ai_client import AIClient

logger = logging.getLogger(__name__)


class DeepEvalCopilot:
    """Main orchestrator for DeepEval strategy generation."""

    def __init__(self, ai_client: Optional[AIClient] = None):
        """Initialize DeepEval Copilot with all components.
        
        Args:
            ai_client: Optional AI client for enhanced analysis
        """
        self.ai_client = ai_client
        self.component_detector = ComponentDetector()
        self.metric_selector = MetricSelector()
        self.risk_analyzer = RiskAnalyzer()
        self.scenario_generator = ScenarioGenerator(ai_client)
        self.evaluation_data_analyzer = EvaluationDataAnalyzer(ai_client)
        self.new_metric_analyzer = NewMetricAnalyzer(ai_client)
        self.value_analyzer = ValueAnalyzer(ai_client)
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
        
        # Step 2: Analyze if issue provides evaluation value
        provides_value, value_assessment = self.value_analyzer.analyze_evaluation_value(
            components, title, body, issue_type
        )
        logger.info(f"Provides evaluation value: {provides_value} - {value_assessment}")
        
        # If no value, return early with minimal strategy
        if not provides_value:
            return DeepEvalStrategy(
                issue_type=issue_type,
                issue_title=title,
                components=components,
                evaluation_focus=[],
                metric_recommendations=[],
                new_metric_suggestions=[],
                evaluation_data=[],
                conversational_test_cases=[],
                prompt_injection_tests=[],
                quality_risks=[],
                recommendations=[f"This issue does not provide evaluation value: {value_assessment}"],
                provides_evaluation_value=False,
                value_assessment=value_assessment
            )
        
        # Step 3: Metric Applicability Analysis
        metric_recommendations = self.metric_selector.analyze_metric_applicability(
            components, issue_type, title, body
        )
        logger.info(f"Metric recommendations: {len(metric_recommendations)}")
        
        # Step 4: Risk Analysis
        risks = self.risk_analyzer.analyze_risks(components, issue_type, title)
        logger.info(f"Risks identified: {len(risks)}")
        
        # Step 5: Evaluation Data Suggestions
        evaluation_data = self.evaluation_data_analyzer.suggest_evaluation_data(
            components, metric_recommendations, title, body
        )
        logger.info(f"Evaluation data suggested: {len(evaluation_data)}")
        
        # Step 6: New Metric Analysis
        new_metric_suggestions = self.new_metric_analyzer.analyze_new_metric_needs(
            components, title, body, metric_recommendations
        )
        logger.info(f"New metric suggestions: {len(new_metric_suggestions)}")
        
        # Step 7: Conversational Test Cases
        conversational_test_cases = self.scenario_generator.generate_conversational_test_cases(
            components, title, body
        )
        logger.info(f"Conversational test cases: {len(conversational_test_cases)}")
        
        # Step 8: Prompt Injection Tests
        prompt_injection_tests = self.scenario_generator.generate_prompt_injection_tests(
            components, title, body
        )
        logger.info(f"Prompt injection tests: {len(prompt_injection_tests)}")
        
        # Determine evaluation focus
        evaluation_focus = self._determine_evaluation_focus(components)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            components, metric_recommendations, risks, issue_type, title, body
        )
        
        # Generate strategy
        strategy = DeepEvalStrategy(
            issue_type=issue_type,
            issue_title=title,
            components=components,
            evaluation_focus=evaluation_focus,
            metric_recommendations=metric_recommendations,
            new_metric_suggestions=new_metric_suggestions,
            evaluation_data=evaluation_data,
            conversational_test_cases=conversational_test_cases,
            prompt_injection_tests=prompt_injection_tests,
            quality_risks=risks,
            recommendations=recommendations,
            provides_evaluation_value=True,
            value_assessment=value_assessment
        )
        
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
        metric_recommendations: List,
        risks: List,
        issue_type: str,
        issue_title: str = "",
        issue_body: str = ""
    ) -> List[str]:
        """Generate recommendations based on analysis and issue context."""
        recommendations = []
        
        # Generate context-specific recommendations using AI
        context_recommendations = self._generate_context_aware_recommendations(
            components, metric_recommendations, risks, issue_type, issue_title, issue_body
        )
        recommendations.extend(context_recommendations)
        
        # Add standard recommendations
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
        
        if metric_recommendations:
            metric_names = [metric.name for metric in metric_recommendations if metric.applies]
            recommendations.append(
                f"Focus on these key metrics: {', '.join(metric_names)}"
            )
        
        return recommendations

    def _generate_context_aware_recommendations(
        self,
        components: ComponentDetection,
        metric_recommendations: List,
        risks: List,
        issue_type: str,
        issue_title: str,
        issue_body: str
    ) -> List[str]:
        """Generate context-aware recommendations using AI."""
        recommendations = []
        
        # Build context for AI
        context_parts = []
        context_parts.append(f"Issue: {issue_title}")
        if issue_body:
            context_parts.append(f"Description: {issue_body[:500]}...")
        context_parts.append(f"Issue Type: {issue_type}")
        
        component_info = []
        if components.frontend:
            component_info.append("Frontend UI")
        if components.backend_api:
            component_info.append("Backend API")
        if components.conversational_ai:
            component_info.append("Conversational AI")
        context_parts.append(f"Components: {', '.join(component_info)}")
        
        applicable_metrics = [m.name for m in metric_recommendations if m.applies]
        context_parts.append(f"Applicable Metrics: {', '.join(applicable_metrics)}")
        
        context = "\n".join(context_parts)
        
        # Use AI to generate specific recommendations
        try:
            prompt = f"""Based on the following GitHub issue context, generate 2-3 specific, actionable recommendations for testing and evaluation:

{context}

Generate recommendations that:
1. Are specific to the issue described
2. Reference the actual functionality mentioned in the issue
3. Suggest concrete testing scenarios or evaluation approaches
4. Are practical and implementable
5. Focus on evaluation data collection (questions, ground truth) rather than code generation

Format each recommendation on a new line, starting with "- "."""
            
            response = self.ai_client.generate_completion_sync(prompt)
            
            if response:
                lines = response.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("- "):
                            recommendations.append(line[2:])
                        else:
                            recommendations.append(line)
        except Exception as e:
            logger.warning(f"Failed to generate AI recommendations: {e}")
        
        return recommendations

    def format_strategy_as_comment(self, strategy: DeepEvalStrategy) -> str:
        """Format strategy as a GitHub comment."""
        lines = []
        
        lines.append("## 🤖 DeepEval Evaluation Strategy Analysis")
        lines.append("")
        lines.append(f"**Issue Type:** {strategy.issue_type}")
        lines.append(f"**Issue:** {strategy.issue_title}")
        lines.append("")
        
        # Value Assessment
        lines.append("### 💡 Evaluation Value Assessment")
        if strategy.provides_evaluation_value:
            lines.append("✅ **This issue provides value for evaluation purposes**")
        else:
            lines.append("❌ **This issue does not provide evaluation value**")
        lines.append(f"*{strategy.value_assessment}*")
        lines.append("")
        
        if not strategy.provides_evaluation_value:
            lines.append("---")
            lines.append("")
            lines.append("*Generated by QA Pilot*")
            return "\n".join(lines)
        
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
        
        # Metric Recommendations
        lines.append("### 📊 Metric Applicability Analysis")
        applicable_metrics = [m for m in strategy.metric_recommendations if m.applies]
        if applicable_metrics:
            for metric in applicable_metrics:
                lines.append(f"✓ **{metric.name}** ({metric.priority} priority)")
                lines.append(f"- {metric.reason}")
                lines.append("")
        else:
            lines.append("No applicable metrics identified for this issue")
            lines.append("")
        
        # Evaluation Data Suggestions (CSV Format)
        if strategy.evaluation_data:
            lines.append("### 📝 Evaluation Data (CSV Format)")
            lines.append("```csv")
            lines.append("question,ground_truth,metric_name,business_context")
            for data in strategy.evaluation_data:
                # Escape quotes for CSV
                question = data.question.replace('"', '""')
                ground_truth = data.ground_truth.replace('"', '""')
                business_context = data.business_context.replace('"', '""')
                lines.append(f'"{question}","{ground_truth}","{data.metric_name}","{business_context}"')
            lines.append("```")
            lines.append("")
        
        # New Metric Suggestions (Python Code)
        if strategy.new_metric_suggestions:
            lines.append("### 🆕 New Metrics (Python Implementation)")
            lines.append("```python")
            lines.append("from deepeval.metrics import GEval")
            lines.append("from deepeval.test_case import LLMTestCaseParams")
            lines.append("")
            
            for metric in strategy.new_metric_suggestions:
                lines.append(f"eval_{metric.name.lower().replace(' ', '_')} = GEval(")
                lines.append(f'    name="{metric.name}",')
                lines.append("    evaluation_steps=(")
                for i, step in enumerate(metric.evaluation_steps, 1):
                    lines.append(f'        "{i}. {step}",')
                lines.append("    ),")
                lines.append("    evaluation_params=[")
                lines.append("        LLMTestCaseParams.INPUT,")
                lines.append("        LLMTestCaseParams.ACTUAL_OUTPUT,")
                lines.append("    ],")
                lines.append("    threshold=0.85,")
                lines.append("    model=local_model,")
                lines.append(")")
                lines.append("")
            
            lines.append("```")
            lines.append("")
        
        # Conversational Test Cases
        if strategy.conversational_test_cases:
            lines.append("### 💬 Business-Specific Conversational Test Cases")
            for test in strategy.conversational_test_cases:
                lines.append(f"**{test.test_id}: {test.test_name}**")
                lines.append(f"**Scenario:** {test.scenario}")
                if test.context_requirements:
                    lines.append(f"**Context Requirements:** {', '.join(test.context_requirements)}")
                lines.append(f"**Business Value:** {test.business_value}")
                lines.append("")
                
                # Show multi-turn conversation
                for turn in test.turns:
                    lines.append(f"**Turn {turn.turn_id}:**")
                    lines.append(f"💬 **User:** {turn.user_input}")
                    lines.append(f"🤖 **Assistant:** {turn.expected_response}")
                    lines.append(f"🎯 **Ground Truth:** {', '.join(turn.ground_truth_requirements)}")
                    lines.append(f"📊 **Metrics:** {', '.join(turn.evaluation_metrics)}")
                    lines.append("")
                lines.append("")
        
        # Prompt Injection Tests
        if strategy.prompt_injection_tests:
            lines.append("### 🔐 Prompt Injection Tests")
            for test in strategy.prompt_injection_tests:
                lines.append(f"**{test.test_id}: {test.attack_type.title()} Attack**")
                lines.append(f"**Attack Scenario:** {test.attack_scenario}")
                lines.append(f"**Expected Protection:** {test.expected_protection}")
                lines.append(f"**Evaluation Metrics:** {', '.join(test.evaluation_metrics)}")
                lines.append(f"**Relevance:** {test.relevance}")
                lines.append("")
        
        # CSV Export Format
        if strategy.conversational_test_cases:
            lines.append("### 📋 CSV Export Format (Ready for DeepEval)")
            lines.append("```csv")
            lines.append("test_id,turn_id,user_input,expected_behavior,evaluation_metrics,ground_truth_requirements")
            
            for test in strategy.conversational_test_cases:
                for turn in test.turns:
                    metrics = "|".join(turn.evaluation_metrics)
                    requirements = "|".join(turn.ground_truth_requirements)
                    # Escape quotes and commas for CSV
                    user_input = f'"{turn.user_input.replace('"', '""')}"'
                    expected = f'"{turn.expected_response.replace('"', '""')}"'
                    
                    lines.append(f"{test.test_id},{turn.turn_id},{user_input},{expected},{metrics},{requirements}")
            
            lines.append("```")
            lines.append("")
        
        # Quality Risks
        lines.append("### ⚠️ Quality Risks")
        for risk in strategy.quality_risks:
            lines.append(f"**{risk.level}** - {risk.description}")
            lines.append(f"- *Mitigation: {risk.mitigation}*")
            lines.append("")
        
        # Recommendations
        lines.append("### 💡 Recommendations")
        for recommendation in strategy.recommendations:
            lines.append(f"- {recommendation}")
        lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*Generated by QA Pilot*")
        
        return "\n".join(lines)

    @staticmethod
    def from_env() -> "DeepEvalCopilot":
        """Create DeepEval Copilot from environment variables."""
        ai_client = AIClient.from_env()
        return DeepEvalCopilot(ai_client=ai_client)
