"""
Agent Manager - Agent lifecycle management

Spawns, monitors, retires, and replaces agents based on workflow needs.
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid

from autoos.core.models import Agent, AgentStatus, TrustLevel, FailureRecord
from autoos.memory.working_memory import WorkingMemory
from autoos.memory.session_memory import SessionMemory
from autoos.infrastructure.event_bus import EventBus
from autoos.infrastructure.logging import get_logger
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class AgentManager:
    """
    Agent lifecycle manager

    Features:
    - Spawn agents with required capabilities
    - Monitor agent health and performance
    - Retire completed or failed agents
    - Replace failing agents automatically
    - Enforce trust level restrictions
    - Limit concurrent agents
    """

    def __init__(
        self,
        working_memory: WorkingMemory,
        session_memory: SessionMemory,
        event_bus: EventBus,
        max_concurrent_agents: int = 10,
    ):
        """
        Initialize agent manager

        Args:
            working_memory: Working memory instance
            session_memory: Session memory instance
            event_bus: Event bus instance
            max_concurrent_agents: Maximum concurrent agents
        """
        self.working_memory = working_memory
        self.session_memory = session_memory
        self.event_bus = event_bus
        self.max_concurrent_agents = max_concurrent_agents

        self.active_agents: Dict[str, Agent] = {}

        logger.info(
            f"Agent manager initialized", max_concurrent_agents=max_concurrent_agents
        )

    def spawn_agent(
        self,
        capabilities: List[str],
        trust_level: str,
        goal: str,
        workflow_id: Optional[str] = None,
    ) -> Agent:
        """
        Create new agent with specified configuration

        Args:
            capabilities: Required capabilities
            trust_level: Trust level (restricted, standard, elevated, privileged)
            goal: Agent goal
            workflow_id: Associated workflow ID

        Returns:
            Spawned agent

        Raises:
            Exception: If max concurrent agents reached
        """
        # Check concurrent agent limit
        if len(self.active_agents) >= self.max_concurrent_agents:
            raise Exception(
                f"Maximum concurrent agents ({self.max_concurrent_agents}) reached"
            )

        # Create agent
        agent = Agent(
            agent_id=str(uuid.uuid4()),
            goal=goal,
            capabilities=capabilities,
            allowed_tools=self._get_allowed_tools(TrustLevel(trust_level)),
            preferred_llm_roles={
                "planning": "planner",
                "execution": "executor",
                "verification": "verifier",
            },
            trust_level=TrustLevel(trust_level),
            memory_scope="workflow" if workflow_id else "session",
            confidence_threshold=0.75,
            failure_history=[],
            created_at=datetime.utcnow(),
            status=AgentStatus.INITIALIZING,
        )

        # Store in active agents
        self.active_agents[agent.agent_id] = agent

        # Initialize agent memory
        self.working_memory.store_agent_memory(
            agent.agent_id,
            {
                "goal": goal,
                "capabilities": capabilities,
                "trust_level": trust_level,
                "created_at": agent.created_at.isoformat(),
            },
        )

        # Update agent status
        agent.status = AgentStatus.READY

        # Record metrics
        metrics.record_agent_spawned()

        # Publish event
        self.event_bus.publish(
            "agent.spawned",
            {
                "agent_id": agent.agent_id,
                "capabilities": capabilities,
                "trust_level": trust_level,
                "workflow_id": workflow_id,
            },
        )

        logger.info(
            f"Spawned agent",
            agent_id=agent.agent_id,
            capabilities=capabilities,
            trust_level=trust_level,
        )

        return agent

    def retire_agent(self, agent_id: str, reason: str = "completed") -> None:
        """
        Shutdown agent and archive memory

        Args:
            agent_id: Agent ID
            reason: Retirement reason (completed, failed, replaced)
        """
        agent = self.active_agents.get(agent_id)

        if not agent:
            logger.warning(f"Agent not found for retirement", agent_id=agent_id)
            return

        # Update agent status
        agent.status = AgentStatus.RETIRED

        # Archive agent memory to session memory (if needed)
        agent_memory = self.working_memory.get_agent_memory(agent_id)
        if agent_memory:
            # Store important data in session memory
            # (Simplified - full implementation would use proper archival)
            pass

        # Clear working memory
        self.working_memory.clear_agent_memory(agent_id)

        # Remove from active agents
        del self.active_agents[agent_id]

        # Record metrics
        metrics.record_agent_retired(reason)

        # Publish event
        self.event_bus.publish(
            "agent.retired", {"agent_id": agent_id, "reason": reason}
        )

        logger.info(f"Retired agent", agent_id=agent_id, reason=reason)

    def replace_agent(self, agent_id: str, reason: str) -> Agent:
        """
        Replace failing agent with new instance

        Args:
            agent_id: Agent ID to replace
            reason: Replacement reason

        Returns:
            New agent with same capabilities
        """
        old_agent = self.active_agents.get(agent_id)

        if not old_agent:
            raise ValueError(f"Agent {agent_id} not found")

        logger.info(f"Replacing agent", agent_id=agent_id, reason=reason)

        # Record failure
        failure = FailureRecord(
            failure_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            failure_type="agent_failure",
            error_message=reason,
            context={"agent_id": agent_id},
            recovery_action="agent_replacement",
            recovery_success=True,
        )

        # Retire old agent
        self.retire_agent(agent_id, reason="replaced")

        # Spawn new agent with same capabilities
        new_agent = self.spawn_agent(
            capabilities=old_agent.capabilities,
            trust_level=old_agent.trust_level.value,
            goal=old_agent.goal,
        )

        # Copy failure history
        new_agent.failure_history = old_agent.failure_history + [failure]

        # Record metrics
        metrics.record_recovery_attempt("agent_swap", True)

        # Publish event
        self.event_bus.publish(
            "agent.replaced",
            {
                "old_agent_id": agent_id,
                "new_agent_id": new_agent.agent_id,
                "reason": reason,
            },
        )

        logger.info(
            f"Replaced agent",
            old_agent_id=agent_id,
            new_agent_id=new_agent.agent_id,
        )

        return new_agent

    def get_agent_health(self, agent_id: str) -> Dict[str, any]:
        """
        Check agent health and performance metrics

        Args:
            agent_id: Agent ID

        Returns:
            Health status dictionary
        """
        agent = self.active_agents.get(agent_id)

        if not agent:
            return {"status": "not_found"}

        # Get agent memory
        memory = self.working_memory.get_agent_memory(agent_id)

        return {
            "status": agent.status.value,
            "created_at": agent.created_at.isoformat(),
            "failure_count": len(agent.failure_history),
            "memory_size": len(str(memory)) if memory else 0,
            "trust_level": agent.trust_level.value,
            "confidence_threshold": agent.confidence_threshold,
        }

    def _get_allowed_tools(self, trust_level: TrustLevel) -> List[str]:
        """
        Get tools allowed for trust level

        Args:
            trust_level: Agent trust level

        Returns:
            List of allowed tool names
        """
        # Tool permissions by trust level
        tool_permissions = {
            TrustLevel.RESTRICTED: ["read_file", "list_directory"],
            TrustLevel.STANDARD: [
                "read_file",
                "list_directory",
                "write_file",
                "http_request",
            ],
            TrustLevel.ELEVATED: [
                "read_file",
                "list_directory",
                "write_file",
                "http_request",
                "execute_command",
            ],
            TrustLevel.PRIVILEGED: ["all"],
        }

        return tool_permissions.get(trust_level, [])

    def get_active_agent_count(self) -> int:
        """
        Get number of active agents

        Returns:
            Active agent count
        """
        return len(self.active_agents)

    def get_all_agents(self) -> List[Agent]:
        """
        Get all active agents

        Returns:
            List of active agents
        """
        return list(self.active_agents.values())
