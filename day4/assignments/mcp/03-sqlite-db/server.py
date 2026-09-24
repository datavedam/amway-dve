"""Assignment 3: tools backed by a SQLite database (a tiny todo list).

Uses only the Python standard library (sqlite3) — no extra dependency to
install. The database file (tasks.db) is created next to this script the
first time a tool runs.

Run directly (this folder is its own uv project, see pyproject.toml —
cd into this folder first, then):
    uv run --directory $PWD python server.py

Set MCP_TRANSPORT=streamable-http to serve over HTTP instead of stdio.
"""

import os
import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("assignment-03-sqlite-db")

DB_PATH = Path(__file__).parent / "tasks.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    return conn


@mcp.tool()
def add_task(title: str) -> str:
    """Add a new task and return its id."""
    with _connect() as conn:
        cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        return f"added task #{cursor.lastrowid}: {title}"


@mcp.tool()
def list_tasks() -> str:
    """List all tasks with their id and done status."""
    with _connect() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    if not rows:
        return "no tasks yet"
    return "\n".join(f"[{'x' if done else ' '}] #{task_id} {title}" for task_id, title, done in rows)


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as done by id."""
    with _connect() as conn:
        cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            return f"no task with id {task_id}"
    return f"marked task #{task_id} done"


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "8003")),
            stateless_http=True,
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
