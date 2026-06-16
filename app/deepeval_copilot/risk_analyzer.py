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
        
        if components.conversational_ai:
            # High priority risks for AI components
            risks.append(self._create_risk("context_loss"))
            risks.append(self._create_risk("intent_misunderstanding"))
            risks.append(self._create_risk("prompt_injection"))
            
            # Medium priority risks
            risks.append(self._create_risk("inconsistent_responses"))
            risks.append(self._create_risk("hallucination"))
            risks.append(self._create_risk("bias_fairness"))
            
            # Privacy risk for data-heavy applications
            if any(word in title_lower for word in ["data", "personal", "private", "sensitive", "customer"]):
                risks.append(self._create_risk("privacy_leakage"))
        
        if components.frontend:
            # Frontend-specific risks
            risks.append(QualityRisk(
                level="Medium",
                description="UI/UX issues may affect user interaction with AI features",
                mitigation="Implement comprehensive UI testing and user feedback collection"
            ))
        
        if components.backend_api:
            # Backend-specific risks
            risks.append(QualityRisk(
                level="Medium",
                description="API failures or rate limiting may disrupt AI service availability",
                mitigation="Implement retry logic, circuit breakers, and comprehensive API monitoring"
            ))
        
        # Issue type-specific risks
        if issue_type == "Bug":
            risks.append(QualityRisk(
                level="High",
                description="Regression risk - bug fix may introduce new issues in AI behavior",
                mitigation="Implement comprehensive regression testing for AI scenarios"
            ))
        elif issue_type == "Tech Debt":
            risks.append(QualityRisk(
                level="Medium",
                description="Refactoring may inadvertently affect AI model performance or behavior",
                mitigation="Maintain AI evaluation baseline before and after refactoring"
            ))
        
        logger.info(f"Identified {len(risks)} quality risks for issue: {issue_title}")
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
