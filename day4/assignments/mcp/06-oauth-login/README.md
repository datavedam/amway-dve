# Assignment 6 — the full OAuth dance, backed by SQLite

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` dependency and its own `.venv`, independent of the
root project and the other assignments.

Assignments 4 and 5 both hit a wall: connecting without a manually-supplied
`--header` failed with `Dynamic Client Registration rejected (HTTP 404): Not
Found`, because those servers only checked a static token/JWT and never
implemented the actual OAuth endpoints a real client tries first. This
assignment implements those endpoints for real, so the same automatic
attempt *succeeds* instead — this is the mechanism behind `/mcp` prompting
you to log in for a real remote MCP server (Atlassian, Linear, etc.), with
no token to copy-paste by hand.

Unlike assignment 5's two processes (`auth_server.py` for login,
`server.py` for the MCP tools), **there's only one process here** — one
`server.py`, one terminal, one port. It plays both roles at once:

1. **Authorization server** — publishes `/.well-known/oauth-authorization-server`,
   accepts dynamic client registration at `/register` (RFC 7591), serves a
   real login page at `/login`, and issues tokens at `/token` via the
   authorization-code + PKCE flow (RFC 6749 + RFC 7636).
2. **Resource server** — the actual MCP server. It publishes
   `/.well-known/oauth-protected-resource/mcp` (RFC 9728) so a client knows
   where to send you to log in, and only lets `whoami()` /
   `get_confidential_report()` run for a caller with a token it issued.

**Everything is persisted in SQLite** (`oauth.db`, created next to this
script on first run): the two demo users (with hashed, salted passwords —
never plaintext), every dynamically-registered client, in-flight
authorization requests, one-time authorization codes, and issued access +
refresh tokens. Restart the server and none of that is lost; delete
`oauth.db` to reset the whole demo from scratch. You can inspect it live:

```bash
sqlite3 oauth.db "select username, scopes from users"
sqlite3 oauth.db "select client_id from clients"
sqlite3 oauth.db "select token, client_id, subject, expires_at from access_tokens"
```

Two demo users, seeded into SQLite the first time the server runs:

| Username | Password | Scopes |
|----------|----------|--------|
| `alice` | `wonderland123` | `reports:read` |
| `bob` | `builder123` | *(none)* |

Access tokens expire after 5 minutes, same as assignment 5 — but unlike
assignment 5, this server also implements **refresh tokens**, so a
spec-compliant client renews silently instead of forcing you to log in
again every 5 minutes.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> **cd into this folder first** — every command below assumes your current
> directory is `assignments/mcp/06-oauth-login` (this folder), not the
> project root:
> ```bash
> cd assignments/mcp/06-oauth-login
> ```
> (same `cd` command works in Bash/zsh, PowerShell, and cmd.exe)

## 0. Install dependencies

```bash
uv sync
```

## Part A — stdio mode (no auth applies)

Same reasoning as assignments 4/5: over stdio there's no network hop, so
`server.py` runs there too but skips the token check entirely.

### 1. Install

**Bash/zsh:**
```bash
amclaude mcp add assignment-06-oauth-stdio -- uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
amclaude mcp add assignment-06-oauth-stdio -- uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add assignment-06-oauth-stdio -- uv run --directory %CD% python server.py
```

### 2. Explore its tools in the Inspector (devtools)

**Bash/zsh:**
```bash
npx --yes @modelcontextprotocol/inspector uv run --directory $PWD python server.py
```

Click **Connect** → **List Tools** → run `whoami` with no arguments. It
succeeds with no token at all and returns `no authenticated caller (running
over stdio, where auth is skipped)`.

### 3. Remove

```bash
amclaude mcp remove assignment-06-oauth-stdio
```

## Part B — streamable-http mode (the full interactive flow)

> **There is no separate `auth_server.py` here, unlike assignment 5.**
> Assignment 5 split the login server and the MCP server into two processes
> you started in two terminals. This assignment's `server.py` plays both
> roles in one process — the same `MCPServer` object publishes the OAuth
> authorization-server endpoints (`/register`, `/authorize`, `/login`,
> `/token`) *and* the MCP resource-server endpoint (`/mcp`). One terminal,
> one process, one port (`8007`).

### 1. Start the combined authorization server + MCP server

Run this in its own terminal (it keeps running until you stop it with
`Ctrl+C`) — remember to `cd assignments/mcp/06-oauth-login` in that terminal
too:

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && uv run --directory %CD% python server.py
```

It listens on `http://127.0.0.1:8007`.

### 2. Confirm the discovery endpoints are real (unlike assignments 4/5)

```bash
curl -s http://127.0.0.1:8007/.well-known/oauth-authorization-server
echo
curl -s http://127.0.0.1:8007/.well-known/oauth-protected-resource/mcp
```

Both return real JSON metadata (`authorization_endpoint`, `token_endpoint`,
`registration_endpoint`, and the resource pointing back at this issuer) —
this is what a spec-compliant client reads before it does anything else.

Now hit the MCP endpoint with no token:

```bash
curl -s -i -X POST http://127.0.0.1:8007/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

You get `401`, and — unlike assignments 4/5 — a `WWW-Authenticate` header
pointing at the protected-resource metadata above. That's the breadcrumb a
real client follows to find `/register` and `/authorize`.

### 3. Install — no `--header` needed this time

**Bash/zsh:**
```bash
amclaude mcp add --transport http assignment-06-oauth-http http://127.0.0.1:8007/mcp
```

**PowerShell:**
```powershell
amclaude mcp add --transport http assignment-06-oauth-http http://127.0.0.1:8007/mcp
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add --transport http assignment-06-oauth-http http://127.0.0.1:8007/mcp
```

### 4. Trigger the login

```bash
amclaude mcp get assignment-06-oauth-http
```

Where assignments 4/5 gave you `Dynamic Client Registration rejected (HTTP
404)`, this server implements `/register`, so Claude Code registers itself
successfully and should open your browser straight to this server's
`/login` page (or print the URL to open manually, depending on your Claude
Code version). Log in as `alice` / `wonderland123`. You'll land back on a
"connected" state — no token was ever visible to you or typed anywhere; it
was exchanged over the `/token` endpoint behind the scenes using the PKCE
code Claude Code generated when it built the `/authorize` URL.

If you'd rather see every hop explicitly before trusting the one-line
`amclaude` flow, the **Manual walkthrough** section below drives the same
five requests with `curl`, so you can watch the authorization code and
tokens change hands.

### 5. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-06-oauth-http
```

Look for `✔ Connected`.

### 6. Explore its tools

Ask Claude, in a session with this MCP server installed:

```
Call the whoami tool, then call get_confidential_report, and show me the raw
output of both.
```

`whoami` should return `sub=alice scopes=['reports:read'] expires_in=<n>s` —
that identity only exists because the server decoded a token it minted for
*this* login, not something the model could fabricate.

### 7. Prove refresh tokens actually work

Wait past the 5-minute access-token expiry, then ask Claude to call
`whoami` again. Unlike assignment 5 (hard `401`, forced re-login), a
spec-compliant client silently exchanges the refresh token for a new access
token behind the scenes — the tool call just works, with no new browser
prompt. You can watch this happen at the SQLite level: the old row in
`access_tokens` is gone and a new one appears with a later `expires_at`,
each time a refresh happens (`sqlite3 oauth.db "select token, expires_at
from access_tokens"`).

### 8. Prove scope enforcement is real

Repeat step 3's install under a different name and log in as `bob` /
`builder123` instead of `alice`. Ask Claude to pull the confidential report
through that connection — it authenticates fine (bob is a real, valid
caller) but the tool itself refuses him: `forbidden: bob lacks the
reports:read scope`. Scopes are enforced per-tool, inside the tool's own
code, not as an all-or-nothing gate on the connection.

### 9. Remove

```bash
amclaude mcp remove assignment-06-oauth-http
```

### 10. Stop the server

Go back to the first terminal and press `Ctrl+C`.

## Manual walkthrough (curl, no Claude Code)

This traces the exact five requests a spec-compliant client makes, so you
can see the authorization code and tokens change hands instead of trusting
a browser popup.

**1. Register a client (RFC 7591):**
```bash
curl -s -X POST http://127.0.0.1:8007/register -H "Content-Type: application/json" -d "{\"redirect_uris\":[\"http://127.0.0.1:9999/callback\"],\"token_endpoint_auth_method\":\"none\",\"grant_types\":[\"authorization_code\",\"refresh_token\"],\"response_types\":[\"code\"]}"
```
Copy the `client_id` from the response into the commands below.

**2. Build a PKCE pair and open `/authorize` in your browser:**
```bash
python3 -c "import base64,hashlib,secrets; v=secrets.token_urlsafe(32); c=base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).decode().rstrip('='); print('verifier:',v); print('challenge:',c)"
```
Then open, with your own `client_id` and `code_challenge` substituted:
```
http://127.0.0.1:8007/authorize?client_id=<CLIENT_ID>&redirect_uri=http://127.0.0.1:9999/callback&response_type=code&code_challenge=<CHALLENGE>&code_challenge_method=S256&state=demo
```
The server redirects your browser to `/login?request_id=...` — log in as
`alice` / `wonderland123`. Your browser then tries to redirect to
`http://127.0.0.1:9999/callback?code=...&state=demo`, which will fail to
load (nothing is listening there) — that's expected; just copy the `code`
out of the browser's address bar.

**3. Exchange the code for tokens:**
```bash
curl -s -X POST http://127.0.0.1:8007/token -d "grant_type=authorization_code&code=<CODE>&redirect_uri=http://127.0.0.1:9999/callback&client_id=<CLIENT_ID>&code_verifier=<VERIFIER>"
```

**4. Call a tool with the access token:**
```bash
curl -s -X POST http://127.0.0.1:8007/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer <ACCESS_TOKEN>" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"whoami\",\"arguments\":{}}}"
```

**5. Refresh instead of logging in again:**
```bash
curl -s -X POST http://127.0.0.1:8007/token -d "grant_type=refresh_token&refresh_token=<REFRESH_TOKEN>&client_id=<CLIENT_ID>"
```
Try step 5 twice with the *same* refresh token — the second call fails with
`invalid_grant: refresh token does not exist`, because refresh tokens
rotate (single use), same as the authorization code from step 2.

## Change the users or scopes

Edit the `DEMO_USERS` dict at the top of `server.py`, then delete `oauth.db`
so it reseeds on next run (existing rows are never overwritten in place).
