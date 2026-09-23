# MCP assignments

Hands-on exercises for running an MCP server two ways — **stdio** (a spawned
child process, used by Claude Code/Desktop) and **streamable-http** (a
standalone HTTP server, the 2026-07-28 "modern" stateless protocol) — and
inspecting its tools with the MCP Inspector devtools.

Every command below is copy-paste ready. Nothing needs editing — other than
picking the Bash/zsh or PowerShell version where both are shown. Run
everything from the project root (the directory containing `pyproject.toml`).

## 0. Check your environment

You already have Claude Code. This checks the rest (`python`/`python3`, `uv`,
`pip`, `npx` for the Inspector):

**Bash/zsh:**
```bash
bash assignments/check-environment.sh
```

**PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File assignments/check-environment.ps1
```

**Command Prompt (cmd.exe):**
```bat
assignments\check-environment.cmd
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

Each assignment folder (`01-basic-tools/`, `02-api-call/`, `03-sqlite-db/`)
is its own standalone `uv` project with its own `pyproject.toml` and its own
`.venv` — they don't share dependencies with each other or with the root
project. Each one declares the `mcp` Python package (the MCP SDK the servers
are built on, including the `mcp[cli]` extra the Inspector needs) as its
only dependency.

To install it for a given assignment, `cd` into that folder and sync — same
command for every shell:

```bash
cd assignments/01-basic-tools   # or 02-api-call / 03-sqlite-db
uv sync
cd ../..                        # back to the project root
```

You'll see output like `Resolved N packages` / `Installed N packages`. You
don't need to run `pip install mcp` yourself, and you don't even need to run
this manually before each assignment — every `uv run --directory ...`
command in this guide points at that assignment's own `pyproject.toml` and
syncs dependencies automatically the first time it's invoked. Running it
once up front just makes that first `uv run` in Part A faster and lets you
confirm the install succeeded before you start.

## The three use cases

| # | Folder | What it teaches |
|---|--------|------------------|
| 1 | [`01-basic-tools/`](01-basic-tools/README.md) | The basics: `echo`, `sum`, `greet` — three plain tools, no external dependencies. |
| 2 | [`02-api-call/`](02-api-call/README.md) | A tool that makes a real outbound HTTP call to a public API. |
| 3 | [`03-sqlite-db/`](03-sqlite-db/README.md) | Tools backed by a SQLite database — a tiny todo list that persists between calls. |

Do them in order — each one only adds one new idea on top of the last.

## What each assignment covers

Every assignment's guide walks through, for **both** stdio and
streamable-http:

1. **Install** — register the server with Claude Code (`claude mcp add`).
2. **Verify it's installed** — `claude mcp list` / `claude mcp get`.
3. **Explore its tools in the Inspector (devtools)** — see the tool list,
   schemas, and call them by hand in a browser/CLI, independent of Claude Code.
4. **Remove** — `claude mcp remove`, so you end each exercise with a clean slate.
5. **Validate** — confirm the server is installed, then confirm it was
   actually *used* — once by telling Claude to call the tool directly (manual
   trigger), and once by asking a natural question that never names the tool,
   to see if Claude decides to call it on its own (auto trigger).
