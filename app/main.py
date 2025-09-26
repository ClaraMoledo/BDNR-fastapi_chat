"""main.py — inicialização do FastAPI e montagem das rotas + WebSocket."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timezone

from .config import APP_HOST, APP_PORT
from .database import get_db
from .models import serialize, MessageIn
from .ws_manager import WSManager
from .routes import messages as messages_router

app = FastAPI(title="FastAPI Chat + MongoDB Atlas (refatorado)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount static (cliente)
ROOT = Path(__file__).resolve().parents[1]
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(str(ROOT / "static" / "index.html"))

# incluir routes REST
app.include_router(messages_router.router)

# WS manager
manager = WSManager()

@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    """Conexão WS por sala. Envia histórico inicial e broadcast de mensagens."""
    await manager.connect(room, ws)
    try:
        # histórico inicial (20 últimas)
        cursor = get_db()["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        while True:
            payload = await ws.receive_json()
            # validação mínima com Pydantic
            try:
                msg = MessageIn(**payload)
            except Exception:
                # ignora mensagens inválidas (poderia retornar um error type se desejar)
                continue

            # novamente garante que content não seja vazio
            if not msg.content:
                continue

            doc = {
                "room": room,
                "username": msg.username,
                "content": msg.content,
                "created_at": datetime.now(timezone.utc),
            }
            res = await get_db()["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id
            await manager.broadcast(room, {"type": "message", "item": serialize(doc)})

    except WebSocketDisconnect:
        manager.disconnect(room, ws)
