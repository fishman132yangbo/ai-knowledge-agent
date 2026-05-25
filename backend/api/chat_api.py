
from fastapi import APIRouter
from pydantic import BaseModel
from llm.client import client, model_name

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
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": req.query}],
    )
    return ChatResponse(answer=f"Echo: {response.choices[0].message.content}",code=200)