"""Assignment 1: basic tools — echo, greet, sum.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
"""

import os

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("assignment-01-basic-tools")

_greet_count = 0


@mcp.tool()
def echo(text: str) -> str:
    """Echo back the given text."""
    return text


@mcp.tool()
def sum(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name, tracking how many greetings have been sent."""
    global _greet_count
    _greet_count += 1
    return f"Hello, {name}! (greeting #{_greet_count})"


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "8001")),
            stateless_http=True,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
