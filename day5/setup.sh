#!/usr/bin/env bash
# Day 5 quick-lab setup. Run from the day4/ folder:   bash ../day5/setup.sh
set -e
if [ ! -d lab/samples ] || [ ! -d ../day5 ]; then
  echo "Run this from amway-dve/day4:  cd amway-dve/day4 && bash ../day5/setup.sh"; exit 1
fi
# work/.day5 marks a work/ folder this setup made, so running setup again during Day 5 is fine.
if [ -d work ] && [ ! -e work/.day5 ]; then
  for f in impact.md frozen-contract.md EVIDENCE.md adr-002-switchover.md i3343k; do
    if [ -e "work/$f" ]; then
      echo "work/ has files from the Day 4 lab. Keep them by renaming the folder, then run setup again:  mv work work-day4 && bash ../day5/setup.sh"; exit 1
    fi
  done
fi
mkdir -p .claude/skills .claude/agents work
touch work/.day5
command cp -rf ../day3/skills/inumber-intake ../day3/skills/kafka-topic-contract .claude/skills/
command cp -rf skills/parity-check .claude/skills/
command cp -f agents/ailc-gate-reviewer.md .claude/agents/
command cp -f lab-settings.json .claude/settings.json
[ -f work/salesorder-to-orderudm.vm ] || command cp ../day5/starter/salesorder-to-orderudm.vm work/
[ -f work/EVIDENCE.md ] || printf '%s\n' '# Evidence' '' '| Round | What ran | Output (pasted) | Name |' '|---|---|---|---|' > work/EVIDENCE.md
echo "Skills:  $(ls .claude/skills | tr '\n' ' ')"
echo "Agent:   ailc-gate-reviewer"
echo "Rules:   .claude/settings.json (no reading solutions/ or lab/samples/generate.py, no editing lab/samples/)"
echo "Starter: work/salesorder-to-orderudm.vm, work/EVIDENCE.md"
uv run -q --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py selftest
