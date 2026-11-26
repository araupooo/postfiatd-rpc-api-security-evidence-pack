#!/usr/bin/env python3
"""Build data/method_inventory.json from the pinned postfiatd checkout.

Run once by the pack author (build-time). The generated JSON is vendored
in data/ and verified by scripts/check_inventory.py against the vendored
handler-table excerpt (data/source_excerpts.json, E-01) and, with --pin,
against a real checkout.

Usage: python3 build_inventory.py [--pin PATH] [--out PATH]
Default pin: ~/workspace/postfiatd-pin-0085a1f
"""
import json
import os
import re
import subprocess
import sys

PIN = os.path.expanduser("~/workspace/postfiatd-pin-0085a1f")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "method_inventory.json")

# Methods never probed live, with the reason. Everything else classified
# PROBE (read-only USER) or REFUSAL (ADMIN, one no-param call).
SKIP = {
    "submit": "state-changing: would broadcast a transaction",
    "submit_multisigned": "state-changing: would broadcast a transaction",
    "sign": "secret-bearing: signing requires a private key in the request",
    "sign_for": "secret-bearing: signing requires a private key in the request",
    "channel_authorize": "secret-bearing: creates a payment-channel signature",
    "simulate": "heavy: transaction simulation; not attempted",
}

# Per-method probe params (JSON-RPC params[0]). Empty dict = {}.
PARAMS = {
    "account_info": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_currencies": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_lines": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_channels": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_nfts": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_objects": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_offers": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "account_tx": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "amm_info": {"amm_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "book_offers": {"taker_pays": {"currency": "XRP"},
                    "taker_gets": {"currency": "USD", "issuer": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"}},
    "book_changes": {"taker_pays": {"currency": "XRP"},
                     "taker_gets": {"currency": "USD", "issuer": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"}},
    "channel_verify": {"amount": "1", "public_key": "aB",
                       "signature": "00"},
    "deposit_authorized": {"source_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
                           "destination_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "gateway_balances": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "get_aggregate_price": {"base": {"currency": "XRP"},
                            "quote": {"currency": "USD"}},
    "ledger": {"ledger_index": "validated", "transactions": False,
               "expand": False, "owner_funds": False},
    "ledger_data": {"ledger_index": "validated", "limit": 1},
    "ledger_entry": {"index": "00" * 32},
    "ledger_header": {"ledger_index": "validated"},
    "manifest": {"public_key": "nHBAToXoTH6eZtC1cMJDvjG7eRb7ufZ3GUpeisvNVT4ofruRdVvd"},
    "nft_buy_offers": {"tokenid": "00" * 32},
    "nft_sell_offers": {"tokenid": "00" * 32},
    "noripple_check": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "owner_info": {"account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"},
    "path_find": {"source_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
                  "destination_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
                  "destination_amount": {"currency": "XRP", "value": "1"}},
    "ripple_path_find": {"source_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
                         "destination_account": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59",
                         "destination_amount": {"currency": "XRP", "value": "1"}},
    "tx": {"transaction": "00" * 32},
    "transaction_entry": {"tx_hash": "00" * 32},
    "validator_votes": {"validation_public_key": "ED4D4244B734459A6D88DA611B2F2D94951181E422381AB078FAF75A41F0470A59"},
}


def grep_file(pattern, path):
    out = subprocess.run(
        ["grep", "-n", "-E", pattern, path],
        capture_output=True, text=True)
    return out.stdout.splitlines()


def find_handler_def(fn, handlers_dir):
    """Return (file, line) of the `fn(` definition line, or (None, None)."""
    for name in sorted(os.listdir(handlers_dir)):
        if not name.endswith(".cpp"):
            continue
        p = os.path.join(handlers_dir, name)
        for line in grep_file(r"^" + re.escape(fn) + r"\(", p):
            ln = int(line.split(":", 1)[0])
            return ("src/xrpld/rpc/handlers/" + name, ln)
    return (None, None)


def main():
    pin = PIN
    out = OUT
    args = sys.argv[1:]
    if "--pin" in args:
        pin = args[args.index("--pin") + 1]
    if "--out" in args:
        out = args[args.index("--out") + 1]

    handler_cpp = os.path.join(pin, "src/xrpld/rpc/detail/Handler.cpp")
    text = open(handler_cpp).read()
    lines = text.splitlines()

    # Parse the handlerArray table: entries are {"name", byRef(&doX), Role::Y, COND}
    # possibly spanning several lines.
    entries = []
    pat = re.compile(
        r'\{\s*"([a-z_0-9]+)"\s*,\s*byRef\(&([A-Za-z0-9]+)\),\s*'
        r'Role::(USER|ADMIN)\s*,\s*([A-Z_]+)',
        re.S)
    for m in pat.finditer(text):
        start_line = text[:m.start()].count("\n") + 1
        entries.append({
            "method": m.group(1),
            "handler_fn": m.group(2),
            "role": m.group(3),
            "condition": m.group(4),
            "table_line": start_line,
            "table_file": "src/xrpld/rpc/detail/Handler.cpp",
        })

    handlers_dir = os.path.join(pin, "src/xrpld/rpc/handlers")
    for e in entries:
        f, ln = find_handler_def(e["handler_fn"], handlers_dir)
        e["handler_file"] = f
        e["handler_line"] = ln
        if e["method"] in SKIP:
            e["probe_class"] = "SKIP"
            e["probe_reason"] = SKIP[e["method"]]
        elif e["role"] == "ADMIN":
            e["probe_class"] = "REFUSAL"
            e["probe_reason"] = "ADMIN method: one no-param call; role check precedes dispatch (RPCHandler.cpp:167), so no handler code runs"
        else:
            e["probe_class"] = "PROBE"
            e["probe_reason"] = "USER read-only method (or error-shape probe with inert params)"
        e["probe_params"] = PARAMS.get(e["method"], {})

    # addHandler classes: ledger + version (not in the table literal).
    extra = [
        {"method": "ledger", "handler_fn": "LedgerHandler",
         "role": "USER", "condition": "NO_CONDITION",
         "table_line": 248, "table_file": "src/xrpld/rpc/detail/Handler.cpp",
         "handler_file": "src/xrpld/rpc/handlers/LedgerHandler.h",
         "handler_line": 63, "probe_class": "PROBE",
         "probe_reason": "USER read-only method (default params only; full/accounts gated in-handler by isUnlimited, LedgerHandler.cpp:67-71)",
         "probe_params": PARAMS["ledger"]},
        {"method": "version", "handler_fn": "VersionHandler",
         "role": "USER", "condition": "NO_CONDITION",
         "table_line": 249, "table_file": "src/xrpld/rpc/detail/Handler.cpp",
         "handler_file": "src/xrpld/rpc/handlers/Version.h",
         "handler_line": 49, "probe_class": "PROBE",
         "probe_reason": "USER read-only method",
         "probe_params": {}},
    ]
    # subscribe/unsubscribe are USER but evented (websocket-only): probe once
    # for the error shape.
    for e in entries:
        if e["method"] in ("subscribe", "unsubscribe"):
            e["probe_class"] = "PROBE"
            e["probe_reason"] = "USER evented method: one no-param call records the HTTP JSON-RPC error shape (websocket-only)"

    methods = sorted(entries + extra, key=lambda x: x["method"])
    admin = [m for m in methods if m["role"] == "ADMIN"]
    user = [m for m in methods if m["role"] == "USER"]
    print(f"table entries: {len(entries)}; total methods: {len(methods)} "
          f"(ADMIN {len(admin)}, USER {len(user)})")
    print("probe classes:",
          {c: sum(1 for m in methods if m["probe_class"] == c)
           for c in ("PROBE", "REFUSAL", "SKIP")})
    missing = [m["method"] for m in methods if not m["handler_file"]]
    print("methods without handler file:", missing)
    nod = [m["method"] for m in methods if not m["handler_line"]]
    print("methods without handler line:", nod)

    doc = {
        "pin": "0085a1ff885d6a446369cf73a4430f75af22be55",
        "pin_date": "2026-10-10",
        "source_table": "src/xrpld/rpc/detail/Handler.cpp handlerArray (lines 83-201) + addHandler LedgerHandler/VersionHandler (lines 248-249)",
        "note": "Role is the table role (Role::USER / Role::ADMIN). In-tree, an ADMIN method called by a non-admin returns JSON rpcNO_PERMISSION (RPCHandler.cpp:167), mapped to HTTP 401 (ErrorCodes.cpp:100). probe_params are inert/safe values only; state-changing and secret-bearing methods are SKIP and never called.",
        "totals": {
            "methods": len(methods),
            "admin": len(admin),
            "user": len(user),
            "probe": sum(1 for m in methods if m["probe_class"] == "PROBE"),
            "refusal": sum(1 for m in methods if m["probe_class"] == "REFUSAL"),
            "skip": sum(1 for m in methods if m["probe_class"] == "SKIP"),
        },
        "methods": methods,
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
