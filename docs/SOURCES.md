# Sources

Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10). All line numbers were verified with `grep -n` on a local
checkout of that revision, never from a raw-file fetch. Every excerpt in
`data/source_excerpts.json` is verbatim; verify with
`python3 scripts/check_excerpts.py --pin <checkout>`.

## Pinned source excerpts (19)

| ID | File | Lines | What it proves |
|---|---|---|---|
| E-01 | src/xrpld/rpc/detail/Handler.cpp | 83-201 | Full handlerArray table: 72 methods, handler, table role, condition. |
| E-02 | src/xrpld/rpc/detail/Handler.cpp | 248-249 | addHandler<LedgerHandler>() and addHandler<VersionHandler>() — methods not in the table literal. |
| E-03 | src/xrpld/rpc/handlers/LedgerHandler.h | 63-71 | LedgerHandler: name `ledger`, role USER, condition NO_CONDITION. |
| E-04 | src/xrpld/rpc/handlers/Version.h | 49-57 | VersionHandler: name `version`, role USER, condition NO_CONDITION. |
| E-05 | src/xrpld/rpc/Role.h | 44 | Role enum: GUEST, USER, IDENTIFIED, ADMIN, PROXY, FORBID. |
| E-06 | src/xrpld/rpc/detail/Role.cpp | 28-46 | passwordUnrequiredOrSentCorrect: no password required when admin_user/admin_password are empty. |
| E-07 | src/xrpld/rpc/detail/Role.cpp | 96-120 | isAdmin (IP allowlist AND password) and requestRole (ADMIN required + not admin -> FORBID). |
| E-08 | src/xrpld/rpc/detail/RPCHandler.cpp | 165-168 | ADMIN handler + non-admin caller -> rpcNO_PERMISSION (before dispatch). |
| E-09 | src/xrpld/rpc/detail/RPCHandler.cpp | 261-268 | roleRequired: unknown method -> Role::FORBID. |
| E-10 | src/xrpld/rpc/detail/ServerHandler.cpp | 703-724 | processJson: role computed via requestRole(required = roleRequired(method)). |
| E-11 | src/xrpld/rpc/detail/ServerHandler.cpp | 752-757 | role == FORBID -> HTTP 403 `Forbidden` (non-batch) — the observed refusal path for ADMIN methods. |
| E-12 | src/xrpld/rpc/detail/ServerHandler.cpp | 85-87, 299-312 | authorized(): port user/password empty -> true (no port-level auth); onRequest: non-HTTP(S) port or failed auth -> HTTP 403. |
| E-13 | src/xrpld/rpc/detail/ServerHandler.cpp | 609 | JSON error code `forbidden` = -32605. |
| E-14 | src/libxrpl/protocol/ErrorCodes.cpp | 100 | rpcNO_PERMISSION maps to HTTP 401 (`noPermission`). |
| E-15 | src/xrpld/rpc/handlers/LedgerHandler.cpp | 67-71 | ledger with full/accounts requires an unlimited role -> rpcNO_PERMISSION (second, in-handler gate). |
| E-16 | src/xrpld/rpc/handlers/Feature1.cpp | 47, 78-89 | feature: isAdmin flag; vetoing a feature without admin -> rpcNO_PERMISSION; reply is role-aware (getJson(feature, isAdmin)). |
| E-17 | src/xrpld/overlay/detail/OverlayImpl.cpp | 690-691 | Manifest rate-limit cap policy: trusted peers uncapped, untrusted capped (overlay only, not RPC). |
| E-18 | src/xrpld/rpc/handlers/TransactionEntry.cpp | 54-60 | transaction_entry: "We don't support any transaction yet" -> notYetImplemented. |
| E-19 | src/xrpld/rpc/detail/Role.cpp | 125-131 | isUnlimited: ADMIN or IDENTIFIED roles only. |

## Live endpoints probed

- Public JSON-RPC: https://rpc.testnet.postfiat.org (68 calls + 12-request burst, 2026-11-26T04:17:28Z).
- Agent API: https://tasknode.postfiat.org (6 probes + 5-request burst, 2026-11-26T04:18:58Z).

## Prior packs whose numbers are re-verified here

- Amendment-governance pack: 101 amendments (64 enabled / 37 disabled) — re-verified live by the `feature` probe (M-07) and by `exclusion_info` returning `notEnabled` (R-12).
- Validator key-management pack: validator master key nHBAToXoTH6eZtC1cMJDvjG7eRb7ufZ3GUpeisvNVT4ofruRdVvd — re-verified live by the `manifest` probe returning details (domain app.w.ai, seq 1) (M-10).
- Prior-window network pack: the 122-request figure is carried forward as [UNSUPPORTED] U-07; it was not re-measured here.

## What this pack does not claim

- No rate-limit threshold is claimed (U-01). No admin-password configuration is claimed (U-02). No claim is made about other public nodes (U-03) or about authenticated /api/tasks behavior (U-05).
