from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.letta_client import LettaManager
from src.core.chat_service import ChatService
from src.api.chat import create_chat_router


# FastAPI App & CORS
app = FastAPI(title="Universal MCP Assistant", version="1.0.0")

# If your frontend is on a different origin/port, adjust allow_origins accordingly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Global instances
letta_manager: LettaManager = None
chat_service: ChatService = None


@app.on_event("startup")
def startup_event():
    """Initialize Letta, register all MCP tools, and create agent."""
    global letta_manager, chat_service
    
    # Initialize Letta manager
    letta_manager = LettaManager(base_url="http://localhost:8283")
    letta_manager.initialize_client()
    
    # List available MCP servers (for debugging/logging if needed)
    all_mcp = letta_manager.list_mcp_servers()
    # e.g. → [{"name": "toolbox", ...}, { "name": "github", ...}, ... ]
    
    # Choose the MCP server you want to pull tools from
    mcp_server_name = "toolbox"
    tool_ids = letta_manager.setup_mcp_tools(mcp_server_name)
    
    # Create agent with the tools
    letta_manager.create_agent(tool_ids)
    
    # Initialize chat service
    chat_service = ChatService(letta_manager)
    
    # Add chat router
    chat_router = create_chat_router(chat_service)
    app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
