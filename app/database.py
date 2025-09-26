"""database.py — cria e expõe a conexão com MongoDB e helpers simples."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from .config import MONGO_URL, MONGO_DB

_client: Optional[AsyncIOMotorClient] = None

def get_db() -> AsyncIOMotorDatabase:
    """
    Retorna o objeto AsyncIOMotorDatabase.
    Cria a conexão lazily na primeira chamada.
    Lança RuntimeError se MONGO_URL não estiver setada.
    """
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("Defina MONGO_URL no .env (string do MongoDB Atlas).")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[MONGO_DB]
