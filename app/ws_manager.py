from typing import Dict, Set
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket) -> None:
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket) -> None:
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict) -> None:
        conns = list(self.rooms.get(room, []))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)
