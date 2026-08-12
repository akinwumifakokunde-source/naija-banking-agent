from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.agent import run_agent


router = APIRouter(
    prefix="/api/v1/agent",
    tags=["AI Agent"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    response = run_agent(
        user_message=request.message,
        session_id=request.session_id,
    )

    return {
        "response": response,
    }