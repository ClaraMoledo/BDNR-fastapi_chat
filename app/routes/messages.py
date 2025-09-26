"""routes/messages.py — rotas REST relacionadas a mensagens."""

from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from bson import ObjectId, errors as bson_errors
from datetime import datetime, timezone

from ..database import get_db
from ..models import serialize, MessageIn

router = APIRouter()

@router.get("/rooms/{room}/messages")
async def get_messages(
    room: str,
    limit: int = Query(20, ge=1, le=100),
    before_id: Optional[str] = Query(None),
):
    """
    Retorna histórico da sala.
    Se before_id for informado e inválido, retorna HTTP 400.
    """
    query = {"room": room}
    if before_id:
        try:
            query["_id"] = {"$lt": ObjectId(before_id)}
        except (TypeError, bson_errors.InvalidId):
            raise HTTPException(status_code=400, detail="before_id inválido")

    cursor = get_db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}

@router.post("/rooms/{room}/messages", status_code=status.HTTP_201_CREATED)
async def post_message(room: str, payload: MessageIn):
    """
    Recebe MessageIn, valida (Pydantic) e salva.
    Mensagens sem conteúdo não são salvas (validação Pydantic já impede).
    """
    db = get_db()
    doc = {
        "room": room,
        "username": payload.username[:50],
        "content": payload.content[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    res = await db["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)
