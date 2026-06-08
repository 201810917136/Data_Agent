from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    if request.username == "admin" and request.password == "admin":
        return {"token": "mock-jwt-token", "user": {"id": 1, "username": "admin", "role": "admin"}}
    return {"error": "Invalid credentials"}
