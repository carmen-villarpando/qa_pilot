"""DeepEval metric selection engine with intelligent reasoning."""

import logging
from typing import List

from .models import ComponentDetection, DeepEvalMetric

logger = logging.getLogger(__name__)


class MetricSelector:
    """Selects appropriate DeepEval metrics based on component detection."""

    def __init__(self):
        """Initialize metric selector with DeepEval metric definitions."""
        self.metrics = {
            "answer_relevancy": {
                "name": "Answer Relevancy",
                "description": "Measures how relevant the AI's response is to the user's question",
                "code": """from deepeval.metrics import AnswerRelevancyMetric
answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)""",
                "threshold": 0.7,
                "use_cases": ["general_ai", "chatbot", "assistant"]
            },
            "conversation_relevancy": {
                "name": "Conversation Relevancy",
                "description": "Measures how relevant the AI's responses are throughout a multi-turn conversation",
                "code": """from deepeval.metrics import ConversationRelevancyMetric
conversation_relevancy_metric = ConversationRelevancyMetric(threshold=0.6)""",
                "threshold": 0.6,
                "use_cases": ["conversation", "multi_turn", "chatbot"]
            },
            "conversation_completeness": {
                "name": "Conversation Completeness",
                "description": "Measures whether the conversation reaches a satisfactory conclusion",
                "code": """from deepeval.metrics import ConversationCompletenessMetric
conversation_completeness_metric = ConversationCompletenessMetric(threshold=0.7)""",
                "threshold": 0.7,
                "use_cases": ["conversation", "task_completion", "workflow"]
            },
            "faithfulness": {
                "name": "Faithfulness",
                "description": "Measures whether the AI's response is factually consistent with the context",
                "code": """from deepeval.metrics import FaithfulnessMetric
faithfulness_metric = FaithfulnessMetric(threshold=0.7)""",
                "threshold": 0.7,
                "use_cases": ["rag", "retrieval", "factual_accuracy"]
            },
            "bias": {
                "name": "Bias",
                "description": "Measures whether the AI's responses contain unfair bias",
                "code": """from deepeval.metrics import BiasMetric
bias_metric = BiasMetric(threshold=0.5)""",
                "threshold": 0.5,
                "use_cases": ["fairness", "sensitive_topics", "user_demographics"]
            },
            "toxicity": {
                "name": "Toxicity",
                "description": "Measures whether the AI's responses contain toxic or harmful content",
                "code": """from deepeval.metrics import ToxicityMetric
toxicity_metric = ToxicityMetric(threshold=0.5)""",
                "threshold": 0.5,
                "use_cases": ["safety", "moderation", "user_generated_content"]
            }
        }

    def select_metrics(
        self,
        components: ComponentDetection,
        issue_type: str,
        issue_title: str
    ) -> List[DeepEvalMetric]:
        """Select appropriate metrics based on components and issue type."""
        selected_metrics = []
        title_lower = issue_title.lower()
        
        # Always include Answer Relevancy for AI components
        if components.conversational_ai:
            selected_metrics.append(self._create_metric("answer_relevancy", 
                "Essential for ensuring chatbot responses directly address user questions"))
        
        # Include Conversation Relevancy for multi-turn conversations
        if components.conversational_ai and any(word in title_lower for word in 
            ["conversation", "follow-up", "context", "multi-turn", "dialogue"]):
            selected_metrics.append(self._create_metric("conversation_relevancy",
                "Critical for maintaining context across multi-turn conversations"))
        
        # Include Conversation Completeness for task-oriented chatbots
        if components.conversational_ai and any(word in title_lower for word in
            ["complete", "finish", "resolve", "task", "workflow"]):
            selected_metrics.append(self._create_metric("conversation_completeness",
                "Important for ensuring conversations reach satisfactory conclusions"))
        
        # Include Faithfulness for RAG applications
        if components.conversational_ai and any(word in title_lower for word in
            ["rag", "retrieval", "document", "knowledge", "context"]):
            selected_metrics.append(self._create_metric("faithfulness",
                "Crucial for RAG applications to ensure factual consistency with retrieved context"))
        
        # Include Bias for sensitive topics
        if components.conversational_ai and any(word in title_lower for word in
            ["bias", "fair", "discrimination", "sensitive", "demographic"]):
            selected_metrics.append(self._create_metric("bias",
                "Important for ensuring fair and unbiased responses"))
        
        # Include Toxicity for user-generated content moderation
        if components.conversational_ai and any(word in title_lower for word in
            ["toxic", "harmful", "moderation", "safety", "content"]):
            selected_metrics.append(self._create_metric("toxicity",
                "Essential for content safety and moderation"))
        
        # If no specific metrics selected but AI detected, include default metrics
        if components.conversational_ai and not selected_metrics:
            selected_metrics.append(self._create_metric("answer_relevancy",
                "Default metric for ensuring response relevance"))
            selected_metrics.append(self._create_metric("conversation_relevancy",
                "Default metric for conversation context management"))
        
        logger.info(f"Selected {len(selected_metrics)} metrics for issue: {issue_title}")
        return selected_metrics

    def _create_metric(self, metric_key: str, custom_reason: str) -> DeepEvalMetric:
        """Create a DeepEvalMetric from metric definition."""
        metric_def = self.metrics[metric_key]
        return DeepEvalMetric(
            name=metric_def["name"],
            reason=f"{metric_def['description']}. {custom_reason}",
            code_snippet=metric_def["code"],
            threshold=metric_def["threshold"]
        )
