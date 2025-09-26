"""
Rotas REST para histórico e envio de mensagens.
"""

from fastapi import APIRouter, Query, HTTPException, status
from app.database import db
from app.models import MessageIn, MessageOut, serialize
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/rooms")

@router.get("/{room}/messages", response_model=dict)
async def get_messages(
    room: str, 
    limit: int = Query(20, ge=1, le=100), 
    before_id: Optional[str] = Query(None)
):
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="before_id inválido")

    cursor = db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}

@router.post("/{room}/messages", response_model=MessageOut, status_code=201)
async def post_message(room: str, msg: MessageIn):
    if not msg.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conteúdo não pode ser vazio")
    doc = {
        "room": room,
        "username": msg.username,
        "content": msg.content,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db()["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)