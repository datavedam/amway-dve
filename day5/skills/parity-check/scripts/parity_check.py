#!/usr/bin/env python3
"""Parity check: does the new mapping produce the same data as the old flow?

Renders a Velocity mapping (.vm) against each new-source input message and
compares the result, field by field, with the output the OLD flow produced
for the same order (the recording). Structure may change; data may not.

usage:
  parity_check.py run    --vm <mapping.vm> --samples <dir> [--allowed <allowed-differences.yaml>]
  parity_check.py render --vm <mapping.vm> --input <message.json>
  parity_check.py selftest

<dir> must contain nextgen-input/<name>.json and recorded-orderudm/<name>.json.

Needs: airspeed (Python Velocity engine) and pyyaml. Easiest:
  uv run --with airspeed --with pyyaml python parity_check.py run ...

Honest limit: airspeed is a Python implementation of Velocity, not the engine
Camel runs. It covers the map style in your skeleton ($out.put, $list.add,
#foreach, #if, $foreach.count). Real parity runs the bundle itself: Pipeline
Recorder records the old flow, POST /api/replay/{route_id} replays through the new one.
"""
import ast
import json
import sys
from pathlib import Path


def render(vm_text, message):
    import airspeed
    out = airspeed.Template(vm_text).merge({"body": message}).strip()
    for parse in (json.loads, ast.literal_eval):
        try:
            return parse(out)
        except Exception:
            pass
    raise ValueError("mapping output is not a map/JSON:\n" + out[:400])


def diff(old, new, path=""):
    """Yield (path, old, new) for every difference. Types count: 2 != "2"."""
    if isinstance(old, dict) and isinstance(new, dict):
        for k in sorted(set(old) | set(new)):
            p = f"{path}.{k}" if path else k
            if k not in new:
                yield p, old[k], "<missing>"
            elif k not in old:
                yield p, "<not in old output>", new[k]
            else:
                yield from diff(old[k], new[k], p)
    elif isinstance(old, list) and isinstance(new, list):
        if len(old) != len(new):
            yield f"{path}.length", len(old), len(new)
        for i, (a, b) in enumerate(zip(old, new)):
            yield from diff(a, b, f"{path}[{i}]")
    elif type(old) is not type(new) or old != new:
        yield path, old, new


PLACEHOLDER_WORDS = r"(open|tbd|tbc|todo|placeholder)"          # the value is, or starts with, one of these words
NOT_A_PERSON = r"((the\s+)?(gi\s+)?team|n/?a|none|nobody|-+)"   # a team or "n/a" is not a named approver


def is_placeholder(text, person=False):
    """True for template text. Judges the whole (trimmed) value, never a substring, so
    "Priya Nair <priya.nair@amway.com>", "Kenji Todo" or a reason that mentions
    "replace" are real text. Placeholders: empty; wrapped in <...>; OPEN / TBD / TBC /
    TODO / placeholder (whole value or first word); starting with "replace". For a
    person (approved_by), also a team or n/a ("team", "GI team", "n/a"), whole value
    or first words."""
    import re
    t = str(text or "").strip()
    if not t or (t.startswith("<") and t.endswith(">")):
        return True
    if re.match(PLACEHOLDER_WORDS + r"\b", t, re.I) or re.match(r"replace", t, re.I):
        return True
    return person and bool(re.match(NOT_A_PERSON + r"(\b|$)", t, re.I))


MIN_REASON = 15


def check_entries(entries):
    allowed, errors = [], []
    for e in entries:
        who = str(e.get("approved_by") or "").strip()
        why = str(e.get("reason") or "").strip()
        if (not e.get("path") or is_placeholder(why) or len(why) < MIN_REASON
                or is_placeholder(who, person=True)):
            errors.append(f"allowed difference {e.get('path')!r} needs path, a real reason (at least "
                          f"{MIN_REASON} characters) and a named person as approved_by (not empty, not OPEN, "
                          "not a team, not a placeholder like <...> or TBD)")
        else:
            allowed.append(e["path"])
    return allowed, errors


def load_allowed(path):
    if not path:
        return [], []
    import yaml
    doc = yaml.safe_load(Path(path).read_text()) or {}
    return check_entries(doc.get("allowed", []))


def is_allowed(p, allowed):
    """`lines[*].note` matches lines[0].note, lines[1].note, ...; `*` matches one field name."""
    import re
    for pat in allowed:
        rx = "^" + re.escape(pat).replace(r"\[\*\]", r"\[\d+\]").replace(r"\*", "[^.]+") + "$"
        if re.match(rx, p):
            return True
    return False


def run(vm, samples, allowed_file):
    vm_text = Path(vm).read_text()
    allowed, errors = load_allowed(allowed_file) if allowed_file else ([], [])
    for e in errors:
        print("ERROR " + e)
    inputs = sorted((Path(samples) / "nextgen-input").glob("*.json"))
    if not inputs:
        print(f"ERROR no inputs in {samples}/nextgen-input")
        return 2
    bad_samples = bad_fields = accepted = 0
    for f in inputs:
        rec = Path(samples) / "recorded-orderudm" / f.name
        try:
            new = render(vm_text, json.loads(f.read_text()))
        except Exception as ex:
            print(f"FAIL  {f.stem}: mapping did not render — {ex}")
            bad_samples += 1
            continue
        found = list(diff(json.loads(rec.read_text()), new))
        real = [d for d in found if not is_allowed(d[0], allowed)]
        accepted += len(found) - len(real)
        if real:
            bad_samples += 1
            bad_fields += len(real)
            print(f"FAIL  {f.stem}")
            for p, a, b in real:
                print(f"      {p}: old={json.dumps(a)} new={json.dumps(b)}")
        else:
            note = f" ({len(found)} allowed difference(s))" if found else ""
            print(f"PASS  {f.stem}{note}")
    if errors:
        print("PARITY FAIL (allowed-differences file is not signed off)")
        return 1
    if bad_samples:
        print(f"PARITY FAIL ({bad_fields} data difference(s) in {bad_samples} of {len(inputs)} samples)")
        return 1
    print(f"PARITY PASS ({len(inputs)}/{len(inputs)} samples match; {accepted} allowed difference(s) accepted)")
    return 0


def selftest():
    old = {"a": 1, "b": "2", "lines": [{"n": 1}, {"n": 2}], "src": "HYBRIS"}
    cases = [({"a": 1, "b": "2", "lines": [{"n": 1}, {"n": 2}], "src": "HYBRIS"}, 0),
             ({"a": 1, "b": 2, "lines": [{"n": 1}, {"n": 2}], "src": "HYBRIS"}, 1),        # type change
             ({"a": 1, "b": "2", "lines": [{"n": 1}], "src": "HYBRIS"}, 1),                # lost a line
             ({"a": 1, "lines": [{"n": 1}, {"n": 2}], "src": "HYBRIS"}, 1),                # missing field
             ({"a": 1, "b": "2", "lines": [{"n": 0}, {"n": 1}], "src": "HYBRIS"}, 2)]      # 0-based numbering
    for new, want in cases:
        got = len(list(diff(old, new)))
        if got != want:
            print(f"selftest FAIL: expected {want}, got {got} for {new}")
            return 1
    if not is_allowed("sourceSystem", ["sourceSystem"]) or is_allowed("orderId", ["sourceSystem"]):
        print("selftest FAIL: allowed-path matching")
        return 1
    if not is_allowed("lines[3].note", ["lines[*].note"]):
        print("selftest FAIL: [*] matching")
        return 1
    signed = {"path": "sourceSystem", "reason": "Change request asks for it", "approved_by": "Anita Rao"}
    if check_entries([signed])[1] != []:
        print("selftest FAIL: sign-off rules rejected a signed entry")
        return 1
    for bad in ({"approved_by": "<principal's name>"}, {"approved_by": "OPEN"}, {"approved_by": ""},
                {"approved_by": "TBD"}, {"approved_by": "tbc"}, {"approved_by": "Replace with a name"},
                {"approved_by": "team"}, {"approved_by": "GI team"}, {"approved_by": "the GI Team"},
                {"approved_by": "n/a"}, {"approved_by": "TODO: ask the principal"},
                {"reason": "TBD"}, {"reason": ""}, {"reason": "OPEN"}, {"reason": "because"},
                {"reason": "<why this difference is allowed>"}, {"reason": "replace with the reason"},
                {"path": ""}):
        if check_entries([{**signed, **bad}])[1] == []:
            print(f"selftest FAIL: sign-off rules accepted {bad}")
            return 1
    for good in ({"reason": "HYBRIS -> NGC per the change request"},
                 {"reason": "NextGen will replace Hybris; the change request requires NGC."},
                 {"reason": "The change request requires NGC. Whether I1001 uses sourceSystem is OPEN "
                            "\u2014 ask the I1001 owner."},
                 {"approved_by": "Priya Nair <priya.nair@amway.com>"}, {"approved_by": "Kenji Todo"},
                 {"approved_by": "Anita Rao (training)"}):
        if check_entries([{**signed, **good}])[1] != []:
            print(f"selftest FAIL: sign-off rules rejected {good}")
            return 1
    try:
        tpl = '#set($o = {})#set($i = $o.put("x", $body.v))#set($l = [])' \
              '#foreach($e in $body.e)#set($i = $l.add($foreach.count))#end#set($i = $o.put("l", $l))$o'
        assert render(tpl, {"v": "k", "e": ["p", "q"]}) == {"x": "k", "l": [1, 2]}
    except ImportError:
        print("selftest PASS (diff rules, sign-off rules; Velocity rendering skipped: airspeed not installed)")
        return 0
    print("selftest PASS (diff rules, allowed paths, sign-off rules, Velocity rendering)")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2
    args = dict(zip(argv[2::2], argv[3::2]))
    if argv[1] == "selftest":
        return selftest()
    if argv[1] == "render":
        print(json.dumps(render(Path(args["--vm"]).read_text(), json.loads(Path(args["--input"]).read_text())), indent=2))
        return 0
    if argv[1] == "run":
        return run(args["--vm"], args["--samples"], args.get("--allowed"))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
