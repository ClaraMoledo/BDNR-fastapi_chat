"""
Inicialização do FastAPI, montagem das rotas e WebSocket.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_HOST, APP_PORT
from app.ws_manager import WSManager
from app.models import serialize
from app.database import db
from app.routes import messages

app = FastAPI(title="FastAPI Chat + MongoDB Atlas (Refatorado)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(messages.router)

@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("app/static/index.html")

manager = WSManager()

@app.websocket("/ws/{room}")
async def ws_room(ws: WebSocket, room: str):
    await manager.connect(room, ws)
    try:
        cursor = db()["messages"].find({"room": room}).sort("_id", -1).limit(20)
        items = [serialize(d) async for d in cursor]
        items.reverse()
        await ws.send_json({"type": "history", "items": items})

        while True:
            payload = await ws.receive_json()
            username = str(payload.get("username", "anon"))[:50]
            content = str(payload.get("content", "")).strip()
            if not content:
                continue
            doc = {
                "room": room,
                "username": username,
                "content": content,
                "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            }
            res = await db()["messages"].insert_one(doc)
            doc["_id"] = res.inserted_id
            await manager.broadcast(room, {"type": "message", "item": serialize(doc)})
    except WebSocketDisconnect:
        manager.disconnect(room, ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host=APP_HOST, port=APP_PORT)