"""Assignment 5: an MCP server authenticated via JWTs from auth_server.py.

Start auth_server.py first (it issues tokens), then this server (it
verifies them) — both must agree on JWT_SECRET. Log in via auth_server.py's
/login endpoint to get a token, then pass it to this server as
Authorization: Bearer <token>.

Bearer-token auth is an HTTP concept — it only applies to the
streamable-http transport below. Over stdio there's no network hop, so this
server still runs there (for consistency with the other assignments) but
skips the token check entirely in that mode.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
"""

import os
import time

import jwt
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer

HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8005"))
JWT_SECRET = os.environ.get("JWT_SECRET", "demo-jwt-signing-secret-please-change-me")
AUTH_HOST = os.environ.get("AUTH_HOST", "127.0.0.1")
AUTH_PORT = int(os.environ.get("AUTH_PORT", "8006"))
ISSUER_URL = f"http://{AUTH_HOST}:{AUTH_PORT}"


class JWTVerifier(TokenVerifier):
    """Verifies tokens issued by auth_server.py's /login endpoint.

    Checks the signature (proves it came from auth_server.py, not a
    tampered copy), the issuer, and the expiry — all three come free with
    jwt.decode(); a static shared-secret check (assignment 4) gets none of
    them.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"],
                issuer=ISSUER_URL,
                options={"require": ["exp", "sub"]},
            )
        except jwt.PyJWTError:
            return None
        return AccessToken(
            token=token,
            client_id=claims["sub"],
            scopes=claims.get("scopes", []),
            expires_at=claims["exp"],
        )


mcp = MCPServer(
    "assignment-05-jwt-login",
    token_verifier=JWTVerifier(),
    auth=AuthSettings(
        # Unlike assignment 4's placeholder, this issuer_url is real:
        # auth_server.py actually implements the login and token-issuing
        # side that this URL points at.
        issuer_url=ISSUER_URL,
        resource_server_url=f"http://{HOST}:{PORT}/mcp",
        validate_token_resource=False,
    ),
)


@mcp.tool()
def whoami() -> str:
    """Return the identity, scopes, and expiry of the authenticated caller."""
    access_token = get_access_token()
    if access_token is None:
        return "no authenticated caller (running over stdio, where auth is skipped)"
    expires_in = int(access_token.expires_at - time.time()) if access_token.expires_at else None
    return f"sub={access_token.client_id} scopes={access_token.scopes} expires_in={expires_in}s"


@mcp.tool()
def get_confidential_report() -> str:
    """Return a confidential report. Requires the reports:read scope."""
    access_token = get_access_token()
    scopes = access_token.scopes if access_token else []
    if "reports:read" not in scopes:
        caller = access_token.client_id if access_token else "(stdio, unauthenticated)"
        return f"forbidden: {caller} lacks the reports:read scope"
    return "Q3 confidential report: revenue up 12%, headcount steady, launch on track for October."


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host=HOST, port=PORT, stateless_http=True)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
