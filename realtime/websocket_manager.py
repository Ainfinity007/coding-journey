"""
WebSocket connection manager with Redis Pub/Sub for horizontal scaling.
Supports per-user connections, channel broadcasting, and heartbeats.
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 30  # seconds
MAX_MESSAGE_SIZE = 64 * 1024  # 64KB


class ConnectionManager:
    """Manages WebSocket connections with Redis Pub/Sub broadcasting."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url)
        return self._redis

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info("WebSocket connected: user=%s total=%d", user_id, self.total_connections)

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info("WebSocket disconnected: user=%s total=%d", user_id, self.total_connections)

    @property
    def total_connections(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """Send message to all connections for a user. Returns delivered count."""
        if user_id not in self.active_connections:
            return 0
        delivered = 0
        dead_sockets = set()
        for ws in self.active_connections[user_id].copy():
            try:
                await ws.send_json(message)
                delivered += 1
            except Exception as exc:
                logger.warning("Failed to send to user %s: %s", user_id, exc)
                dead_sockets.add(ws)
        for ws in dead_sockets:
            self.active_connections[user_id].discard(ws)
        return delivered

    async def broadcast_to_all(self, message: dict) -> None:
        """Broadcast message to all connected users on this instance."""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)

    async def publish_to_channel(self, channel: str, message: dict) -> None:
        """Publish to Redis channel for cross-instance delivery."""
        r = await self._get_redis()
        await r.publish(channel, json.dumps(message))

    async def start_subscriber(self) -> None:
        """Subscribe to Redis channels and forward messages to local connections."""
        r = await self._get_redis()
        pubsub = r.pubsub()
        await pubsub.psubscribe("notifications:*", "analytics:live", "broadcast:all")
        logger.info("Redis Pub/Sub subscriber started")

        async for message in pubsub.listen():
            if message["type"] not in ("pmessage", "message"):
                continue
            try:
                channel = message["channel"].decode() if isinstance(message["channel"], bytes) else message["channel"]
                data = json.loads(message["data"])

                if channel.startswith("notifications:"):
                    user_id = channel.split(":", 1)[1]
                    await self.send_to_user(user_id, data)
                elif channel in ("analytics:live", "broadcast:all"):
                    await self.broadcast_to_all(data)
            except Exception as exc:
                logger.error("Subscriber error: %s", exc)

    async def send_heartbeat(self, websocket: WebSocket) -> None:
        """Send periodic ping to keep connection alive."""
        while True:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            try:
                await websocket.send_json({"type": "ping"})
            except Exception:
                break


manager = ConnectionManager()
