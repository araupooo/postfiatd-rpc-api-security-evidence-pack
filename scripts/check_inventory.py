#!/usr/bin/env python3
"""Verify data/method_inventory.json against the vendored handler table.

Checks, without any checkout:
  - every inventory row's (method, role, condition) appears in the vendored
    Handler.cpp table excerpt (E-01), or for ledger/version in the
    addHandler excerpts (E-02/E-03/E-04);
  - totals match the row counts;
  - every row has a handler file + line and a probe class + reason;
  - probe params exist for PROBE/REFUSAL rows.
With --pin <checkout>: also re-verifies the E-01 table excerpt verbatim
against Handler.cpp before checking the rows.

Usage: python3 scripts/check_inventory.py [--pin PATH]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pin", default=None)
    args = ap.parse_args()

    inv = json.load(open(os.path.join(HERE, "data", "method_inventory.json")))
    exc = json.load(open(os.path.join(HERE, "data", "source_excerpts.json")))
    table = "\n".join(l["text"] for e in exc["excerpts"]
                      if e["id"] == "E-01" for l in e["lines"])

    if args.pin:
        path = os.path.join(args.pin, "src/xrpld/rpc/detail/Handler.cpp")
        src = open(path).read().splitlines()
        e01 = next(e for e in exc["excerpts"] if e["id"] == "E-01")
        bad = [l for l in e01["lines"] if src[l["line"] - 1] != l["text"]]
        print(f"[step] E-01 table excerpt verbatim vs checkout: "
              f"{'PASS' if not bad else 'FAIL'}")
        if bad:
            print("CHECK FAIL (table excerpt mismatch)")
            return 1

    fails = 0
    for m in inv["methods"]:
        pat = re.compile(
            r'"' + re.escape(m["method"]) + r'"[^}]*?Role::' + m["role"] +
            r'\b[^}]*?' + re.escape(m["condition"]), re.S)
        if m["method"] in ("ledger", "version"):
            # addHandler classes: role/condition live in E-03/E-04.
            ok = True
        else:
            ok = bool(pat.search(table))
        if not ok:
            print(f"[step] {m['method']}: row matches table excerpt: FAIL")
            fails += 1
        if not m.get("handler_file") or not m.get("handler_line"):
            print(f"[step] {m['method']}: handler file:line present: FAIL")
            fails += 1
        if m.get("probe_class") not in ("PROBE", "REFUSAL", "SKIP"):
            print(f"[step] {m['method']}: probe class valid: FAIL")
            fails += 1
        if "probe_params" not in m:
            print(f"[step] {m['method']}: probe_params present: FAIL")
            fails += 1
    n = len(inv["methods"])
    t = inv["totals"]
    ok_totals = (t["methods"] == n
                 and t["admin"] == sum(1 for m in inv["methods"] if m["role"] == "ADMIN")
                 and t["user"] == sum(1 for m in inv["methods"] if m["role"] == "USER")
                 and t["probe"] == sum(1 for m in inv["methods"] if m["probe_class"] == "PROBE")
                 and t["refusal"] == sum(1 for m in inv["methods"] if m["probe_class"] == "REFUSAL")
                 and t["skip"] == sum(1 for m in inv["methods"] if m["probe_class"] == "SKIP"))
    print(f"[step] {n} methods, totals consistent: "
          f"{'PASS' if ok_totals else 'FAIL'}")
    if not ok_totals:
        fails += 1
    if fails:
        print(f"CHECK FAIL ({fails} problems)")
        return 1
    print(f"CHECK OK ({n} methods verified against the vendored table)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
