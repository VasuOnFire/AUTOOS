"""
Event Bus implementation using Redis Streams

Provides publish-subscribe messaging for decoupled component communication.
"""

import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event data structure"""

    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Subscription:
    """Subscription handle"""

    subscription_id: str
    event_types: List[str]
    consumer_group: str
    consumer_name: str


class EventBus:
    """
    Redis Streams-based event bus for system-wide communication

    Provides:
    - Publish-subscribe patterns
    - At-least-once delivery guarantee
    - Event replay capability
    - Consumer groups for load balancing
    - Backpressure handling
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        stream_prefix: str = "autoos:events:",
    ):
        """
        Initialize event bus

        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (optional)
            stream_prefix: Prefix for stream keys
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
        )
        self.stream_prefix = stream_prefix
        self._subscriptions: Dict[str, Subscription] = {}

        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _get_stream_key(self, event_type: str) -> str:
        """Get Redis stream key for event type"""
        return f"{self.stream_prefix}{event_type}"

    def publish(self, event_type: str, payload: Dict[str, Any]) -> str:
        """
        Publish event to stream

        Args:
            event_type: Type of event (e.g., 'workflow.started')
            payload: Event data

        Returns:
            Event ID assigned by Redis

        Raises:
            RedisError: If publish fails
        """
        event = Event(event_type=event_type, payload=payload, timestamp=datetime.utcnow())

        stream_key = self._get_stream_key(event_type)

        try:
            # Add to Redis stream
            event_id = self.redis_client.xadd(
                stream_key, {"data": json.dumps(event.to_dict())}, maxlen=10000  # Limit stream size
            )

            logger.debug(f"Published event {event_type} with ID {event_id}")
            return event_id

        except RedisError as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise

    def subscribe(
        self,
        event_types: List[str],
        callback: Callable[[Event], None],
        consumer_group: str = "default",
        consumer_name: Optional[str] = None,
    ) -> Subscription:
        """
        Subscribe to event types

        Args:
            event_types: List of event types to subscribe to
            callback: Function to call when event is received
            consumer_group: Consumer group name for load balancing
            consumer_name: Unique consumer name (auto-generated if None)

        Returns:
            Subscription handle
        """
        import uuid

        subscription_id = str(uuid.uuid4())
        consumer_name = consumer_name or f"consumer-{subscription_id[:8]}"

        # Create consumer groups for each event type
        for event_type in event_types:
            stream_key = self._get_stream_key(event_type)
            try:
                # Create consumer group (ignore if exists)
                self.redis_client.xgroup_create(
                    stream_key, consumer_group, id="0", mkstream=True
                )
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise

        subscription = Subscription(
            subscription_id=subscription_id,
            event_types=event_types,
            consumer_group=consumer_group,
            consumer_name=consumer_name,
        )

        self._subscriptions[subscription_id] = subscription

        logger.info(
            f"Created subscription {subscription_id} for {event_types} "
            f"in group {consumer_group}"
        )

        return subscription

    def consume(
        self,
        subscription: Subscription,
        callback: Callable[[Event], None],
        count: int = 10,
        block: int = 1000,
    ) -> int:
        """
        Consume events from subscription

        Args:
            subscription: Subscription handle
            callback: Function to call for each event
            count: Maximum number of events to read
            block: Block time in milliseconds

        Returns:
            Number of events processed
        """
        processed = 0

        for event_type in subscription.event_types:
            stream_key = self._get_stream_key(event_type)

            try:
                # Read from consumer group
                messages = self.redis_client.xreadgroup(
                    subscription.consumer_group,
                    subscription.consumer_name,
                    {stream_key: ">"},
                    count=count,
                    block=block,
                )

                for stream, events in messages:
                    for event_id, event_data in events:
                        try:
                            # Parse event
                            event_dict = json.loads(event_data["data"])
                            event = Event.from_dict(event_dict)
                            event.event_id = event_id

                            # Call callback
                            callback(event)

                            # Acknowledge message
                            self.redis_client.xack(
                                stream_key, subscription.consumer_group, event_id
                            )

                            processed += 1

                        except Exception as e:
                            logger.error(f"Error processing event {event_id}: {e}")
                            # Don't acknowledge - will be redelivered

            except RedisError as e:
                logger.error(f"Error consuming from {stream_key}: {e}")

        return processed

    def replay_events(
        self, event_type: str, start_time: datetime, end_time: datetime
    ) -> List[Event]:
        """
        Replay historical events

        Args:
            event_type: Type of events to replay
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of events in time range
        """
        stream_key = self._get_stream_key(event_type)
        events = []

        try:
            # Read all messages from stream
            messages = self.redis_client.xrange(stream_key, "-", "+")

            for event_id, event_data in messages:
                event_dict = json.loads(event_data["data"])
                event = Event.from_dict(event_dict)
                event.event_id = event_id

                # Filter by time range
                if start_time <= event.timestamp <= end_time:
                    events.append(event)

            logger.info(f"Replayed {len(events)} events of type {event_type}")
            return events

        except RedisError as e:
            logger.error(f"Error replaying events: {e}")
            raise

    def get_pending_count(self, subscription: Subscription) -> int:
        """
        Get number of pending messages for subscription

        Args:
            subscription: Subscription handle

        Returns:
            Number of pending messages
        """
        total_pending = 0

        for event_type in subscription.event_types:
            stream_key = self._get_stream_key(event_type)

            try:
                # Get pending messages info
                pending_info = self.redis_client.xpending(
                    stream_key, subscription.consumer_group
                )

                if pending_info:
                    total_pending += pending_info["pending"]

            except RedisError as e:
                logger.error(f"Error getting pending count: {e}")

        return total_pending

    def close(self) -> None:
        """Close Redis connection"""
        self.redis_client.close()
        logger.info("Event bus connection closed")
