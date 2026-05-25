
from fastapi import APIRouter, HTTPException
from openai import OpenAIError
from pydantic import BaseModel
from llm.client import get_client, get_model_name

router = APIRouter(prefix="/chat", tags=["chat"])

class chatRequest(BaseModel):
    session_id: str
    query: str
    collection: str
    top_k: int = 5
    score_threshold: float = 0.3

class ChatResponse(BaseModel):
    answer: str
    code: int = 200

@router.post("", response_model=ChatResponse) 

def chat(req: chatRequest):
    try:
        response = get_client().chat.completions.create(
            model=get_model_name(),
            messages=[{"role": "user", "content": req.query}],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail="LLM provider request failed") from e

    return ChatResponse(answer=f"Echo: {response.choices[0].message.content}",code=200)
