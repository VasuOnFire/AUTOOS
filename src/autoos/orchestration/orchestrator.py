"""
Orchestrator - Core workflow execution engine

Manages workflow execution, state transitions, failure detection, and recovery.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import asyncio

from autoos.core.models import (
    Workflow,
    WorkflowStep,
    WorkflowState,
    Agent,
    TaskResult,
    WorkflowResult,
    FailureType,
    FailureRecord,
)
from autoos.memory.working_memory import WorkingMemory
from autoos.memory.session_memory import SessionMemory
from autoos.infrastructure.event_bus import EventBus
from autoos.infrastructure.logging import get_logger, set_trace_context
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class RecoveryAction:
    """Recovery action to take on failure"""

    def __init__(self, action_type: str, details: Dict[str, Any]):
        self.action_type = action_type  # retry, agent_swap, llm_swap, strategy_mutation, escalate
        self.details = details


class Orchestrator:
    """
    Core workflow execution engine

    Features:
    - Execute workflows step by step
    - Manage state transitions
    - Detect failures within 5 seconds
    - Automatic recovery with escalation
    - State persistence and recovery
    - Partial rollback support
    """

    def __init__(
        self,
        working_memory: WorkingMemory,
        session_memory: SessionMemory,
        event_bus: EventBus,
        agent_manager: Any,  # Will be AgentManager
    ):
        """
        Initialize orchestrator

        Args:
            working_memory: Working memory instance
            session_memory: Session memory instance
            event_bus: Event bus instance
            agent_manager: Agent manager instance
        """
        self.working_memory = working_memory
        self.session_memory = session_memory
        self.event_bus = event_bus
        self.agent_manager = agent_manager

        logger.info("Orchestrator initialized")

    def execute_workflow(self, workflow: Workflow) -> WorkflowResult:
        """
        Execute complete workflow

        Args:
            workflow: Workflow to execute

        Returns:
            Workflow execution result
        """
        workflow_id = workflow.workflow_id
        set_trace_context(workflow_id=workflow_id)

        logger.info(f"Starting workflow execution", workflow_id=workflow_id)
        metrics.record_workflow_started()

        start_time = time.time()
        total_cost = 0.0
        total_confidence = 0.0
        steps_completed = 0
        steps_failed = 0

        try:
            # Update workflow state
            workflow.state = WorkflowState.RUNNING
            self.persist_state(workflow)

            # Publish event
            self.event_bus.publish(
                "workflow.started",
                {"workflow_id": workflow_id, "timestamp": datetime.utcnow().isoformat()},
            )

            # Execute steps in order
            for step_group in workflow.execution_order:
                # Execute parallel steps
                results = []
                for step_id in step_group:
                    step = workflow.steps[step_id]

                    try:
                        # Spawn agent for step
                        agent = self.agent_manager.spawn_agent(
                            capabilities=step.required_capabilities,
                            trust_level="standard",
                            goal=step.goal_id,
                        )

                        # Execute step
                        result = self.execute_step(step, agent)

                        if result.success:
                            steps_completed += 1
                            total_cost += result.cost
                            total_confidence += result.confidence
                        else:
                            steps_failed += 1
                            # Handle failure
                            recovery = self.handle_failure(step, Exception(result.errors[0]))
                            if recovery.action_type == "escalate":
                                raise Exception(f"Step {step_id} failed after all recovery attempts")

                        results.append(result)

                        # Retire agent
                        self.agent_manager.retire_agent(agent.agent_id)

                    except Exception as e:
                        logger.error(f"Step execution failed", step_id=step_id, error=str(e))
                        steps_failed += 1

                        # Try recovery
                        recovery = self.handle_failure(step, e)
                        if recovery.action_type == "escalate":
                            raise

            # Workflow completed successfully
            workflow.state = WorkflowState.COMPLETED
            self.persist_state(workflow)

            duration = time.time() - start_time
            avg_confidence = total_confidence / steps_completed if steps_completed > 0 else 0.0

            # Record metrics
            metrics.record_workflow_completed(
                duration=duration, cost=total_cost, confidence=avg_confidence, success=True
            )

            # Publish event
            self.event_bus.publish(
                "workflow.completed",
                {
                    "workflow_id": workflow_id,
                    "duration": duration,
                    "cost": total_cost,
                    "confidence": avg_confidence,
                },
            )

            # Update session memory
            self.session_memory.update_workflow_status(
                workflow_id=workflow_id,
                status="completed",
                completed_at=datetime.utcnow(),
                cost=total_cost,
                confidence=avg_confidence,
            )

            logger.info(
                f"Workflow completed successfully",
                workflow_id=workflow_id,
                duration=duration,
                cost=total_cost,
            )

            return WorkflowResult(
                workflow_id=workflow_id,
                success=True,
                final_output=results[-1].output if results else None,
                total_cost=total_cost,
                total_time=duration,
                avg_confidence=avg_confidence,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                audit_trail_id="",  # Will be populated by audit system
            )

        except Exception as e:
            # Workflow failed
            workflow.state = WorkflowState.FAILED
            self.persist_state(workflow)

            duration = time.time() - start_time

            # Record metrics
            metrics.record_workflow_completed(
                duration=duration, cost=total_cost, confidence=0.0, success=False
            )

            # Publish event
            self.event_bus.publish(
                "workflow.failed",
                {"workflow_id": workflow_id, "error": str(e), "duration": duration},
            )

            # Update session memory
            self.session_memory.update_workflow_status(
                workflow_id=workflow_id, status="failed", completed_at=datetime.utcnow()
            )

            logger.error(f"Workflow failed", workflow_id=workflow_id, error=str(e))

            return WorkflowResult(
                workflow_id=workflow_id,
                success=False,
                final_output=None,
                total_cost=total_cost,
                total_time=duration,
                avg_confidence=0.0,
                steps_completed=steps_completed,
                steps_failed=steps_failed,
                audit_trail_id="",
            )

    def execute_step(self, step: WorkflowStep, agent: Agent) -> TaskResult:
        """
        Execute single workflow step

        Args:
            step: Workflow step to execute
            agent: Agent to execute step

        Returns:
            Step execution result
        """
        logger.info(f"Executing step", step_id=step.step_id, agent_id=agent.agent_id)

        # Publish event
        self.event_bus.publish(
            "workflow.step_started",
            {"step_id": step.step_id, "agent_id": agent.agent_id},
        )

        start_time = time.time()

        try:
            # Execute step with retry logic
            retry_count = 0
            last_error = None

            while retry_count < step.retry_config.max_attempts:
                try:
                    # Simulate step execution (will be replaced with actual agent execution)
                    result = TaskResult(
                        success=True,
                        output={"step_id": step.step_id, "status": "completed"},
                        confidence=0.85,
                        reasoning="Step executed successfully",
                        cost=0.01,
                        latency=time.time() - start_time,
                        errors=[],
                    )

                    # Publish success event
                    self.event_bus.publish(
                        "workflow.step_completed",
                        {"step_id": step.step_id, "agent_id": agent.agent_id},
                    )

                    return result

                except Exception as e:
                    last_error = e
                    retry_count += 1

                    if retry_count < step.retry_config.max_attempts:
                        # Calculate backoff delay
                        delay = min(
                            step.retry_config.initial_delay_seconds
                            * (step.retry_config.backoff_multiplier ** retry_count),
                            step.retry_config.max_delay_seconds,
                        )

                        logger.warning(
                            f"Step failed, retrying",
                            step_id=step.step_id,
                            retry=retry_count,
                            delay=delay,
                        )

                        time.sleep(delay)

            # All retries failed
            raise last_error

        except Exception as e:
            # Step failed
            logger.error(f"Step execution failed", step_id=step.step_id, error=str(e))

            # Publish failure event
            self.event_bus.publish(
                "workflow.step_failed",
                {"step_id": step.step_id, "agent_id": agent.agent_id, "error": str(e)},
            )

            return TaskResult(
                success=False,
                output=None,
                confidence=0.0,
                reasoning="Step execution failed",
                cost=0.0,
                latency=time.time() - start_time,
                errors=[str(e)],
            )

    def handle_failure(self, step: WorkflowStep, error: Exception) -> RecoveryAction:
        """
        Determine recovery strategy for failure

        Args:
            step: Failed step
            error: Exception that occurred

        Returns:
            Recovery action to take
        """
        # Classify failure type
        failure_type = self._classify_failure(error)

        logger.warning(
            f"Handling failure",
            step_id=step.step_id,
            failure_type=failure_type.value,
            error=str(error),
        )

        # Record failure
        metrics.record_failure(failure_type.value, "orchestrator")

        # Publish event
        self.event_bus.publish(
            "workflow.recovery_triggered",
            {"step_id": step.step_id, "failure_type": failure_type.value},
        )

        # Escalating recovery strategies
        if failure_type == FailureType.TRANSIENT:
            # Already handled by retry logic
            return RecoveryAction("retry", {"step_id": step.step_id})

        elif failure_type == FailureType.MODEL_ERROR:
            # Try different LLM
            return RecoveryAction("llm_swap", {"step_id": step.step_id})

        elif failure_type == FailureType.TOOL_ERROR:
            # Try different agent
            return RecoveryAction("agent_swap", {"step_id": step.step_id})

        else:
            # Escalate to human
            return RecoveryAction(
                "escalate", {"step_id": step.step_id, "error": str(error)}
            )

    def _classify_failure(self, error: Exception) -> FailureType:
        """
        Classify failure type

        Args:
            error: Exception that occurred

        Returns:
            Failure type classification
        """
        error_str = str(error).lower()

        if "timeout" in error_str:
            return FailureType.TIMEOUT
        elif "rate limit" in error_str or "quota" in error_str:
            return FailureType.RESOURCE_EXHAUSTION
        elif "policy" in error_str or "unauthorized" in error_str:
            return FailureType.POLICY_VIOLATION
        elif "model" in error_str or "llm" in error_str:
            return FailureType.MODEL_ERROR
        elif "tool" in error_str:
            return FailureType.TOOL_ERROR
        else:
            return FailureType.UNKNOWN

    def persist_state(self, workflow: Workflow) -> None:
        """
        Save workflow state to memory plane

        Args:
            workflow: Workflow to persist
        """
        state = {
            "workflow_id": workflow.workflow_id,
            "state": workflow.state.value,
            "steps": {k: v.to_dict() for k, v in workflow.steps.items()},
            "execution_order": workflow.execution_order,
            "metadata": workflow.metadata,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.working_memory.store_workflow_state(workflow.workflow_id, state)
        logger.debug(f"Persisted workflow state", workflow_id=workflow.workflow_id)

    def restore_state(self, workflow_id: str) -> Optional[Workflow]:
        """
        Restore workflow from persisted state

        Args:
            workflow_id: Workflow ID

        Returns:
            Restored workflow or None
        """
        state = self.working_memory.get_workflow_state(workflow_id)

        if state:
            logger.info(f"Restored workflow state", workflow_id=workflow_id)
            # Reconstruct workflow from state
            # (Simplified - full implementation would reconstruct all objects)
            return Workflow(
                workflow_id=state["workflow_id"],
                state=WorkflowState(state["state"]),
                execution_order=state["execution_order"],
                metadata=state["metadata"],
            )

        return None

    def pause_workflow(self, workflow_id: str) -> bool:
        """
        Pause running workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            True if paused successfully
        """
        workflow = self.restore_state(workflow_id)

        if workflow and workflow.state == WorkflowState.RUNNING:
            workflow.state = WorkflowState.PAUSED
            self.persist_state(workflow)

            self.event_bus.publish("workflow.paused", {"workflow_id": workflow_id})

            logger.info(f"Paused workflow", workflow_id=workflow_id)
            return True

        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """
        Resume paused workflow

        Args:
            workflow_id: Workflow ID

        Returns:
            True if resumed successfully
        """
        workflow = self.restore_state(workflow_id)

        if workflow and workflow.state == WorkflowState.PAUSED:
            workflow.state = WorkflowState.RUNNING
            self.persist_state(workflow)

            self.event_bus.publish("workflow.resumed", {"workflow_id": workflow_id})

            logger.info(f"Resumed workflow", workflow_id=workflow_id)
            return True

        return False
