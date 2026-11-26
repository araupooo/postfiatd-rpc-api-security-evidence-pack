# Claim Index

Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
Probe window: 2026-11-26T04:17:28Z (RPC) and 2026-11-26T04:18:58Z (agent API).
Labels: [MEASURED] = observed in this pack's live probe or verified against the
pinned checkout; [SIMULATED] = no simulation in this pack (the section is
empty by design); [UNSUPPORTED] = could not be verified from the evidence.

## Measured

| ID | Claim | Evidence |
|---|---|---|
| M-01 | The public JSON-RPC surface has 74 methods: 72 table entries in Handler.cpp plus `ledger` and `version` from addHandler. 23 ADMIN, 51 USER. | `data/method_inventory.json` (74 rows); `data/source_excerpts.json` E-01 (Handler.cpp:83-201), E-02 (:248-249), E-03 (LedgerHandler.h:63-71), E-04 (Version.h:49-57) |
| M-02 | 68 methods called, 6 skipped. Outcomes: 21 true results, 24 error-results, 23 HTTP 403, 0 HTTP 401, 0 HTTP 429. | `outputs/rpc_probe.log:97` (summary line); `outputs/rpc_probe_raw.json` (68 called records) |
| M-03 | Rate-limit bursts saw no refusal: 12 x server_info (0.25 s apart) all HTTP 200, 0 x 429; 5 x GET /api/tasks (0.5 s apart) all HTTP 200, 0 x 429. | `outputs/rpc_probe.log:98-110` (burst); `outputs/api_probe.log:8-12` (burst) |
| M-04 | All 23 ADMIN methods are refused with HTTP 403 and an 11-byte plain-text body (`Forbidden`). | `outputs/rpc_probe_raw.json` (23 REFUSAL records, http 403, body `Forbidden\r\n`) |
| M-05 | GET /api/tasks returns HTTP 200, 1,970 bytes of JSON, unauthenticated. Top keys: dailyRewardCap, networkTasks, requests, outstanding, verification, refused, rewarded, sync, reinstatement. | `outputs/api_probe.log:5` (P-04 line); `outputs/api_probe_raw.json` P-04 record |
| M-06 | server_info: build 1.0.9, network id 2025, complete ledgers 8300054-8374370, peers 21, hostid MUFF, node public key n9K4AomBUHA8XGwXtZs6qfCjXm5aXre9UchiD6oGuZx1UeRLUweE. Ports: 2559 peer, 6005 ws, 50051 grpc. | `outputs/rpc_probe_raw.json` server_info record |
| M-07 | The feature method returns 101 amendments: 64 enabled, 37 disabled. Both PostFiat-specific amendments (PF_AccountExclusion, PF_ValidatorVoteTracking) are disabled. 0 changes vs the amendment-governance pack window. | `outputs/rpc_probe_raw.json` feature record (101 features) |
| M-08 | RPC call latency: min 818.3 ms, median 977.5 ms, max 1562.7 ms (68 calls). | `outputs/rpc_probe_raw.json` (latency_ms fields) |
| M-09 | exclusion_info returns error `notEnabled` (code 12): `PF_AccountExclusion feature is not enabled`. | `outputs/rpc_probe_raw.json` exclusion_info record |
| M-10 | manifest with master key nHBAToXoTH6eZtC1cMJDvjG7eRb7ufZ3GUpeisvNVT4ofruRdVvd returns details: domain app.w.ai, seq 1. | `outputs/rpc_probe_raw.json` manifest record |
| M-11 | ledger_current_index is 8374362 at probe time. | `outputs/rpc_probe_raw.json` ledger_current record |
| M-12 | fee drops: base_fee 10, median_fee 5000, minimum_fee 10, open_ledger_fee 10. | `outputs/rpc_probe_raw.json` fee record |
| M-13 | All 68 RPC responses carry `Server: Caddy` and `Content-Type: application/json; charset=UTF-8`. The agent API responses carry no Server or Content-Type header. The 403 responses additionally carry a second Server header, `postfiat-json-rpc/postfiatd-1.0.9` (direct header inspection 2026-11-26T04:52:33Z). | `outputs/rpc_probe_raw.json` (server_header Caddy on 68/68); `outputs/api_probe_raw.json` (server_header null on 6/6) |
| M-14 | The HTTP 403 for ADMIN methods is emitted by rippled itself: ServerHandler.cpp computes the role via requestRole and returns HTTP 403 when the role is FORBID. | `data/source_excerpts.json` E-10 (ServerHandler.cpp:703-724), E-11 (:752-757), E-07 (Role.cpp:96-120) |
| M-15 | No per-user data leaked in any probe: account_* return actNotFound (code 19) for the genesis test account; /api/tasks has walletAddress null, requestCount 0, all record lists empty. | `outputs/rpc_probe_raw.json` error-result records; `outputs/api_probe_raw.json` P-04 record |

## Simulated

None. This pack contains no simulations. Every claim is either measured
above or unsupported below.

## Unsupported

| ID | Claim | Why it stays unsupported |
|---|---|---|
| U-01 | The rate-limit threshold of the public RPC endpoint (if any). | 0 HTTP 429 in 68 calls + a 12-request burst is absence of a signal, not a measured limit. |
| U-02 | Whether the public RPC port has an admin password configured. | Not observable from outside; the 403s are consistent with either configuration. |
| U-03 | Whether sign/submit are blocked on other public nodes. | Only https://rpc.testnet.postfiat.org was probed. |
| U-04 | The Caddy routing details (which backend node served each request). | Only the Server header is visible; backend topology is not. |
| U-05 | Whether /api/tasks returns per-user data when authenticated. | Probes were unauthenticated by design; no credentials were used. |
| U-06 | The load-shedding threshold (HTTP 503) of the public endpoint. | Never triggered in this window. |
| U-07 | The 122-request figure from the prior window. | Carried forward from the prior pack's artifacts; not re-measured here. |
