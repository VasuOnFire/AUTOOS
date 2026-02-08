"""
Autonomous Agent - Self-directed agent with goal decomposition

Inspired by AutoGPT, BabyAGI, and other autonomous agent systems.
Agents can break down complex goals, plan steps, and execute autonomously.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from autoos.core.models import Agent, TaskResult
from autoos.infrastructure.logging import get_logger

logger = get_logger(__name__)


class Goal:
    """Represents a goal with sub-goals"""

    def __init__(
        self,
        goal_id: str,
        description: str,
        priority: int = 5,
        parent_goal_id: Optional[str] = None,
    ):
        self.goal_id = goal_id
        self.description = description
        self.priority = priority
        self.parent_goal_id = parent_goal_id
        self.status = "pending"  # pending, in_progress, completed, failed
        self.sub_goals: List[Goal] = []
        self.result: Optional[Any] = None


class AutonomousAgent:
    """
    Autonomous agent with self-directed behavior

    Features:
    - Goal decomposition (break complex goals into sub-goals)
    - Self-planning (create execution plans)
    - Self-reflection (evaluate own performance)
    - Memory management (remember past actions)
    - Tool selection (choose appropriate tools)
    - Continuous learning (improve from experience)
    """

    def __init__(self, agent: Agent, llm_provider: Any):
        """
        Initialize autonomous agent

        Args:
            agent: Base agent configuration
            llm_provider: LLM provider for reasoning
        """
        self.agent = agent
        self.llm_provider = llm_provider
        self.goals: List[Goal] = []
        self.memory: List[Dict[str, Any]] = []
        self.learned_patterns: Dict[str, Any] = {}

        logger.info(f"Autonomous agent initialized", agent_id=agent.agent_id)

    def decompose_goal(self, goal_description: str) -> List[Goal]:
        """
        Break down complex goal into sub-goals

        Args:
            goal_description: High-level goal description

        Returns:
            List of sub-goals
        """
        logger.info(f"Decomposing goal", goal=goal_description)

        # Use LLM to decompose goal
        prompt = f"""
        Break down this high-level goal into specific, actionable sub-goals:
        
        Goal: {goal_description}
        
        Provide a list of sub-goals in order of execution.
        Each sub-goal should be:
        1. Specific and actionable
        2. Measurable
        3. Achievable with available tools
        4. Relevant to the main goal
        
        Format as JSON array:
        [
            {{"description": "sub-goal 1", "priority": 1}},
            {{"description": "sub-goal 2", "priority": 2}}
        ]
        """

        # Simulate LLM response (in production, would call actual LLM)
        sub_goals_data = [
            {"description": "Analyze current state", "priority": 1},
            {"description": "Identify required actions", "priority": 2},
            {"description": "Execute actions", "priority": 3},
            {"description": "Verify results", "priority": 4},
        ]

        # Create Goal objects
        main_goal = Goal(
            goal_id=f"goal_{datetime.utcnow().timestamp()}",
            description=goal_description,
            priority=0,
        )

        sub_goals = []
        for i, sub_goal_data in enumerate(sub_goals_data):
            sub_goal = Goal(
                goal_id=f"subgoal_{i}_{datetime.utcnow().timestamp()}",
                description=sub_goal_data["description"],
                priority=sub_goal_data["priority"],
                parent_goal_id=main_goal.goal_id,
            )
            sub_goals.append(sub_goal)
            main_goal.sub_goals.append(sub_goal)

        self.goals.append(main_goal)

        logger.info(
            f"Goal decomposed into {len(sub_goals)} sub-goals",
            goal_id=main_goal.goal_id,
        )

        return sub_goals

    def create_execution_plan(self, goal: Goal) -> List[Dict[str, Any]]:
        """
        Create detailed execution plan for goal

        Args:
            goal: Goal to plan for

        Returns:
            List of execution steps
        """
        logger.info(f"Creating execution plan", goal_id=goal.goal_id)

        # Use LLM to create plan
        prompt = f"""
        Create a detailed execution plan for this goal:
        
        Goal: {goal.description}
        
        Available tools: {self.agent.capabilities}
        
        Provide step-by-step plan with:
        1. Action to take
        2. Tool to use
        3. Expected outcome
        4. Success criteria
        
        Format as JSON array.
        """

        # Simulate plan (in production, would call LLM)
        plan = [
            {
                "step": 1,
                "action": "Gather information",
                "tool": "read_file",
                "expected_outcome": "Data collected",
                "success_criteria": "File read successfully",
            },
            {
                "step": 2,
                "action": "Process data",
                "tool": "analyze_data",
                "expected_outcome": "Insights generated",
                "success_criteria": "Analysis complete",
            },
            {
                "step": 3,
                "action": "Generate output",
                "tool": "write_file",
                "expected_outcome": "Results saved",
                "success_criteria": "File written successfully",
            },
        ]

        logger.info(f"Execution plan created with {len(plan)} steps")

        return plan

    def self_reflect(self, task_result: TaskResult) -> Dict[str, Any]:
        """
        Reflect on task execution and learn

        Args:
            task_result: Result of task execution

        Returns:
            Reflection insights
        """
        logger.info(f"Self-reflecting on task execution")

        # Analyze what went well and what didn't
        reflection = {
            "success": task_result.success,
            "confidence": task_result.confidence,
            "what_worked": [],
            "what_failed": [],
            "improvements": [],
            "learned_patterns": [],
        }

        if task_result.success:
            reflection["what_worked"].append("Task completed successfully")
            reflection["learned_patterns"].append(
                f"Approach with confidence {task_result.confidence} succeeded"
            )
        else:
            reflection["what_failed"].append("Task failed")
            reflection["improvements"].append("Try alternative approach")

        # Store in memory
        self.memory.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "task_result": task_result.to_dict(),
                "reflection": reflection,
            }
        )

        # Update learned patterns
        pattern_key = f"task_type_{task_result.output.get('type', 'unknown')}"
        if pattern_key not in self.learned_patterns:
            self.learned_patterns[pattern_key] = {
                "success_count": 0,
                "failure_count": 0,
                "best_approach": None,
            }

        if task_result.success:
            self.learned_patterns[pattern_key]["success_count"] += 1
        else:
            self.learned_patterns[pattern_key]["failure_count"] += 1

        logger.info(f"Self-reflection completed", insights=len(reflection["learned_patterns"]))

        return reflection

    def select_best_tool(self, task_description: str) -> str:
        """
        Select most appropriate tool for task

        Args:
            task_description: Description of task

        Returns:
            Tool name
        """
        logger.info(f"Selecting best tool for task")

        # Use LLM to select tool
        prompt = f"""
        Select the best tool for this task:
        
        Task: {task_description}
        Available tools: {self.agent.capabilities}
        
        Consider:
        1. Tool capabilities
        2. Past success rates
        3. Task requirements
        
        Return tool name.
        """

        # Simulate tool selection (in production, would call LLM)
        # Check learned patterns
        for pattern_key, pattern_data in self.learned_patterns.items():
            if pattern_data["best_approach"]:
                logger.info(f"Using learned best approach: {pattern_data['best_approach']}")
                return pattern_data["best_approach"]

        # Default selection
        if self.agent.capabilities:
            selected_tool = self.agent.capabilities[0]
        else:
            selected_tool = "default_tool"

        logger.info(f"Selected tool: {selected_tool}")

        return selected_tool

    def execute_autonomously(self, goal_description: str) -> Dict[str, Any]:
        """
        Execute goal autonomously with full self-direction

        Args:
            goal_description: High-level goal

        Returns:
            Execution results
        """
        logger.info(f"Starting autonomous execution", goal=goal_description)

        results = {
            "goal": goal_description,
            "sub_goals_completed": 0,
            "total_sub_goals": 0,
            "success": False,
            "reflections": [],
        }

        try:
            # Step 1: Decompose goal
            sub_goals = self.decompose_goal(goal_description)
            results["total_sub_goals"] = len(sub_goals)

            # Step 2: Execute each sub-goal
            for sub_goal in sub_goals:
                logger.info(f"Executing sub-goal", sub_goal=sub_goal.description)

                # Create execution plan
                plan = self.create_execution_plan(sub_goal)

                # Execute plan steps
                for step in plan:
                    # Select tool
                    tool = self.select_best_tool(step["action"])

                    # Execute (simulated)
                    task_result = TaskResult(
                        success=True,
                        output={"step": step["step"], "result": "completed"},
                        confidence=0.85,
                        reasoning=f"Executed {step['action']} using {tool}",
                        cost=0.01,
                        latency=1.0,
                        errors=[],
                    )

                    # Self-reflect
                    reflection = self.self_reflect(task_result)
                    results["reflections"].append(reflection)

                sub_goal.status = "completed"
                results["sub_goals_completed"] += 1

            results["success"] = True

            logger.info(
                f"Autonomous execution completed",
                sub_goals_completed=results["sub_goals_completed"],
            )

        except Exception as e:
            logger.error(f"Autonomous execution failed", error=str(e))
            results["error"] = str(e)

        return results

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get summary of agent's memory

        Returns:
            Memory summary
        """
        return {
            "total_memories": len(self.memory),
            "learned_patterns": len(self.learned_patterns),
            "recent_memories": self.memory[-5:] if self.memory else [],
        }

    def clear_memory(self) -> None:
        """Clear agent's memory"""
        self.memory.clear()
        logger.info(f"Memory cleared", agent_id=self.agent.agent_id)
