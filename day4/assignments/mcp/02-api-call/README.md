# Assignment 2 — calling a real API

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` dependency and its own `.venv`, independent of the
root project and the other assignments.

`server.py` exposes one tool, `get_advice()`, which makes a real outbound
HTTPS call to the public [api.adviceslip.com](https://api.adviceslip.com) and
returns a random piece of advice. It uses only Python's standard library
(`urllib`) — no extra dependency to install.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> **cd into this folder first** — every command below assumes your current
> directory is `assignments/mcp/02-api-call` (this folder), not the project
> root:
> ```bash
> cd assignments/mcp/02-api-call
> ```
> (same `cd` command works in Bash/zsh, PowerShell, and cmd.exe)

## 0. Install dependencies

```bash
uv sync
```

## Part A — stdio mode

Claude Code spawns the server as a child process and talks JSON-RPC over
its stdin/stdout.

### 1. Install

**Bash/zsh:**
```bash
amclaude mcp add assignment-02-api-stdio -- uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
amclaude mcp add assignment-02-api-stdio -- uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add assignment-02-api-stdio -- uv run --directory %CD% python server.py
```

### 2. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-02-api-stdio
```

You should see `✔ Connected`.

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

Click **Connect** → **List Tools** → run `get_advice` with no arguments —
each call hits the real API and returns a different piece of advice.

### 4. Remove

```bash
amclaude mcp remove assignment-02-api-stdio
```

## Part B — streamable-http mode (modern protocol)

Here the server runs as a standalone HTTP process and Claude Code connects
over the network instead of spawning it.

### 1. Start the server

Run this in its own terminal (it keeps running until you stop it with `Ctrl+C`) —
remember to `cd assignments/mcp/02-api-call` in that terminal too:

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8002 uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8002"; uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && set MCP_PORT=8002 && uv run --directory %CD% python server.py
```

### 2. Install

```bash
amclaude mcp add --transport http assignment-02-api-http http://127.0.0.1:8002/mcp
```

### 3. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-02-api-http
```

### 4. Explore its tools in the Inspector (devtools)

This forces the Inspector to negotiate the 2026-07-28 modern protocol via
`server/discover` instead of the legacy handshake. Use CLI mode — same
negotiation, prints straight to the terminal:

```bash
# list tools
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8002/mcp --transport http --protocol-era modern --method tools/list

# call the tool (no arguments)
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8002/mcp --transport http --protocol-era modern --method tools/call --tool-name get_advice
```

> Note: use `--protocol-era modern`, not `legacy` — `legacy` expects a
> session id, which this stateless server never issues, and the request will
> hang until it times out.

### 5. Remove

```bash
amclaude mcp remove assignment-02-api-http
```

### 6. Stop the server

Go back to the first terminal and press `Ctrl+C`.

## Validation

### 1. Validate the MCP is installed

```bash
amclaude mcp list
amclaude mcp get assignment-02-api-stdio    # or assignment-02-api-http
```
Look for `✔ Connected`. This only proves the connection exists — not that
Claude has actually called anything yet.

### 2. Validate the MCP has actually been used

#### a) Manual trigger

Explicitly tell Claude to call the tool:

```
Call the get_advice tool and show me the exact raw text it returns.
```

Check two things:
- The transcript shows a tool-call block labeled `mcp__assignment-02-api-stdio__get_advice`
  (or `..._http__get_advice`) right before the reply.
- The advice text is a real, specific sentence (not a generic "here's some
  advice" from the model) — since it comes from a live third-party API, ask
  it to call the tool twice and confirm you get two *different* pieces of
  advice. The model has no way to predict what api.adviceslip.com will return.

#### b) Auto trigger

Don't name the tool — phrase a natural request that only matches the tool's
*description*, and see if Claude decides on its own to call it:

```
I could use some life advice right now, got anything?
```

Check the transcript for the same `mcp__assignment-02-api-stdio__get_advice`
tool-call block appearing — if it's there, Claude recognized the tool from
its description (`"Fetch a random piece of advice from api.adviceslip.com."`)
and invoked it without being told to. If Claude just gives generic advice in
plain text with no tool-call block, it did not auto-trigger.
