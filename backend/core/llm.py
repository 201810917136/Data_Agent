# -*- coding: utf-8 -*-
import httpx
from config import AGNES_API_KEY, AGNES_BASE_URL, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
from datetime import datetime, timezone


async def call_llm(system_prompt: str, user_question: str, trace_id: str = None) -> str:
    headers = {
        'Authorization': f'Bearer {AGNES_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': 'agnes-1.5-flash',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_question},
        ],
        'temperature': 0.1,
    }
    start_time = datetime.now(timezone.utc)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f'{AGNES_BASE_URL}/chat/completions',
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            end_time = datetime.now(timezone.utc)
            # 记录 Langfuse trace
            try:
                from langfuse import Langfuse
                from langfuse.types import TraceContext
                langfuse = Langfuse(
                    public_key=LANGFUSE_PUBLIC_KEY,
                    secret_key=LANGFUSE_SECRET_KEY,
                    host=LANGFUSE_BASE_URL,
                )
                if trace_id:
                    tc = TraceContext(trace_id=trace_id)
                    gen = langfuse.start_generation(
                        trace_context=tc,
                        name='agnes-1.5-flash',
                        input={'system': system_prompt, 'user': user_question},
                        output=content,
                        metadata={'model': 'agnes-1.5-flash'},
                        usage_details={'inputTokens': len(system_prompt) // 4, 'outputTokens': len(content) // 4},
                    )
                    gen.end()
                    langfuse.flush()
            except Exception:
                pass
            return content
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        try:
            from langfuse import Langfuse
            from langfuse.types import TraceContext
            langfuse = Langfuse(
                public_key=LANGFUSE_PUBLIC_KEY,
                secret_key=LANGFUSE_SECRET_KEY,
                host=LANGFUSE_BASE_URL,
            )
            if trace_id:
                tc = TraceContext(trace_id=trace_id)
                gen = langfuse.start_generation(
                    trace_context=tc,
                    name='agnes-1.5-flash',
                    input={'system': system_prompt, 'user': user_question},
                    output=None,
                    status_message=str(e),
                )
                gen.end()
                langfuse.flush()
        except Exception:
            pass
        raise