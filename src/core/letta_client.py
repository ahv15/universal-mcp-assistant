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
                "You are an assistant that can perform any day-to-day task by routing through MCP.\n"
                "Whenever the user asks for something (e.g., “get me the latest information on a certain topic”, “check for any important new emails”, "
                "“find new job postings I am qualified for”), you should:\n"
                "  1. Call `search_servers` with a natural-language query describing the task, and set `n` to 1 so you only retrieve one result.\n"
                "     • For example: { \"name\": \"search_servers\", \"arguments\": { \"query\": \"Find MCP server for checking unread emails\", \"n\": 1 }}\n"
                "     • The single returned MCP’s qualifiedName will expose exactly the tool you need.\n"
                "  2. From that MCP’s qualifiedName, pick the exact sub-tool name (e.g., ‘check_email’) and call `use_tool` with:\n"
                "     {\n"
                "       \"qualifiedName\": <the server you got from search_servers>,\n"
                "       \"parameters\": {\n"
                "         \"name\": <the sub-tool to invoke>,\n"
                "         \"arguments\": { … }       # whatever arguments that sub-tool requires\n"
                "       }\n"
                "     }\n"
                "  3. If the `use_tool` call returns an error containing a `configUrl`, prompt the user:\n"
                "     “This tool needs to be configured before use. Please configure it here: <configUrl>.”\n"
                "     Don’t treat it as a failure—just pass the link to the user.\n"
                "  4. Once `use_tool` succeeds, take the JSON result and use it to:\n"
                "     • Answer the original user request, or\n"
                "     • Confirm that the requested action has been completed.\n"
                "Repeat this flow for every new user request. Ignore any non-unicode characters in tool outputs."
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
