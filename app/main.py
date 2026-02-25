from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.api import auth, exam, users
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import redis_client
from app.websocket.manager import manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    yield
    await redis_client.aclose()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(exam.router, prefix=settings.API_V1_PREFIX)


@app.get('/health')
async def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}


@app.websocket('/ws/exam/{session_id}')
async def exam_session_ws(websocket: WebSocket, session_id: UUID):
    await manager.connect(session_id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            await manager.broadcast(session_id, payload)
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
