#!/usr/bin/env python3
"""Check an I-number intake brief: every field filled (OPEN allowed), owner named.

Usage:
  python check_brief.py <brief.md>
  python check_brief.py selftest
Exit 0 = pass (OPEN fields listed as warnings), 1 = fail.
"""
import re
import sys

FIELDS = [
    "I-number", "Source system", "Source contract/topic", "Target system",
    "Target interface", "Trigger", "Volume", "Ordering need",
    "Failure behaviour", "Owner", "Gate owner",
]
LINE = re.compile(r"^\s*[-*]\s*\*\*(?P<k>[^*]+?):\*\*\s*(?P<v>.*)$")


def parse(text):
    found = {}
    for line in text.splitlines():
        m = LINE.match(line)
        if m:
            found[m.group("k").strip()] = m.group("v").strip()
    return found


def check(text):
    errors, warnings = [], []
    found = parse(text)
    for f in FIELDS:
        if f not in found:
            errors.append(f"missing field: {f}")
        elif not found[f]:
            errors.append(f"empty field: {f}")
        elif found[f].upper() == "OPEN":
            if f == "Owner":
                errors.append("Owner is OPEN — a named owner is required")
            else:
                warnings.append(f"OPEN: {f}")
    opens = [w for w in warnings]
    if opens:
        section = text.split("## Open questions", 1)
        qs = [l for l in section[1].splitlines() if l.strip().lstrip("-* ").strip()] if len(section) > 1 else []
        if not qs:
            errors.append("fields are OPEN but the 'Open questions' section is empty")
    return errors, warnings


def run(path):
    with open(path, encoding="utf-8") as fh:
        errors, warnings = check(fh.read())
    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("FAIL" if errors else "PASS")
    return 1 if errors else 0


def selftest():
    good = "\n".join(f"- **{f}:** x" for f in FIELDS)
    assert check(good) == ([], []), check(good)
    opened = good.replace("**Volume:** x", "**Volume:** OPEN") + "\n## Open questions\n- Volume? ask Manhattan team\n"
    e, w = check(opened)
    assert not e and w == ["OPEN: Volume"], (e, w)
    e, _ = check(good.replace("**Volume:** x", "**Volume:** OPEN"))
    assert any("Open questions" in x for x in e), e
    e, _ = check(good.replace("**Owner:** x", "**Owner:** OPEN"))
    assert any("Owner" in x for x in e), e
    e, _ = check(good.replace("**Trigger:** x", "**Trigger:** "))
    assert "empty field: Trigger" in e, e
    e, _ = check(good.replace("- **Gate owner:** x", ""))
    assert "missing field: Gate owner" in e, e
    print("selftest PASS (6 cases)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(selftest() if sys.argv[1] == "selftest" else run(sys.argv[1]))
