"""
Prometheus metrics collection for AUTOOS

Tracks system performance, costs, and health metrics.
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from typing import Dict, Any
import time


class MetricsCollector:
    """
    Centralized metrics collection for AUTOOS

    Tracks:
    - Workflow success/failure rates
    - Agent utilization
    - LLM latency and costs
    - Tool execution times
    - Recovery success rates
    - Confidence scores
    """

    def __init__(self, registry: CollectorRegistry = None):
        """
        Initialize metrics collector

        Args:
            registry: Prometheus registry (creates new if None)
        """
        self.registry = registry or CollectorRegistry()

        # Workflow metrics
        self.workflow_total = Counter(
            "autoos_workflow_total",
            "Total number of workflows",
            ["status"],
            registry=self.registry,
        )

        self.workflow_duration = Histogram(
            "autoos_workflow_duration_seconds",
            "Workflow execution duration",
            ["status"],
            registry=self.registry,
        )

        self.workflow_cost = Histogram(
            "autoos_workflow_cost_dollars",
            "Workflow execution cost in USD",
            registry=self.registry,
        )

        self.workflow_confidence = Histogram(
            "autoos_workflow_confidence",
            "Average confidence score per workflow",
            registry=self.registry,
        )

        # Agent metrics
        self.agent_active = Gauge(
            "autoos_agent_active",
            "Number of active agents",
            registry=self.registry,
        )

        self.agent_spawned = Counter(
            "autoos_agent_spawned_total",
            "Total agents spawned",
            registry=self.registry,
        )

        self.agent_retired = Counter(
            "autoos_agent_retired_total",
            "Total agents retired",
            ["reason"],
            registry=self.registry,
        )

        self.agent_task_duration = Histogram(
            "autoos_agent_task_duration_seconds",
            "Agent task execution duration",
            ["status"],
            registry=self.registry,
        )

        # LLM metrics
        self.llm_calls = Counter(
            "autoos_llm_calls_total",
            "Total LLM API calls",
            ["provider", "model", "role"],
            registry=self.registry,
        )

        self.llm_latency = Histogram(
            "autoos_llm_latency_seconds",
            "LLM response latency",
            ["provider", "model"],
            registry=self.registry,
        )

        self.llm_tokens = Counter(
            "autoos_llm_tokens_total",
            "Total tokens used",
            ["provider", "model"],
            registry=self.registry,
        )

        self.llm_cost = Counter(
            "autoos_llm_cost_dollars_total",
            "Total LLM cost in USD",
            ["provider", "model"],
            registry=self.registry,
        )

        self.llm_confidence = Histogram(
            "autoos_llm_confidence",
            "LLM response confidence scores",
            ["provider", "model", "role"],
            registry=self.registry,
        )

        # Tool execution metrics
        self.tool_executions = Counter(
            "autoos_tool_executions_total",
            "Total tool executions",
            ["tool_name", "status"],
            registry=self.registry,
        )

        self.tool_duration = Histogram(
            "autoos_tool_duration_seconds",
            "Tool execution duration",
            ["tool_name"],
            registry=self.registry,
        )

        # Failure and recovery metrics
        self.failures = Counter(
            "autoos_failures_total",
            "Total failures",
            ["failure_type", "component"],
            registry=self.registry,
        )

        self.recovery_attempts = Counter(
            "autoos_recovery_attempts_total",
            "Total recovery attempts",
            ["strategy"],
            registry=self.registry,
        )

        self.recovery_success = Counter(
            "autoos_recovery_success_total",
            "Successful recoveries",
            ["strategy"],
            registry=self.registry,
        )

        # Memory metrics
        self.memory_operations = Counter(
            "autoos_memory_operations_total",
            "Memory plane operations",
            ["layer", "operation"],
            registry=self.registry,
        )

        # Policy metrics
        self.policy_checks = Counter(
            "autoos_policy_checks_total",
            "Policy checks performed",
            ["policy_type", "result"],
            registry=self.registry,
        )

    # ========================================================================
    # Workflow Metrics
    # ========================================================================

    def record_workflow_started(self) -> None:
        """Record workflow start"""
        self.workflow_total.labels(status="started").inc()

    def record_workflow_completed(
        self, duration: float, cost: float, confidence: float, success: bool
    ) -> None:
        """
        Record workflow completion

        Args:
            duration: Execution time in seconds
            cost: Total cost in USD
            confidence: Average confidence score
            success: Whether workflow succeeded
        """
        status = "completed" if success else "failed"
        self.workflow_total.labels(status=status).inc()
        self.workflow_duration.labels(status=status).observe(duration)
        self.workflow_cost.observe(cost)
        self.workflow_confidence.observe(confidence)

    # ========================================================================
    # Agent Metrics
    # ========================================================================

    def record_agent_spawned(self) -> None:
        """Record agent spawn"""
        self.agent_spawned.inc()
        self.agent_active.inc()

    def record_agent_retired(self, reason: str = "completed") -> None:
        """
        Record agent retirement

        Args:
            reason: Retirement reason (completed, failed, replaced)
        """
        self.agent_retired.labels(reason=reason).inc()
        self.agent_active.dec()

    def record_agent_task(self, duration: float, success: bool) -> None:
        """
        Record agent task execution

        Args:
            duration: Task duration in seconds
            success: Whether task succeeded
        """
        status = "success" if success else "failure"
        self.agent_task_duration.labels(status=status).observe(duration)

    # ========================================================================
    # LLM Metrics
    # ========================================================================

    def record_llm_call(
        self,
        provider: str,
        model: str,
        role: str,
        latency: float,
        tokens: int,
        cost: float,
        confidence: float,
    ) -> None:
        """
        Record LLM API call

        Args:
            provider: Provider name (openai, anthropic, etc.)
            model: Model name
            role: LLM role (planner, executor, etc.)
            latency: Response time in seconds
            tokens: Tokens used
            cost: Call cost in USD
            confidence: Response confidence score
        """
        self.llm_calls.labels(provider=provider, model=model, role=role).inc()
        self.llm_latency.labels(provider=provider, model=model).observe(latency)
        self.llm_tokens.labels(provider=provider, model=model).inc(tokens)
        self.llm_cost.labels(provider=provider, model=model).inc(cost)
        self.llm_confidence.labels(provider=provider, model=model, role=role).observe(confidence)

    # ========================================================================
    # Tool Metrics
    # ========================================================================

    def record_tool_execution(self, tool_name: str, duration: float, success: bool) -> None:
        """
        Record tool execution

        Args:
            tool_name: Name of tool
            duration: Execution time in seconds
            success: Whether execution succeeded
        """
        status = "success" if success else "failure"
        self.tool_executions.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)

    # ========================================================================
    # Failure and Recovery Metrics
    # ========================================================================

    def record_failure(self, failure_type: str, component: str) -> None:
        """
        Record failure

        Args:
            failure_type: Type of failure
            component: Component where failure occurred
        """
        self.failures.labels(failure_type=failure_type, component=component).inc()

    def record_recovery_attempt(self, strategy: str, success: bool) -> None:
        """
        Record recovery attempt

        Args:
            strategy: Recovery strategy used
            success: Whether recovery succeeded
        """
        self.recovery_attempts.labels(strategy=strategy).inc()
        if success:
            self.recovery_success.labels(strategy=strategy).inc()

    # ========================================================================
    # Memory Metrics
    # ========================================================================

    def record_memory_operation(self, layer: str, operation: str) -> None:
        """
        Record memory operation

        Args:
            layer: Memory layer (working, session, long_term, audit)
            operation: Operation type (read, write, delete)
        """
        self.memory_operations.labels(layer=layer, operation=operation).inc()

    # ========================================================================
    # Policy Metrics
    # ========================================================================

    def record_policy_check(self, policy_type: str, allowed: bool) -> None:
        """
        Record policy check

        Args:
            policy_type: Type of policy
            allowed: Whether action was allowed
        """
        result = "allowed" if allowed else "denied"
        self.policy_checks.labels(policy_type=policy_type, result=result).inc()

    # ========================================================================
    # Export
    # ========================================================================

    def export_metrics(self) -> bytes:
        """
        Export metrics in Prometheus format

        Returns:
            Metrics data as bytes
        """
        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """
        Get content type for metrics endpoint

        Returns:
            Content type string
        """
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
_metrics_collector: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector instance

    Returns:
        Metrics collector
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def initialize_metrics() -> MetricsCollector:
    """
    Initialize global metrics collector

    Returns:
        Metrics collector instance
    """
    global _metrics_collector
    _metrics_collector = MetricsCollector()
    return _metrics_collector
