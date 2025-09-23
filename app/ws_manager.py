from typing import Dict, Set, Tuple
from fastapi import WebSocket


class WSManager:
    """
    Gerenciador de conexões WebSocket por sala.
    Agora suporta broadcast e mensagens privadas.
    """

    def __init__(self) -> None:
        # Estrutura:
        # rooms = { "sala1": { "user1": ws1, "user2": ws2, ... } }
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room: str, username: str, ws: WebSocket) -> None:
        """
        Aceita conexão e adiciona o WebSocket do usuário à sala.
        """
        await ws.accept()
        self.rooms.setdefault(room, {})[username] = ws

    def disconnect(self, room: str, username: str) -> None:
        """
        Remove o usuário da sala. Se a sala ficar vazia, remove do dict.
        """
        conns = self.rooms.get(room)
        if conns and username in conns:
            conns.pop(username)
            if not conns:
                self.rooms.pop(room, None)

    async def broadcast(self, room: str, payload: dict) -> None:
        """
        Envia payload para todos os usuários da sala.
        """
        conns = list(self.rooms.get(room, {}).items())
        for username, ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(room, username)

    async def send_private(self, room: str, to_user: str, payload: dict) -> bool:
        """
        Envia uma mensagem privada para `to_user` dentro da sala.
        Retorna True se enviou, False se o usuário não está conectado.
        """
        ws = self.rooms.get(room, {}).get(to_user)
        if not ws:
            return False
        try:
            await ws.send_json(payload)
            return True
        except Exception:
            self.disconnect(room, to_user)
            return False
