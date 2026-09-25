#!/usr/bin/env bash
# Day 5 lab setup. Run from the day5/ folder:   bash setup.sh
set -e
if [ ! -d lab/samples ] || [ ! -d skills/parity-check ]; then
  echo "Run this from amway-dve/day5:  cd amway-dve/day5 && bash setup.sh"; exit 1
fi
mkdir -p .claude/skills .claude/agents work
command cp -rf skills/inumber-intake skills/kafka-topic-contract skills/parity-check .claude/skills/
command cp -f agents/ailc-gate-reviewer.md .claude/agents/
command cp -f lab-settings.json .claude/settings.json
[ -f work/salesorder-to-orderudm.vm ] || command cp starter/salesorder-to-orderudm.vm work/
[ -f work/EVIDENCE.md ] || printf '%s\n' '# Evidence' '' '| Round | What ran | Output (pasted) | Name |' '|---|---|---|---|' > work/EVIDENCE.md
echo "Skills:  $(ls .claude/skills | tr '\n' ' ')"
echo "Agent:   ailc-gate-reviewer"
echo "Rules:   .claude/settings.json (no reading solutions/ or lab/samples/generate.py, no editing lab/samples/)"
echo "Starter: work/salesorder-to-orderudm.vm, work/EVIDENCE.md"
uv run -q --with airspeed --with pyyaml python .claude/skills/parity-check/scripts/parity_check.py selftest
