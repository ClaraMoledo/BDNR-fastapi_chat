"""models.py — Pydantic models e funções de serialização."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId

# --- Pydantic models ---
class MessageIn(BaseModel):
    """Modelo de entrada para POST/WS (validação)."""
    username: str = Field(..., max_length=50)
    content: str = Field(..., min_length=1, max_length=1000)

    @validator("username", pre=True, always=True)
    def default_username(cls, v):
        if v is None:
            return "anon"
        return str(v)[:50]

    @validator("content", pre=True)
    def strip_content(cls, v):
        return str(v).strip()

class MessageOut(BaseModel):
    """Modelo de saída padronizado para responses e WS."""
    _id: str
    room: str
    username: str
    content: str
    created_at: str

# --- helpers ---
def iso(dt: datetime) -> str:
    """Converte datetime para ISO com timezone (UTC se ausente)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def serialize(doc: dict) -> dict:
    """
    Serializa documento Mongo -> dict JSON-friendly.
    Converte _id para str e created_at para ISO.
    """
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = iso(d["created_at"])
    return d
