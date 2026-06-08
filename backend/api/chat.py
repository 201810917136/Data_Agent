from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.text2sql import generate_sql
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    result = await generate_sql(request.message, db)
    return result
