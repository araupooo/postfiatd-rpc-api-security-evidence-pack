# Probe Report

## RPC probe — https://rpc.testnet.postfiat.org

Window: 2026-11-26T04:17:28Z. One request per PROBE/REFUSAL method (68 calls),
then a 12-request `server_info` burst (0.25 s apart). 0.15 s delay between
calls. Read-only; no state-changing calls; no credentials. Full unedited log:
`outputs/rpc_probe.log`; raw records: `outputs/rpc_probe_raw.json`.

Summary: called=68 result=21 error-result=24 error=0 http403=23 http401=0
http429=0 burst_n=12 burst_429=0.

Latency: min 818.3 ms, median 977.5 ms, max 1562.7 ms (68 calls).

### True results (21)

account_tx, book_changes, book_offers, feature, fee, gateway_balances, ledger,
ledger_closed, ledger_current, ledger_data, ledger_header, manifest, owner_info,
ping, random, server_definitions, server_info, server_state, tx_reduce_relay,
validator_votes, version.

### Error-results (24, all HTTP 200 with an error in the result body)

| Method | Error | Code |
|---|---|---|
| account_channels | actNotFound | 19 |
| account_currencies | actNotFound | 19 |
| account_info | actNotFound | 19 |
| account_lines | actNotFound | 19 |
| account_nfts | actNotFound | 19 |
| account_objects | actNotFound | 19 |
| account_offers | actNotFound | 19 |
| amm_info | actMalformed | 35 |
| channel_verify | invalidParams | 31 |
| deposit_authorized | srcActNotFound | 67 |
| exclusion_info | notEnabled | 12 |
| get_aggregate_price | invalidParams | 31 |
| ledger_entry | entryNotFound | 98 |
| nft_buy_offers | invalidParams | 31 |
| nft_sell_offers | invalidParams | 31 |
| noripple_check | invalidParams | 31 |
| path_find | invalidParams | 31 |
| ripple_path_find | dstAmtMalformed | 51 |
| subscribe | invalidParams | 31 |
| transaction_entry | notYetImplemented | - |
| tx | txnNotFound | 29 |
| tx_history | invalidParams | 31 |
| unsubscribe | invalidParams | 31 |
| vault_info | malformedRequest | 31 |

All account_* probes used the genesis test account; `actNotFound` is the
expected response for an unknown account, not a refusal. `exclusion_info`
returning `notEnabled` (code 12) re-verifies the governance pack live
(PF_AccountExclusion is disabled). `transaction_entry` returning
`notYetImplemented` is a dead method in the table (R-08). `subscribe` /
`unsubscribe` returning `invalidParams` (code 31) is the websocket-only
transport requirement (R-10).

### Refusals (23, all HTTP 403)

blacklist, can_delete, connect, consensus_info, fetch_info, get_counts,
ledger_accept, ledger_cleaner, ledger_request, log_level, logrotate,
peer_reservations_add, peer_reservations_del, peer_reservations_list, peers,
print, stop, unl_list, validation_create, validator_info,
validator_list_sites, validators, wallet_propose.

Every refusal is HTTP 403 with an 11-byte plain-text body (`Forbidden`) and
`Server: Caddy`. The 403 is emitted by rippled itself (ServerHandler.cpp:752-757)
via the in-tree FORBID path (R-13). No HTTP 401 was observed; the
`rpcNO_PERMISSION` -> 401 path (RPCHandler.cpp:167, ErrorCodes.cpp:100) is a
different code path the public HTTP endpoint never reaches for these calls.

### Server snapshot

- server_info: build 1.0.9, network id 2025, complete ledgers 8300054-8374370,
  peers 21, hostid MUFF, node public key
  n9K4AomBUHA8XGwXtZs6qfCjXm5aXre9UchiD6oGuZx1UeRLUweE.
- Ports: 2559 peer, 6005 ws, 50051 grpc.
- ledger_current_index: 8374362.
- fee drops: base_fee 10, median_fee 5000, minimum_fee 10, open_ledger_fee 10.
- feature: 101 amendments, 64 enabled, 37 disabled (0 changes vs the
  amendment-governance pack window).
- manifest (master key nHBAToXoTH6eZtC1cMJDvjG7eRb7ufZ3GUpeisvNVT4ofruRdVvd):
  domain app.w.ai, seq 1.
- All 68 responses: `Server: Caddy`, `Content-Type: application/json;
  charset=UTF-8`. The 403 responses additionally carry a second Server
  header, `postfiat-json-rpc/postfiatd-1.0.9` (observed by direct header
  inspection 2026-11-26T04:52:33Z; urllib's `get("Server")` returns only the
  first header, so the raw records show `Caddy`).

## Agent API probe — https://tasknode.postfiat.org

Window: 2026-11-26T04:18:58Z. 6 probes (P-01..P-06, same set as the prior
window) + a 5-request GET /api/tasks burst (0.5 s apart). Read-only, no
credentials. Full unedited log: `outputs/api_probe.log`; raw records:
`outputs/api_probe_raw.json`.

| Probe | Request | Result |
|---|---|---|
| P-01 | GET / | 200, 1,141 bytes (SPA shell) |
| P-02 | GET /robots.txt | 404, 66 bytes |
| P-03 | GET /api | 200, 1,141 bytes (same SPA shell) |
| P-04 | GET /api/tasks | 200, 1,970 bytes, UNAUTHENTICATED-JSON-READ |
| P-05 | POST /api/tasks | 405, 128 bytes |
| P-06 | POST /api/tasks | 405, 128 bytes |

Burst: 5 x GET /api/tasks, all HTTP 200, 1,970 bytes each, 0 x 429.

P-04 body top keys: dailyRewardCap (8), networkTasks, requests, outstanding,
verification, refused, rewarded, sync, reinstatement. The response exposes the
internal eligibility policy (schema `pf.task_node.network_task_eligibility.v1`,
`requiresSignedInAccount`, `requiresLinkedPftWallet`,
`requiresNetworkTaskOperatingBadge`), the account gate list, and per-wallet
sync status — with walletAddress null, requestCount 0, and all record lists
empty (A-01, R-14). No Server or Content-Type header was observed on any API
response.

## Negative searches

Full log: `outputs/negative_search.log` (re-runnable:
`bash scripts/negative_search.sh`).

| ID | Search | Result |
|---|---|---|
| N-1 | Per-method auth beyond the table roles (`admin_password` / `passwordUnrequired` in src/xrpld/rpc/) | 12 hits, all plumbing (port/client setup and role checks); none per-method |
| N-2 | Rate limiting / throttling in src/xrpld/rpc/ | 0 hits |
| N-2b | Same terms across all of src/ | Manifest rate limiting (ManifestRateLimitCapPolicy) + ValidatorExclusionManager change throttling only |
| N-3 | `api/tasks` in the pinned tree | 0 hits |
| N-4 | Switch to disable sign/submit on a public node | 0 hits |
| N-5 | Per-method allowlist/blocklist in src/xrpld/rpc/ | 0 hits |
| N-6 | HTTP 403 / `forbidden` emitters in-tree | 5 hits, all in ServerHandler.cpp (:303, :311, :609, :757, :761) |
| N-7 | `passwordUnrequiredOrSentCorrect` call sites | Role.cpp:30 (definition), :34, :91 |
