"""Assignment 2: a tool that calls a real external API.

Uses only the Python standard library (urllib) for the HTTP call — no extra
dependency to install.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
"""

import json
import os
import urllib.request

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("assignment-02-api-call")

ADVICE_URL = "https://api.adviceslip.com/advice"


@mcp.tool()
def get_advice() -> str:
    """Fetch a random piece of advice from api.adviceslip.com."""
    with urllib.request.urlopen(ADVICE_URL, timeout=5) as response:
        data = json.load(response)
    return data["slip"]["advice"]


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "8002")),
            stateless_http=True,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
