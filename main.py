from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.letta_client import LettaManager
from src.core.chat_service import ChatService
from src.api.chat import create_chat_router
from src.config.settings import settings


# FastAPI App & CORS
app = FastAPI(title="Universal MCP Assistant", version="1.0.0")

# Configure CORS with settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Global instances
letta_manager: LettaManager = None
chat_service: ChatService = None


@app.on_event("startup")
def startup_event():
    """Initialize Letta, register all MCP tools, and create agent."""
    global letta_manager, chat_service
    
    # Initialize Letta manager with settings
    letta_manager = LettaManager(base_url=settings.letta_base_url)
    letta_manager.initialize_client()
    
    # List available MCP servers (for debugging/logging if needed)
    all_mcp = letta_manager.list_mcp_servers()
    print(f"Available MCP servers: {[server.get('name', 'unknown') for server in all_mcp]}")
    
    # Choose the MCP server you want to pull tools from
    mcp_server_name = "toolbox"
    tool_ids = letta_manager.setup_mcp_tools(mcp_server_name)
    print(f"Registered {len(tool_ids)} tools from {mcp_server_name}")
    
    # Create agent with the tools
    letta_manager.create_agent(tool_ids)
    print("Letta agent created successfully")
    
    # Initialize chat service
    chat_service = ChatService(letta_manager)
    
    # Add chat router
    chat_router = create_chat_router(chat_service)
    app.include_router(chat_router)
    
    print(f"Universal MCP Assistant started on {settings.server_host}:{settings.server_port}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Universal MCP Assistant is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.server_host, 
        port=settings.server_port,
        reload=True
    )
