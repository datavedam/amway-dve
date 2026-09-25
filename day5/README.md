# Day 5 – Brownfield, then decisions at runtime

| Time | Block | Material |
|---|---|---|
| 0:00–2:00 | **Brownfield lab, walked together**: six rounds - why (slide), do (you), what you should see (slide) | [`LAB.md`](LAB.md) |
| 2:00–2:05 | Break | |
| 2:05–3:00 | **jev**: a model that decides instead of writing | Slides + live demo |

## Start here
Open a terminal (Git Bash on Windows) and start Claude in the lab folder:
```
cd training/repo/amway-dve/day5
claude
```
Then follow [`LAB.md`](LAB.md): every round is one prompt you paste into Claude -
including the setup. Everything for the lab is in this folder.

## The six rounds
| Round | Question | You produce |
|---|---|---|
| 0 | Set up | skills, deny rules, starter mapping, `EVIDENCE.md` |
| 1 | Who gets hit? | `work/impact.md` |
| 2 | What must not change? | `work/frozen-contract.md` (signed) + topic-name check |
| 3 | Write the new mapping | `work/salesorder-to-orderudm.vm` |
| 4 | Prove it: parity | parity on your mapping + on the naive draft |
| 5 | The one allowed difference | `work/allowed-differences.yaml` (signed) → `PARITY PASS` |
| 6 | The gate | the reviewer's verdict table |

## What's in this folder
```
day5/
  README.md            this page
  LAB.md               the lab - one Claude prompt per round
  setup.sh             setup (Claude runs it for you in Round 0)
  lab/                 diagrams, order flow, change request, old + new field rules,
                       made-up sample orders (lab/samples/)
  skills/              parity-check, kafka-topic-contract, inumber-intake
  agents/              the gate reviewer
  starter/             the mapping you finish in Round 3
  demo/naive-draft.vm  a first draft that looks right and is wrong in four places (Round 4)
  solutions/           reference answers (Claude is not allowed to read them)
  lab-settings.json    the lab's deny rules (copied to .claude/settings.json)
```
