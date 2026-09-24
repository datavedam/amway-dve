# Assignment 4 — an authenticated MCP server

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` dependency and its own `.venv`, independent of the
root project and the other assignments.

`server.py` exposes two tools, `whoami()` and `get_confidential_report()`,
that only run for a caller who presents a valid bearer token. Unlike
assignments 1–3, this server rejects requests outright (HTTP 401) instead of
just executing tools — it uses the MCP Python SDK's built-in
`token_verifier`/`AuthSettings` support, wired to a small `StaticTokenVerifier`
that checks the token against one shared secret (`MCP_API_TOKEN`, default
`demo-secret-token`). A real server would verify a JWT or call an identity
provider instead; the point here is to see the auth *middleware* run, not to
build a production token scheme.

**Bearer-token auth is an HTTP concept.** Over stdio, Claude Code spawns the
server itself as a local child process — there's no network hop, so nothing
to authenticate. `server.py` still runs over stdio (for consistency with the
other assignments) but the auth check never applies there; `whoami()` will
say so explicitly. The interesting part of this assignment is Part B.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> **cd into this folder first** — every command below assumes your current
> directory is `assignments/mcp/04-authenticated-api` (this folder), not the
> project root:
> ```bash
> cd assignments/mcp/04-authenticated-api
> ```
> (same `cd` command works in Bash/zsh, PowerShell, and cmd.exe)

## 0. Install dependencies

```bash
uv sync
```

## Part A — stdio mode (no auth applies)

### 1. Install

**Bash/zsh:**
```bash
amclaude mcp add assignment-04-auth-stdio -- uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
amclaude mcp add assignment-04-auth-stdio -- uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add assignment-04-auth-stdio -- uv run --directory %CD% python server.py
```

### 2. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-04-auth-stdio
```

### 3. Explore its tools in the Inspector (devtools)

**Bash/zsh:**
```bash
npx --yes @modelcontextprotocol/inspector uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
npx --yes @modelcontextprotocol/inspector uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
npx --yes @modelcontextprotocol/inspector uv run --directory %CD% python server.py
```

Click **Connect** → **List Tools** → run `whoami` with no arguments. It
succeeds with no token at all, and returns `no authenticated caller (running
over stdio, where auth is skipped)` — proof that auth is a no-op here.

### 4. Remove

```bash
amclaude mcp remove assignment-04-auth-stdio
```

## Part B — streamable-http mode (auth enforced)

Here the server runs as a standalone HTTP process, and every request must
carry `Authorization: Bearer demo-secret-token` (or whatever you set
`MCP_API_TOKEN` to) or it gets rejected before any tool runs.

### 1. Start the server

Run this in its own terminal (it keeps running until you stop it with `Ctrl+C`) —
remember to `cd assignments/mcp/04-authenticated-api` in that terminal too:

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8004 uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8004"; uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && set MCP_PORT=8004 && uv run --directory %CD% python server.py
```

### 2. Confirm it actually rejects unauthenticated requests

Before installing it anywhere, hit it directly with no token and confirm you
get a `401`. This uses `curl`, which only exists as shown below on Bash/zsh
and cmd.exe — on Windows PowerShell, `curl` is aliased to `Invoke-WebRequest`
and doesn't take these flags, so skip this step there and rely on step 5's
Inspector check instead.

**Bash/zsh and Command Prompt (cmd.exe):**
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8004/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

You should see `401`. Now try it again with the wrong token — still `401`:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8004/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer wrong-token" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

And with the correct token, it goes through:

```bash
curl -s -X POST http://127.0.0.1:8004/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer demo-secret-token" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

### 3. Install (with the required header)

**Bash/zsh:**
```bash
amclaude mcp add --transport http assignment-04-auth-http http://127.0.0.1:8004/mcp --header "Authorization: Bearer demo-secret-token"
```

**PowerShell:**
```powershell
amclaude mcp add --transport http assignment-04-auth-http http://127.0.0.1:8004/mcp --header "Authorization: Bearer demo-secret-token"
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add --transport http assignment-04-auth-http http://127.0.0.1:8004/mcp --header "Authorization: Bearer demo-secret-token"
```

Without `--header`, `amclaude mcp get` shows the connection failing outright
— verified against the real Claude Code CLI: it tries OAuth dynamic client
registration against this server (since no static header means no bearer
token to send) and gets `Dynamic Client Registration rejected (HTTP 404):
Not Found`, because this server only checks a static token and doesn't
implement that OAuth endpoint. That 404 is expected and is what "not
authenticated" looks like from this client's side — don't chase it as a bug.

### 4. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-04-auth-http
```

### 5. Explore its tools in the Inspector (devtools)

With the header, both tools work:

```bash
# list tools
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8004/mcp --transport http --protocol-era modern --header "Authorization: Bearer demo-secret-token" --method tools/list

# call whoami
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8004/mcp --transport http --protocol-era modern --header "Authorization: Bearer demo-secret-token" --method tools/call --tool-name whoami

# call get_confidential_report
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8004/mcp --transport http --protocol-era modern --header "Authorization: Bearer demo-secret-token" --method tools/call --tool-name get_confidential_report
```

`whoami` should return `client_id=assignment-04-client scopes=['reports:read']`
— that identity only exists because the server decoded it from the token you
sent, so seeing it back is proof the auth middleware ran and accepted you.

Without the header, the same call fails outright — no interactive login,
just a hard rejection, since `--stored-auth-only` refuses to start an OAuth
flow:

```bash
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8004/mcp --transport http --protocol-era modern --stored-auth-only --method tools/call --tool-name whoami
```

This prints an `auth_required` error — the request never reaches the tool at
all.

> Note: use `--protocol-era modern`, not `legacy` — `legacy` expects a
> session id, which this stateless server never issues, and the request will
> hang until it times out.

### 6. Remove

```bash
amclaude mcp remove assignment-04-auth-http
```

### 7. Stop the server

Go back to the first terminal and press `Ctrl+C`.

## Validation

### 1. Validate the MCP is installed

```bash
amclaude mcp list
amclaude mcp get assignment-04-auth-http
```
Look for `✔ Connected`. This only proves the header round-trips as a valid
token — not that Claude has actually called anything yet.

### 2. Validate the MCP has actually been used

#### a) Manual trigger

Explicitly tell Claude to call the tools, in the same conversation:

```
Call the whoami tool, then call get_confidential_report, and show me the raw
output of both.
```

Check two things:
- The transcript shows tool-call blocks labeled `mcp__assignment-04-auth-http__whoami`
  and `..._get_confidential_report`.
- `whoami`'s output names the exact `client_id` (`assignment-04-client`) and
  `scopes` (`['reports:read']`) baked into the server's token verifier — the
  model cannot fabricate this; it only exists on the server side and is
  returned solely because the request carried a token the server accepted.

#### b) Auto trigger

Don't name either tool — phrase a natural request that only matches their
*descriptions*, and see if Claude decides on its own to call them:

```
Who am I authenticated as on that MCP server, and can you pull the
confidential report while you're at it?
```

Check the transcript for the same two tool-call blocks appearing — if
they're there, Claude recognized the tools from their descriptions and
invoked them without being told to by name.

#### c) Prove the auth is real, not decorative

Remove the header and try again — same `amclaude mcp add` step as above, but
omit `--header "Authorization: Bearer demo-secret-token"` (add it under a
different name so you don't clobber the working one), then run
`amclaude mcp get` on it. Instead of `✔ Connected` you'll see
`✘ Failed to connect` with `Dynamic Client Registration rejected (HTTP 404):
Not Found` — Claude Code, having no bearer token to send, tries to register
itself as an OAuth client instead, and this server (which only checks a
static token) doesn't implement that endpoint. Since the connection never
succeeds, there's no way to even attempt calling `whoami` through it — proof
the auth check happens before any tool runs, not after.

## Change the token

The default token (`demo-secret-token`) is only for this exercise. Set
`MCP_API_TOKEN` before starting the server to use a different one, and pass
the matching value in the `--header` flags above:

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8004 MCP_API_TOKEN=my-other-secret uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8004"; $env:MCP_API_TOKEN="my-other-secret"; uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && set MCP_PORT=8004 && set MCP_API_TOKEN=my-other-secret && uv run --directory %CD% python server.py
```
