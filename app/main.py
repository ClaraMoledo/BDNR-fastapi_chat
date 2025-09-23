from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from .routes import messages
from .ws_manager import WSManager
from .database import get_db
from .models import serialize, MessageIn

app = FastAPI(title="FastAPI Chat + MongoDB Atlas (Privado + Broadcast)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static client ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("app/static/index.html")

# --- REST ---
app.include_router(messages.router)

# --- WS Manager ---
manager = WSManager()

@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    username = None
    try:
        # Espera a primeira mensagem para saber quem é o usuário
        first_payload = await ws.receive_json()
        username = first_payload.get("username", "anon").strip()[:50]
        if not username:
            username = "anon"

        # Conectar o usuário
        await manager.connect(room, username, ws)

        # Enviar histórico inicial
        cursor = get_db()["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        # Loop principal
        while True:
            payload = await ws.receive_json()
            content = str(payload.get("content", "")).strip()
            to_user = payload.get("to")  # opcional

            if not content:
                continue

            # Documento base
            doc = {
                "room": room,
                "username": username,
                "content": content,
                "created_at": datetime.now(timezone.utc),
            }
            res = await get_db()["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id

            if to_user:
                # Mensagem privada
                sent = await manager.send_private(
                    room,
                    to_user,
                    {
                        "type": "private",
                        "from": username,
                        "content": content,
                        "created_at": doc["created_at"].isoformat(),
                    },
                )
                if not sent:
                    await ws.send_json(
                        {"type": "error", "msg": f"{to_user} não está online"}
                    )
            else:
                # Broadcast normal
                await manager.broadcast(room, {"type": "message", "item": serialize(doc)})

    except WebSocketDisconnect:
        if username:
            manager.disconnect(room, username)
