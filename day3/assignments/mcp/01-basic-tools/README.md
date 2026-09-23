# Assignment 1 — basic tools

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` dependency and its own `.venv`, independent of the
root project and the other assignments.

`server.py` exposes three plain tools, no external dependencies:
`echo(text)`, `sum(a, b)`, `greet(name)`.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> Run every command in this guide from the **project root** (the top-level
> directory containing `README.md`, not this assignment folder) — the
> commands build the assignment's path from `$PWD`/`%CD%`.

## Part A — stdio mode

Claude Code spawns the server as a child process and talks JSON-RPC over
its stdin/stdout.

### 1. Install

**Bash/zsh:**
```bash
claude mcp add assignment-01-basic-stdio -- uv run --directory $PWD/assignments/mcp/01-basic-tools python server.py
```

**PowerShell:**
```powershell
claude mcp add assignment-01-basic-stdio -- uv run --directory $PWD/assignments/mcp/01-basic-tools python server.py
```

**Command Prompt (cmd.exe):**
```bat
claude mcp add assignment-01-basic-stdio -- uv run --directory %CD%/assignments/mcp/01-basic-tools python server.py
```

### 2. Verify it's installed

```bash
claude mcp list
claude mcp get assignment-01-basic-stdio
```

You should see `✔ Connected`.

### 3. Explore its tools in the Inspector (devtools)

**Bash/zsh or PowerShell:**
```bash
npx --yes @modelcontextprotocol/inspector uv run --directory $PWD/assignments/mcp/01-basic-tools python server.py
```

**Command Prompt (cmd.exe):**
```bat
npx --yes @modelcontextprotocol/inspector uv run --directory %CD%/assignments/mcp/01-basic-tools python server.py
```

This opens a browser UI. Click **Connect**, then **List Tools** — you'll see
`echo`, `sum`, `greet` with their schemas, and can call each one by hand.

### 4. Remove

```bash
claude mcp remove assignment-01-basic-stdio
```

## Part B — streamable-http mode (modern protocol)

Here the server runs as a standalone HTTP process and Claude Code connects
over the network instead of spawning it.

### 1. Start the server

Run this in its own terminal (it keeps running until you stop it with `Ctrl+C`):

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8001 uv run --directory $PWD/assignments/mcp/01-basic-tools python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8001"; uv run --directory $PWD/assignments/mcp/01-basic-tools python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && set MCP_PORT=8001 && uv run --directory %CD%/assignments/mcp/01-basic-tools python server.py
```

### 2. Install

In a second terminal:

```bash
claude mcp add --transport http assignment-01-basic-http http://127.0.0.1:8001/mcp
```

### 3. Verify it's installed

```bash
claude mcp list
claude mcp get assignment-01-basic-http
```

### 4. Explore its tools in the Inspector (devtools)

This forces the Inspector to negotiate the 2026-07-28 modern protocol via
`server/discover` instead of the legacy handshake — the connection panel
will show `2026-07-28`:

```bash
npx --yes @modelcontextprotocol/inspector --web --transport http --server-url http://127.0.0.1:8001/mcp --protocol-era modern
```

Prefer no browser? Use CLI mode instead — same negotiation, prints straight
to the terminal:

```bash
# list tools
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8001/mcp --transport http --protocol-era modern --method tools/list

# call a tool
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8001/mcp --transport http --protocol-era modern --method tools/call --tool-name echo --tool-arg text=hi
```

> Note: use `--protocol-era modern`, not `legacy` — `legacy` expects a
> session id, which this stateless server never issues, and the request will
> hang until it times out.

### 5. Remove

```bash
claude mcp remove assignment-01-basic-http
```

### 6. Stop the server

Go back to the first terminal and press `Ctrl+C`.

## Validation

### 1. Validate the MCP is installed

```bash
claude mcp list
claude mcp get assignment-01-basic-stdio    # or assignment-01-basic-http
```
Look for `✔ Connected`. This only proves the connection exists — not that
Claude has actually called anything yet.

### 2. Validate the MCP has actually been used

#### a) Manual trigger

Explicitly tell Claude to call the tool, twice, in the same conversation:

```
Call the greet tool with name "validation-test", then call it again with the
same name "validation-test", and show me the raw output of both calls.
```

Check two things:
- The transcript shows a tool-call block labeled `mcp__assignment-01-basic-stdio__greet`
  (or `..._http__greet`) right before each reply.
- The counter actually incremented — first call returns `greeting #1`, second
  returns `greeting #2`. Claude cannot fabricate a shared incrementing counter
  it has no access to, so this is real proof the tool executed both times.

#### b) Auto trigger

This time, don't name the tool at all — phrase a natural request that only
matches the tool's *description*, and see if Claude decides on its own to
call it:

```
I need to greet my colleague Priya, and I want to keep count of how many
times you've greeted her so far today.
```

Check the transcript for the same `mcp__assignment-01-basic-stdio__greet`
tool-call block appearing — if it's there, Claude recognized the tool from
its description (`"Greet someone by name, tracking how many greetings have
been sent."`) and invoked it without being told to. If Claude just replies in
plain text with no tool-call block, it did not auto-trigger — try rephrasing
to lean more on the "tracking a count" part of the tool's description.

## Reset the greeting count

The `_greet_count` counter lives in the server process's memory — stop and
restart the server (`Ctrl+C` then re-run the start command) to reset it to 0.
