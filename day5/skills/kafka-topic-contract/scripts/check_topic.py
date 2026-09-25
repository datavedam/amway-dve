#!/usr/bin/env python3
"""Check Kafka topic names against reference/naming.yaml.

Usage:
  python check_topic.py <topic> [<topic> ...]
  python check_topic.py selftest
Exit 0 = all pass, 1 = at least one fails.
"""
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
NAMING = os.path.join(HERE, "..", "reference", "naming.yaml")


def load_rule(path=NAMING):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def check(names, rule):
    rx = re.compile(rule["pattern"])
    results = []
    for n in names:
        if "{env}" not in n:
            results.append((n, False, "use {env} as a placeholder, not a concrete env"))
        elif not rx.match(n):
            results.append((n, False, "does not match " + rule["pattern"]))
        else:
            results.append((n, True, "ok"))
    return results


def run(names):
    rule = load_rule()
    print(f"rule ({rule.get('status', '')}): {rule['pattern']}")
    results = check(names, rule)
    for n, ok, why in results:
        print(("PASS  " if ok else "FAIL  ") + n + ("" if ok else "  -> " + why))
    return 0 if all(ok for _, ok, _ in results) else 1


def selftest():
    rule = load_rule()
    for n, ok, why in check(rule["known_good"], rule):
        assert ok, (n, why)
    bad = ["Valuechain_{env}_000_x_pub_v1", "valuechain_dv_000_unshippedqty_pub_v1",
           "valuechain_{env}_000_unshippedqty_v1", "valuechain_{env}_000_unshippedqty_pub"]
    for n, ok, _ in check(bad, rule):
        assert not ok, n
    print(f"selftest PASS ({len(rule['known_good'])} known-good, {len(bad)} bad)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(selftest() if sys.argv[1] == "selftest" else run(sys.argv[1:]))
