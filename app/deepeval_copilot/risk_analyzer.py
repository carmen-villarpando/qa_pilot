"""Quality risk analysis focused on AI/LLM specific risks."""

import logging
from typing import List

from .models import ComponentDetection, QualityRisk

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Analyzes quality risks for AI/LLM applications."""

    def __init__(self):
        """Initialize risk analyzer with AI-specific risk definitions."""
        self.risk_definitions = {
            "context_loss": {
                "level": "High",
                "description": "Conversation context may be lost during complex or multi-turn interactions",
                "mitigation": "Implement robust context management with token limits and conversation summarization"
            },
            "intent_misunderstanding": {
                "level": "High",
                "description": "User intent may be misunderstood, especially in emotional or ambiguous situations",
                "mitigation": "Use intent classification with confidence scores and fallback to human clarification"
            },
            "prompt_injection": {
                "level": "High",
                "description": "Malicious users may attempt prompt injection attacks to bypass safety measures",
                "mitigation": "Implement input validation, output filtering, and adversarial testing"
            },
            "inconsistent_responses": {
                "level": "Medium",
                "description": "Similar prompts may generate inconsistent responses due to model non-determinism",
                "mitigation": "Use temperature control, seed values, and response consistency testing"
            },
            "hallucination": {
                "level": "Medium",
                "description": "AI may generate factually incorrect or hallucinated information",
                "mitigation": "Implement fact-checking, RAG with reliable sources, and citation requirements"
            },
            "bias_fairness": {
                "level": "Medium",
                "description": "Responses may contain unfair bias against certain demographics",
                "mitigation": "Regular bias testing, diverse training data, and bias mitigation techniques"
            },
            "privacy_leakage": {
                "level": "High",
                "description": "AI may inadvertently expose private or sensitive information",
                "mitigation": "Implement PII detection, data masking, and strict access controls"
            },
            "edge_cases": {
                "level": "Low",
                "description": "Unusual edge cases may produce unexpected or poor responses",
                "mitigation": "Comprehensive edge case testing and graceful error handling"
            },
            "performance_latency": {
                "level": "Low",
                "description": "AI responses may have high latency affecting user experience",
                "mitigation": "Implement caching, streaming responses, and performance monitoring"
            }
        }

    def analyze_risks(
        self,
        components: ComponentDetection,
        issue_type: str,
        issue_title: str
    ) -> List[QualityRisk]:
        """Analyze quality risks based on components and issue type."""
        risks = []
        title_lower = issue_title.lower()
        
        # Contextual risk analysis based on issue content
        if components.conversational_ai:
            # Analyze specific context from issue title
            if any(word in title_lower for word in ["mortgage", "payment", "assistance", "financial", "loan", "account"]):
                risks.append(QualityRisk(
                    level="High",
                    description=f"AI may provide inaccurate financial guidance for '{issue_title}' affecting member decisions",
                    mitigation="Validate all financial advice against BECU policies and compliance requirements"
                ))
                risks.append(QualityRisk(
                    level="High",
                    description="PII leakage risk - chatbot may expose sensitive member financial information",
                    mitigation="Implement strict PII detection and masking for all financial data"
                ))
            
            # General AI risks but more contextual
            risks.append(QualityRisk(
                level="High",
                description="Context loss in multi-turn financial conversations may lead to incorrect advice",
                mitigation="Implement conversation summarization and explicit context verification"
            ))
            
            risks.append(QualityRisk(
                level="High",
                description="Prompt injection attacks could bypass safety measures for financial guidance",
                mitigation="Add adversarial testing specifically for financial compliance scenarios"
            ))
            
            # Only include medium priority risks if relevant
            if "bug" in title_lower or "fix" in title_lower:
                risks.append(QualityRisk(
                    level="Medium",
                    description="Inconsistent AI responses after bug fix may confuse members",
                    mitigation="Implement consistency testing with seed values for reproducible outputs"
                ))
        
        if components.frontend and components.conversational_ai:
            risks.append(QualityRisk(
                level="Medium",
                description="Chatbot interface usability issues may prevent members from accessing critical financial services",
                mitigation="Conduct usability testing with actual member scenarios and accessibility requirements"
            ))
        
        if components.backend_api and components.conversational_ai:
            risks.append(QualityRisk(
                level="Medium",
                description="API integration failures may disrupt chatbot availability during peak usage",
                mitigation="Implement circuit breakers and graceful degradation for AI services"
            ))
        
        # Issue type-specific contextual risks
        if issue_type == "Bug":
            risks.append(QualityRisk(
                level="High",
                description=f"Bug fix for '{issue_title}' may introduce regressions in existing AI behavior",
                mitigation="Run full regression suite on all existing GEval metrics before deployment"
            ))
        elif issue_type == "Tech Debt":
            risks.append(QualityRisk(
                level="Medium",
                description="Refactoring may affect AI model performance or metric thresholds",
                mitigation="Establish baseline scores for all GEval metrics before and after changes"
            ))
        
        # Limit to most relevant risks (max 5)
        risks = risks[:5]
        
        logger.info(f"Identified {len(risks)} contextual quality risks for issue: {issue_title}")
        return risks

    def _create_risk(self, risk_key: str) -> QualityRisk:
        """Create a QualityRisk from risk definition."""
        risk_def = self.risk_definitions[risk_key]
        return QualityRisk(
            level=risk_def["level"],
            description=risk_def["description"],
            mitigation=risk_def["mitigation"]
        )

    def determine_issue_type(self, title: str, labels: List[str] = None) -> str:
        """Determine issue type from title and labels."""
        title_lower = title.lower()
        labels = labels or []
        labels_lower = [label.lower() for label in labels]
        
        # Check for explicit type indicators
        if "bug" in title_lower or "bug" in labels_lower or "fix" in title_lower:
            return "Bug"
        elif "tech debt" in title_lower or "refactor" in title_lower or "cleanup" in title_lower:
            return "Tech Debt"
        elif "story" in title_lower or "feature" in title_lower or "add" in title_lower or "implement" in title_lower:
            return "Story"
        
        # Default to Story if no explicit type
        return "Story"
