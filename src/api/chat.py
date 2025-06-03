from fastapi import APIRouter
from src.models.chat import ChatRequest, ChatResponse
from src.core.chat_service import ChatService


def create_chat_router(chat_service: ChatService) -> APIRouter:
    """Create and configure the chat router."""
    router = APIRouter()
    
    @router.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(req: ChatRequest):
        """
        Accepts { "message": "<user's text>" }, forwards it to Letta,
        and returns { "reply": "<assistant's response>" }.
        """
        return await chat_service.process_message(req)
    
    return router
