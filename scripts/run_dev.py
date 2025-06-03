#!/usr/bin/env python3
"""Development server runner script."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    from src.config.settings import settings
    
    print("Starting Universal MCP Assistant in development mode...")
    print(f"Server will run on {settings.server_host}:{settings.server_port}")
    print(f"Letta server expected at {settings.letta_base_url}")
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        reload_dirs=[str(project_root / "src")],
        log_level="info"
    )
