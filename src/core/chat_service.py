from typing import List
from fastapi import HTTPException
from src.models.chat import ChatRequest, ChatResponse
from src.core.letta_client import LettaManager


class ChatService:
    """Service for handling chat interactions."""
    
    def __init__(self, letta_manager: LettaManager):
        self.letta_manager = letta_manager
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process a chat message and return the response."""
        user_prompt = request.message.strip()
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Empty message")
        
        # Build the single 'user' message payload
        payload = [
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Have Letta's agent process the conversation
            response = self.letta_manager.send_message(payload)
            
            # Pull out all 'assistant_message' contents
            assistant_contents = [
                msg.content
                for msg in response.messages
                if msg.message_type == "assistant_message"
            ]
            
            # If there was no assistant message, that's unexpected
            if not assistant_contents:
                raise HTTPException(status_code=500, detail="No assistant reply found")
            
            # Return the first assistant reply
            return ChatResponse(reply=assistant_contents[0])
        
        except Exception as e:
            # Catch any Letta or network errors
            raise HTTPException(status_code=500, detail=f"Error from Letta: {e}")
