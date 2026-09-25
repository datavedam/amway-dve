# Day 5 – Brownfield, then decisions at runtime

| Time | Block | Material |
|---|---|---|
| 0:00–1:00 | **Brownfield**: change what's already running — theory with live demos | Slides |
| 1:00–2:00 | **Quick lab**: prove I1001 won't notice | [`LAB.md`](LAB.md) |
| 2:00–2:05 | Break | |
| 2:05–3:00 | **jev**: a model that decides instead of writing | Slides + live demo |

## Setup
```
cd training/repo/amway-dve && git pull
cd day4
bash ../day5/setup.sh
```
The lab runs inside `day4/`, which holds the brownfield material (diagrams, sample
orders, old mapping rules, change request, parity-check skill).

## What's in this folder
```
day5/
  README.md                          this page
  LAB.md                             the 1-hour brownfield lab
  setup.sh                           one-command setup (run from day4/)
  starter/salesorder-to-orderudm.vm  the mapping you finish in the lab
  demo/naive-draft.vm                the facilitator's "looks right, is wrong" first draft
```
