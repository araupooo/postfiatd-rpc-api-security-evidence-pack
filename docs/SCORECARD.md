# Scorecard

Scale 0-5, higher is better. Machine-readable form: `data/scorecard.json`.
Overall: **2.5 / 5** — mean of the six surface scores
(5 + 2 + 0 + 4 + 3 + 1) / 6 = 2.5.

| Surface | Score | Basis |
|---|---|---|
| Inventory completeness | 5 | 74/74 methods mapped to handler file:line, table role, and condition; 72 table entries plus `ledger` and `version` from addHandler; every row carries a probe class and reason. |
| Authentication / authorization | 2 | Table roles are enforced (23 ADMIN methods refused with 403). But admin degrades to an IP allowlist when no admin password is set (Role.cpp:36), and there is no per-method authentication beyond the table roles (N-1: 12 hits, all plumbing). |
| Rate limiting | 0 | No rate limiting for public RPC anywhere in `src/xrpld/rpc/` (N-2: 0 hits). Only overlay manifest rate limiting and ValidatorExclusionManager change throttling exist tree-wide. 0 HTTP 429 observed in 68 calls + 12-request burst + 5-request API burst. |
| Refusal consistency | 4 | All 23 ADMIN methods refused identically (HTTP 403, 11-byte plain-text body) via the in-tree FORBID path. One inconsistency: `ledger` full/accounts is refused with `rpcNO_PERMISSION` (HTTP 401) by a second in-handler gate the table does not show. |
| Data leakage | 3 | No per-user data leaked in any probe. But `server_info` fingerprints the node (build, hostid, pubkey, ports, peers) and `manifest` enables validator enumeration. |
| Agent API | 1 | GET /api/tasks returns internal task state without authentication (fresh re-probe). POST /api/tasks correctly returns 405. No rate limiting observed on the API either (5-request burst, 0 x 429). |

Overall basis: the surface is inventory-complete and refusal-consistent, but
rate limiting is absent, the agent API is unauthenticated, and admin auth can
degrade to an IP allowlist.
