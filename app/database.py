"""
Conexão com MongoDB e funções auxiliares.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URL, MONGO_DB

_client = None

def db():
    """
    Retorna a instância do banco de dados MongoDB.
    """
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("Defina MONGO_URL no .env (string do MongoDB Atlas).")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[MONGO_DB]