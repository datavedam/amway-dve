# Day 1 – Setup & Assignments

No prior experience with Git or Claude is needed. Just follow the steps in order, run each command, and **read what shows up on your screen** — most answers are already there.

---

## Step 1: Download the Training Files

You don't need to know Git — just copy-paste the commands below.

1. **Check if Git is already installed.**
   Open the `Terminal` app (Mac) or **Git Bash** (Windows), type this, and press Enter:
   ```
   git --version
   ```
   - If you see something like `git version 2.x.x` → Git is already installed, skip to step 2.
   - If you see an error instead → Git is not installed yet, follow the install step below.

   **Install Git** (only if the check above showed an error)
   - **Mac**: Running `git --version` with Git missing will prompt macOS to offer an install — click Install, then run `git --version` again to confirm.
   - **Windows**: Download and install from https://git-scm.com/download/win (keep the default options). After installing, open **Git Bash** from the Start menu — use it instead of Command Prompt for the rest of these steps.

2. **Create a `training` folder, and a `repo` folder inside it**, then move into `repo`:
   ```
   mkdir -p training/repo
   cd training/repo
   ```

3. **Download (clone) the repo** — copy-paste this exactly and press Enter (make sure you're inside the `repo` folder from step 2):
   ```
   git clone https://github.com/datavedam/amway-dve.git
   ```
   Read the lines that appear on screen — they'll confirm the repo was cloned into a new folder called `amway-dve`.

4. **Move into today's folder**:
   ```
   cd amway-dve/day1
   ```

You're now ready for the assignments below. Run every command from inside this `day1` folder.

---

## Step 2: Assignments

For each assignment: run the command, then **look at what appears on screen** and answer the question — don't guess ahead of time.

### Assignment 1 — Check your setup
Run the setup-check script in your sandbox:
```
./scripts/check_installs.sh
```
Read the output line by line and note which tools show green `[OK]` and which show red `[MISS]`. If anything is `[MISS]`, ask the trainer before continuing.

### Assignment 2 — Open Claude
Start Claude Code from your local terminal:
```
claude
```
Once it opens, type `hi` and press Enter. Read how it replies — this confirms it's working and is the tool you'll use for the rest of the assignments.

### Assignment 3 — List down the models
Inside Claude, run:
```
/model
```
Read what shows up on screen, write down the model names you see, and pick the one that's currently selected.

### Assignment 4 — List down the contexts
Inside Claude, run:
```
/context
```
Read the breakdown that appears (files, system prompt, tools, etc.) and write down what's taking up the most space. This helps you understand what Claude "sees" without you telling it directly.

### Assignment 5 — How many skills are there?
Inside Claude, run:
```
/skills
```
Read the list, write down the number, and pick one skill that sounds useful for your own work.

### Assignment 6 — Practice writing a prompt

**Step A: Guess first, before running anything.**
If you asked Claude to just "write some code" — no other details — write down your guess: what do you think it will write? Will it ask you a question back, or just assume something?

**Step B: Run three prompts, in the same order, in the same Claude session.**
1. > Write a Python function that adds two numbers, with a comment explaining what it does.
2. > write some code
3. > ...

Fill this in as you go:

| Prompt | What did it actually do? | Matched your guess? (Y/N) |
|---|---|---|
| 1 — clear | | — |
| 2 — vague | | |
| 3 — very vague | | |

**Step C: Score each reply, 1 (bad) to 5 (great).**

| Prompt | Length | Correctness | Follow-up needed (5 = none needed) |
|---|---|---|---|
| 1 — clear | | | |
| 2 — vague | | | |
| 3 — very vague | | | |

**Step D: Your turn.**
Think of one real task from your own work. Write a clear prompt for it and run it. Then write a vague version of the same task and run that too.

Not sure what a "vague version" looks like? Just strip out the details — drop the goal, the specifics, everything. For example, if your clear prompt is:
> Write a function to validate an email address, and include a few test cases.

...the vague version is simply:
> check emails

Did the same pattern show up as before? Share one surprise with the person next to you.

Now check what those two prompts cost you:
1. Run `/context` and read the size/length metrics — how much context has been used so far?
2. Run `/cost` and read the numbers — how much did this conversation cost so far?

### Assignment 7 — Practice understanding context
1. Ask Claude: `What does check_installs.sh do?`
   Read the answer — did it need you to paste the file's contents, or could it already see it? This is called **context**.
2. Close Claude and open a brand new terminal window. Run `claude` again and ask the same question.
   Read the new answer — does it remember anything from your earlier conversation, or does it start fresh?

### Assignment 8 — Practice improving a prompt
Take your vague prompt from Assignment 6 and make it better by adding:
- **What you want** (the goal)
- **Any constraints** (language, style, length)
- **An example** of input/output, if helpful

For example, turning the vague prompt from Assignment 6:
> write some code

...into an improved one might look like this:
> Write a Python function called `add_numbers(a, b)` that returns the sum of two numbers. Add a one-line comment explaining what it does. Example: `add_numbers(2, 3)` should return `5`.

Run your own improved version, read the new reply, and compare it to your very first attempt in Assignment 6. Write down one thing that improved.

### Assignment 9 — Create your first custom skill
A **skill** is a saved set of instructions Claude can reuse — instead of re-typing a long prompt every time, you save it once and trigger it with a short command.

Inside Claude, ask it to build one for you:
> Create a Claude Code skill called `daily-standup`. When I type `/daily-standup`, it should ask me three questions: what I did yesterday, what I'll do today, and any blockers I have. Gets today's date and writes the recap to standups/<YYYY-MM-DD>.md at the project root. Overwrites that day's file if the skill is run again the same day, instead of appending or asking.

Read what Claude does step by step — it will likely explain what it's about to create and ask permission before writing any files. Approve it, then read where it tells you the skill was saved.

Once it's done:
1. Close Claude and reopen it (`claude`) — skills are only picked up on a fresh start. Or you can run `/reload-skills`
2. Run `/skills` and check the count went up by one compared to Assignment 5.
3. Run `/daily-standup` and see it trigger.

### Assignment 10 — Personalize a skill for your own work
Think of one small repetitive task from your own job — a status update format, a checklist you fill out often, a template you copy-paste. Ask Claude to turn it into a skill the same way you did in Assignment 9, describing what it should ask or do.

Test it by running your new skill's command. Read the output — does it match what you asked for? If not, tell Claude what's off and let it adjust the skill, then test again.

### Assignment 11 — Skill vs. plain prompt
Do the same small task twice, in the same Claude session:
1. Trigger it using your skill from Assignment 9 (e.g. `/daily-standup`).
2. Ask for the same thing again, but this time typing it out as a plain prompt instead of using the skill.

Fill this in:

| | Skill | Plain prompt |
|---|---|---|
| How much did you have to type? | | |
| Was the output consistent with what you got last time? | | |
| Anything missing or different? | | |

