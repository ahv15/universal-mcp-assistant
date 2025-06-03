import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from src.core.chat_service import ChatService
from src.models.chat import ChatRequest, ChatResponse


class TestChatService:
    """Test cases for ChatService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_letta_manager = Mock()
        self.chat_service = ChatService(self.mock_letta_manager)
    
    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test successful message processing."""
        # Arrange
        request = ChatRequest(message="Hello, world!")
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.message_type = "assistant_message"
        mock_message.content = "Hello! How can I help you?"
        mock_response.messages = [mock_message]
        
        self.mock_letta_manager.send_message.return_value = mock_response
        
        # Act
        result = await self.chat_service.process_message(request)
        
        # Assert
        assert isinstance(result, ChatResponse)
        assert result.reply == "Hello! How can I help you?"
        self.mock_letta_manager.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_message_empty_message(self):
        """Test handling of empty messages."""
        # Arrange
        request = ChatRequest(message="   ")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await self.chat_service.process_message(request)
        
        assert exc_info.value.status_code == 400
        assert "Empty message" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_process_message_no_assistant_reply(self):
        """Test handling when no assistant reply is found."""
        # Arrange
        request = ChatRequest(message="Hello")
        
        mock_response = MagicMock()
        mock_response.messages = []  # No messages
        
        self.mock_letta_manager.send_message.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await self.chat_service.process_message(request)
        
        assert exc_info.value.status_code == 500
        assert "No assistant reply found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_process_message_letta_error(self):
        """Test handling of Letta errors."""
        # Arrange
        request = ChatRequest(message="Hello")
        
        self.mock_letta_manager.send_message.side_effect = Exception("Letta connection error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await self.chat_service.process_message(request)
        
        assert exc_info.value.status_code == 500
        assert "Error from Letta" in str(exc_info.value.detail)
