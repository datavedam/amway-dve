# Day 3 — Skills for the Integration Lifecycle

Three kinds of skills today:

1. **Your own GI skills** — `camel-integration-author` and `mft-config-generator`
   from your `gi-ai-skills` repo. They already cover stage 4 (Build).
2. **Public skills from [skills.sh](https://skills.sh)** — installed below, one per stage.
3. **Stage skills in this folder** — written for the unshipped-quantity flow.

Run everything inside `day3/`. After each install, run `/skills` and confirm it
appears before moving on.

---

## 0. Before you install anything: check it

A skill is instructions **and scripts** that run on your machine. Popular is not
the same as safe. On every skills.sh page, look at the three security audits
(Gen Agent Trust Hub, Socket, Snyk). Real examples:

| Skill | Installs | Audits |
|---|---|---|
| `getsentry/skills/security-review` | 16K | **Fails 2 of 3** |
| `mattpocock/skills/code-review` | 600K | **Fails Snyk** |
| `dboeckli/ai-agent-skills/camel-matrix` (the only "Camel" skill on skills.sh) | 1.8K | **Fails Trust Hub** — and only covers Spring Boot versions |

Checklist before you adopt a skill for the team:

- [ ] All three audits read — any Fail is a stop
- [ ] `SKILL.md` and every script read end to end — what does it run, what does it call over the network?
- [ ] Publisher — vendor-official (Anthropic, Confluent, Buf) or an individual?
- [ ] Does it contradict your house rules? A generic Kafka skill will happily write a raw `kafka:` endpoint or turn on `auto.register.schemas`. **Your skill must win.**
- [ ] Pinned (commit), copied into the repo's `.claude/skills/`, one named owner

---

## 1. Your own GI skills (stage 4 — Build)

Copy them into this project so every exercise can use them:
```
mkdir -p .claude/skills
cp -r <path-to-your-gi-ai-skills>/camel-integration-author .claude/skills/
cp -r <path-to-your-gi-ai-skills>/mft-config-generator     .claude/skills/
pip install pyyaml openpyxl
```

## 2. Today's stage skills (stages 1, 2, 6)
```
cp -r skills/inumber-intake skills/kafka-topic-contract skills/env-promotion-check .claude/skills/
mkdir -p .claude/agents && cp agents/*.md .claude/agents/
```

## 3. Public skills, by stage

**Graph — map what exists**
([source](https://skills.sh/graphify-labs/graphify/graphify)) — Pass / Warn / Pass
```
pip install graphifyy
npx skills add https://github.com/graphify-labs/graphify --skill graphify
```

**Write skills** — Anthropic's official skill workflow
([source](https://skills.sh/anthropics/skills/skill-creator))
```
npx skills add https://github.com/anthropics/skills --skill skill-creator
```

**Stage 2 — Contract:** schema compatibility review
([source](https://skills.sh/lensesio/agentic-engineering-for-apache-kafka/kafka-schema-review)) — Pass ×3.
Built for the Lenses MCP server (MCP was covered on Day 2 — `TOOLS.md`); without a Kafka MCP connected, it checks the code only.
```
npx skills add https://github.com/lensesio/agentic-engineering-for-apache-kafka --skill kafka-schema-review
```
`.proto` authoring and breaking-change rules, from the Buf team
([source](https://skills.sh/bufbuild/claude-plugins/protobuf)) — Pass ×3
```
npx skills add https://github.com/bufbuild/claude-plugins --skill protobuf
```

**Stage 4 — Build:** "what happens if this runs twice?" — Kafka → JDBC
([source](https://skills.sh/cursor/plugins/principle-make-operations-idempotent)) — Pass ×3
```
npx skills add https://github.com/cursor/plugins --skill principle-make-operations-idempotent
```

**Stage 5 — Verify:** no "done" without fresh evidence
([source](https://skills.sh/obra/superpowers/verification-before-completion)) — Pass ×3
```
npx skills add https://github.com/obra/superpowers --skill verification-before-completion
```

**Subagents — parallel reviews**
([source](https://skills.sh/obra/superpowers/dispatching-parallel-agents)) — Pass ×3
```
npx skills add https://github.com/obra/superpowers --skill dispatching-parallel-agents
```

**Stage 7 — Operate:** dead-letter review and runbooks
([dlq](https://skills.sh/lensesio/agentic-engineering-for-apache-kafka/kafka-dlq-review),
[runbook](https://skills.sh/anthropics/knowledge-work-plugins/runbook))
```
npx skills add https://github.com/lensesio/agentic-engineering-for-apache-kafka --skill kafka-dlq-review
npx skills add https://github.com/anthropics/knowledge-work-plugins --skill runbook
```

Already installed on Day 2 (`day2/install-necessary-skills.md`) and used again today:
`documentation-and-adrs` (stage 3 ADR), `subagent-driven-development`, and the
`mattpocock-skills` plugin (`/grill-me` is useful at the stage 1 and stage 3 gates).
If you are on a new machine, run that Day 2 file first.

## 4. Verify
```
/skills
```
You should see: `camel-integration-author`, `inumber-intake`, `kafka-topic-contract`,
`env-promotion-check`, `graphify`, `skill-creator`, `kafka-schema-review`, `protobuf`,
`principle-make-operations-idempotent`, `verification-before-completion`,
`dispatching-parallel-agents`, `kafka-dlq-review`, `runbook`.
If one is missing, re-run its step and read the error — don't continue on a partial install.

---

## Where the gaps are

No public skill exists for **webMethods, Oracle EBS staging, Amway-style Camel,
Delinea Secret Server or ServiceNow ExceptionEvent**. Those are exactly the skills
your team writes — see [`assignments/SKILLS_GAP.md`](assignments/SKILLS_GAP.md).
