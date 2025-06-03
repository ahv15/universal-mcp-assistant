from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

from letta_client import Letta
from letta_client.types.child_tool_rule import ChildToolRule

# 1) Pydantic Schemas

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# 2) FastAPI App & CORS

app = FastAPI()

# If your frontend is on a different origin/port, adjust allow_origins accordingly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


#  3) Global Letta Variables 

letta_client: Letta = None
agent_state = None


#  4) Startup Event: Initialize Letta, Register All MCP Tools, Create Agent 

@app.on_event("startup")
def startup_event():
    global letta_client, agent_state

    # 4.1) Instantiate Letta client (point to your local MCP server)
    letta_client = Letta(base_url="http://localhost:8283")

    # 4.2) List available MCP servers (for debugging/logging if needed)
    all_mcp = letta_client.tools.list_mcp_servers()
    # e.g. → [{"name": "toolbox", ...}, { "name": "github", ...}, ... ]

    # 4.3) Choose the MCP server you want to pull tools from
    mcp_server_name = "toolbox"
    mcp_tools = letta_client.tools.list_mcp_tools_by_server(
        mcp_server_name=mcp_server_name
    )

    # 4.4) Add each tool from that MCP server into Letta
    tool_ids = []
    for tool in mcp_tools:
        added = letta_client.tools.add_mcp_tool(
            mcp_server_name=mcp_server_name,
            mcp_tool_name=tool.name
        )
        tool_ids.append(added.id)

    # 4.5) Create a Letta agent that knows how to route requests through MCP
    agent_state = letta_client.agents.create(
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


#  5) /chat Endpoint 

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Accepts { "message": "<user’s text>" }, forwards it to Letta,
    and returns { "reply": "<assistant’s response>" }.
    """
    user_prompt = req.message.strip()
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Empty message")

    # 5.1) Build the single “user” message payload
    payload = [
        {"role": "user", "content": user_prompt}
    ]

    try:
        # 5.2) Have Letta’s agent process that single‐turn conversation
        response = letta_client.agents.messages.create(
            agent_id=agent_state.id,
            messages=payload,
        )

        # 5.3) Pull out all “assistant_message” contents in one line
        assistant_contents = [
            msg.content
            for msg in response.messages
            if msg.message_type == "assistant_message"
        ]

        # 5.4) If there was no assistant message, that’s unexpected
        if not assistant_contents:
            raise HTTPException(status_code=500, detail="No assistant reply found")

        # 5.5) Return the first assistant reply
        return ChatResponse(reply=assistant_contents[0])

    except Exception as e:
        # Catch any Letta or network errors
        raise HTTPException(status_code=500, detail=f"Error from Letta: {e}")
