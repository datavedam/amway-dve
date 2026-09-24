# Assignment 5 — login with a username/password, then use the JWT it gives you

This folder is its own standalone `uv` project (see `pyproject.toml`) — it
has its own `mcp[cli]` + `pyjwt` dependencies and its own `.venv`,
independent of the root project and the other assignments.

Assignment 4 used one shared static secret for every caller — anyone who
knew the string could authenticate as the same generic identity. This
assignment is closer to how a real system like Atlassian's remote MCP
server works, just with a local, from-scratch identity provider standing in
for `id.atlassian.com`:

1. **`auth_server.py`** — a tiny login server. You send it a username and
   password (a browser form at `/login`, or a JSON POST for `curl`/scripts).
   If they match one of the two demo users, it signs a JWT containing your
   identity (`sub`) and permissions (`scopes`) and hands it back.
2. **`server.py`** — the actual MCP server. It never sees a password — it
   only ever checks the *signature* on a JWT you present as a bearer token,
   using the secret it shares with `auth_server.py`. It also enforces
   scopes: `whoami()` works for anyone with a valid token, but
   `get_confidential_report()` checks for the `reports:read` scope itself
   and refuses callers who don't have it.

Two demo users, defined in `auth_server.py`:

| Username | Password | Scopes |
|----------|----------|--------|
| `alice` | `wonderland123` | `reports:read` |
| `bob` | `builder123` | *(none)* |

Tokens expire after 5 minutes (`TOKEN_TTL_SECONDS`, default `300`) — a static
secret never expires, a JWT does, and you'll see that below.

**This is still HTTP-only auth**, same reasoning as assignment 4 — see
Part A below.

Every command below is copy-paste ready — nothing needs editing, other than
picking the block for your shell where more than one is shown.

> **cd into this folder first** — every command below assumes your current
> directory is `assignments/mcp/05-jwt-login` (this folder), not the project
> root:
> ```bash
> cd assignments/mcp/05-jwt-login
> ```
> (same `cd` command works in Bash/zsh, PowerShell, and cmd.exe)

## 0. Install dependencies

```bash
uv sync
```

## Part A — stdio mode (no auth applies)

Same reasoning as assignment 4: over stdio there's no network hop, so
`server.py` runs there too but skips the token check entirely.

### 1. Install

**Bash/zsh:**
```bash
amclaude mcp add assignment-05-jwt-stdio -- uv run --directory $PWD python server.py
```

**PowerShell:**
```powershell
amclaude mcp add assignment-05-jwt-stdio -- uv run --directory $PWD python server.py
```

**Command Prompt (cmd.exe):**
```bat
amclaude mcp add assignment-05-jwt-stdio -- uv run --directory %CD% python server.py
```

### 2. Verify it's installed

```bash
amclaude mcp list
amclaude mcp get assignment-05-jwt-stdio
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
succeeds with no token at all and returns `no authenticated caller (running
over stdio, where auth is skipped)`. Now run `get_confidential_report` — it
also succeeds as a tool call, but returns `forbidden: (stdio,
unauthenticated) lacks the reports:read scope`, since there's no token to
read a scope from.

### 4. Remove

```bash
amclaude mcp remove assignment-05-jwt-stdio
```

## Part B — streamable-http mode (login required)

### 1. Start the login server

Run this in its own terminal (it keeps running until you stop it with
`Ctrl+C`) — remember to `cd assignments/mcp/05-jwt-login` in that terminal
too:

**Bash/zsh:**
```bash
uv run --directory $PWD python auth_server.py
```

**PowerShell:**
```powershell
uv run --directory $PWD python auth_server.py
```

**Command Prompt (cmd.exe):**
```bat
uv run --directory %CD% python auth_server.py
```

It listens on `http://127.0.0.1:8006`.

### 2. Log in and get a JWT

**Bash/zsh — capture the token straight into a variable** (verified against
a live server; every later step that uses `$ALICE_TOKEN`/`$BOB_TOKEN` builds
on this, so nothing below needs manual copy-pasting):
```bash
ALICE_TOKEN=$(curl -s -X POST http://127.0.0.1:8006/login -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"wonderland123\"}" | uv run --directory $PWD python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "$ALICE_TOKEN"
```
```bash
BOB_TOKEN=$(curl -s -X POST http://127.0.0.1:8006/login -H "Content-Type: application/json" -d "{\"username\":\"bob\",\"password\":\"builder123\"}" | uv run --directory $PWD python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "$BOB_TOKEN"
```

**PowerShell and Command Prompt (cmd.exe) — use the browser instead.** Open
`http://127.0.0.1:8006/login`, log in as `alice` / `wonderland123`, and copy
the JWT shown on the result page; repeat as `bob` / `builder123`. Everywhere
below that shows `$ALICE_TOKEN` or `$BOB_TOKEN`, paste the matching token in
its place — these two shells' quoting rules make a one-line variable capture
too easy to get subtly wrong to hand you as copy-paste-ready, so a manual
copy is the safer instruction here.

Try a wrong password too, to see it actually checks (Bash/zsh and cmd.exe;
`curl` on PowerShell is aliased to `Invoke-WebRequest` and won't take these
flags):
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8006/login -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"wrong\"}"
```
You should see `401`.

### 3. Start the MCP server

In a second terminal (also `cd assignments/mcp/05-jwt-login` there):

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

It listens on `http://127.0.0.1:8005` and only accepts tokens signed by the
login server from step 1 — they share `JWT_SECRET`.

### 4. Confirm it actually verifies the token

**Bash/zsh and Command Prompt (cmd.exe):**
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8005/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```
No token → `401`.

Now with Alice's token:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8005/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer $ALICE_TOKEN" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```
→ `200`.

Now tamper with it — append any extra character and resend:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8005/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer ${ALICE_TOKEN}x" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```
The signature no longer matches → `401`. This is the thing a static shared
secret (assignment 4) can't give you: proof the token wasn't altered after
the login server signed it.

(On PowerShell/cmd.exe, substitute the token you copied from the browser in
step 2 wherever `$ALICE_TOKEN` appears.)

### 5. Install in Claude Code (with the JWT as the header)

**Bash/zsh:**
```bash
amclaude mcp add --transport http assignment-05-jwt-http http://127.0.0.1:8005/mcp --header "Authorization: Bearer $ALICE_TOKEN"
```

**PowerShell and Command Prompt (cmd.exe):** substitute the token you copied
from the browser:
```bash
amclaude mcp add --transport http assignment-05-jwt-http http://127.0.0.1:8005/mcp --header "Authorization: Bearer <ALICE_TOKEN>"
```

```bash
amclaude mcp list
amclaude mcp get assignment-05-jwt-http
```
Look for `✔ Connected`.

Without a header, `amclaude mcp get` reports `✘ Failed to connect` with
`Dynamic Client Registration rejected (HTTP 404): not found` — same idea as
assignment 4 (Claude Code falls back to OAuth client registration when it
has no header to send), though the exact wording differs because here the
404 comes from `auth_server.py`'s own plain-text 404 handler rather than a
framework's.

### 6. Explore its tools in the Inspector (devtools)

```bash
# whoami as alice
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8005/mcp --transport http --protocol-era modern --header "Authorization: Bearer $ALICE_TOKEN" --method tools/call --tool-name whoami

# get_confidential_report as alice — she has reports:read
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8005/mcp --transport http --protocol-era modern --header "Authorization: Bearer $ALICE_TOKEN" --method tools/call --tool-name get_confidential_report

# get_confidential_report as bob — he doesn't have reports:read
npx --yes @modelcontextprotocol/inspector --cli --server-url http://127.0.0.1:8005/mcp --transport http --protocol-era modern --header "Authorization: Bearer $BOB_TOKEN" --method tools/call --tool-name get_confidential_report
```

(PowerShell/cmd.exe: substitute the tokens you copied from the browser.)

Bob's call to `get_confidential_report` succeeds as a tool call (no
transport-level error) but returns `forbidden: bob lacks the reports:read
scope` — this server checks scopes per tool, inside the tool's own code, not
as an all-or-nothing gate on the whole connection. That's deliberate: on a
server with many tools, different tools often need different scopes, so a
single connection-wide scope check wouldn't be enough anyway.

> Note: use `--protocol-era modern`, not `legacy` — `legacy` expects a
> session id, which this stateless server never issues, and the request will
> hang until it times out.

### 7. Remove

```bash
amclaude mcp remove assignment-05-jwt-http
```

### 8. Stop the servers

Go back to both terminals (login server and MCP server) and press `Ctrl+C`
in each.

## Validation

### 1. Validate the MCP is installed

```bash
amclaude mcp list
amclaude mcp get assignment-05-jwt-http
```
Look for `✔ Connected`.

### 2. Validate the MCP has actually been used

#### a) Manual trigger

```
Call the whoami tool, then call get_confidential_report, and show me the raw
output of both.
```

Check that the transcript shows `mcp__assignment-05-jwt-http__whoami` and
`..._get_confidential_report` tool-call blocks, and that `whoami`'s output
names the exact `sub` (`alice`) and `scopes` (`['reports:read']`) that were
in the JWT you logged in with — the model has no way to know that identity
except by the server having decoded a token you supplied.

#### b) Auto trigger

```
Who am I authenticated as on that MCP server, and can you pull the
confidential report while you're at it?
```

Check the same two tool-call blocks appear without the tools being named
directly.

#### c) Prove expiry is real

Wait 5 minutes (`TOKEN_TTL_SECONDS`) after logging in, then retry step 4's
curl command with the same token. It now returns `401` even though nothing
else changed — the signature is still valid, only the `exp` claim has
passed. To see this sooner, start the login server with a short TTL:

**Bash/zsh:**
```bash
TOKEN_TTL_SECONDS=10 uv run --directory $PWD python auth_server.py
```

**PowerShell:**
```powershell
$env:TOKEN_TTL_SECONDS="10"; uv run --directory $PWD python auth_server.py
```

**Command Prompt (cmd.exe):**
```bat
set TOKEN_TTL_SECONDS=10 && uv run --directory %CD% python auth_server.py
```

Log in, wait 10 seconds, then try the token — `401`.

#### d) Prove scope enforcement is real

Install a second Claude Code connection with Bob's token:
```bash
amclaude mcp add --transport http assignment-05-jwt-bob http://127.0.0.1:8005/mcp --header "Authorization: Bearer $BOB_TOKEN"
```
Then ask Claude to pull the confidential report through that connection. It
authenticates fine (bob is a real, valid caller) but the report tool itself
refuses him — a different failure mode than assignment 4's all-or-nothing
401, and worth noticing the difference.

## Change the secret or credentials

`JWT_SECRET` must be identical between `auth_server.py` and `server.py` —
set it before starting *both*. Add or change users by editing the `USERS`
dict at the top of `auth_server.py` (`username: (password, scopes)`).
