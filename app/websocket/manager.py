from collections import defaultdict
from typing import DefaultDict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: DefaultDict[UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[session_id].append(websocket)

    def disconnect(self, session_id: UUID, websocket: WebSocket) -> None:
        if websocket in self._connections[session_id]:
            self._connections[session_id].remove(websocket)
        if not self._connections[session_id]:
            self._connections.pop(session_id, None)

    async def broadcast(self, session_id: UUID, message: dict) -> None:
        for connection in self._connections.get(session_id, []):
            await connection.send_json(message)


manager = ConnectionManager()
