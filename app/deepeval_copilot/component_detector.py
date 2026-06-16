"""Component detection logic for identifying Frontend, Backend, and AI components."""

import logging

from .models import ComponentDetection

logger = logging.getLogger(__name__)


class ComponentDetector:
    """Detects components involved in a GitHub issue."""

    def __init__(self):
        """Initialize component detector with keyword patterns."""
        self.frontend_keywords = [
            "ui",
            "interface",
            "button",
            "scroll",
            "widget",
            "chatbot widget",
            "frontend",
            "client",
            "browser",
            "responsive",
            "mobile",
            "desktop",
            "display",
            "render",
            "view",
            "screen",
            "form",
            "input",
            "click",
        ]

        self.backend_keywords = [
            "api",
            "endpoint",
            "service",
            "backend",
            "server",
            "database",
            "integration",
            "webhook",
            "rest",
            "graphql",
            "microservice",
            "auth",
            "authentication",
            "authorization",
            "token",
            "session",
        ]

        self.ai_keywords = [
            "chatbot",
            "assistant",
            "conversation",
            "ai",
            "llm",
            "gpt",
            "claude",
            "openai",
            "anthropic",
            "langchain",
            "prompt",
            "context",
            "intent",
            "nlp",
            "natural language",
            "ai agent",
            "rag",
            "retrieval",
            "embedding",
            "vector",
            "semantic",
        ]

    def detect_components(self, title: str, body: str = "") -> ComponentDetection:
        """Detect components from issue title and body."""
        text = f"{title} {body}".lower()

        frontend_detected = self._detect_frontend(text)
        backend_detected = self._detect_backend(text)
        ai_detected = self._detect_ai(text)

        reasoning = self._generate_reasoning(
            frontend_detected, backend_detected, ai_detected, title
        )

        confidence = self._calculate_confidence(
            frontend_detected, backend_detected, ai_detected, text
        )

        return ComponentDetection(
            frontend=frontend_detected,
            backend_api=backend_detected,
            conversational_ai=ai_detected,
            reasoning=reasoning,
            confidence=confidence,
        )

    def _detect_frontend(self, text: str) -> bool:
        """Detect if issue involves frontend components."""
        return any(keyword in text for keyword in self.frontend_keywords)

    def _detect_backend(self, text: str) -> bool:
        """Detect if issue involves backend API components."""
        return any(keyword in text for keyword in self.backend_keywords)

    def _detect_ai(self, text: str) -> bool:
        """Detect if issue involves AI/conversational components."""
        return any(keyword in text for keyword in self.ai_keywords)

    def _generate_reasoning(
        self, frontend: bool, backend: bool, ai: bool, title: str
    ) -> str:
        """Generate reasoning for component detection."""
        reasons = []

        if frontend:
            reasons.append(
                "Frontend UI components involved (chatbot interface, user interaction elements, or client-side display)"
            )
        if backend:
            reasons.append(
                "Backend API integration required (data processing, service endpoints, or system integration)"
            )
        if ai:
            reasons.append(
                "Conversational AI/LLM components (chatbot logic, natural language processing, or AI response generation)"
            )

        if not reasons:
            reasons.append("Generic issue - no specific components detected")

        return ". ".join(reasons) + "."

    def _calculate_confidence(
        self, frontend: bool, backend: bool, ai: bool, text: str
    ) -> float:
        """Calculate confidence score for component detection."""
        detected_count = sum([frontend, backend, ai])

        if detected_count == 0:
            return 0.3  # Low confidence for generic issues
        elif detected_count == 1:
            return 0.7  # Medium confidence for single component
        elif detected_count == 2:
            return 0.85  # High confidence for two components
        else:
            return 0.95  # Very high confidence for all three components
