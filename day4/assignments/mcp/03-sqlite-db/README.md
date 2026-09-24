# Assignment 3 — a SQLite-backed tool

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` dependency and its own `.venv`, independent of the
root project and the other assignments.

`server.py` is a tiny todo list backed by a real SQLite database
(`tasks.db`, created automatically next to the script on first use). It
exposes three tools: `add_task(title)`, `list_tasks()`,
`complete_task(task_id)`. Uses only Python's standard library (`sqlite3`) —
no extra dependency to install.

Because the data lives in a file, tasks you add persist across restarts —
that's the point of this exercise: unlike the in-memory `greet` counter from
assignment 1, this state survives the server process dying.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> **cd into this folder first** — every command below assumes your current
> directory is `assignments/mcp/03-sqlite-db` (this folder), not the project
> root:
> ```bash
> cd assignments/mcp/03-sqlite-db
> ```
> (same `cd` command works in Bash/zsh, PowerShell, and cmd.exe)

## 0. Install dependencies

```bash
uv sync
```

## Part A — stdio mode

### 1. Install

**Bash/zsh:**
```bash
amclaude mcp add assignment-03-sqlite-stdio -- uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
amclaude mcp add assignment-03-sqlite-stdio -- uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add assignment-03-sqlite-stdio -- uv run --directory %CD% python server.py
```

### 2. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-03-sqlite-stdio
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

Try, in order: `add_task` with `title="buy milk"`, `add_task` again with a
different title, then `list_tasks` (both show up), then `complete_task` with
the first task's id, then `list_tasks` again (it now shows `[x]` for that one).

### 4. Remove

```bash
amclaude mcp remove assignment-03-sqlite-stdio
```

## Part B — streamable-http mode (modern protocol)

### 1. Start the server

Run this in its own terminal (it keeps running until you stop it with `Ctrl+C`) —
remember to `cd assignments/mcp/03-sqlite-db` in that terminal too:

**Bash/zsh:**
```bash
MCP_TRANSPORT=streamable-http MCP_PORT=8003 uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
$env:MCP_TRANSPORT="streamable-http"; $env:MCP_PORT="8003"; uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
set MCP_TRANSPORT=streamable-http && set MCP_PORT=8003 && uv run --directory %CD% python server.py
```

### 2. Install

```bash
amclaude mcp add --transport http assignment-03-sqlite-http http://127.0.0.1:8003/mcp
```

### 3. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-03-sqlite-http
```

### 4. Explore its tools in the Inspector (devtools)

This forces the Inspector to negotiate the 2026-07-28 modern protocol via
`server/discover` instead of the legacy handshake. Use CLI mode — same
negotiation, prints straight to the terminal:

```bash
# list tools
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8003/mcp --transport http --protocol-era modern --method tools/list

# add a task
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8003/mcp --transport http --protocol-era modern --method tools/call --tool-name add_task --tool-arg title="buy milk"

# list tasks
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8003/mcp --transport http --protocol-era modern --method tools/call --tool-name list_tasks
```

> Note: use `--protocol-era modern`, not `legacy` — `legacy` expects a
> session id, which this stateless server never issues, and the request will
> hang until it times out.

Note this hits the same `tasks.db` file as Part A — the stdio and
streamable-http servers are two different ways to reach the same underlying
storage, not two different databases.

### 5. Remove

```bash
amclaude mcp remove assignment-03-sqlite-http
```

### 6. Stop the server

Go back to the first terminal and press `Ctrl+C`.

## Validation

### 1. Validate the MCP is installed

```bash
amclaude mcp list
amclaude mcp get assignment-03-sqlite-stdio    # or assignment-03-sqlite-http
```
Look for `✔ Connected`. This only proves the connection exists — not that
Claude has actually called anything yet.

### 2. Validate the MCP has actually been used

#### a) Manual trigger

Explicitly tell Claude to call the tools:

```
Call add_task with title "validate-manual-trigger", then call list_tasks and
show me the raw output.
```

Check two things:
- The transcript shows tool-call blocks labeled `mcp__assignment-03-sqlite-stdio__add_task`
  and `..._list_tasks` (or `..._http__...`).
- The exact string `"validate-manual-trigger"` appears in the `list_tasks`
  output. That value only exists because it was written into (and read back
  from) the real `tasks.db` file — the model has no other way to produce it.

#### b) Auto trigger

Don't name any tool — phrase a natural request that only matches the tools'
*descriptions*, and see if Claude decides on its own to call them:

```
Add "validate-auto-trigger" to my todo list, then tell me everything that's
currently on it.
```

Check the transcript for `mcp__assignment-03-sqlite-stdio__add_task` and
`..._list_tasks` tool-call blocks appearing, and confirm
`"validate-auto-trigger"` shows up in the response — if both are present,
Claude recognized the tools from their descriptions (`"Add a new task..."`,
`"List all tasks..."`) and invoked them without being told to by name.

## Reset the database

If you want to start the todo list over from empty (run this from this
assignment's own directory, same as everything else above):

**Bash/zsh:**
```bash
rm -f tasks.db
```

**PowerShell:**
```powershell
Remove-Item -Force tasks.db -ErrorAction SilentlyContinue
```

**Command Prompt (cmd.exe):**
```bat
del /q tasks.db 2>nul
```
