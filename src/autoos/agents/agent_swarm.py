"""
Agent Swarm Intelligence

Inspired by swarm intelligence algorithms and multi-agent systems.
Large numbers of simple agents work together to solve complex problems.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import random

from autoos.core.models import Agent
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class SwarmAgent:
    """Simple agent in a swarm"""

    def __init__(self, agent_id: str, position: Dict[str, float]):
        self.agent_id = agent_id
        self.position = position  # Position in solution space
        self.velocity = {k: 0.0 for k in position.keys()}
        self.best_position = position.copy()
        self.best_score = float('-inf')
        self.current_score = float('-inf')

    def update_position(self, global_best: Dict[str, float], inertia: float = 0.7) -> None:
        """Update agent position based on swarm intelligence"""
        for key in self.position.keys():
            # Cognitive component (personal best)
            cognitive = random.random() * (self.best_position[key] - self.position[key])

            # Social component (global best)
            social = random.random() * (global_best[key] - self.position[key])

            # Update velocity
            self.velocity[key] = (
                inertia * self.velocity[key] + cognitive + social
            )

            # Update position
            self.position[key] += self.velocity[key]

    def evaluate(self, objective_function: Any) -> float:
        """Evaluate current position"""
        self.current_score = objective_function(self.position)

        # Update personal best
        if self.current_score > self.best_score:
            self.best_score = self.current_score
            self.best_position = self.position.copy()

        return self.current_score


class AgentSwarm:
    """
    Swarm of agents working together

    Features:
    - Particle Swarm Optimization
    - Ant Colony Optimization
    - Bee Algorithm
    - Collective decision making
    - Emergent behavior
    """

    def __init__(self, swarm_id: str, swarm_size: int = 50):
        """
        Initialize agent swarm

        Args:
            swarm_id: Swarm identifier
            swarm_size: Number of agents in swarm
        """
        self.swarm_id = swarm_id
        self.swarm_size = swarm_size
        self.agents: List[SwarmAgent] = []
        self.global_best_position: Optional[Dict[str, float]] = None
        self.global_best_score = float('-inf')
        self.iteration = 0

        logger.info(f"Agent swarm initialized", swarm_id=swarm_id, size=swarm_size)

    def initialize_swarm(self, search_space: Dict[str, tuple]) -> None:
        """
        Initialize swarm agents in search space

        Args:
            search_space: Dictionary of {dimension: (min, max)}
        """
        self.agents = []

        for i in range(self.swarm_size):
            # Random initial position
            position = {
                key: random.uniform(bounds[0], bounds[1])
                for key, bounds in search_space.items()
            }

            agent = SwarmAgent(
                agent_id=f"{self.swarm_id}_agent_{i}",
                position=position,
            )

            self.agents.append(agent)

        logger.info(f"Swarm initialized with {len(self.agents)} agents")

    def optimize(
        self,
        objective_function: Any,
        max_iterations: int = 100,
        convergence_threshold: float = 0.001,
    ) -> Dict[str, Any]:
        """
        Optimize using swarm intelligence

        Args:
            objective_function: Function to optimize
            max_iterations: Maximum iterations
            convergence_threshold: Convergence threshold

        Returns:
            Optimization results
        """
        logger.info(f"Starting swarm optimization", swarm_id=self.swarm_id)

        results = {
            "swarm_id": self.swarm_id,
            "iterations": [],
            "converged": False,
            "best_solution": None,
            "best_score": float('-inf'),
        }

        for iteration in range(max_iterations):
            self.iteration = iteration

            # Evaluate all agents
            scores = []
            for agent in self.agents:
                score = agent.evaluate(objective_function)
                scores.append(score)

                # Update global best
                if score > self.global_best_score:
                    self.global_best_score = score
                    self.global_best_position = agent.position.copy()

            # Record iteration
            avg_score = sum(scores) / len(scores)
            results["iterations"].append(
                {
                    "iteration": iteration,
                    "best_score": self.global_best_score,
                    "avg_score": avg_score,
                    "diversity": self._calculate_diversity(),
                }
            )

            # Check convergence
            if iteration > 0:
                improvement = (
                    self.global_best_score - results["iterations"][-2]["best_score"]
                )
                if abs(improvement) < convergence_threshold:
                    results["converged"] = True
                    logger.info(f"Swarm converged at iteration {iteration}")
                    break

            # Update agent positions
            if self.global_best_position:
                for agent in self.agents:
                    agent.update_position(self.global_best_position)

        results["best_solution"] = self.global_best_position
        results["best_score"] = self.global_best_score
        results["total_iterations"] = self.iteration + 1

        logger.info(
            f"Swarm optimization completed",
            swarm_id=self.swarm_id,
            iterations=results["total_iterations"],
            best_score=results["best_score"],
        )

        return results

    def _calculate_diversity(self) -> float:
        """Calculate swarm diversity"""
        if not self.agents or not self.global_best_position:
            return 0.0

        # Calculate average distance from global best
        distances = []
        for agent in self.agents:
            distance = sum(
                (agent.position[key] - self.global_best_position[key]) ** 2
                for key in agent.position.keys()
            )
            distances.append(distance ** 0.5)

        return sum(distances) / len(distances)

    def get_swarm_status(self) -> Dict[str, Any]:
        """Get swarm status"""
        return {
            "swarm_id": self.swarm_id,
            "swarm_size": len(self.agents),
            "iteration": self.iteration,
            "global_best_score": self.global_best_score,
            "diversity": self._calculate_diversity(),
        }


class ConsensusSwarm:
    """
    Swarm for building consensus

    Features:
    - Voting mechanisms
    - Opinion aggregation
    - Conflict resolution
    - Collective intelligence
    """

    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.agents: List[Dict[str, Any]] = []

    def add_agent_opinion(
        self, agent_id: str, opinion: Any, confidence: float
    ) -> None:
        """
        Add agent opinion

        Args:
            agent_id: Agent identifier
            opinion: Agent's opinion
            confidence: Confidence in opinion (0-1)
        """
        self.agents.append(
            {
                "agent_id": agent_id,
                "opinion": opinion,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def build_consensus(self, method: str = "weighted_voting") -> Dict[str, Any]:
        """
        Build consensus from agent opinions

        Args:
            method: Consensus method (weighted_voting, majority, unanimous)

        Returns:
            Consensus result
        """
        logger.info(f"Building consensus", swarm_id=self.swarm_id, method=method)

        if not self.agents:
            return {"consensus": None, "confidence": 0.0, "method": method}

        if method == "weighted_voting":
            # Weight opinions by confidence
            opinion_weights: Dict[Any, float] = {}

            for agent in self.agents:
                opinion = agent["opinion"]
                confidence = agent["confidence"]

                if opinion not in opinion_weights:
                    opinion_weights[opinion] = 0.0

                opinion_weights[opinion] += confidence

            # Select opinion with highest weight
            consensus_opinion = max(opinion_weights.items(), key=lambda x: x[1])

            return {
                "consensus": consensus_opinion[0],
                "confidence": consensus_opinion[1] / len(self.agents),
                "method": method,
                "votes": opinion_weights,
            }

        elif method == "majority":
            # Simple majority vote
            opinion_counts: Dict[Any, int] = {}

            for agent in self.agents:
                opinion = agent["opinion"]
                opinion_counts[opinion] = opinion_counts.get(opinion, 0) + 1

            consensus_opinion = max(opinion_counts.items(), key=lambda x: x[1])

            return {
                "consensus": consensus_opinion[0],
                "confidence": consensus_opinion[1] / len(self.agents),
                "method": method,
                "votes": opinion_counts,
            }

        elif method == "unanimous":
            # Require unanimous agreement
            opinions = [agent["opinion"] for agent in self.agents]
            unanimous = len(set(opinions)) == 1

            return {
                "consensus": opinions[0] if unanimous else None,
                "confidence": 1.0 if unanimous else 0.0,
                "method": method,
                "unanimous": unanimous,
            }

        return {"consensus": None, "confidence": 0.0, "method": method}
