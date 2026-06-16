"""Quality risk analysis focused on AI/LLM specific risks."""

import logging

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
                "mitigation": "Implement robust context management with token limits and conversation summarization",
            },
            "intent_misunderstanding": {
                "level": "High",
                "description": "User intent may be misunderstood, especially in emotional or ambiguous situations",
                "mitigation": "Use intent classification with confidence scores and fallback to human clarification",
            },
            "prompt_injection": {
                "level": "High",
                "description": "Malicious users may attempt prompt injection attacks to bypass safety measures",
                "mitigation": "Implement input validation, output filtering, and adversarial testing",
            },
            "inconsistent_responses": {
                "level": "Medium",
                "description": "Similar prompts may generate inconsistent responses due to model non-determinism",
                "mitigation": "Use temperature control, seed values, and response consistency testing",
            },
            "hallucination": {
                "level": "Medium",
                "description": "AI may generate factually incorrect or hallucinated information",
                "mitigation": "Implement fact-checking, RAG with reliable sources, and citation requirements",
            },
            "bias_fairness": {
                "level": "Medium",
                "description": "Responses may contain unfair bias against certain demographics",
                "mitigation": "Regular bias testing, diverse training data, and bias mitigation techniques",
            },
            "privacy_leakage": {
                "level": "High",
                "description": "AI may inadvertently expose private or sensitive information",
                "mitigation": "Implement PII detection, data masking, and strict access controls",
            },
            "edge_cases": {
                "level": "Low",
                "description": "Unusual edge cases may produce unexpected or poor responses",
                "mitigation": "Comprehensive edge case testing and graceful error handling",
            },
            "performance_latency": {
                "level": "Low",
                "description": "AI responses may have high latency affecting user experience",
                "mitigation": "Implement caching, streaming responses, and performance monitoring",
            },
        }

    def analyze_risks(
        self, components: ComponentDetection, issue_type: str, issue_title: str
    ) -> list[QualityRisk]:
        """Analyze exactly 3 potential quality risks based on components and issue type."""
        risks = []
        title_lower = issue_title.lower()

        # Focus on exactly 3 most relevant risks
        if components.conversational_ai:
            # Risk 1: Financial accuracy (highest priority for financial domain)
            if any(
                word in title_lower
                for word in [
                    "mortgage",
                    "payment",
                    "assistance",
                    "financial",
                    "loan",
                    "account",
                ]
            ):
                risks.append(
                    QualityRisk(
                        level="High",
                        description=f"AI may provide inaccurate financial guidance for '{issue_title}' affecting member decisions",
                        mitigation="Validate all financial advice against BECU policies and compliance requirements",
                    )
                )
            else:
                risks.append(
                    QualityRisk(
                        level="High",
                        description="AI may provide inaccurate or incomplete information affecting user decisions",
                        mitigation="Implement fact-checking and validation against reliable sources",
                    )
                )

            # Risk 2: PII leakage (critical for financial systems)
            risks.append(
                QualityRisk(
                    level="High",
                    description="PII leakage risk - chatbot may expose sensitive member financial information",
                    mitigation="Implement strict PII detection and masking for all financial data",
                )
            )

            # Risk 3: Context retention or security (choose based on relevance)
            if any(
                word in title_lower
                for word in ["multi-turn", "conversation", "follow-up", "context"]
            ):
                risks.append(
                    QualityRisk(
                        level="High",
                        description="Context loss in multi-turn conversations may lead to incorrect advice",
                        mitigation="Implement conversation summarization and explicit context verification",
                    )
                )
            else:
                risks.append(
                    QualityRisk(
                        level="High",
                        description="Prompt injection attacks could bypass safety measures for financial guidance",
                        mitigation="Add adversarial testing specifically for financial compliance scenarios",
                    )
                )

        elif components.frontend and not components.conversational_ai:
            # For UI-only issues
            risks.append(
                QualityRisk(
                    level="Medium",
                    description="UI changes may affect user experience and accessibility",
                    mitigation="Conduct usability testing with actual member scenarios",
                )
            )
            risks.append(
                QualityRisk(
                    level="Medium",
                    description="Frontend changes may introduce visual inconsistencies",
                    mitigation="Implement design system compliance testing",
                )
            )
            risks.append(
                QualityRisk(
                    level="Low",
                    description="Performance impact from UI changes",
                    mitigation="Monitor performance metrics and optimize rendering",
                )
            )

        elif components.backend_api:
            # For backend-only issues
            risks.append(
                QualityRisk(
                    level="Medium",
                    description="API changes may break existing integrations",
                    mitigation="Implement backward compatibility testing",
                )
            )
            risks.append(
                QualityRisk(
                    level="Medium",
                    description="Data processing errors may affect downstream systems",
                    mitigation="Add comprehensive data validation and error handling",
                )
            )
            risks.append(
                QualityRisk(
                    level="Low",
                    description="Performance degradation from new backend logic",
                    mitigation="Implement performance monitoring and optimization",
                )
            )

        # Ensure exactly 3 risks (pad with generic if needed)
        while len(risks) < 3:
            risks.append(
                QualityRisk(
                    level="Low",
                    description="General quality risk for system changes",
                    mitigation="Implement standard testing and monitoring practices",
                )
            )

        # Return exactly 3 risks
        return risks[:3]

    def _create_risk(self, risk_key: str) -> QualityRisk:
        """Create a QualityRisk from risk definition."""
        risk_def = self.risk_definitions[risk_key]
        return QualityRisk(
            level=risk_def["level"],
            description=risk_def["description"],
            mitigation=risk_def["mitigation"],
        )

    def determine_issue_type(self, title: str, labels: list[str] = None) -> str:
        """Determine issue type from title and labels."""
        title_lower = title.lower()
        labels = labels or []
        labels_lower = [label.lower() for label in labels]

        # Check for explicit type indicators
        if "bug" in title_lower or "bug" in labels_lower or "fix" in title_lower:
            return "Bug"
        elif (
            "tech debt" in title_lower
            or "refactor" in title_lower
            or "cleanup" in title_lower
        ):
            return "Tech Debt"
        elif (
            "story" in title_lower
            or "feature" in title_lower
            or "add" in title_lower
            or "implement" in title_lower
        ):
            return "Story"

        # Default to Story if no explicit type
        return "Story"
