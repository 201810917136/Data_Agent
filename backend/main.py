from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.auth import router as auth_router

app = FastAPI(
    title="AI Auction Analytics",
    description="AI 问数系统 - 二手车拍卖数据仓库",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")

@app.get("/")
async def root():
    return {"status": "ok", "service": "ai-auction-analytics"}
