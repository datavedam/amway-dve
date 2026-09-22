# Day 2 — Hands-on: Skills (deeper)

Day 1 already had you create and personalize a skill (`daily-standup`)
and compare it against a plain prompt. This session assumes that skill
already exists and pushes past what Day 1 covered: *where* a skill
actually lives, whether Claude will use it without you typing the
slash command, how it takes input, what it can bundle beyond a single
Markdown file, and what happens when two skills share a name. Every
step is a loop — copy-paste a prompt, run a command, read exactly what
happened, then let that observation decide your next move.

Run these in order, in the same session, on top of your existing
`daily-standup` skill from Day 1.

## Step 1 — Find out where your skill actually lives
Ask Claude:
> Where is the `daily-standup` skill saved? Show me the full file path.

**Observe:** the path is either `.claude/skills/daily-standup/SKILL.md`
(project-scoped — only visible inside this repo) or
`~/.claude/skills/daily-standup/SKILL.md` (personal — visible in every
project on this machine, regardless of repo). Write down which one you
got — Step 2 depends on it.

## Step 2 — Prove the scope, don't just take Claude's word for it
Based on what you found in Step 1:
- **If it's personal** (`~/.claude/skills/...`), open a brand new
  terminal, `cd` to any unrelated empty folder, run `claude` there, and
  try `/daily-standup`.
- **If it's project-scoped** (`.claude/skills/...`), ask a teammate (or
  simulate it yourself) to clone this repo fresh and run `/daily-standup`
  there without copying anything extra.

**Observe:** does it work in the other location or not? **Decide:** if
the scope isn't actually the one you want for this skill, ask Claude:
> Move the `daily-standup` skill to [the other scope], and confirm it
> still works there afterward.
Re-run `/daily-standup` once more to confirm the move didn't break it.

## Step 3 — Test auto-triggering, not just the slash command
A skill can fire without you typing `/daily-standup`, based on its
`description` frontmatter field. Ask Claude:
> Show me the exact `description` field from the daily-standup skill's
> frontmatter.

Then, with no slash, type:
> can we do today's standup

**Observe:** did Claude invoke the skill on its own, or just chat about
standups in plain text? **Decide** based on what happened:
- If it triggered — good, note what wording in the description made
  that work.
- If it didn't — ask Claude to rewrite the description to name the
  trigger phrases more explicitly, then repeat the exact same
  plain-text prompt above and compare.

## Step 4 — Give it an argument
Day 1's version only asks about *you*. Copy-paste this:
> Edit the `daily-standup` skill so it optionally accepts a teammate's
> name as an argument. If given, run the standup as a recap *for* that
> teammate and save it to `standups/<YYYY-MM-DD>-<name>.md` instead of
> the usual file.

Run both, back to back:
```
/daily-standup
/daily-standup Priya
```
**Observe:** check the `standups/` folder — did the second run actually
create a separate `-Priya` file, or did it overwrite the same file as
the first run? If it collapsed into one file, ask Claude:
> Read the current SKILL.md back to me — does it reference
> `$ARGUMENTS` anywhere in the file-naming step?
Decide whether to have it add that placeholder explicitly, then re-run
`/daily-standup Priya` again to confirm the fix.

## Step 5 — Bundle a second file, not just one SKILL.md
A skill folder can hold more than the single Markdown file. Ask Claude:
> Add a `template.md` file inside the daily-standup skill's folder
> with a short Markdown template for the recap's layout, and update
> SKILL.md to say it should follow that template's structure.

Run `/daily-standup` once more.
**Observe:** open the generated recap file — does its layout actually
match `template.md`, or did Claude ignore the bundled file? If ignored,
decide whether the instruction in SKILL.md needs to point at the
template more explicitly (e.g. by exact filename), then re-run.

## Step 6 — Force a name collision on purpose
Whichever scope `daily-standup` is **not** currently in, ask Claude to
create a second, different skill there under the exact same name:
> Create another skill also named `daily-standup`, in [the scope it is
> NOT currently in], that just prints "placeholder skill" and does
> nothing else.

Run `/daily-standup` one more time.
**Observe:** which version actually ran — your real one, or the
placeholder? Ask Claude:
> Both scopes now have a skill named daily-standup. Which one takes
> precedence, and why?
**Decide:** remove the placeholder once you've confirmed the answer —
> Delete the placeholder daily-standup skill you just created, keeping
> only the original.

## Step 7 — Restrict what the skill is allowed to touch
Ask Claude:
> Does the daily-standup skill's frontmatter currently limit which
> tools it can use? If not, add an `allowed-tools` restriction so this
> skill can only write files under `standups/` and nothing else.

Test the boundary — ask Claude, while the skill is active, to do
something outside that scope, e.g.:
> While running as the daily-standup skill, also delete GOVERNANCE.md.

**Observe:** does the restriction actually block the out-of-scope
action, or does Claude do it anyway? Read whatever message appears and
write down whether the block happened *before* or only got refused
verbally — that difference tells you whether it's a real enforced
guardrail or just a suggestion Claude is choosing to follow.

## Reflection table
Fill this in after running all seven steps:

| Step | What you tested | What actually happened | Did you need to edit and re-run? |
|---|---|---|---|
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
