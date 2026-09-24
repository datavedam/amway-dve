"""Assignment 4: an MCP server that requires authentication.

Bearer-token auth is an HTTP concept — it only applies to the
streamable-http transport below. Over stdio, Claude Code spawns the server
itself as a local child process, so there is no network hop and nothing to
authenticate; this server still runs over stdio (for consistency with the
other assignments) but skips the token check entirely in that mode.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
Set MCP_API_TOKEN to override the demo bearer token (default below).
"""

import os
import secrets

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer

API_TOKEN = os.environ.get("MCP_API_TOKEN", "demo-secret-token")
HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8004"))


class StaticTokenVerifier(TokenVerifier):
    """Checks the bearer token against a single shared secret.

    A real server would verify a JWT or call out to an identity provider —
    this is a stand-in that's enough to prove the auth middleware runs.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        if not secrets.compare_digest(token, API_TOKEN):
            return None
        return AccessToken(token=token, client_id="assignment-04-client", scopes=["reports:read"])


mcp = MCPServer(
    "assignment-04-authenticated-api",
    token_verifier=StaticTokenVerifier(),
    auth=AuthSettings(
        # We're only using this server as a resource server that checks a
        # static token, not running a real OAuth authorization server — but
        # the issuer_url still has to resolve, since clients probe it during
        # discovery. Point it at ourselves (a loopback address always
        # resolves) rather than an unresolvable placeholder.
        issuer_url=f"http://{HOST}:{PORT}",
        resource_server_url=f"http://{HOST}:{PORT}/mcp",
        # Our verifier doesn't set AccessToken.resource, so it has nothing
        # to check the audience against — validating it would reject every
        # token.
        validate_token_resource=False,
    ),
)


@mcp.tool()
def whoami() -> str:
    """Return the identity and scopes of the authenticated caller."""
    access_token = get_access_token()
    if access_token is None:
        return "no authenticated caller (running over stdio, where auth is skipped)"
    return f"client_id={access_token.client_id} scopes={access_token.scopes}"


@mcp.tool()
def get_confidential_report() -> str:
    """Return a confidential report that only an authenticated caller may read."""
    return "Q3 confidential report: revenue up 12%, headcount steady, launch on track for October."


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=HOST,
            port=PORT,
            stateless_http=True,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
