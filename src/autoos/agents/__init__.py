"""
AUTOOS Agent Systems

Complete agent capabilities gathered from leading AI agent frameworks:
- AutoGPT: Autonomous agents with goal decomposition
- BabyAGI: Self-directed task execution
- CrewAI: Collaborative multi-agent teams
- Microsoft Autogen: Inter-agent communication
- MetaGPT: Role-based agent collaboration
- LangChain Agents: Tool-using agents
- Swarm Intelligence: Collective problem solving

All integrated with AUTOOS's advanced intelligence systems.
"""

from autoos.agents.autonomous_agent import AutonomousAgent, Goal
from autoos.agents.collaborative_agents import (
    CollaborativeAgent,
    AgentTeam,
    AgentRole,
    Message,
)
from autoos.agents.specialized_agents import (
    CodeGeneratorAgent,
    DataAnalystAgent,
    ResearchAgent,
    QualityAssuranceAgent,
    DocumentationAgent,
    OptimizationAgent,
    AgentFactory,
)
from autoos.agents.agent_swarm import (
    AgentSwarm,
    ConsensusSwarm,
    SwarmAgent,
)

__all__ = [
    # Autonomous Agents
    "AutonomousAgent",
    "Goal",
    # Collaborative Agents
    "CollaborativeAgent",
    "AgentTeam",
    "AgentRole",
    "Message",
    # Specialized Agents
    "CodeGeneratorAgent",
    "DataAnalystAgent",
    "ResearchAgent",
    "QualityAssuranceAgent",
    "DocumentationAgent",
    "OptimizationAgent",
    "AgentFactory",
    # Swarm Intelligence
    "AgentSwarm",
    "ConsensusSwarm",
    "SwarmAgent",
]
