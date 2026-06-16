"""Multi-provider AI client supporting GitHub Models, OpenAI, and local models."""

import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class AIClient:
    """Multi-provider AI client with fallback support."""

    def __init__(
        self,
        provider: str = "github_models",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize AI client with specified provider.
        
        Args:
            provider: AI provider (github_models, openai, local)
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = provider
        self.api_key = api_key or self._get_default_api_key(provider)
        self.model = model or self._get_default_model(provider)
        
        logger.info(f"Initialized AI client with provider: {provider}, model: {self.model}")

    def _get_default_api_key(self, provider: str) -> Optional[str]:
        """Get default API key from environment variables."""
        if provider == "github_models":
            return os.getenv("GITHUB_MODELS_TOKEN")
        elif provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif provider == "local":
            return None  # Local models don't need API key
        return None

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        if provider == "github_models":
            return "gpt-4o-mini"  # GitHub Models default
        elif provider == "openai":
            return "gpt-4o-mini"  # OpenAI cost-effective model
        elif provider == "local":
            return "llama3.2"  # Common local model
        return "gpt-4o-mini"

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate completion using the configured provider.
        
        Args:
            prompt: The prompt to send to the AI
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            if self.provider == "github_models":
                return await self._github_models_completion(prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return await self._openai_completion(prompt, max_tokens, temperature)
            elif self.provider == "local":
                return await self._local_completion(prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating completion with {self.provider}: {e}")
            # Try fallback to GitHub Models if available
            if self.provider != "github_models" and os.getenv("GITHUB_MODELS_TOKEN"):
                logger.info("Falling back to GitHub Models")
                return await self._github_models_completion(prompt, max_tokens, temperature)
            raise

    def generate_completion_sync(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Synchronous wrapper for generate_completion.
        
        Args:
            prompt: The prompt to send to the AI
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        import asyncio
        
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, we need to run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.generate_completion(prompt, max_tokens, temperature))
                    return future.result()
            else:
                # If no loop is running, we can just run the coroutine
                return asyncio.run(self.generate_completion(prompt, max_tokens, temperature))
        except Exception as e:
            logger.error(f"Error in sync completion: {e}")
            raise

    async def _github_models_completion(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate completion using GitHub Models API."""
        if not self.api_key:
            raise ValueError("GITHUB_MODELS_TOKEN environment variable required")
        
        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _openai_completion(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate completion using OpenAI API."""
        try:
            from openai import AsyncOpenAI
            
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable required")
            
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except ImportError:
            logger.warning("OpenAI package not installed, falling back to HTTP API")
            # Fallback to direct HTTP API
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

    async def _local_completion(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate completion using local model (Ollama)."""
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.ConnectError:
            logger.error("Cannot connect to local Ollama server. Make sure Ollama is running.")
            raise ValueError("Local model server not available. Start Ollama with: ollama serve")

    @staticmethod
    def from_env() -> "AIClient":
        """Create AI client from environment variables."""
        provider = os.getenv("AI_PROVIDER", "github_models")
        return AIClient(provider=provider)
