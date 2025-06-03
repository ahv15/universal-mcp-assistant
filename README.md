# Universal MCP Assistant

A modular FastAPI application that provides a universal interface for interacting with MCP (Model Context Protocol) servers through Letta agents.

## Project Structure

```
universal-mcp-assistant/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py              # Chat API routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── letta_client.py      # Letta client management
│   │   └── chat_service.py      # Chat business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py              # Pydantic models
│   └── __init__.py
├── config/
│   └── mcp_config.json          # MCP server configuration
├── public/
│   └── chat.html                # Chat UI frontend
├── main.py                      # Application entry point
└── README.md                    # This file
```

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for API, core logic, and models
- **MCP Integration**: Seamless integration with MCP servers through Letta agents
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Modern UI**: Tailwind CSS-powered chat interface
- **CORS Support**: Configurable CORS middleware for cross-origin requests

## Quick Start

### Prerequisites

- Python 3.8+
- Letta server running on `localhost:8283`
- MCP servers configured (e.g., Smithery Toolbox)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ahv15/universal-mcp-assistant.git
cd universal-mcp-assistant
```

2. Install dependencies:
```bash
pip install fastapi uvicorn letta-client pydantic
```

3. Configure MCP servers in `config/mcp_config.json`:
```json
{
  "mcpServers": {
    "toolbox": {
      "command": "cmd",
      "args": [
        "/c",
        "npx",
        "-y",
        "@smithery/cli@latest",
        "run",
        "@smithery/toolbox",
        "--key",
        "YOUR_SMITHERY_KEY_HERE",
        "--profile",
        "YOUR_PROFILE_HERE"
      ]
    }
  }
}
```

### Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

2. Open the chat interface:
   - Open `public/chat.html` in your browser
   - Or visit the API docs at `http://localhost:8000/docs`

## API Endpoints

### POST /chat

Send a message to the MCP assistant.

**Request:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "reply": "Assistant's response"
}
```

## Configuration

### MCP Servers

Configure your MCP servers in `config/mcp_config.json`. The application currently supports:

- **Smithery Toolbox**: Provides various utility tools
- **Custom MCP Servers**: Add your own server configurations

### Letta Agent

The Letta agent is configured with:
- Model: `openai/gpt-4o`
- Embedding: `openai/text-embedding-3-small`
- Tool routing through MCP servers

## Development

### Adding New API Routes

1. Create a new router in `src/api/`
2. Define your endpoints
3. Register the router in `main.py`

### Adding New Services

1. Create service classes in `src/core/`
2. Implement business logic
3. Inject dependencies as needed

### Adding New Models

1. Define Pydantic models in `src/models/`
2. Use type hints for better IDE support
3. Add validation as needed

## Troubleshooting

### Common Issues

1. **Letta Connection Error**: Ensure Letta server is running on `localhost:8283`
2. **MCP Server Not Found**: Check your MCP server configuration and ensure tools are available
3. **CORS Issues**: Verify the `allow_origins` setting in the CORS middleware

### Debugging

- Check the FastAPI logs for detailed error messages
- Use the interactive API docs at `/docs` to test endpoints
- Verify MCP server status through Letta client

## Contributing

This project follows a clean architecture pattern. Please:

1. Maintain separation of concerns
2. Add type hints to all functions
3. Include docstrings for public methods
4. Write tests for new functionality

## License

MIT License - see LICENSE file for details.
