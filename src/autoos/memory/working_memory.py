"""
Working Memory - Redis-based fast storage for active workflow state

Provides temporary storage with TTL for agent working memory and workflow state.
"""

from typing import Dict, Any, Optional
import json
import redis
from redis.exceptions import RedisError

from autoos.infrastructure.logging import get_logger
from autoos.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)
metrics = get_metrics_collector()


class WorkingMemory:
    """
    Redis-based working memory for active workflows and agents

    Features:
    - Fast read/write for execution
    - Automatic TTL for cleanup
    - Workflow state caching
    - Agent memory isolation
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        default_ttl: int = 3600,
    ):
        """
        Initialize working memory

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (optional)
            default_ttl: Default TTL in seconds
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
        )
        self.default_ttl = default_ttl

        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"Connected to Redis working memory at {redis_host}:{redis_port}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _workflow_key(self, workflow_id: str) -> str:
        """Get Redis key for workflow state"""
        return f"autoos:workflow:{workflow_id}"

    def _agent_key(self, agent_id: str) -> str:
        """Get Redis key for agent memory"""
        return f"autoos:agent:{agent_id}"

    def store_workflow_state(
        self, workflow_id: str, state: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """
        Save current workflow state

        Args:
            workflow_id: Workflow ID
            state: Workflow state dictionary
            ttl: Time to live in seconds (uses default if None)
        """
        key = self._workflow_key(workflow_id)
        ttl = ttl or self.default_ttl

        try:
            self.redis_client.setex(key, ttl, json.dumps(state))
            metrics.record_memory_operation("working", "write")
            logger.debug(f"Stored workflow state", workflow_id=workflow_id)

        except RedisError as e:
            logger.error(f"Failed to store workflow state: {e}", workflow_id=workflow_id)
            raise

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve workflow state

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow state dictionary or None if not found
        """
        key = self._workflow_key(workflow_id)

        try:
            data = self.redis_client.get(key)
            metrics.record_memory_operation("working", "read")

            if data:
                return json.loads(data)
            return None

        except RedisError as e:
            logger.error(f"Failed to get workflow state: {e}", workflow_id=workflow_id)
            raise

    def delete_workflow_state(self, workflow_id: str) -> None:
        """
        Delete workflow state

        Args:
            workflow_id: Workflow ID
        """
        key = self._workflow_key(workflow_id)

        try:
            self.redis_client.delete(key)
            metrics.record_memory_operation("working", "delete")
            logger.debug(f"Deleted workflow state", workflow_id=workflow_id)

        except RedisError as e:
            logger.error(f"Failed to delete workflow state: {e}", workflow_id=workflow_id)
            raise

    def store_agent_memory(
        self, agent_id: str, memory: Dict[str, Any], ttl: Optional[int] = None
    ) -> None:
        """
        Save agent working memory

        Args:
            agent_id: Agent ID
            memory: Agent memory dictionary
            ttl: Time to live in seconds (uses default if None)
        """
        key = self._agent_key(agent_id)
        ttl = ttl or self.default_ttl

        try:
            self.redis_client.setex(key, ttl, json.dumps(memory))
            metrics.record_memory_operation("working", "write")
            logger.debug(f"Stored agent memory", agent_id=agent_id)

        except RedisError as e:
            logger.error(f"Failed to store agent memory: {e}", agent_id=agent_id)
            raise

    def get_agent_memory(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent memory

        Args:
            agent_id: Agent ID

        Returns:
            Agent memory dictionary or None if not found
        """
        key = self._agent_key(agent_id)

        try:
            data = self.redis_client.get(key)
            metrics.record_memory_operation("working", "read")

            if data:
                return json.loads(data)
            return None

        except RedisError as e:
            logger.error(f"Failed to get agent memory: {e}", agent_id=agent_id)
            raise

    def clear_agent_memory(self, agent_id: str) -> None:
        """
        Delete agent memory on retirement

        Args:
            agent_id: Agent ID
        """
        key = self._agent_key(agent_id)

        try:
            self.redis_client.delete(key)
            metrics.record_memory_operation("working", "delete")
            logger.debug(f"Cleared agent memory", agent_id=agent_id)

        except RedisError as e:
            logger.error(f"Failed to clear agent memory: {e}", agent_id=agent_id)
            raise

    def extend_ttl(self, workflow_id: str, ttl: int) -> None:
        """
        Extend TTL for workflow state

        Args:
            workflow_id: Workflow ID
            ttl: New TTL in seconds
        """
        key = self._workflow_key(workflow_id)

        try:
            self.redis_client.expire(key, ttl)
            logger.debug(f"Extended TTL for workflow", workflow_id=workflow_id, ttl=ttl)

        except RedisError as e:
            logger.error(f"Failed to extend TTL: {e}", workflow_id=workflow_id)
            raise

    def get_all_workflow_ids(self) -> list[str]:
        """
        Get all active workflow IDs

        Returns:
            List of workflow IDs
        """
        try:
            keys = self.redis_client.keys("autoos:workflow:*")
            workflow_ids = [key.split(":")[-1] for key in keys]
            return workflow_ids

        except RedisError as e:
            logger.error(f"Failed to get workflow IDs: {e}")
            raise

    def close(self) -> None:
        """Close Redis connection"""
        self.redis_client.close()
        logger.info("Working memory connection closed")
