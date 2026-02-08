"""
Collaborative Multi-Agent System

Inspired by CrewAI, Microsoft Autogen, and MetaGPT.
Multiple agents work together, communicate, and coordinate to solve complex tasks.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from autoos.core.models import Agent
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class AgentRole(Enum):
    """Agent roles in collaborative system"""

    LEADER = "leader"  # Coordinates other agents
    RESEARCHER = "researcher"  # Gathers information
    ANALYST = "analyst"  # Analyzes data
    EXECUTOR = "executor"  # Executes actions
    REVIEWER = "reviewer"  # Reviews and validates
    SPECIALIST = "specialist"  # Domain expert


class Message:
    """Message between agents"""

    def __init__(
        self,
        sender_id: str,
        receiver_id: str,
        content: str,
        message_type: str = "info",
    ):
        self.message_id = f"msg_{datetime.utcnow().timestamp()}"
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.message_type = message_type  # info, request, response, error
        self.timestamp = datetime.utcnow().isoformat()


class CollaborativeAgent:
    """
    Agent that can collaborate with other agents

    Features:
    - Inter-agent communication
    - Task delegation
    - Knowledge sharing
    - Consensus building
    - Conflict resolution
    """

    def __init__(self, agent: Agent, role: AgentRole):
        """
        Initialize collaborative agent

        Args:
            agent: Base agent configuration
            role: Agent's role in collaboration
        """
        self.agent = agent
        self.role = role
        self.inbox: List[Message] = []
        self.outbox: List[Message] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.collaborators: Dict[str, "CollaborativeAgent"] = {}

        logger.info(
            f"Collaborative agent initialized",
            agent_id=agent.agent_id,
            role=role.value,
        )

    def send_message(self, receiver_id: str, content: str, message_type: str = "info") -> Message:
        """
        Send message to another agent

        Args:
            receiver_id: Receiver agent ID
            content: Message content
            message_type: Type of message

        Returns:
            Sent message
        """
        message = Message(
            sender_id=self.agent.agent_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
        )

        self.outbox.append(message)

        # Deliver to receiver if available
        if receiver_id in self.collaborators:
            self.collaborators[receiver_id].receive_message(message)

        logger.info(
            f"Message sent",
            from_agent=self.agent.agent_id,
            to_agent=receiver_id,
            type=message_type,
        )

        return message

    def receive_message(self, message: Message) -> None:
        """
        Receive message from another agent

        Args:
            message: Received message
        """
        self.inbox.append(message)

        logger.info(
            f"Message received",
            agent_id=self.agent.agent_id,
            from_agent=message.sender_id,
            type=message.message_type,
        )

    def process_messages(self) -> List[Dict[str, Any]]:
        """
        Process all pending messages

        Returns:
            List of processed messages with responses
        """
        processed = []

        for message in self.inbox:
            response = self._handle_message(message)
            processed.append(
                {
                    "message": message,
                    "response": response,
                    "processed_at": datetime.utcnow().isoformat(),
                }
            )

        # Clear inbox
        self.inbox.clear()

        logger.info(f"Processed {len(processed)} messages", agent_id=self.agent.agent_id)

        return processed

    def _handle_message(self, message: Message) -> Optional[str]:
        """Handle incoming message based on type"""
        if message.message_type == "request":
            # Handle request based on role
            if self.role == AgentRole.RESEARCHER:
                return self._handle_research_request(message.content)
            elif self.role == AgentRole.ANALYST:
                return self._handle_analysis_request(message.content)
            elif self.role == AgentRole.EXECUTOR:
                return self._handle_execution_request(message.content)
            elif self.role == AgentRole.REVIEWER:
                return self._handle_review_request(message.content)

        return None

    def _handle_research_request(self, request: str) -> str:
        """Handle research request"""
        return f"Research completed for: {request}"

    def _handle_analysis_request(self, request: str) -> str:
        """Handle analysis request"""
        return f"Analysis completed for: {request}"

    def _handle_execution_request(self, request: str) -> str:
        """Handle execution request"""
        return f"Execution completed for: {request}"

    def _handle_review_request(self, request: str) -> str:
        """Handle review request"""
        return f"Review completed for: {request}"

    def share_knowledge(self, key: str, value: Any) -> None:
        """
        Share knowledge with collaborators

        Args:
            key: Knowledge key
            value: Knowledge value
        """
        self.knowledge_base[key] = value

        # Broadcast to collaborators
        for collaborator_id, collaborator in self.collaborators.items():
            collaborator.receive_knowledge(key, value, self.agent.agent_id)

        logger.info(
            f"Knowledge shared",
            agent_id=self.agent.agent_id,
            key=key,
            collaborators=len(self.collaborators),
        )

    def receive_knowledge(self, key: str, value: Any, source_agent_id: str) -> None:
        """
        Receive knowledge from another agent

        Args:
            key: Knowledge key
            value: Knowledge value
            source_agent_id: Source agent ID
        """
        self.knowledge_base[key] = {
            "value": value,
            "source": source_agent_id,
            "received_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Knowledge received",
            agent_id=self.agent.agent_id,
            key=key,
            from_agent=source_agent_id,
        )

    def add_collaborator(self, collaborator: "CollaborativeAgent") -> None:
        """
        Add collaborator agent

        Args:
            collaborator: Collaborator agent
        """
        self.collaborators[collaborator.agent.agent_id] = collaborator

        logger.info(
            f"Collaborator added",
            agent_id=self.agent.agent_id,
            collaborator_id=collaborator.agent.agent_id,
            collaborator_role=collaborator.role.value,
        )


class AgentTeam:
    """
    Team of collaborative agents working together

    Features:
    - Team coordination
    - Task distribution
    - Consensus building
    - Conflict resolution
    - Performance tracking
    """

    def __init__(self, team_id: str, team_name: str):
        """
        Initialize agent team

        Args:
            team_id: Team identifier
            team_name: Team name
        """
        self.team_id = team_id
        self.team_name = team_name
        self.members: Dict[str, CollaborativeAgent] = {}
        self.leader: Optional[CollaborativeAgent] = None
        self.task_history: List[Dict[str, Any]] = []

        logger.info(f"Agent team initialized", team_id=team_id, name=team_name)

    def add_member(self, agent: CollaborativeAgent, is_leader: bool = False) -> None:
        """
        Add member to team

        Args:
            agent: Agent to add
            is_leader: Whether agent is team leader
        """
        self.members[agent.agent.agent_id] = agent

        # Connect agent with all other members
        for member_id, member in self.members.items():
            if member_id != agent.agent.agent_id:
                agent.add_collaborator(member)
                member.add_collaborator(agent)

        if is_leader:
            self.leader = agent

        logger.info(
            f"Member added to team",
            team_id=self.team_id,
            agent_id=agent.agent.agent_id,
            role=agent.role.value,
            is_leader=is_leader,
        )

    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute task as a team

        Args:
            task_description: Task description

        Returns:
            Task execution results
        """
        logger.info(f"Team executing task", team_id=self.team_id, task=task_description)

        result = {
            "task": task_description,
            "team_id": self.team_id,
            "started_at": datetime.utcnow().isoformat(),
            "steps": [],
            "success": False,
        }

        try:
            # Step 1: Leader breaks down task
            if self.leader:
                self.leader.send_message(
                    "broadcast",
                    f"New task: {task_description}",
                    "info",
                )

            # Step 2: Assign sub-tasks to specialists
            sub_tasks = self._distribute_tasks(task_description)
            result["steps"].append({"step": "task_distribution", "sub_tasks": len(sub_tasks)})

            # Step 3: Execute sub-tasks
            for sub_task in sub_tasks:
                agent_id = sub_task["assigned_to"]
                if agent_id in self.members:
                    agent = self.members[agent_id]
                    agent.send_message(
                        agent_id,
                        sub_task["description"],
                        "request",
                    )

            result["steps"].append({"step": "execution", "agents": len(sub_tasks)})

            # Step 4: Collect results
            for agent_id, agent in self.members.items():
                processed = agent.process_messages()
                result["steps"].append(
                    {
                        "step": "processing",
                        "agent_id": agent_id,
                        "messages": len(processed),
                    }
                )

            # Step 5: Build consensus
            consensus = self._build_consensus()
            result["consensus"] = consensus
            result["steps"].append({"step": "consensus", "achieved": consensus["achieved"]})

            result["success"] = True
            result["completed_at"] = datetime.utcnow().isoformat()

            # Store in history
            self.task_history.append(result)

            logger.info(
                f"Team task completed",
                team_id=self.team_id,
                success=result["success"],
            )

        except Exception as e:
            logger.error(f"Team task failed", team_id=self.team_id, error=str(e))
            result["error"] = str(e)

        return result

    def _distribute_tasks(self, task_description: str) -> List[Dict[str, Any]]:
        """Distribute task among team members"""
        sub_tasks = []

        # Assign based on roles
        for agent_id, agent in self.members.items():
            if agent.role == AgentRole.RESEARCHER:
                sub_tasks.append(
                    {
                        "description": f"Research for: {task_description}",
                        "assigned_to": agent_id,
                        "role": agent.role.value,
                    }
                )
            elif agent.role == AgentRole.ANALYST:
                sub_tasks.append(
                    {
                        "description": f"Analyze: {task_description}",
                        "assigned_to": agent_id,
                        "role": agent.role.value,
                    }
                )
            elif agent.role == AgentRole.EXECUTOR:
                sub_tasks.append(
                    {
                        "description": f"Execute: {task_description}",
                        "assigned_to": agent_id,
                        "role": agent.role.value,
                    }
                )

        return sub_tasks

    def _build_consensus(self) -> Dict[str, Any]:
        """Build consensus among team members"""
        # Collect opinions from all members
        opinions = []
        for agent_id, agent in self.members.items():
            # Simulate opinion (in production, would query agent)
            opinions.append(
                {
                    "agent_id": agent_id,
                    "role": agent.role.value,
                    "opinion": "agree",
                    "confidence": 0.85,
                }
            )

        # Calculate consensus
        agree_count = sum(1 for op in opinions if op["opinion"] == "agree")
        consensus_ratio = agree_count / len(opinions) if opinions else 0.0

        return {
            "achieved": consensus_ratio >= 0.7,
            "ratio": consensus_ratio,
            "opinions": opinions,
        }

    def get_team_status(self) -> Dict[str, Any]:
        """Get team status"""
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "members": len(self.members),
            "leader": self.leader.agent.agent_id if self.leader else None,
            "tasks_completed": len(self.task_history),
            "member_roles": {
                agent_id: agent.role.value
                for agent_id, agent in self.members.items()
            },
        }
