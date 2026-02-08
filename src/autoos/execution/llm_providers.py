"""
LLM Provider abstraction layer

Provides unified interface for multiple LLM providers with automatic fallback.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import openai
import anthropic
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from autoos.core.models import LLMProvider, LLMResponse, LLMRole
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM call"""

    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, provider: LLMProvider, api_key: str):
        """
        Initialize provider

        Args:
            provider: Provider configuration
            api_key: API key for provider
        """
        self.provider = provider
        self.api_key = api_key

    @abstractmethod
    def call(self, prompt: str, config: LLMConfig, role: LLMRole) -> LLMResponse:
        """
        Call LLM with prompt

        Args:
            prompt: Input prompt
            config: LLM configuration
            role: LLM role for this call

        Returns:
            LLM response with metadata
        """
        pass

    def _calculate_confidence(self, response_text: str, metadata: Dict[str, Any]) -> float:
        """
        Calculate confidence score for response

        Args:
            response_text: Response text
            metadata: Response metadata

        Returns:
            Confidence score (0-1)
        """
        # Simple heuristic - can be enhanced with more sophisticated methods
        confidence = 0.8

        # Reduce confidence for very short responses
        if len(response_text) < 50:
            confidence -= 0.1

        # Reduce confidence if response contains uncertainty markers
        uncertainty_markers = [
            "i'm not sure",
            "i don't know",
            "maybe",
            "perhaps",
            "possibly",
            "unclear",
        ]
        if any(marker in response_text.lower() for marker in uncertainty_markers):
            confidence -= 0.2

        # Increase confidence if response is detailed
        if len(response_text) > 500:
            confidence += 0.1

        return max(0.0, min(1.0, confidence))


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""

    def __init__(self, provider: LLMProvider, api_key: str):
        super().__init__(provider, api_key)
        self.client = openai.OpenAI(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def call(self, prompt: str, config: LLMConfig, role: LLMRole) -> LLMResponse:
        """Call OpenAI API"""
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.provider.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences,
            )

            latency = time.time() - start_time
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = tokens_used * self.provider.cost_per_token

            confidence = self._calculate_confidence(
                response_text, {"finish_reason": response.choices[0].finish_reason}
            )

            logger.info(
                f"OpenAI call completed",
                model=self.provider.model_name,
                tokens=tokens_used,
                latency=latency,
                cost=cost,
            )

            return LLMResponse(
                provider=self.provider,
                role=role,
                prompt=prompt,
                response=response_text,
                confidence=confidence,
                tokens_used=tokens_used,
                latency=latency,
                cost=cost,
            )

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider"""

    def __init__(self, provider: LLMProvider, api_key: str):
        super().__init__(provider, api_key)
        self.client = anthropic.Anthropic(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def call(self, prompt: str, config: LLMConfig, role: LLMRole) -> LLMResponse:
        """Call Anthropic API"""
        start_time = time.time()

        try:
            response = self.client.messages.create(
                model=self.provider.model_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                messages=[{"role": "user", "content": prompt}],
                stop_sequences=config.stop_sequences,
            )

            latency = time.time() - start_time
            response_text = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = tokens_used * self.provider.cost_per_token

            confidence = self._calculate_confidence(
                response_text, {"stop_reason": response.stop_reason}
            )

            logger.info(
                f"Anthropic call completed",
                model=self.provider.model_name,
                tokens=tokens_used,
                latency=latency,
                cost=cost,
            )

            return LLMResponse(
                provider=self.provider,
                role=role,
                prompt=prompt,
                response=response_text,
                confidence=confidence,
                tokens_used=tokens_used,
                latency=latency,
                cost=cost,
            )

        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise


class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""

    def __init__(self, provider: LLMProvider, api_key: str):
        super().__init__(provider, api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.provider.model_name)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def call(self, prompt: str, config: LLMConfig, role: LLMRole) -> LLMResponse:
        """Call Google Gemini API"""
        start_time = time.time()

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                top_p=config.top_p,
                stop_sequences=config.stop_sequences,
            )

            response = self.model.generate_content(prompt, generation_config=generation_config)

            latency = time.time() - start_time
            response_text = response.text

            # Estimate tokens (Google doesn't provide exact count in all cases)
            tokens_used = len(prompt.split()) + len(response_text.split())
            cost = tokens_used * self.provider.cost_per_token

            confidence = self._calculate_confidence(response_text, {})

            logger.info(
                f"Google call completed",
                model=self.provider.model_name,
                tokens=tokens_used,
                latency=latency,
                cost=cost,
            )

            return LLMResponse(
                provider=self.provider,
                role=role,
                prompt=prompt,
                response=response_text,
                confidence=confidence,
                tokens_used=tokens_used,
                latency=latency,
                cost=cost,
            )

        except Exception as e:
            logger.error(f"Google API call failed: {e}")
            raise


class LLMProviderFactory:
    """Factory for creating LLM provider instances"""

    @staticmethod
    def create(provider: LLMProvider, api_key: str) -> BaseLLMProvider:
        """
        Create provider instance

        Args:
            provider: Provider configuration
            api_key: API key

        Returns:
            Provider instance

        Raises:
            ValueError: If provider not supported
        """
        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
        }

        provider_class = provider_map.get(provider.provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider.provider_name}")

        return provider_class(provider, api_key)
