"""Notification endpoints — currently polling-based."""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models

router = APIRouter()

# In-memory connection manager — NOT horizontally scalable
# TODO: replace with Redis pub/sub for multi-instance support
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_notification(self, user_id: int, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)

manager = ConnectionManager()

@router.get("/")
def get_notifications(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    # Polling endpoint — clients hit this every 30 seconds
    # TODO: remove once WebSocket is implemented
    return db.query(models.Notification).order_by(
        models.Notification.created_at.desc()
    ).offset(skip).limit(limit).all()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # TODO: implement authentication before accepting connection
    # TODO: implement heartbeat ping/pong
    # TODO: deliver offline messages on reconnect
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
