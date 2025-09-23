from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


# ---------- Schemas Pydantic ----------

class MessageIn(BaseModel):
    """
    Schema de entrada para mensagens.
    """
    username: str = Field(..., max_length=50, description="Nome do usuário")
    content: str = Field(..., max_length=1000, description="Conteúdo da mensagem")

    @validator("username", pre=True, always=True)
    def default_username(cls, v: Optional[str]) -> str:
        return (v or "anon").strip()

    @validator("content")
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content não pode estar vazio")
        return v.strip()


class MessageOut(BaseModel):
    """
    Schema de saída para mensagens.
    """
    _id: str
    room: str
    username: str
    content: str
    created_at: str


# ---------- Helpers ----------

def iso(dt: datetime) -> str:
    """
    Converte datetime em string ISO 8601 com timezone UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def serialize(doc: dict) -> dict:
    """
    Converte um documento MongoDB para dict serializável.
    - _id vira str
    - created_at vira ISO
    """
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d


def is_valid_objectid(oid: str) -> bool:
    """
    Verifica se uma string é um ObjectId válido do MongoDB.
    """
    try:
        ObjectId(oid)
        return True
    except Exception:
        return False
