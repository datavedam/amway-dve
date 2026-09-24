"""Assignment 6: a self-contained OAuth 2.1 authorization server + MCP
resource server, with every client, login, code, and token persisted in
SQLite instead of memory or environment variables.

Assignment 5 required a human to log in via curl/browser and paste a JWT
into the MCP client by hand. This server implements the full spec instead:
protected-resource metadata, authorization-server metadata, dynamic client
registration (RFC 7591), and the authorization-code + PKCE flow (RFC 6749 +
RFC 7636). That means an MCP client that speaks the spec — including Claude
Code itself — can discover this server, register itself, open your browser
to /login, and exchange the resulting code for tokens with no copy-pasting.
This is the same mechanism behind `/mcp` prompting you to log in for a real
remote MCP server.

One process plays both roles (authorization server AND resource server) for
simplicity; a production deployment often splits them, with the resource
server validating tokens against a separate identity provider instead of
minting them itself.

Uses only the Python standard library (sqlite3, hashlib) plus mcp[cli] — no
extra dependency to install. The database file (oauth.db) is created next to
this script the first time the server runs, and seeded with two demo users.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
Bearer-token auth is an HTTP concept — over stdio there's no network hop, so
this server still runs there (for consistency with the other assignments)
but skips the token check entirely in that mode.
"""

import hashlib
import html
import os
import secrets
import sqlite3
import time
from pathlib import Path

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.mcpserver import MCPServer
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8007"))
ISSUER_URL = f"http://{HOST}:{PORT}"
DB_PATH = Path(__file__).parent / "oauth.db"

PENDING_AUTH_TTL_SECONDS = 600
AUTH_CODE_TTL_SECONDS = 300
ACCESS_TOKEN_TTL_SECONDS = 300
REFRESH_TOKEN_TTL_SECONDS = 86400
PBKDF2_ITERATIONS = 200_000

# username -> (password, scopes). Demo credentials only.
DEMO_USERS = {
    "alice": ("wonderland123", ["reports:read"]),
    "bob": ("builder123", []),
}

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    scopes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS clients (
    client_id TEXT PRIMARY KEY,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pending_authorizations (
    request_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    redirect_uri_provided_explicitly INTEGER NOT NULL,
    code_challenge TEXT NOT NULL,
    state TEXT,
    scopes TEXT NOT NULL,
    resource TEXT,
    expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_codes (
    code TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at REAL NOT NULL,
    code_challenge TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    redirect_uri_provided_explicitly INTEGER NOT NULL,
    resource TEXT,
    subject TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS access_tokens (
    token TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at INTEGER,
    resource TEXT,
    subject TEXT,
    refresh_token TEXT
);
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    scopes TEXT NOT NULL,
    expires_at INTEGER,
    resource TEXT,
    subject TEXT,
    access_token TEXT
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    return conn


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS).hex()


def _create_user(conn: sqlite3.Connection, username: str, password: str, scopes: list[str]) -> None:
    salt = secrets.token_bytes(16)
    conn.execute(
        "INSERT INTO users (username, password_hash, salt, scopes) VALUES (?, ?, ?, ?)",
        (username, _hash_password(password, salt), salt.hex(), " ".join(scopes)),
    )


def _verify_password(username: str, password: str) -> list[str] | None:
    """Return the user's scopes if the password is correct, else None."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT password_hash, salt, scopes FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row is None:
        return None
    password_hash, salt, scopes = row
    candidate = _hash_password(password, bytes.fromhex(salt))
    if not secrets.compare_digest(candidate, password_hash):
        return None
    return scopes.split() if scopes else []


def _seed_users_once() -> None:
    with _connect() as conn:
        if conn.execute("SELECT 1 FROM users LIMIT 1").fetchone():
            return
        for username, (password, scopes) in DEMO_USERS.items():
            _create_user(conn, username, password, scopes)


_seed_users_once()


def _mint_token_pair(client_id: str, scopes: list[str], resource: str | None, subject: str | None) -> OAuthToken:
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    now = time.time()
    with _connect() as conn:
        conn.execute(
            """INSERT INTO access_tokens (token, client_id, scopes, expires_at, resource, subject, refresh_token)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (access_token, client_id, " ".join(scopes), int(now + ACCESS_TOKEN_TTL_SECONDS), resource, subject, refresh_token),
        )
        conn.execute(
            """INSERT INTO refresh_tokens (token, client_id, scopes, expires_at, resource, subject, access_token)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (refresh_token, client_id, " ".join(scopes), int(now + REFRESH_TOKEN_TTL_SECONDS), resource, subject, access_token),
        )
    return OAuthToken(
        access_token=access_token,
        token_type="Bearer",
        expires_in=ACCESS_TOKEN_TTL_SECONDS,
        scope=" ".join(scopes),
        refresh_token=refresh_token,
    )


class SQLiteOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """An OAuthAuthorizationServerProvider that persists every client, code,
    and token in SQLite instead of memory, so registrations and logins
    survive a server restart.
    """

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        with _connect() as conn:
            row = conn.execute("SELECT data FROM clients WHERE client_id = ?", (client_id,)).fetchone()
        return OAuthClientInformationFull.model_validate_json(row[0]) if row else None

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO clients (client_id, data) VALUES (?, ?)",
                (client_info.client_id, client_info.model_dump_json()),
            )

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        # We don't redirect to a third-party IdP — /login below is our own
        # login page. Stash the pending request in SQLite, keyed by a random
        # id, so /login can pick it back up after the user submits the form.
        request_id = secrets.token_urlsafe(16)
        with _connect() as conn:
            conn.execute(
                """INSERT INTO pending_authorizations
                   (request_id, client_id, redirect_uri, redirect_uri_provided_explicitly,
                    code_challenge, state, scopes, resource, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    request_id,
                    client.client_id,
                    str(params.redirect_uri),
                    int(params.redirect_uri_provided_explicitly),
                    params.code_challenge,
                    params.state,
                    " ".join(params.scopes or []),
                    params.resource,
                    time.time() + PENDING_AUTH_TTL_SECONDS,
                ),
            )
        return f"{ISSUER_URL}/login?request_id={request_id}"

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        with _connect() as conn:
            row = conn.execute(
                """SELECT client_id, scopes, expires_at, code_challenge, redirect_uri,
                          redirect_uri_provided_explicitly, resource, subject
                   FROM auth_codes WHERE code = ?""",
                (authorization_code,),
            ).fetchone()
        if row is None:
            return None
        client_id, scopes, expires_at, code_challenge, redirect_uri, explicit, resource, subject = row
        return AuthorizationCode(
            code=authorization_code,
            scopes=scopes.split() if scopes else [],
            expires_at=expires_at,
            client_id=client_id,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
            redirect_uri_provided_explicitly=bool(explicit),
            resource=resource,
            subject=subject,
        )

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        # The framework already checked expiry, redirect_uri, and the PKCE
        # code_verifier before calling this — we just mint tokens and burn
        # the code so it can't be replayed.
        with _connect() as conn:
            conn.execute("DELETE FROM auth_codes WHERE code = ?", (authorization_code.code,))
        return _mint_token_pair(
            client.client_id, authorization_code.scopes, authorization_code.resource, authorization_code.subject
        )

    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> RefreshToken | None:
        with _connect() as conn:
            row = conn.execute(
                "SELECT client_id, scopes, expires_at, resource, subject FROM refresh_tokens WHERE token = ?",
                (refresh_token,),
            ).fetchone()
        if row is None:
            return None
        client_id, scopes, expires_at, resource, subject = row
        return RefreshToken(
            token=refresh_token,
            client_id=client_id,
            scopes=scopes.split() if scopes else [],
            expires_at=expires_at,
            resource=resource,
            subject=subject,
        )

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]
    ) -> OAuthToken:
        # Rotate: the old refresh token (and the access token it was paired
        # with) is single-use, same idea as the authorization code above.
        with _connect() as conn:
            conn.execute("DELETE FROM refresh_tokens WHERE token = ?", (refresh_token.token,))
            conn.execute("DELETE FROM access_tokens WHERE refresh_token = ?", (refresh_token.token,))
        return _mint_token_pair(client.client_id, scopes, refresh_token.resource, refresh_token.subject)

    async def load_access_token(self, token: str) -> AccessToken | None:
        with _connect() as conn:
            row = conn.execute(
                "SELECT client_id, scopes, expires_at, resource, subject FROM access_tokens WHERE token = ?",
                (token,),
            ).fetchone()
        if row is None:
            return None
        client_id, scopes, expires_at, resource, subject = row
        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes.split() if scopes else [],
            expires_at=expires_at,
            resource=resource,
            subject=subject,
        )

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        # Revoke both halves of the pair regardless of which one was handed in.
        with _connect() as conn:
            conn.execute("DELETE FROM access_tokens WHERE token = ? OR refresh_token = ?", (token.token, token.token))
            conn.execute("DELETE FROM refresh_tokens WHERE token = ? OR access_token = ?", (token.token, token.token))


def _load_pending(request_id: str) -> dict | None:
    if not request_id:
        return None
    with _connect() as conn:
        row = conn.execute(
            """SELECT client_id, redirect_uri, redirect_uri_provided_explicitly, code_challenge,
                      state, scopes, resource, expires_at
               FROM pending_authorizations WHERE request_id = ?""",
            (request_id,),
        ).fetchone()
    if row is None:
        return None
    client_id, redirect_uri, explicit, code_challenge, state, scopes, resource, expires_at = row
    if expires_at < time.time():
        return None
    return {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "redirect_uri_provided_explicitly": explicit,
        "code_challenge": code_challenge,
        "state": state,
        "scopes": scopes.split() if scopes else [],
        "resource": resource,
    }


LOGIN_FORM = """<!doctype html>
<title>Assignment 6 login</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(160deg, #fff4e5 0%, #ffe3c2 45%, #ffcf94 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
  }}
  .card {{
    background: #ffffff;
    padding: 44px 40px 36px;
    border-radius: 18px;
    box-shadow: 0 20px 45px rgba(219, 118, 10, 0.18), 0 2px 6px rgba(0, 0, 0, 0.04);
    width: 340px;
    position: relative;
    overflow: hidden;
  }}
  .card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 6px;
    background: linear-gradient(90deg, #ff9d2e, #f4691e);
  }}
  .badge {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff9d2e, #f4691e);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    font-weight: 700;
    margin: 0 auto 18px;
    box-shadow: 0 6px 16px rgba(244, 105, 30, 0.35);
  }}
  h1 {{
    margin: 0 0 4px;
    color: #2b2b2b;
    font-size: 22px;
    text-align: center;
  }}
  .subtitle {{
    margin: 0 0 26px;
    color: #9a9a9a;
    font-size: 13px;
    text-align: center;
  }}
  label {{
    display: block;
    margin-bottom: 16px;
    color: #6b6b6b;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  input {{
    display: block;
    width: 100%;
    margin-top: 8px;
    padding: 12px 14px;
    border: 1.5px solid #e8e2da;
    border-radius: 8px;
    font-size: 14px;
    color: #333;
    background: #fbfaf8;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }}
  input:focus {{
    outline: none;
    border-color: #f4691e;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(244, 105, 30, 0.12);
  }}
  button {{
    width: 100%;
    padding: 13px;
    margin-top: 10px;
    background: linear-gradient(135deg, #ff9d2e, #f4691e);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.02em;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(244, 105, 30, 0.3);
    transition: transform 0.1s ease, box-shadow 0.15s ease;
  }}
  button:hover {{
    box-shadow: 0 10px 22px rgba(244, 105, 30, 0.4);
    transform: translateY(-1px);
  }}
  button:active {{
    transform: translateY(0);
    box-shadow: 0 4px 10px rgba(244, 105, 30, 0.3);
  }}
  .error {{
    background: #fdecea;
    color: #c0392b;
    border: 1px solid #f5c6c0;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    margin-bottom: 18px;
  }}
  .demo {{
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid #f0ece5;
    font-size: 12px;
    color: #a5a5a5;
    text-align: center;
    line-height: 1.6;
  }}
  code {{
    background: #fff0e0;
    color: #b85c0f;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
  }}
</style>
<div class="card">
  <div class="badge">6</div>
  <h1>Welcome back</h1>
  <p class="subtitle">Sign in to continue to Assignment 6</p>
  {error}
  <form method="post" action="/login">
    <input type="hidden" name="request_id" value="{request_id}">
    <label>Username <input name="username" autocomplete="username"></label>
    <label>Password <input name="password" type="password" autocomplete="current-password"></label>
    <button type="submit">Log in</button>
  </form>
  <div class="demo">
    Demo users<br>
    <code>alice / wonderland123</code> &middot; has report access<br>
    <code>bob / builder123</code> &middot; no report access
  </div>
</div>
"""


def _render_login(request_id: str, error: str | None = None) -> HTMLResponse:
    error_html = f"<div class='error'>{html.escape(error)}</div>" if error else ""
    return HTMLResponse(LOGIN_FORM.format(request_id=html.escape(request_id), error=error_html))


provider = SQLiteOAuthProvider()

mcp = MCPServer(
    "assignment-06-oauth-login",
    auth_server_provider=provider,
    auth=AuthSettings(
        issuer_url=ISSUER_URL,
        resource_server_url=f"{ISSUER_URL}/mcp",
        client_registration_options=ClientRegistrationOptions(
            enabled=True,
            valid_scopes=["reports:read"],
            default_scopes=[],
        ),
        revocation_options=RevocationOptions(enabled=True),
        # Unlike assignments 4/5, we mint tokens ourselves and set `resource`
        # on every one (see _mint_token_pair callers), so we can safely ask
        # the framework to enforce the audience check.
        validate_token_resource=True,
    ),
)


@mcp.custom_route("/login", methods=["GET", "POST"])
async def login(request: Request) -> Response:
    if request.method == "GET":
        request_id = request.query_params.get("request_id", "")
        if _load_pending(request_id) is None:
            return HTMLResponse("unknown or expired authorization request", status_code=400)
        return _render_login(request_id)

    form = await request.form()
    request_id = str(form.get("request_id", ""))
    username = str(form.get("username", ""))
    password = str(form.get("password", ""))

    pending = _load_pending(request_id)
    if pending is None:
        return HTMLResponse("unknown or expired authorization request", status_code=400)

    user_scopes = _verify_password(username, password)
    if user_scopes is None:
        return _render_login(request_id, error="invalid username or password")

    # Grant whatever the client requested, narrowed to what this user
    # actually has; an unscoped request grants everything the user has.
    granted_scopes = [s for s in pending["scopes"] if s in user_scopes] if pending["scopes"] else user_scopes

    code = secrets.token_urlsafe(32)
    with _connect() as conn:
        conn.execute(
            """INSERT INTO auth_codes
               (code, client_id, scopes, expires_at, code_challenge, redirect_uri,
                redirect_uri_provided_explicitly, resource, subject)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                code,
                pending["client_id"],
                " ".join(granted_scopes),
                time.time() + AUTH_CODE_TTL_SECONDS,
                pending["code_challenge"],
                pending["redirect_uri"],
                int(pending["redirect_uri_provided_explicitly"]),
                pending["resource"],
                username,
            ),
        )
        conn.execute("DELETE FROM pending_authorizations WHERE request_id = ?", (request_id,))

    redirect_url = construct_redirect_uri(pending["redirect_uri"], code=code, state=pending["state"])
    return RedirectResponse(url=redirect_url, status_code=302)


@mcp.tool()
def whoami() -> str:
    """Return the identity, scopes, and expiry of the authenticated caller."""
    access_token = get_access_token()
    if access_token is None:
        return "no authenticated caller (running over stdio, where auth is skipped)"
    expires_in = int(access_token.expires_at - time.time()) if access_token.expires_at else None
    return f"sub={access_token.subject} scopes={access_token.scopes} expires_in={expires_in}s"


@mcp.tool()
def get_confidential_report() -> str:
    """Return a confidential report. Requires the reports:read scope."""
    access_token = get_access_token()
    scopes = access_token.scopes if access_token else []
    if "reports:read" not in scopes:
        caller = access_token.subject if access_token else "(stdio, unauthenticated)"
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
