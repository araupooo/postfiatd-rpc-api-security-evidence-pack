#!/usr/bin/env python3
"""Verify excerpts in data/source_excerpts.json.

With --pin <checkout>: every recorded line must match the checkout file
at that line, verbatim (CHECK OK only if all match).
Without --pin: structure check only (ids unique, pin is a 40-char hex
SHA, every excerpt has file + lines with matching line numbers).

Usage: python3 scripts/check_excerpts.py [--pin PATH]
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

    doc = json.load(open(os.path.join(HERE, "data", "source_excerpts.json")))
    pin = doc["pin"]
    print(f"[step] pin field present (40-char SHA): "
          f"{'PASS' if re.fullmatch(r'[0-9a-f]{40}', pin) else 'FAIL'}")
    if not re.fullmatch(r"[0-9a-f]{40}", pin):
        print("CHECK FAIL (bad pin)")
        return 1

    ids = [e["id"] for e in doc["excerpts"]]
    ok_ids = len(ids) == len(set(ids))
    print(f"[step] {len(ids)} excerpts, ids unique: "
          f"{'PASS' if ok_ids else 'FAIL'}")
    if not ok_ids:
        print("CHECK FAIL (duplicate ids)")
        return 1

    for e in doc["excerpts"]:
        lines = e["lines"]
        nums = [l["line"] for l in lines]
        ranges = e["line_ranges"]
        flat = [ln for a, b in ranges for ln in range(a, b + 1)]
        if nums != flat:
            print(f"[step] {e['id']} line numbers match ranges: FAIL")
            print("CHECK FAIL (structure)")
            return 1
        if not e["file"] or not lines:
            print(f"[step] {e['id']} has file and lines: FAIL")
            print("CHECK FAIL (structure)")
            return 1
    print(f"[step] {len(ids)} excerpts internally consistent: PASS")

    if args.pin is None:
        print("CHECK OK (structure only; re-run with --pin to verify "
              "against the checkout)")
        return 0

    fails = 0
    for e in doc["excerpts"]:
        path = os.path.join(args.pin, e["file"])
        try:
            src = open(path).read().splitlines()
        except FileNotFoundError:
            print(f"[step] {e['id']} {e['file']}: file missing: FAIL")
            fails += 1
            continue
        bad = [l for l in e["lines"]
               if l["line"] < 1 or l["line"] > len(src)
               or src[l["line"] - 1] != l["text"]]
        if bad:
            print(f"[step] {e['id']} {e['file']}: "
                  f"{len(bad)} mismatched lines: FAIL")
            fails += 1
        else:
            print(f"[step] {e['id']} {e['file']}: verbatim: PASS")
    if fails:
        print(f"CHECK FAIL ({fails} excerpts mismatched)")
        return 1
    print("CHECK OK (all excerpts verified verbatim against the pinned checkout)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
