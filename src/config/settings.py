import json
import os
from typing import Dict, Any
from pathlib import Path


class Settings:
    """Application settings and configuration management."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
    
    @property
    def letta_base_url(self) -> str:
        """Letta server base URL."""
        return os.getenv("LETTA_BASE_URL", "http://localhost:8283")
    
    @property
    def server_host(self) -> str:
        """FastAPI server host."""
        return os.getenv("SERVER_HOST", "0.0.0.0")
    
    @property
    def server_port(self) -> int:
        """FastAPI server port."""
        return int(os.getenv("SERVER_PORT", "8000"))
    
    @property
    def cors_origins(self) -> list:
        """CORS allowed origins."""
        origins = os.getenv("CORS_ORIGINS", "*")
        if origins == "*":
            return ["*"]
        return [origin.strip() for origin in origins.split(",")]
    
    def load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP server configuration."""
        config_file = self.config_dir / "mcp_config.json"
        
        # Try local config first (with secrets)
        local_config_file = self.config_dir / "mcp_config.local.json"
        if local_config_file.exists():
            config_file = local_config_file
        
        if not config_file.exists():
            raise FileNotFoundError(f"MCP config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)


# Global settings instance
settings = Settings()
