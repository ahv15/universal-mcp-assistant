from typing import List, Optional
from letta_client import Letta
from letta_client.types.child_tool_rule import ChildToolRule


class LettaManager:
    """Manages Letta client initialization and agent creation."""
    
    def __init__(self, base_url: str = "http://localhost:8283"):
        self.base_url = base_url
        self.client: Optional[Letta] = None
        self.agent_state = None
    
    def initialize_client(self) -> None:
        """Initialize the Letta client."""
        self.client = Letta(base_url=self.base_url)
    
    def list_mcp_servers(self) -> List[dict]:
        """List available MCP servers."""
        if not self.client:
            raise RuntimeError("Letta client not initialized")
        return self.client.tools.list_mcp_servers()
    
    def setup_mcp_tools(self, mcp_server_name: str = "toolbox") -> List[str]:
        """Setup MCP tools for the specified server."""
        if not self.client:
            raise RuntimeError("Letta client not initialized")
        
        # Get tools from the MCP server
        mcp_tools = self.client.tools.list_mcp_tools_by_server(
            mcp_server_name=mcp_server_name
        )
        
        # Add each tool to Letta
        tool_ids = []
        for tool in mcp_tools:
            added = self.client.tools.add_mcp_tool(
                mcp_server_name=mcp_server_name,
                mcp_tool_name=tool.name
            )
            tool_ids.append(added.id)
        
        return tool_ids
    
    def create_agent(self, tool_ids: List[str]) -> None:
        """Create a Letta agent with the specified tools."""
        if not self.client:
            raise RuntimeError("Letta client not initialized")
        
        self.agent_state = self.client.agents.create(
            name="universal_mcp_assistant",
            system=(
                "Temporary System Prompt"
            ),
            model="openai/gpt-4o",
            embedding="openai/text-embedding-3-small",
            tool_ids=tool_ids,
            tool_rules=[
                ChildToolRule(tool_name="use_tool", children=["send_message"]),
            ]
        )
    
    def send_message(self, messages: List[dict]) -> dict:
        """Send a message to the agent and return the response."""
        if not self.client or not self.agent_state:
            raise RuntimeError("Letta client or agent not initialized")
        
        response = self.client.agents.messages.create(
            agent_id=self.agent_state.id,
            messages=messages,
        )
        
        return response
