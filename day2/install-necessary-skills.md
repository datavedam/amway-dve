# Day 2 — Installing the Skills Used in This Training

A few Day 2 exercises reference skills that aren't part of Claude Code
out of the box — they come from a community plugin and a few
individually-published skills. Run the steps below once, in order,
inside a Claude Code session, **before** starting any assignment that
needs them. Everything here is copy-paste — run each command, then
read what appears before moving to the next.

## 1. Install the Matt Pocock skills plugin
This adds a bundle of skills in one shot (diagnosing bugs, TDD,
domain modeling, code review, and more — including the two used in
steps 2–3 below). Inside Claude, run:
```
/plugin install mattpocock-skills
```
Read the confirmation that appears.

## 2. Run its setup command
Some plugins need a one-time setup step to finish wiring themselves
into your project. Run:
```
/setup-matt-pocock-skills
```
Read what it does — it may ask you to confirm a few things.

## 3. Try one of its skills
Confirm the plugin actually installed a working skill:
```
/grill-me
```
This is the "grilling" skill from the bundle — it should start
stress-testing whatever plan or idea you give it.

## 4. Install individual skills from skills.sh
These three are published separately (not part of the plugin bundle
above), each from its own GitHub repo. Install them one at a time —
run the command, then check `/skills` before moving to the next.

**PRD skill** — from `github/awesome-copilot`
([source](https://www.skills.sh/github/awesome-copilot/prd)):
```
npx skills add https://github.com/github/awesome-copilot --skill prd
```

**Subagent-driven development** — from `obra/superpowers`
([source](https://www.skills.sh/obra/superpowers/subagent-driven-development)):
```
npx skills add https://github.com/obra/superpowers --skill subagent-driven-development
```

**Documentation and ADRs** — from `addyosmani/agent-skills`
([source](https://www.skills.sh/addyosmani/agent-skills/documentation-and-adrs)):
```
npx skills add https://github.com/addyosmani/agent-skills --skill documentation-and-adrs
```

## 5. Verify everything installed
Inside Claude, run:
```
/skills
```
Confirm the list now includes skills from the `mattpocock-skills`
plugin (e.g. `grilling`, `tdd`, `diagnosing-bugs`) as well as `prd`,
`subagent-driven-development`, and `documentation-and-adrs`. If any
are missing, re-run that step's command and read the error output
before continuing — don't skip ahead with a partial install.
