"""
Analytics event pipeline for collecting, aggregating, and streaming user events.
Supports batch ingestion, real-time streaming, and materialized aggregations.
"""
import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

# Buffer configuration
BUFFER_MAX_SIZE = 1000
BUFFER_FLUSH_INTERVAL = 5.0  # seconds
LIVE_ANALYTICS_CHANNEL = "analytics:live"


@dataclass
class AnalyticsEvent:
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    event_data: Dict[str, Any] = field(default_factory=dict)
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class AnalyticsPipeline:
    """
    Buffered analytics event pipeline.

    Events are buffered in memory and flushed to the database in batches
    for efficiency. Live events are also published to Redis for real-time
    dashboard updates via WebSocket.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", db_session_factory=None):
        self._buffer: List[AnalyticsEvent] = []
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._db_session_factory = db_session_factory
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the background flush task."""
        self._redis = await aioredis.from_url(self._redis_url)
        self._flush_task = asyncio.create_task(self._periodic_flush())
        logger.info("Analytics pipeline started")

    async def stop(self) -> None:
        """Gracefully stop, flushing remaining events."""
        if self._flush_task:
            self._flush_task.cancel()
        await self._flush_buffer()
        logger.info("Analytics pipeline stopped")

    async def track(self, event: AnalyticsEvent) -> None:
        """Track a single analytics event."""
        async with self._lock:
            self._buffer.append(event)
            if len(self._buffer) >= BUFFER_MAX_SIZE:
                await self._flush_buffer()

        # Publish to Redis for live dashboard
        if self._redis:
            try:
                live_payload = {
                    "type": "analytics_event",
                    "event_type": event.event_type,
                    "user_id": event.user_id,
                    "timestamp": event.created_at,
                }
                await self._redis.publish(LIVE_ANALYTICS_CHANNEL, json.dumps(live_payload))
            except Exception as exc:
                logger.warning("Failed to publish live event: %s", exc)

    async def track_page_view(self, user_id: str, page_url: str, referrer: str = None, **kwargs) -> None:
        event = AnalyticsEvent(
            event_type="page_view",
            user_id=user_id,
            page_url=page_url,
            referrer=referrer,
            **kwargs,
        )
        await self.track(event)

    async def track_api_call(self, user_id: str, endpoint: str, method: str, status_code: int, duration_ms: int) -> None:
        event = AnalyticsEvent(
            event_type="api_call",
            user_id=user_id,
            event_data={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        await self.track(event)

    async def _periodic_flush(self) -> None:
        """Periodically flush the event buffer."""
        while True:
            await asyncio.sleep(BUFFER_FLUSH_INTERVAL)
            await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Write buffered events to the database."""
        async with self._lock:
            if not self._buffer:
                return
            events_to_flush = self._buffer[:]
            self._buffer.clear()

        logger.info("Flushing %d analytics events", len(events_to_flush))
        # In production: bulk-insert to PostgreSQL analytics_events table
        # For now, log for demonstration
        for event in events_to_flush:
            logger.debug("Event: %s", json.dumps(event.to_dict()))

    async def get_daily_active_users(self, days: int = 7) -> List[Dict]:
        """Query DAU from Redis cache (materialized in PostgreSQL in production)."""
        if not self._redis:
            return []
        results = []
        for i in range(days):
            day_key = f"dau:{datetime.utcnow().strftime('%Y-%m-%d')}"
            count = await self._redis.get(day_key) or 0
            results.append({"day": day_key, "dau": int(count)})
        return results


pipeline = AnalyticsPipeline()
