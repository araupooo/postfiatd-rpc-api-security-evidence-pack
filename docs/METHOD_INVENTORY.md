# Method Inventory

Pinned postfiatd revision: `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10).
Source: `src/xrpld/rpc/detail/Handler.cpp` handlerArray (E-01, lines 83-201),
plus `ledger` and `version` from addHandler (E-02/E-03/E-04).
Every row is verified against the vendored table by `scripts/check_inventory.py`.

Totals: **74 methods — ADMIN 23, USER 51; PROBE 45, REFUSAL 23, SKIP 6**.

| Method | Role | Condition | Probe class | Handler | Observed |
|---|---|---|---|---|---|
| account_channels | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountChannels.cpp:68 | HTTP 200 error-result 19 |
| account_currencies | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountCurrenciesHandler.cpp:32 | HTTP 200 error-result 19 |
| account_info | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountInfo.cpp:50 | HTTP 200 error-result 19 |
| account_lines | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountLines.cpp:81 | HTTP 200 error-result 19 |
| account_nfts | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountObjects.cpp:50 | HTTP 200 error-result 19 |
| account_objects | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountObjects.cpp:181 | HTTP 200 error-result 19 |
| account_offers | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountOffers.cpp:57 | HTTP 200 error-result 19 |
| account_tx | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AccountTx.cpp:408 | HTTP 200 result |
| amm_info | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/AMMInfo.cpp:76 | HTTP 200 error-result 35 |
| blacklist | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/BlackList.cpp:29 | HTTP 403 |
| book_changes | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/BookOffers.cpp:222 | HTTP 200 result |
| book_offers | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/BookOffers.cpp:37 | HTTP 200 result |
| can_delete | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/CanDelete.cpp:35 | HTTP 403 |
| channel_authorize | USER | NO_CONDITION | SKIP | src/xrpld/rpc/handlers/PayChanClaim.cpp:42 | SKIP (not called) |
| channel_verify | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/PayChanClaim.cpp:113 | HTTP 200 error-result 31 |
| connect | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Connect.cpp:39 | HTTP 403 |
| consensus_info | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/ConsensusInfo.cpp:30 | HTTP 403 |
| deposit_authorized | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/DepositAuthorized.cpp:41 | HTTP 200 error-result 67 |
| exclusion_info | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/ExclusionInfo.cpp:35 | HTTP 200 error-result 12 |
| feature | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Feature1.cpp:36 | HTTP 200 result |
| fee | USER | NEEDS_CURRENT_LEDGER | PROBE | src/xrpld/rpc/handlers/Fee1.cpp:30 | HTTP 200 result |
| fetch_info | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/FetchInfo.cpp:30 | HTTP 403 |
| gateway_balances | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/GatewayBalances.cpp:54 | HTTP 200 result |
| get_aggregate_price | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/GetAggregatePrice.cpp:153 | HTTP 200 error-result 31 |
| get_counts | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/GetCounts.cpp:138 | HTTP 403 |
| ledger | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/LedgerHandler.h:63 | HTTP 200 result |
| ledger_accept | ADMIN | NEEDS_CURRENT_LEDGER | REFUSAL | src/xrpld/rpc/handlers/LedgerAccept.cpp:34 | HTTP 403 |
| ledger_cleaner | ADMIN | NEEDS_NETWORK_CONNECTION | REFUSAL | src/xrpld/rpc/handlers/LedgerCleanerHandler.cpp:30 | HTTP 403 |
| ledger_closed | USER | NEEDS_CLOSED_LEDGER | PROBE | src/xrpld/rpc/handlers/LedgerClosed.cpp:30 | HTTP 200 result |
| ledger_current | USER | NEEDS_CURRENT_LEDGER | PROBE | src/xrpld/rpc/handlers/LedgerCurrent.cpp:30 | HTTP 200 result |
| ledger_data | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/LedgerData.cpp:46 | HTTP 200 result |
| ledger_entry | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/LedgerEntry.cpp:755 | HTTP 200 error-result 98 |
| ledger_header | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/LedgerHeader.cpp:34 | HTTP 200 result |
| ledger_request | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/LedgerRequest.cpp:36 | HTTP 403 |
| log_level | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/LogLevel.cpp:34 | HTTP 403 |
| logrotate | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/LogRotate.cpp:29 | HTTP 403 |
| manifest | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/DoManifest.cpp:30 | HTTP 200 result |
| nft_buy_offers | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/NFTOffers.cpp:165 | HTTP 200 error-result 31 |
| nft_sell_offers | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/NFTOffers.cpp:151 | HTTP 200 error-result 31 |
| noripple_check | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/NoRippleCheck.cpp:62 | HTTP 200 error-result 31 |
| owner_info | USER | NEEDS_CURRENT_LEDGER | PROBE | src/xrpld/rpc/handlers/OwnerInfo.cpp:35 | HTTP 200 result |
| path_find | USER | NEEDS_CURRENT_LEDGER | PROBE | src/xrpld/rpc/handlers/PathFind.cpp:33 | HTTP 200 error-result 31 |
| peer_reservations_add | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Reservations.cpp:36 | HTTP 403 |
| peer_reservations_del | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Reservations.cpp:89 | HTTP 403 |
| peer_reservations_list | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Reservations.cpp:116 | HTTP 403 |
| peers | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Peers.cpp:33 | HTTP 403 |
| ping | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Ping.cpp:33 | HTTP 200 result |
| print | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Print.cpp:30 | HTTP 403 |
| random | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Random.cpp:39 | HTTP 200 result |
| ripple_path_find | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/RipplePathFind.cpp:33 | HTTP 200 error-result 51 |
| server_definitions | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/ServerInfo.cpp:299 | HTTP 200 result |
| server_info | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/ServerInfo.cpp:322 | HTTP 200 result |
| server_state | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/ServerState.cpp:30 | HTTP 200 result |
| sign | USER | NO_CONDITION | SKIP | src/xrpld/rpc/handlers/SignHandler.cpp:34 | SKIP (not called) |
| sign_for | USER | NO_CONDITION | SKIP | src/xrpld/rpc/handlers/SignFor.cpp:35 | SKIP (not called) |
| simulate | USER | NEEDS_CURRENT_LEDGER | SKIP | src/xrpld/rpc/handlers/Simulate.cpp:311 | SKIP (not called) |
| stop | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Stop.cpp:32 | HTTP 403 |
| submit | USER | NEEDS_CURRENT_LEDGER | SKIP | src/xrpld/rpc/handlers/Submit.cpp:45 | SKIP (not called) |
| submit_multisigned | USER | NEEDS_CURRENT_LEDGER | SKIP | src/xrpld/rpc/handlers/SubmitMultiSigned.cpp:34 | SKIP (not called) |
| subscribe | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Subscribe.cpp:38 | HTTP 200 error-result 31 |
| transaction_entry | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/TransactionEntry.cpp:38 | HTTP 200 error-result notYetImplemented |
| tx | USER | NEEDS_NETWORK_CONNECTION | PROBE | src/xrpld/rpc/handlers/Tx.cpp:286 | HTTP 200 error-result 29 |
| tx_history | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/TxHistory.cpp:39 | HTTP 200 error-result 31 |
| tx_reduce_relay | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/TxReduceRelay.cpp:29 | HTTP 200 result |
| unl_list | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/UnlList.cpp:30 | HTTP 403 |
| unsubscribe | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Unsubscribe.cpp:33 | HTTP 200 error-result 31 |
| validation_create | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/ValidationCreate.cpp:45 | HTTP 403 |
| validator_info | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/ValidatorInfo.cpp:31 | HTTP 403 |
| validator_list_sites | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/ValidatorListSites.cpp:29 | HTTP 403 |
| validator_votes | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/ValidatorVotes.cpp:46 | HTTP 200 result |
| validators | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/Validators.cpp:29 | HTTP 403 |
| vault_info | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/VaultInfo.cpp:79 | HTTP 200 error-result 31 |
| version | USER | NO_CONDITION | PROBE | src/xrpld/rpc/handlers/Version.h:49 | HTTP 200 result |
| wallet_propose | ADMIN | NO_CONDITION | REFUSAL | src/xrpld/rpc/handlers/WalletPropose.cpp:68 | HTTP 403 |

## Probe classes

- **PROBE (45):** called once with the params in `data/method_inventory.json` (`probe_params`).
- **REFUSAL (23):** called once; every one returned HTTP 403 with an 11-byte plain-text body (`Forbidden`).
- **SKIP (6):** never called. `submit`, `submit_multisigned` (state-changing: would broadcast a transaction); `sign`, `sign_for` (secret-bearing: signing requires a private key in the request); `channel_authorize` (secret-bearing: creates a payment-channel signature); `simulate` (heavy: transaction simulation).

## Notes

- The table's Condition enum describes ledger state (NO_CONDITION / NEEDS_CURRENT_LEDGER / NEEDS_CLOSED_LEDGER / NEEDS_VALIDATED_LEDGER), not mutability; operators cannot tell from the table which methods mutate state (R-04).
- `ledger` is listed as USER in the table, but a second in-handler check returns `rpcNO_PERMISSION` for full ledgers and accounts (R-05).
- `transaction_entry` is listed in the table but returns `notYetImplemented` (R-08).
- `subscribe` and `unsubscribe` return `invalidParams` (code 31) over HTTP JSON-RPC; they require a websocket (R-10).
