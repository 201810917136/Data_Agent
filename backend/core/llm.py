# -*- coding: utf-8 -*-
import httpx
from config import AGNES_API_KEY, AGNES_BASE_URL

async def call_llm(system_prompt: str, user_question: str) -> str:
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-1.5-flash",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
        "temperature": 0.1,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]