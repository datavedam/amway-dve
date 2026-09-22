# Day 2 — Hands-on: Tools (built-in, MCP, and Skills)

A **tool** is a specific action Claude is allowed to take — reading a
file, running a shell command, editing a file. Not every "tool" you can
imagine creating is the same kind of thing under the hood. This session
walks through how to actually see Claude's tool list, why no single
command dumps it, and the three different ways you can add a new
capability — each with very different effort and a different claim to
being a "real" tool.

## Step 1 — See what /context tells you (and what it doesn't)
Run:
```
/context
```
Find the "System tools" and "System tools (deferred)" lines. Read them
closely — notice they give you a **token cost**, not a list of names.
Write down: based on `/context` alone, could you name a single tool
Claude has access to?

## Step 2 — Ask directly for the full list
Now ask Claude:
> What tools do you have access to right now?

Read the answer. Compare it to Step 1 — this is the only reliable way to
get actual names; `/context` only tells you the aggregate size.

## Step 3 — Understand deferred tools
Ask Claude:
> What is a deferred tool?

Read the explanation: a deferred tool's *name* is known, but its full
parameter schema isn't loaded — Claude can't call it until it fetches
the schema on demand (via a search-style tool). Write down, in your own
words, why a system would bother deferring tools instead of just loading
everything upfront. (Hint: think about what `/context` showed you in
Step 1 about token cost.)

## Step 4 — Built-in vs. MCP
Ask Claude:
> Is your Read or Bash tool coming from an MCP server?

Read the distinction it draws:
- **Built-in tools** (`Read`, `Bash`, `Edit`, `Write`, ...) — compiled
  into the Claude Code CLI itself. Always present. No setup, no config.
- **MCP tools** — served by an external process you explicitly connect
  (`claude mcp add` or a `.mcp.json` config). Only present if that
  server is running and connected for this session.

Run `/mcp` yourself and read what it shows — if nothing is connected,
that's expected; it confirms MCP tools are opt-in infrastructure, not
part of the default set.

## Step 5 — Try to create a "tool" at each level
Pick a trivial goal: a `hello` action that prints "hello amway". Try it
two ways, in the same session, and read what's actually created each
time.

**5a. As a Skill** (fastest):
> Create a Claude Code skill called `hello`. When I type `/hello`,
> print "hello amway".

Trigger `/hello` once created. This reuses tools Claude already has
(most likely just its own text output) — a skill is *saved
instructions*, not a new tool.

**5b. As a local script Claude calls via an existing tool**:
> Write a script scripts/hello.sh that prints "hello amway", make it
> executable.

Ask Claude to run it. Notice which tool Claude uses to execute your new
script — the script is new, the tool running it (`Bash`) isn't.


**5c. Ask about a genuine built-in tool**:
> Can I add a new built-in tool to Claude Code myself, the way Read or
> Bash exist?

Read the answer. This is the one level you cannot reach from a session
— built-in tools ship inside the Claude Code binary itself, controlled
by Anthropic, not by project config, skills, or MCP servers.
