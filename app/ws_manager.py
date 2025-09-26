"""ws_manager.py — gerencia conexões WebSocket por sala."""

from typing import Dict, Set
from fastapi import WebSocket

class WSManager:
    """
    Gerenciador simples de WebSockets por 'room'.
    - connect(room, ws): aceita e registra ws
    - disconnect(room, ws): remove
    - broadcast(room, payload): envia JSON para todos da sala
    """
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)

    def disconnect(self, room: str, ws: WebSocket):
        conns = self.rooms.get(room)
        if conns and ws in conns:
            conns.remove(ws)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict):
        """Envia payload (serializável) para todos WS da sala. Conexões com erro são removidas."""
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                # falha ao enviar -> desconecta
                self.disconnect(room, ws)
