from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from bson import ObjectId
from ..database import get_db
from ..models import serialize, MessageIn, is_valid_objectid
from datetime import datetime, timezone

router = APIRouter()

@router.get("/rooms/{room}/messages")
async def get_messages(room: str, limit: int = Query(20, ge=1, le=100), before_id: Optional[str] = Query(None)):
    query = {"room": room}
    if before_id is not None:
        if not is_valid_objectid(before_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="before_id inválido")
        query["_id"] = {"$lt": ObjectId(before_id)}

    cursor = get_db()["messages"].find(query).sort("_id", -1).limit(limit)
    docs = [serialize(d) async for d in cursor]
    docs.reverse()
    next_cursor = docs[0]["_id"] if docs else None
    return {"items": docs, "next_cursor": next_cursor}

@router.post("/rooms/{room}/messages", status_code=201)
async def post_message(room: str, payload: MessageIn):
    doc = {
        "room": room,
        "username": payload.username[:50],
        "content": payload.content[:1000],
        "created_at": datetime.now(timezone.utc),
    }
    res = await get_db()["messages"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize(doc)
