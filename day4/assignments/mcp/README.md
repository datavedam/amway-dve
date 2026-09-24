# MCP assignments

Hands-on exercises for running an MCP server two ways — **stdio** (a spawned
child process, used by Claude Code/Desktop) and **streamable-http** (a
standalone HTTP server, the 2026-07-28 "modern" stateless protocol) — and
inspecting its tools with the MCP Inspector devtools.

Every command below is copy-paste ready. Nothing needs editing — other than
picking the block for your shell where more than one is shown. Steps 0 and 1
below run from the project root; each assignment's own README (linked under
"The five use cases") then has you `cd` into that assignment's folder and
run everything from there instead.

## 0. Check your environment

You already have Claude Code. This checks the rest (`python`/`python3`, `uv`,
`pip`, `npx` for the Inspector):

**Bash/zsh:**
```bash
bash assignments/mcp/check-environment.sh
```

**PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File assignments/mcp/check-environment.ps1
```

**Command Prompt (cmd.exe):**
```bat
assignments\mcp\check-environment.cmd
```

If anything is missing, the script prints what and a link/command to install it.
`claude` and `npx` need to be installed separately (Claude Code and Node.js);
`uv` you can install directly:

**macOS / Linux (Bash/zsh):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Windows (Command Prompt):**
```bat
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uv` bundles its own Python, so once it's installed you don't need to install
Python separately — `uv run` will fetch an interpreter automatically.

## 1. Install the mcp package

Each assignment folder (`01-basic-tools/`, `02-api-call/`, `03-sqlite-db/`,
`04-authenticated-api/`, `05-jwt-login/`) is its own standalone `uv` project
with its own `pyproject.toml` and its own `.venv` — they don't share
dependencies with each other or with the root project. Each one declares
the `mcp` Python package (the MCP SDK the servers are built on, including
the `mcp[cli]` extra the Inspector needs) as a dependency; `05-jwt-login/`
additionally declares `pyjwt`.

You don't run this from here — `cd` into whichever assignment you're doing
(step 2 below) and its own README walks you through `uv sync` as its first
step. You don't even need to run it manually: every `uv run` command in
those guides syncs dependencies automatically the first time it's invoked.

## The five use cases

`cd` into one of these and follow its own README — every command in that
guide assumes you're sitting inside that folder, not the project root:

| # | Folder | What it teaches |
|---|--------|------------------|
| 1 | [`01-basic-tools/`](01-basic-tools/README.md) | The basics: `echo`, `sum`, `greet` — three plain tools, no external dependencies. |
| 2 | [`02-api-call/`](02-api-call/README.md) | A tool that makes a real outbound HTTP call to a public API. |
| 3 | [`03-sqlite-db/`](03-sqlite-db/README.md) | Tools backed by a SQLite database — a tiny todo list that persists between calls. |
| 4 | [`04-authenticated-api/`](04-authenticated-api/README.md) | An MCP server that requires a bearer token — requests without one are rejected before any tool runs. |
| 5 | [`05-jwt-login/`](05-jwt-login/README.md) | A local login server that issues signed, expiring JWTs, and an MCP server that verifies them and enforces per-tool scopes — the shape of real "log in, then use the token" auth (e.g. Atlassian's remote MCP), without needing real third-party credentials. |

Do them in order — each one only adds one new idea on top of the last.

## What each assignment covers

Every assignment's guide walks through, for **both** stdio and
streamable-http:

1. **Install** — register the server with Claude Code (`amclaude mcp add`).
2. **Verify it's installed** — `amclaude mcp list` / `amclaude mcp get`.
3. **Explore its tools in the Inspector (devtools)** — see the tool list,
   schemas, and call them by hand in a browser/CLI, independent of Claude Code.
4. **Remove** — `amclaude mcp remove`, so you end each exercise with a clean slate.
5. **Validate** — confirm the server is installed, then confirm it was
   actually *used* — once by telling Claude to call the tool directly (manual
   trigger), and once by asking a natural question that never names the tool,
   to see if Claude decides to call it on its own (auto trigger).
