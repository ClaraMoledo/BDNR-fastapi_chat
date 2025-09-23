from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import MONGO_URL, MONGO_DB

# Cliente global reutilizado pela aplicação
_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    """
    Retorna um cliente MongoDB (singleton).
    Cria a conexão caso ainda não exista.
    """
    global _client
    if _client is None:
        if not MONGO_URL:
            raise RuntimeError("❌ Defina MONGO_URL no arquivo .env")
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    """
    Retorna a instância do banco de dados configurado (MONGO_DB).
    """
    return get_client()[MONGO_DB]
