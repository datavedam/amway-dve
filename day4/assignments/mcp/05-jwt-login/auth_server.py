"""Assignment 5: a tiny local login server that issues JWTs.

This stands in for a real identity provider (Atlassian's id.atlassian.com,
Okta, Auth0, ...): you log in here with a username and password, it hands
back a signed JWT, and you paste that JWT into server.py's MCP server as a
bearer token. There's no OAuth redirect dance — just "log in, get a token,
use the token" — the smallest version of that architecture that still does a
real login and a real signature check.

Uses only the Python standard library plus PyJWT (already a transitive
dependency of mcp[cli], declared directly here too).

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python auth_server.py

Set AUTH_PORT to change the port (default 8006).
Set JWT_SECRET to change the signing secret — must match server.py's.
Set TOKEN_TTL_SECONDS to change how long issued tokens stay valid (default 300).
"""

import html
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import jwt

HOST = os.environ.get("AUTH_HOST", "127.0.0.1")
PORT = int(os.environ.get("AUTH_PORT", "8006"))
JWT_SECRET = os.environ.get("JWT_SECRET", "demo-jwt-signing-secret-please-change-me")
ISSUER = f"http://{HOST}:{PORT}"
TOKEN_TTL_SECONDS = int(os.environ.get("TOKEN_TTL_SECONDS", "300"))

# username -> (password, scopes). Demo credentials only.
USERS = {
    "alice": ("wonderland123", ["reports:read"]),
    "bob": ("builder123", []),
}

LOGIN_FORM = """<!doctype html>
<title>Assignment 5 login</title>
<h1>Log in</h1>
<form method="post" action="/login">
  <label>Username <input name="username"></label><br>
  <label>Password <input name="password" type="password"></label><br>
  <button type="submit">Log in</button>
</form>
<p>Demo users: <code>alice / wonderland123</code> (has report access),
<code>bob / builder123</code> (no report access).</p>
"""


def _issue_token(username: str, scopes: list[str]) -> dict:
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "sub": username,
        "scopes": scopes,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
    }
    token = jwt.encode(claims, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "expires_in": TOKEN_TTL_SECONDS, "scopes": scopes}


def _result_page(payload: dict) -> str:
    token = html.escape(payload["access_token"])
    return f"""<!doctype html>
<title>Logged in</title>
<h1>Logged in</h1>
<p>Your access token (valid {payload["expires_in"]}s, scopes {payload["scopes"]}):</p>
<textarea rows="6" cols="80" readonly>{token}</textarea>
<p>Paste it into the MCP client as:<br><code>Authorization: Bearer {token}</code></p>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/login":
            self._send(200, LOGIN_FORM.encode(), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        if self.path != "/login":
            self._send(404, b"not found", "text/plain")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")
        wants_html = "application/json" not in content_type

        if wants_html:
            data = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
        else:
            data = json.loads(raw or b"{}")
        username = data.get("username", "")
        password = data.get("password", "")

        record = USERS.get(username)
        if record is None or password != record[0]:
            self._send(401, b"invalid username or password", "text/plain")
            return

        payload = _issue_token(username, record[1])
        if wants_html:
            self._send(200, _result_page(payload).encode(), "text/html; charset=utf-8")
        else:
            self._send(200, json.dumps(payload).encode(), "application/json")

    def log_message(self, format: str, *args) -> None:
        pass


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Auth server listening on http://{HOST}:{PORT} — open http://{HOST}:{PORT}/login in a browser")
    server.serve_forever()


if __name__ == "__main__":
    main()
