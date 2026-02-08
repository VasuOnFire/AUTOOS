"""
Agent Worker - Executes tasks with reasoning and tool selection

The cognitive core of AUTOOS - agents that reason, select tools, and execute tasks.
"""

from typing import Dict, Any, List, Optional
import time

from autoos.core.models import (
    Agent,
    Task,
    TaskResult,
    Tool,
    ToolResult,
    LLMRole,
)
from autoos.execution.intelligence_fabric import IntelligenceFabric, LLMConfig
from autoos.execution.tool_executor import ToolExecutor
from autoos.infrastructure.logging import get_logger, set_trace_context
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class AgentWorker:
    """
    Agent worker - executes tasks with reasoning

    Features:
    - Reason about task approach
    - Select appropriate tools
    - Execute with confidence tracking
    - Self-report uncertainty
    - Verify trust level compliance
    """

    def __init__(
        self,
        intelligence_fabric: IntelligenceFabric,
        tool_executor: ToolExecutor,
    ):
        """
        Initialize agent worker

        Args:
            intelligence_fabric: Intelligence fabric instance
            tool_executor: Tool executor instance
        """
        self.intelligence_fabric = intelligence_fabric
        self.tool_executor = tool_executor

        logger.info("Agent worker initialized")

    def execute_task(self, task: Task, agent: Agent) -> TaskResult:
        """
        Execute assigned task

        Args:
            task: Task to execute
            agent: Agent executing the task

        Returns:
            Task execution result
        """
        set_trace_context(agent_id=agent.agent_id)

        logger.info(
            f"Agent executing task",
            task_id=task.task_id,
            agent_id=agent.agent_id,
        )

        start_time = time.time()
        total_cost = 0.0

        try:
            # Step 1: Reason about task
            reasoning = self.reason_about_task(task, agent)
            total_cost += reasoning.get("cost", 0.0)

            logger.info(
                f"Task reasoning complete",
                task_id=task.task_id,
                confidence=reasoning.get("confidence", 0.0),
            )

            # Step 2: Select tools
            tools = self.select_tools(task, reasoning, agent)

            logger.info(
                f"Tools selected",
                task_id=task.task_id,
                tools=[t.tool_name for t in tools],
            )

            # Step 3: Execute tools
            tool_results = []
            for tool in tools:
                # Check trust level
                if not self.check_trust_level(tool, agent):
                    logger.warning(
                        f"Tool execution blocked by trust level",
                        tool=tool.tool_name,
                        agent_trust=agent.trust_level.value,
                    )
                    continue

                # Execute tool
                result = self.tool_executor.execute_tool(
                    tool, task.context.get("params", {}), agent
                )
                tool_results.append(result)
                total_cost += result.cost

            # Step 4: Calculate confidence
            confidence = self.self_report_confidence(reasoning, tool_results)

            # Step 5: Check if verification needed
            if confidence < agent.confidence_threshold:
                logger.warning(
                    f"Low confidence detected, verification recommended",
                    task_id=task.task_id,
                    confidence=confidence,
                    threshold=agent.confidence_threshold,
                )

            latency = time.time() - start_time

            # Record metrics
            metrics.record_agent_task(latency, True)

            logger.info(
                f"Task execution completed",
                task_id=task.task_id,
                confidence=confidence,
                cost=total_cost,
            )

            return TaskResult(
                success=True,
                output={
                    "reasoning": reasoning.get("reasoning"),
                    "tools_used": [t.tool_name for t in tools],
                    "tool_results": [r.output for r in tool_results if r.success],
                },
                confidence=confidence,
                reasoning=reasoning.get("reasoning", ""),
                cost=total_cost,
                latency=latency,
                errors=[],
            )

        except Exception as e:
            latency = time.time() - start_time

            logger.error(
                f"Task execution failed",
                task_id=task.task_id,
                error=str(e),
            )

            # Record metrics
            metrics.record_agent_task(latency, False)

            return TaskResult(
                success=False,
                output=None,
                confidence=0.0,
                reasoning="Task execution failed",
                cost=total_cost,
                latency=latency,
                errors=[str(e)],
            )

    def reason_about_task(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """
        Generate reasoning for task approach

        Args:
            task: Task to reason about
            agent: Agent reasoning

        Returns:
            Reasoning with approach and confidence
        """
        # Use PLANNER role for reasoning
        prompt = f"""
Task: {task.description}

Context: {task.context}

Agent Capabilities: {agent.capabilities}

Reason about how to approach this task:
1. What is the goal?
2. What tools or capabilities are needed?
3. What is the step-by-step approach?
4. What are potential risks or challenges?

Provide your reasoning in a structured format.
"""

        config = LLMConfig(temperature=0.7, max_tokens=1000)

        try:
            response = self.intelligence_fabric.execute_with_fallback(
                task, LLMRole.PLANNER, config
            )

            return {
                "reasoning": response.response,
                "confidence": response.confidence,
                "cost": response.cost,
            }

        except Exception as e:
            logger.error(f"Reasoning failed", error=str(e))
            return {
                "reasoning": "Failed to generate reasoning",
                "confidence": 0.0,
                "cost": 0.0,
            }

    def select_tools(
        self, task: Task, reasoning: Dict[str, Any], agent: Agent
    ) -> List[Tool]:
        """
        Choose appropriate tools for task

        Args:
            task: Task to execute
            reasoning: Task reasoning
            agent: Agent selecting tools

        Returns:
            List of selected tools
        """
        # Simple tool selection based on task description
        # In production, this would use LLM to intelligently select tools

        available_tools = [
            Tool(
                tool_name="read_file",
                description="Read file contents",
                parameters_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                required_trust_level=agent.trust_level,
                timeout_seconds=30,
                rate_limit=100,
            ),
            Tool(
                tool_name="http_request",
                description="Make HTTP request",
                parameters_schema={"type": "object", "properties": {"url": {"type": "string"}}},
                required_trust_level=agent.trust_level,
                timeout_seconds=60,
                rate_limit=50,
            ),
        ]

        # Filter by agent's allowed tools
        selected = []
        for tool in available_tools:
            if "all" in agent.allowed_tools or tool.tool_name in agent.allowed_tools:
                selected.append(tool)

        return selected[:3]  # Limit to 3 tools

    def self_report_confidence(
        self, reasoning: Dict[str, Any], tool_results: List[ToolResult]
    ) -> float:
        """
        Report confidence in current reasoning and execution

        Args:
            reasoning: Task reasoning
            tool_results: Tool execution results

        Returns:
            Confidence score (0-1)
        """
        # Start with reasoning confidence
        confidence = reasoning.get("confidence", 0.5)

        # Adjust based on tool success rate
        if tool_results:
            success_rate = sum(1 for r in tool_results if r.success) / len(tool_results)
            confidence = (confidence + success_rate) / 2

        # Reduce confidence if any tools failed
        if any(not r.success for r in tool_results):
            confidence *= 0.8

        return max(0.0, min(1.0, confidence))

    def check_trust_level(self, tool: Tool, agent: Agent) -> bool:
        """
        Verify tool is allowed for agent trust level

        Args:
            tool: Tool to check
            agent: Agent requesting tool

        Returns:
            True if allowed
        """
        return self.tool_executor.check_authorization(tool, agent)
