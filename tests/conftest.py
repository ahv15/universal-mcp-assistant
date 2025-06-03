import pytest
from unittest.mock import Mock

from src.core.letta_client import LettaManager
from src.core.chat_service import ChatService


@pytest.fixture
def mock_letta_manager():
    """Create a mock LettaManager for testing."""
    return Mock(spec=LettaManager)


@pytest.fixture
def chat_service(mock_letta_manager):
    """Create a ChatService instance with mocked dependencies."""
    return ChatService(mock_letta_manager)
