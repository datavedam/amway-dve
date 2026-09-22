# Day 2 — Hands-on: Modes (Manual, Auto-accept, Plan)

Claude Code can run the exact same request three different ways,
depending on **mode** — a session-wide setting for how much it asks
you before acting, completely separate from Skills or hooks. This
session has you do one task under all three modes, in the same
session, and read what's actually different each time rather than
guessing from the names.

Switch modes by pressing **Shift+Tab** at the prompt — it cycles
through the modes in order. The current mode is always shown at the
bottom of the terminal; check it before every step below rather than
assuming the last switch worked.

## Step 1 — Baseline: Manual mode
Manual (the default) mode is what you've been using so far — Claude
asks before every action that changes something. Confirm you're in it
by checking the bottom of the terminal, then copy-paste:
> Create a file called `notes/manual-test.md` with the line "created
> in manual mode".

**Observe:** a permission prompt appears before the file is written.
Approve it. Ask Claude:
> What mode are you in right now, and what does that mode mean?
Write down its answer — you'll compare it to Steps 2 and 3.

## Step 2 — Switch to Auto-accept edits mode
Press **Shift+Tab** once. Check the bottom of the terminal — it should
now say something like "auto-accept edits on". Copy-paste:
> Create a file called `notes/auto-test.md` with the line "created in
> auto-accept mode".

**Observe:** did a permission prompt appear this time, or did the file
just get created? Now push it further — ask for something with more
blast radius:
> Create three files, `notes/a.md`, `notes/b.md`, and `notes/c.md`,
> each containing a different one-line joke.

**Decide:** read all three files afterward. Auto-accept mode skipped
the prompts — was that actually fine here, or can you already see how
this mode would be risky for an edit you *hadn't* actually wanted?
Write down one kind of request you would NOT want to run in this mode.

## Step 3 — Switch to Plan mode
Press **Shift+Tab** again to reach Plan mode. Check the bottom of the
terminal to confirm. Copy-paste this — deliberately pick something
with several steps:
> Reorganize the `notes/` folder: merge `a.md`, `b.md`, and `c.md`
> into one file called `notes/jokes.md`, then delete the three
> originals.

**Observe:** Claude should investigate and describe a plan *without
touching any files yet* — no edits happen, and no permission prompts
for file writes appear, because in Plan mode those tools are disabled.
Instead, at the end, you should see a plan presented for your approval
before anything runs.

## Step 4 — Reject the plan and make it revise
When the plan appears, **reject it** and give a reason:
> Don't delete the originals — keep `a.md`, `b.md`, and `c.md` as they
> are, and just add `notes/jokes.md` as a new combined copy.

**Observe:** does Claude produce a *new* plan reflecting your feedback,
still without having touched any files? This is the point of Plan
mode — you can redirect it as many times as you want at zero cost,
since nothing has actually happened to your files yet.

## Step 5 — Approve and confirm it matches the plan
Once the revised plan matches what you asked for, approve it.
**Observe:** now compare what actually happened on disk to the plan
text you just approved:
```
ls notes/
```
Confirm `a.md`, `b.md`, `c.md` still exist *and* `jokes.md` was added
containing all three jokes — i.e., Claude executed exactly the
approved plan, not something improvised afterward.

## Step 6 — Same task, three modes: decide which one you'd actually use
Ask Claude:
> Summarize, in one line each, what Manual, Auto-accept, and Plan mode
> each let through without asking, and what they always stop for.

Then, based on your own experience in Steps 1–5 (not just the
summary), fill in this table with **your own judgment**, not a
guess — pick a real kind of task for each row:

| Mode | A task you'd feel safe running in this mode | A task you would NOT run in this mode |
|---|---|---|
| Manual | | |
| Auto-accept | | |
| Plan | | |

## Cleanup
Once you're done, delete the scratch files this exercise created:
> Delete the entire `notes/` folder you created during this exercise.

Confirm with `ls notes/` (or `ls` if the folder is gone) that it's
actually removed before moving on.
