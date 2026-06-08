# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.text2sql import generate_sql
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = datetime.now(timezone.utc)
    result = await generate_sql(request.message, db)
    result["duration"] = (datetime.now(timezone.utc) - start_time).total_seconds()
    return result# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from core.text2sql import preview_query, execute_query, generate_sql
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = ""

class ExecuteRequest(BaseModel):
    message: str
    sql: str
    session_id: str = ""

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = datetime.now(timezone.utc)
    result = await generate_sql(request.message, db)
    result["duration"] = (datetime.now(timezone.utc) - start_time).total_seconds()
    return result

@router.post("/chat/preview")
async def chat_preview(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = datetime.now(timezone.utc)
    result = await preview_query(request.message, db)
    result["duration"] = (datetime.now(timezone.utc) - start_time).total_seconds()
    return result

@router.post("/chat/execute")
async def chat_execute(request: ExecuteRequest, db: Session = Depends(get_db)):
    start_time = datetime.now(timezone.utc)
    result = await execute_query(request.message, request.sql, db)
    result["duration"] = (datetime.now(timezone.utc) - start_time).total_seconds()
    return result
