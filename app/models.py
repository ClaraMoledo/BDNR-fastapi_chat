"""
Modelos Pydantic e funções de serialização para mensagens.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId

class MessageIn(BaseModel):
    username: str = Field(..., max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)

class MessageOut(BaseModel):
    id: str
    room: str
    username: str
    content: str
    created_at: datetime

def iso(dt: datetime) -> str:
    """
    Converte datetime para ISO 8601 com timezone.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def serialize(doc: dict) -> dict:
    """
    Serializa documento do MongoDB para dict compatível com MessageOut.
    """
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d