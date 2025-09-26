"""
Gerencia conexões WebSocket entre salas.
"""

from fastapi import WebSocket

class WSManager:
    """
    Gerencia as conexões WebSocket por sala.
    """
    def __init__(self):
        self.rooms = {}

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
        """
        Envia uma mensagem para todos os WebSockets conectados na sala informada.
        """
        for ws in list(self.rooms.get(room, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, ws)