#!/usr/bin/env python3
"""Build data/source_excerpts.json from the pinned postfiatd checkout.

Run once by the pack author (build-time). Each excerpt records file,
1-based line ranges, and the verbatim text of those lines. Verified by
scripts/check_excerpts.py --pin <checkout>.

Usage: python3 build_excerpts.py [--pin PATH] [--out PATH]
"""
import json
import os
import sys

PIN = os.path.expanduser("~/workspace/postfiatd-pin-0085a1f")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "source_excerpts.json")

# (id, file, [(start, end), ...], note)
SPECS = [
    ("E-01", "src/xrpld/rpc/detail/Handler.cpp", [(83, 201)],
     "Full handlerArray table: every method name, handler, table role, condition."),
    ("E-02", "src/xrpld/rpc/detail/Handler.cpp", [(248, 249)],
     "addHandler<LedgerHandler>() and addHandler<VersionHandler>() — methods not in the table literal."),
    ("E-03", "src/xrpld/rpc/handlers/LedgerHandler.h", [(63, 71)],
     "LedgerHandler: name 'ledger', role USER, condition NO_CONDITION."),
    ("E-04", "src/xrpld/rpc/handlers/Version.h", [(49, 57)],
     "VersionHandler: name 'version', role USER, condition NO_CONDITION."),
    ("E-05", "src/xrpld/rpc/Role.h", [(44, 44)],
     "Role enum: GUEST, USER, IDENTIFIED, ADMIN, PROXY, FORBID."),
    ("E-06", "src/xrpld/rpc/detail/Role.cpp", [(28, 46)],
     "passwordUnrequiredOrSentCorrect: no password required when admin_user/admin_password are empty."),
    ("E-07", "src/xrpld/rpc/detail/Role.cpp", [(96, 120)],
     "isAdmin (IP allowlist AND password) and requestRole (ADMIN required + not admin -> FORBID)."),
    ("E-08", "src/xrpld/rpc/detail/RPCHandler.cpp", [(165, 168)],
     "ADMIN handler + non-admin caller -> rpcNO_PERMISSION (before dispatch)."),
    ("E-09", "src/xrpld/rpc/detail/RPCHandler.cpp", [(261, 268)],
     "roleRequired: unknown method -> Role::FORBID."),
    ("E-10", "src/xrpld/rpc/detail/ServerHandler.cpp", [(703, 724)],
     "processJson: role computed via requestRole(required = roleRequired(method))."),
    ("E-11", "src/xrpld/rpc/detail/ServerHandler.cpp", [(752, 757)],
     "role == FORBID -> HTTP 403 'Forbidden' (non-batch) — the observed refusal path for ADMIN methods."),
    ("E-12", "src/xrpld/rpc/detail/ServerHandler.cpp", [(85, 87), (299, 312)],
     "authorized(): port user/password empty -> true (no port-level auth); onRequest: non-HTTP(S) port or failed auth -> HTTP 403."),
    ("E-13", "src/xrpld/rpc/detail/ServerHandler.cpp", [(609, 609)],
     "JSON error code 'forbidden' = -32605."),
    ("E-14", "src/libxrpl/protocol/ErrorCodes.cpp", [(100, 100)],
     "rpcNO_PERMISSION maps to HTTP 401 ('noPermission')."),
    ("E-15", "src/xrpld/rpc/handlers/LedgerHandler.cpp", [(67, 71)],
     "ledger with full/accounts requires isUnlimited role -> rpcNO_PERMISSION (second, in-handler gate)."),
    ("E-16", "src/xrpld/rpc/handlers/Feature1.cpp", [(47, 47), (78, 89)],
     "feature: isAdmin flag; vetoing a feature without admin -> rpcNO_PERMISSION; reply is role-aware (getJson(feature, isAdmin))."),
    ("E-17", "src/xrpld/overlay/detail/OverlayImpl.cpp", [(690, 691)],
     "Manifest rate-limit cap policy: trusted peers uncapped, untrusted capped (overlay only, not RPC)."),
    ("E-18", "src/xrpld/rpc/handlers/TransactionEntry.cpp", [(54, 60)],
     "transaction_entry: 'We don't support any transaction yet' -> notYetImplemented."),
    ("E-19", "src/xrpld/rpc/detail/Role.cpp", [(125, 131)],
     "isUnlimited: ADMIN or IDENTIFIED roles only."),
]


def main():
    pin = PIN
    out = OUT
    args = sys.argv[1:]
    if "--pin" in args:
        pin = args[args.index("--pin") + 1]
    if "--out" in args:
        out = args[args.index("--out") + 1]

    excerpts = []
    for eid, rel, ranges, note in SPECS:
        path = os.path.join(pin, rel)
        lines = open(path).read().splitlines()
        items = []
        for start, end in ranges:
            for ln in range(start, end + 1):
                items.append({"line": ln, "text": lines[ln - 1]})
        excerpts.append({"id": eid, "file": rel,
                         "line_ranges": [[a, b] for a, b in ranges],
                         "lines": items, "note": note})
        print(f"{eid} {rel} {ranges}: {len(items)} lines")

    doc = {"pin": "0085a1ff885d6a446369cf73a4430f75af22be55",
           "pin_date": "2026-10-10",
           "excerpts": excerpts}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"wrote {out} ({len(excerpts)} excerpts)")


if __name__ == "__main__":
    main()
