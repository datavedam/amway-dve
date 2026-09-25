# Day 5 – Brownfield, then decisions at runtime

| Time | Block | Material |
|---|---|---|
| 0:00–2:00 | **Brownfield lab, walked together**: six rounds — why (slide), do (you), what you should see (slide) | [`LAB.md`](LAB.md) |
| 2:00–2:05 | Break | |
| 2:05–3:00 | **jev**: a model that decides instead of writing | Slides + live demo |

## Start here
```
cd training/repo/amway-dve
git pull
cd day4
bash ../day5/setup.sh
claude
```
Windows: use **Git Bash**. The lab runs inside `day4/`, which holds the brownfield
material (diagrams, made-up sample orders, old mapping rules, change request,
parity-check skill). Then follow [`LAB.md`](LAB.md) round by round.

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
  README.md                          this page
  LAB.md                             the lab, round by round
  setup.sh                           one-command setup (run from day4/)
  starter/salesorder-to-orderudm.vm  the mapping you finish in round 3
  demo/naive-draft.vm                a first draft that looks right and is wrong in four places (round 4)
```
