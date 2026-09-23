#!/usr/bin/env python3
"""Check Kafka consumer properties against the certified-pattern rules.

usage: check_pattern.py <properties-file> | selftest
Matches keys by suffix, so camel.route-template[x].kafka.poll_on_error and
pollOnError both work.
"""
import re
import sys

ALIASES = {
    "pollonerror": "pollOnError", "poll_on_error": "pollOnError",
    "breakonfirsterror": "breakOnFirstError", "breakon_firsterror": "breakOnFirstError",
    "allowmanualcommit": "allowManualCommit", "allow_manualcommit": "allowManualCommit",
    "autocommitenable": "autoCommitEnable", "auto_commit_enable": "autoCommitEnable",
    "retries": "retries",
}
NEEDS_BREAK = {"ERROR_HANDLER", "RECONNECT", "RETRY"}


def parse(text):
    props = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = (s.strip() for s in line.split("=", 1))
        last = re.split(r"[.\]]", key)[-1].lower()
        if last in ALIASES:
            props[ALIASES[last]] = val
    return props


def check(props):
    errors = []
    poll = props.get("pollOnError", "").upper()
    brk = props.get("breakOnFirstError", "").lower()
    if poll in NEEDS_BREAK and brk != "true":
        errors.append(f"pollOnError={poll} requires breakOnFirstError=true")
    if "retries" in props and poll not in NEEDS_BREAK:
        errors.append("retries set but pollOnError is not RETRY/ERROR_HANDLER/RECONNECT — it has no effect")
    if props.get("allowManualCommit", "").lower() == "true" and props.get("autoCommitEnable", "").lower() == "true":
        errors.append("manual and auto commit are both on — pick one")
    return errors


def selftest():
    cases = [
        ("pollOnError=RETRY\nbreakOnFirstError=true\nretries=3\n", 0),
        ("pollOnError=RETRY\nbreakOnFirstError=false\n", 1),
        ("camel.route-template[c].kafka.poll_on_error=ERROR_HANDLER\n", 1),
        ("allowManualCommit=true\nautoCommitEnable=true\n", 1),
        ("pollOnError=STOP\nretries=3\n", 1),
        ("allowManualCommit=true\nautoCommitEnable=false\npollOnError=ERROR_HANDLER\nbreakOnFirstError=true\n", 0),
    ]
    for text, want in cases:
        got = len(check(parse(text)))
        if got != want:
            print(f"selftest FAIL: expected {want} error(s), got {got} for:\n{text}")
            return 1
    print(f"selftest PASS ({len(cases)} cases)")
    return 0


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "selftest":
        return selftest()
    with open(sys.argv[1]) as f:
        errors = check(parse(f.read()))
    for e in errors:
        print("ERROR " + e)
    print("FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
