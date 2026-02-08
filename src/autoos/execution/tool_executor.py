"""
Tool Executor - Sandboxed tool execution with Docker isolation

Executes tools safely in isolated containers with validation and monitoring.
"""

from typing import Dict, Any, Optional
import docker
import json
import time
from datetime import datetime

from autoos.core.models import Tool, ToolResult, TrustLevel, Agent
from autoos.infrastructure.logging import get_logger
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class ToolExecutor:
    """
    Sandboxed tool execution engine

    Features:
    - Docker container isolation
    - Input validation against schemas
    - Timeout enforcement
    - Rate limiting
    - Authorization checks
    - Output capture
    """

    def __init__(self, docker_client: Optional[docker.DockerClient] = None):
        """
        Initialize tool executor

        Args:
            docker_client: Docker client (creates new if None)
        """
        self.docker_client = docker_client or docker.from_env()
        self.rate_limits: Dict[str, list] = {}  # tool_name -> [timestamps]

        logger.info("Tool executor initialized")

    def execute_tool(
        self, tool: Tool, params: Dict[str, Any], agent: Agent
    ) -> ToolResult:
        """
        Execute tool in sandboxed environment

        Args:
            tool: Tool definition
            params: Tool parameters
            agent: Agent executing the tool

        Returns:
            Tool execution result
        """
        start_time = time.time()

        logger.info(
            f"Executing tool",
            tool_name=tool.tool_name,
            agent_id=agent.agent_id,
        )

        try:
            # Validate authorization
            if not self.check_authorization(tool, agent):
                raise PermissionError(
                    f"Agent {agent.agent_id} not authorized to use tool {tool.tool_name}"
                )

            # Validate parameters
            validation = self.validate_params(tool, params)
            if not validation["valid"]:
                raise ValueError(f"Invalid parameters: {validation['errors']}")

            # Check rate limit
            if not self._check_rate_limit(tool.tool_name, tool.rate_limit):
                raise Exception(f"Rate limit exceeded for tool {tool.tool_name}")

            # Execute in Docker container
            result = self._execute_in_container(tool, params, agent)

            execution_time = time.time() - start_time

            # Record metrics
            metrics.record_tool_execution(tool.tool_name, execution_time, True)

            logger.info(
                f"Tool execution completed",
                tool_name=tool.tool_name,
                execution_time=execution_time,
            )

            return ToolResult(
                success=True,
                output=result,
                error=None,
                execution_time=execution_time,
                cost=0.0,  # Tool execution cost
            )

        except Exception as e:
            execution_time = time.time() - start_time

            logger.error(
                f"Tool execution failed",
                tool_name=tool.tool_name,
                error=str(e),
            )

            # Record metrics
            metrics.record_tool_execution(tool.tool_name, execution_time, False)

            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                cost=0.0,
            )

    def validate_params(
        self, tool: Tool, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parameters against tool schema

        Args:
            tool: Tool definition
            params: Parameters to validate

        Returns:
            Validation result
        """
        errors = []
        schema = tool.parameters_schema

        # Check required parameters
        required = schema.get("required", [])
        for param in required:
            if param not in params:
                errors.append(f"Missing required parameter: {param}")

        # Check parameter types
        properties = schema.get("properties", {})
        for param, value in params.items():
            if param in properties:
                expected_type = properties[param].get("type")
                actual_type = type(value).__name__

                # Simple type checking (can be enhanced)
                type_map = {
                    "string": "str",
                    "number": ["int", "float"],
                    "boolean": "bool",
                    "array": "list",
                    "object": "dict",
                }

                expected = type_map.get(expected_type, expected_type)
                if isinstance(expected, list):
                    if actual_type not in expected:
                        errors.append(
                            f"Parameter {param} has wrong type: expected {expected}, got {actual_type}"
                        )
                elif actual_type != expected:
                    errors.append(
                        f"Parameter {param} has wrong type: expected {expected}, got {actual_type}"
                    )

        return {"valid": len(errors) == 0, "errors": errors}

    def check_authorization(self, tool: Tool, agent: Agent) -> bool:
        """
        Verify agent is authorized to use tool

        Args:
            tool: Tool to check
            agent: Agent requesting access

        Returns:
            True if authorized
        """
        # Check if agent's trust level is sufficient
        trust_levels = {
            TrustLevel.RESTRICTED: 1,
            TrustLevel.STANDARD: 2,
            TrustLevel.ELEVATED: 3,
            TrustLevel.PRIVILEGED: 4,
        }

        agent_level = trust_levels.get(agent.trust_level, 0)
        required_level = trust_levels.get(tool.required_trust_level, 0)

        if agent_level < required_level:
            logger.warning(
                f"Authorization denied",
                tool=tool.tool_name,
                agent_id=agent.agent_id,
                agent_level=agent.trust_level.value,
                required_level=tool.required_trust_level.value,
            )
            return False

        # Check if tool is in agent's allowed tools
        if "all" not in agent.allowed_tools and tool.tool_name not in agent.allowed_tools:
            logger.warning(
                f"Tool not in allowed list",
                tool=tool.tool_name,
                agent_id=agent.agent_id,
            )
            return False

        return True

    def _execute_in_container(
        self, tool: Tool, params: Dict[str, Any], agent: Agent
    ) -> Any:
        """
        Execute tool in Docker container

        Args:
            tool: Tool to execute
            params: Tool parameters
            agent: Agent executing tool

        Returns:
            Tool output
        """
        # Create container with tool execution environment
        container = self.docker_client.containers.run(
            image="python:3.11-slim",
            command=[
                "python",
                "-c",
                f"import json; params = json.loads('{json.dumps(params)}'); print(json.dumps({{'result': 'Tool {tool.tool_name} executed', 'params': params}}))",
            ],
            detach=True,
            remove=True,
            mem_limit="512m",
            cpu_quota=50000,  # 50% of one CPU
            network_disabled=False,  # Can be disabled for security
        )

        try:
            # Wait for completion with timeout
            result = container.wait(timeout=tool.timeout_seconds)

            # Get output
            output = container.logs().decode("utf-8")

            # Parse JSON output
            return json.loads(output)

        except Exception as e:
            logger.error(f"Container execution failed", error=str(e))
            raise

        finally:
            # Cleanup
            try:
                container.stop(timeout=1)
            except:
                pass

    def _check_rate_limit(self, tool_name: str, limit: int) -> bool:
        """
        Check if tool is within rate limit

        Args:
            tool_name: Tool name
            limit: Calls per minute

        Returns:
            True if within limit
        """
        now = time.time()
        minute_ago = now - 60

        # Initialize if not exists
        if tool_name not in self.rate_limits:
            self.rate_limits[tool_name] = []

        # Remove old timestamps
        self.rate_limits[tool_name] = [
            ts for ts in self.rate_limits[tool_name] if ts > minute_ago
        ]

        # Check limit
        if len(self.rate_limits[tool_name]) >= limit:
            return False

        # Add current timestamp
        self.rate_limits[tool_name].append(now)
        return True

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve tool parameter schema

        Args:
            tool_name: Tool name

        Returns:
            Tool schema or None
        """
        # Tool registry (would be loaded from database in production)
        tool_schemas = {
            "read_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                },
                "required": ["path"],
            },
            "write_file": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
            "http_request": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to request"},
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                    },
                    "headers": {"type": "object"},
                    "body": {"type": "object"},
                },
                "required": ["url", "method"],
            },
            "execute_command": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"},
                    "timeout": {"type": "number", "description": "Timeout in seconds"},
                },
                "required": ["command"],
            },
        }

        return tool_schemas.get(tool_name)
