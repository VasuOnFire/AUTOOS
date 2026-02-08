"""
Intelligence Fabric - Multi-LLM orchestration layer

Routes tasks to appropriate models, performs cross-verification,
detects hallucinations, and manages fallbacks.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from difflib import SequenceMatcher

from autoos.core.models import (
    LLMProvider,
    LLMResponse,
    LLMRole,
    VerificationResult,
    FailureType,
)
from autoos.execution.llm_providers import LLMProviderFactory, BaseLLMProvider, LLMConfig
from autoos.infrastructure.logging import get_logger
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


@dataclass
class Task:
    """Task to be executed by LLM"""

    task_id: str
    description: str
    prompt: str
    context: Dict[str, Any]
    critical: bool = False


class ModelCapabilityRegistry:
    """
    Registry of LLM capabilities, costs, and performance

    Tracks model performance and updates routing heuristics.
    """

    def __init__(self):
        """Initialize registry"""
        self.providers: Dict[str, LLMProvider] = {}
        self.performance_history: Dict[str, List[float]] = {}

    def register_provider(self, provider: LLMProvider) -> None:
        """
        Register LLM provider

        Args:
            provider: Provider configuration
        """
        key = f"{provider.provider_name}:{provider.model_name}"
        self.providers[key] = provider
        logger.info(f"Registered provider: {key}")

    def get_provider(self, provider_name: str, model_name: str) -> Optional[LLMProvider]:
        """
        Get provider by name

        Args:
            provider_name: Provider name
            model_name: Model name

        Returns:
            Provider configuration or None
        """
        key = f"{provider_name}:{model_name}"
        return self.providers.get(key)

    def get_providers_by_role(self, role: LLMRole) -> List[LLMProvider]:
        """
        Get providers suitable for role

        Args:
            role: LLM role

        Returns:
            List of suitable providers
        """
        # Role-based provider selection
        role_preferences = {
            LLMRole.PLANNER: ["gpt-4", "claude-3-opus"],
            LLMRole.EXECUTOR: ["gpt-3.5-turbo", "claude-3-haiku"],
            LLMRole.VERIFIER: ["claude-3-opus", "gpt-4"],
            LLMRole.AUDITOR: ["gpt-4", "claude-3-sonnet"],
            LLMRole.SYNTHESIZER: ["claude-3-opus", "gpt-4"],
        }

        preferred_models = role_preferences.get(role, [])
        suitable_providers = []

        for provider in self.providers.values():
            if any(model in provider.model_name for model in preferred_models):
                suitable_providers.append(provider)

        # Sort by reliability and cost
        suitable_providers.sort(
            key=lambda p: (-p.reliability_score, p.cost_per_token, p.avg_latency)
        )

        return suitable_providers

    def update_performance(
        self, provider: LLMProvider, latency: float, success: bool
    ) -> None:
        """
        Update provider performance metrics

        Args:
            provider: Provider that was used
            latency: Response latency
            success: Whether call succeeded
        """
        key = f"{provider.provider_name}:{provider.model_name}"

        # Update latency
        provider.avg_latency = (provider.avg_latency * 0.9) + (latency * 0.1)

        # Update reliability
        if success:
            provider.reliability_score = min(1.0, provider.reliability_score + 0.01)
        else:
            provider.reliability_score = max(0.0, provider.reliability_score - 0.05)

        logger.debug(
            f"Updated performance for {key}",
            latency=provider.avg_latency,
            reliability=provider.reliability_score,
        )


class IntelligenceFabric:
    """
    Multi-LLM orchestration layer

    Features:
    - Dynamic routing based on task and role
    - Cross-verification for critical decisions
    - Hallucination detection
    - Automatic fallback on failure
    - Cost and latency tracking
    """

    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize intelligence fabric

        Args:
            api_keys: Dictionary of provider API keys
        """
        self.api_keys = api_keys
        self.registry = ModelCapabilityRegistry()
        self.provider_instances: Dict[str, BaseLLMProvider] = {}

        # Initialize default providers
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize default LLM providers"""
        default_providers = [
            LLMProvider(
                provider_name="openai",
                model_name="gpt-4",
                api_endpoint="https://api.openai.com/v1",
                cost_per_token=0.00003,
                capabilities=["reasoning", "planning", "analysis"],
            ),
            LLMProvider(
                provider_name="openai",
                model_name="gpt-3.5-turbo",
                api_endpoint="https://api.openai.com/v1",
                cost_per_token=0.000002,
                capabilities=["execution", "fast_tasks"],
            ),
            LLMProvider(
                provider_name="anthropic",
                model_name="claude-3-opus-20240229",
                api_endpoint="https://api.anthropic.com/v1",
                cost_per_token=0.000015,
                capabilities=["reasoning", "verification", "synthesis"],
            ),
            LLMProvider(
                provider_name="anthropic",
                model_name="claude-3-haiku-20240307",
                api_endpoint="https://api.anthropic.com/v1",
                cost_per_token=0.00000025,
                capabilities=["fast_tasks", "execution"],
            ),
        ]

        for provider in default_providers:
            self.registry.register_provider(provider)

    def route_task(self, task: Task, role: LLMRole) -> LLMProvider:
        """
        Select appropriate LLM for task and role

        Args:
            task: Task to execute
            role: LLM role for this task

        Returns:
            Selected provider

        Raises:
            ValueError: If no suitable provider found
        """
        providers = self.registry.get_providers_by_role(role)

        if not providers:
            raise ValueError(f"No providers available for role {role}")

        # Select best provider (already sorted by performance)
        selected = providers[0]

        logger.info(
            f"Routed task to {selected.provider_name}:{selected.model_name}",
            role=role.value,
            task_id=task.task_id,
        )

        return selected

    def call_llm(
        self, provider: LLMProvider, prompt: str, config: LLMConfig, role: LLMRole
    ) -> LLMResponse:
        """
        Execute LLM call with specified provider

        Args:
            provider: Provider to use
            prompt: Input prompt
            config: LLM configuration
            role: LLM role

        Returns:
            LLM response

        Raises:
            Exception: If call fails after retries
        """
        key = f"{provider.provider_name}:{provider.model_name}"

        # Get or create provider instance
        if key not in self.provider_instances:
            api_key = self.api_keys.get(provider.provider_name)
            if not api_key:
                raise ValueError(f"No API key for provider {provider.provider_name}")

            self.provider_instances[key] = LLMProviderFactory.create(provider, api_key)

        provider_instance = self.provider_instances[key]

        try:
            response = provider_instance.call(prompt, config, role)

            # Update performance metrics
            self.registry.update_performance(provider, response.latency, True)

            # Record metrics
            metrics.record_llm_call(
                provider=provider.provider_name,
                model=provider.model_name,
                role=role.value,
                latency=response.latency,
                tokens=response.tokens_used,
                cost=response.cost,
                confidence=response.confidence,
            )

            return response

        except Exception as e:
            logger.error(f"LLM call failed: {e}", provider=key, role=role.value)
            self.registry.update_performance(provider, 0.0, False)
            metrics.record_failure(FailureType.MODEL_ERROR.value, "intelligence_fabric")
            raise

    def cross_verify(
        self, task: Task, responses: List[LLMResponse]
    ) -> VerificationResult:
        """
        Compare multiple LLM outputs for consistency

        Args:
            task: Original task
            responses: List of responses from different models

        Returns:
            Verification result with consensus decision
        """
        if len(responses) < 2:
            return VerificationResult(
                consensus=True,
                selected_response=responses[0] if responses else None,
                discrepancies=[],
                confidence=responses[0].confidence if responses else 0.0,
            )

        # Compare responses for similarity
        similarities = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = SequenceMatcher(
                    None, responses[i].response, responses[j].response
                ).ratio()
                similarities.append(similarity)

        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

        # Consensus if average similarity > 0.7
        consensus = avg_similarity > 0.7

        # Select response with highest confidence
        selected = max(responses, key=lambda r: r.confidence)

        # Identify discrepancies
        discrepancies = []
        if not consensus:
            for i, response in enumerate(responses):
                if response != selected:
                    discrepancies.append(
                        f"Model {response.provider.model_name} disagreed "
                        f"(similarity: {similarities[i] if i < len(similarities) else 0:.2f})"
                    )

        result = VerificationResult(
            consensus=consensus,
            selected_response=selected,
            discrepancies=discrepancies,
            confidence=selected.confidence if consensus else selected.confidence * 0.5,
        )

        logger.info(
            f"Cross-verification completed",
            task_id=task.task_id,
            consensus=consensus,
            similarity=avg_similarity,
        )

        return result

    def detect_hallucination(
        self, response: LLMResponse, context: Dict[str, Any]
    ) -> bool:
        """
        Identify potential hallucinations

        Args:
            response: LLM response to check
            context: Context for validation

        Returns:
            True if hallucination detected
        """
        # Hallucination indicators
        hallucination_detected = False

        # Low confidence is a strong indicator
        if response.confidence < 0.5:
            hallucination_detected = True
            logger.warning(
                f"Low confidence detected",
                confidence=response.confidence,
                provider=response.provider.model_name,
            )

        # Check for uncertainty markers
        uncertainty_markers = [
            "i'm not sure",
            "i don't know",
            "i cannot verify",
            "this might be incorrect",
        ]
        if any(marker in response.response.lower() for marker in uncertainty_markers):
            hallucination_detected = True
            logger.warning(f"Uncertainty markers detected in response")

        if hallucination_detected:
            metrics.record_failure(FailureType.MODEL_ERROR.value, "hallucination_detection")

        return hallucination_detected

    def calculate_confidence(self, response: LLMResponse) -> float:
        """
        Compute confidence score for response

        Args:
            response: LLM response

        Returns:
            Confidence score (0-1)
        """
        # Already calculated in provider, but can be refined here
        return response.confidence

    def execute_with_fallback(
        self, task: Task, role: LLMRole, config: LLMConfig
    ) -> LLMResponse:
        """
        Execute task with automatic fallback on failure

        Args:
            task: Task to execute
            role: LLM role
            config: LLM configuration

        Returns:
            LLM response

        Raises:
            Exception: If all providers fail
        """
        providers = self.registry.get_providers_by_role(role)

        last_error = None
        for provider in providers:
            try:
                response = self.call_llm(provider, task.prompt, config, role)
                return response

            except Exception as e:
                logger.warning(
                    f"Provider {provider.model_name} failed, trying fallback",
                    error=str(e),
                )
                last_error = e
                metrics.record_recovery_attempt("llm_fallback", False)
                continue

        # All providers failed
        logger.error(f"All LLM providers failed for task {task.task_id}")
        raise Exception(f"All LLM providers failed: {last_error}")

    def execute_critical_task(self, task: Task, role: LLMRole, config: LLMConfig) -> LLMResponse:
        """
        Execute critical task with multi-model verification

        Args:
            task: Critical task
            role: LLM role
            config: LLM configuration

        Returns:
            Verified LLM response
        """
        # Get multiple providers for verification
        providers = self.registry.get_providers_by_role(role)[:2]  # Use top 2

        responses = []
        for provider in providers:
            try:
                response = self.call_llm(provider, task.prompt, config, role)
                responses.append(response)
            except Exception as e:
                logger.warning(f"Provider {provider.model_name} failed: {e}")

        if not responses:
            raise Exception("No providers succeeded for critical task")

        # Cross-verify responses
        verification = self.cross_verify(task, responses)

        if not verification.consensus:
            logger.warning(
                f"Models disagreed on critical task",
                task_id=task.task_id,
                discrepancies=verification.discrepancies,
            )

        return verification.selected_response
