# Remediation

Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
Each finding carries a `source_ref` (the exact file:line or log line that
anchors it) in `data/risk_register.json`. The risk register is the
authoritative list; this document is the human-readable companion.

## A-01 (HIGH) — Authenticate GET /api/tasks

GET https://tasknode.postfiat.org/api/tasks returns HTTP 200 with a 1,970-byte
JSON body to an unauthenticated caller. The body exposes the internal
eligibility policy (schema `pf.task_node.network_task_eligibility.v1`,
`requiresSignedInAccount`, `requiresLinkedPftWallet`,
`requiresNetworkTaskOperatingBadge`), the account gate list, `dailyRewardCap`
(8), and per-wallet sync status. No per-user data leaked in the observed
response (walletAddress null, requestCount 0, all record lists empty), so this
is HIGH, not CRITICAL. The finding persists from the prior window: same
endpoint, same shape, fresh re-probe.

Source: `outputs/api_probe.log` (P-04 line); `outputs/api_probe_raw.json`
(P-04 record: http 200, bytes 1970, tag UNAUTHENTICATED-JSON-READ).

Fix: require authentication on GET /api/tasks. Until then, do not treat its
response as private. Open design decision D-01 (auth scheme: API key vs wallet
signature vs session cookie) is unspecified.

## R-01 (MEDIUM) — Block state-changing and secret-bearing methods on the public endpoint

`submit`, `submit_multisigned`, `sign`, `sign_for`, `channel_authorize`, and
`simulate` are listed in the handler table as USER methods and are therefore
reachable on the public endpoint. They were not called (SKIP, by design).
There is no in-tree switch to disable sign/submit on a public node (negative
search N-4: 0 hits). A caller who sends a private key to `sign` would hand it
to the operator.

Source: `data/method_inventory.json` (submit, submit_multisigned, sign,
sign_for, channel_authorize, simulate rows, probe_class SKIP);
`outputs/negative_search.log` (N-4 count 0).

Fix: proxy-block these six methods on the public endpoint. Open design
decision D-03 (remove from the public table vs proxy-block) is unspecified.

## R-02 (MEDIUM) — Add public RPC rate limiting

Negative search N-2 finds 0 rate-limit/throttle hits in `src/xrpld/rpc/`.
The only rate-limit terms tree-wide are overlay manifest rate limiting
(`ManifestRateLimitCapPolicy`, uncapped for trusted peers) and
ValidatorExclusionManager change throttling. The live probe saw 0 HTTP 429 in
68 calls + a 12-request burst (0.25 s apart) and 0 in a 5-request /api/tasks
burst. The actual rate-limit threshold, if any exists outside the tree, is
[UNSUPPORTED] (U-01): zero 429s is absence of a signal, not a measured limit.

Source: `outputs/negative_search.log` (N-2 count 0 in rpc/, N-2b manifest /
exclusion only); `data/source_excerpts.json` E-17 (OverlayImpl.cpp:690-691).

Fix: add RPC rate limiting with published thresholds and burst policy. Open
design decision D-02 (thresholds) is unspecified.

## R-03 (MEDIUM) — Set an admin password; do not rely on the IP allowlist alone

`passwordUnrequiredOrSentCorrect` returns true when `admin_user` /
`admin_password` are empty, so a request from an admin IP is admin without any
credential. `isAdmin` requires both the IP check AND the password check only
when a password is set. Whether the public port has a password configured is
not observable from outside ([UNSUPPORTED] U-02), but the code path means a
misconfigured port exposes all 23 ADMIN methods to anyone on an admin net.

Source: `data/source_excerpts.json` E-06 (Role.cpp:28-46), E-07
(Role.cpp:96-120).

Fix: set `admin_user` / `admin_password` on every public port and restrict
admin nets to operator IPs. Open design decision D-04 (password policy) is
unspecified.

## R-04 (MEDIUM) — Add per-method authentication for public nodes

Negative search N-1 finds 12 hits for `admin_password` / `passwordUnrequired`
in `src/xrpld/rpc/`, all of them port/client setup and role-check plumbing;
none is per-method. Any unauthenticated caller (GUEST role) can call any USER
method, including state-changing ones (see R-01). The table's Condition enum
describes ledger state, not mutability, so operators cannot tell from the
table which methods mutate state.

Source: `outputs/negative_search.log` (N-1 count 12);
`data/source_excerpts.json` E-01 (Handler.cpp:83-201).

Fix: add a per-method allowlist/blocklist configuration for public nodes.

## R-05 (LOW) — Align the ledger table role with the in-handler gate

The table lists `ledger` as Role USER with NO_CONDITION, but
LedgerHandler.cpp returns `rpcNO_PERMISSION` unless the caller has an
unlimited role (ADMIN or IDENTIFIED). A USER caller requesting a full ledger
or accounts gets `rpcNO_PERMISSION` (HTTP 401). The table understates the
restriction; the real policy lives in the handler body.

Source: `data/source_excerpts.json` E-15 (LedgerHandler.cpp:67-71), E-19
(Role.cpp:125-131).

Fix: make `ledger` full/accounts ADMIN in the table, or document the second
gate. Open design decision D-05 is unspecified.

## R-06 (LOW) — Reduce server_info fingerprinting

`server_info` (USER) returns build version 1.0.9, network id 2025, complete
ledger range, hostid MUFF, the node public key, port list (2559 peer, 6005 ws,
50051 grpc), and peer counts (21). Useful for fingerprinting and targeting a
specific build; no per-user data.

Source: `outputs/rpc_probe_raw.json` (server_info record: build 1.0.9, hostid
MUFF, peers 21).

## R-07 (LOW) — manifest enables validator enumeration

`manifest` (USER) takes a master key and returns the full manifest (domain,
ephemeral key, seq). Probed with the validator master key from the
key-management pack: returns details (domain app.w.ai, seq 1). Public by
design, but it lets anyone enumerate validator domains and sequence numbers.

Source: `outputs/rpc_probe_raw.json` (manifest record: domain app.w.ai, seq 1).

## R-08 (LOW) — transaction_entry is dead in the table

`transaction_entry` returns `notYetImplemented` for a current-ledger query
("We don't support any transaction yet"). The method is dead in the table;
callers cannot distinguish it from a working method without calling it.

Source: `data/source_excerpts.json` E-18 (TransactionEntry.cpp:54-60);
`outputs/rpc_probe_raw.json` (transaction_entry record, error
notYetImplemented).

## R-09 (LOW) — SPA shell masks 404s on the agent API

GET / and GET /api both return HTTP 200 with the same 1,141-byte SPA shell;
only /robots.txt returns 404 (66 B). The routing fallback makes it impossible
to distinguish a real route from a missing one by status code alone.

Source: `outputs/api_probe_raw.json` (P-01 200/1141 B, P-03 200/1141 B, P-02
404/66 B).

## R-10 (LOW) — subscribe/unsubscribe are websocket-only but listed as plain USER methods

`subscribe` and `unsubscribe` over HTTP JSON-RPC return `invalidParams`
(code 31). The table lists them as USER methods with NO_CONDITION and no
transport note, so a reader of the table cannot tell they require a websocket.

Source: `outputs/rpc_probe_raw.json` (subscribe record invalidParams code 31,
unsubscribe record invalidParams code 31).

## R-11 (INFO) — feature listing is role-aware (a working control)

Feature1.cpp returns `rpcNO_PERMISSION` for vetoing a feature without admin,
and the feature list itself is rendered with `getJson(feature, isAdmin)`, so
admin-only fields are hidden from USER callers. This is the one place where
the handler applies a finer-grained check than the table role.

Source: `data/source_excerpts.json` E-16 (Feature1.cpp:47,78-89).

## R-12 (INFO) — exclusion_info confirms PF_AccountExclusion is disabled

`exclusion_info` returns error `notEnabled` (code 12): "PF_AccountExclusion
feature is not enabled". This independently re-verifies the
amendment-governance pack's live inventory (101 amendments, 64 enabled / 37
disabled, both PostFiat-specific amendments disabled).

Source: `outputs/rpc_probe_raw.json` (exclusion_info record, error notEnabled,
code 12).

## R-13 (INFO) — The observed 403s are rippled's own, not the proxy's

All 68 RPC responses carry `Server: Caddy` and `Content-Type: application/json;
charset=UTF-8`. The 403 responses additionally carry a second Server header,
`postfiat-json-rpc/postfiatd-1.0.9` (direct header inspection
2026-11-26T04:52:33Z). The 23 ADMIN refusals are HTTP 403 with an 11-byte plain-text
body (`Forbidden`). The 403 is emitted by rippled itself: ServerHandler.cpp
computes the role via `requestRole` and returns HTTP 403 when the role is
FORBID (ServerHandler.cpp:752-757). The earlier hypothesis that a proxy does
the refusing is wrong; the in-tree path is confirmed by negative search N-6
(5 hits, all in ServerHandler.cpp).

Source: `outputs/rpc_probe_raw.json` (server_header Caddy on 68/68 records;
403 body `Forbidden`, 11 bytes); `data/source_excerpts.json` E-11
(ServerHandler.cpp:752-757).

## R-14 (INFO) — No per-user data leaked in any probe

All account_* probes against the genesis test account return `actNotFound`
(code 19); `ledger_entry` returns `entryNotFound` (98); `tx` returns
`txnNotFound` (29). The /api/tasks response has walletAddress null,
requestCount 0, and all record lists empty. The unauthenticated read (A-01)
exposes policy and configuration, not personal data.

Source: `outputs/rpc_probe_raw.json` (error-result records: actNotFound 19,
entryNotFound 98, txnNotFound 29); `outputs/api_probe_raw.json` (P-04 record:
walletAddress null, requestCount 0).
