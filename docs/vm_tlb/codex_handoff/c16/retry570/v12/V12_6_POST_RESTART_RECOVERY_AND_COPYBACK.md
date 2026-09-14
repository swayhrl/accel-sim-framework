# C16 V12.6 — Post-restart recovery and verified copyback

## Authority

- Active scientific branch: `hrl/vm-c16-g-retry570-v0`
- Reviewed active HEAD: `ef0d89b1ce297518f86c51cddce190abd47e7364`
- Frozen shutdown manifest:
  `docs/vm_tlb/review_packs/C16_H_MEMORY_FINGERPRINT/ROUTE_B_CAPTURE_CONTRACT_V1/LLAMA_RENTAL_SHUTDOWN_MANIFEST.json`
- The rental server has been restarted after an unexpected billing shutdown.

## Immediate policy

Data recovery has priority over new GPU work until all P0 critical artifacts are locally size-and-SHA closed.

Do not run model workloads, nsys, NVBit, NCU, CUTLASS owner probes, canary or formal capture while P0 recovery is incomplete.

Do not delete or modify any sole remote artifact.

Do not mutate the Lane-A active scientific worktree from the copyback lane.

Use the existing Lane-B local destination and queue conventions. Do not invent a second copyback tree if a canonical destination already exists.

## P0 — five critical remote artifacts

The following identities are frozen before restart and are the only acceptance authority for P0.

| role | remote path | bytes | SHA-256 |
| --- | --- | ---: | --- |
| Q1 tiny dynamic raw | `/root/autodl-tmp/c16_retry570/route_b_q1_ac36cbdc/runs/q1_tiny_88168889_20260914T072246Z/raw.jsonl` | 502744 | `420ab3b009bcf20975bde9a38d3792f84882ee4977f8254464bdf8ca07fb1a0b` |
| Q2 Prefill static map | `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_prefill_static_map/ffb46485-1432-4c19-9966-08253b77bf88/raw/EXACT_FUNCTION_STATIC_MAP.tsv` | 110617 | `aa256fac6f71749a420a20b9988928867e1ed7c8d3232dcf6113c40097dbfa13` |
| Q2 Prefill dynamic raw | `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_prefill_dynamic/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/raw.jsonl` | 729983913 | `cf60a7e063524c080593cef9aea409da0af3e8cad9020a28ed3e416f88725667` |
| Q2 Decode static map | `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_decode_static_map/777d7cef-c45c-430d-8d0d-f3535c126d67/raw/EXACT_FUNCTION_STATIC_MAP.tsv` | 88627 | `a8d55ddb4f196ec61de93a38d3fbdba8ee935b3a05ab76242e98a589448dbe1d` |
| Q2 Decode dynamic raw | `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_decode_dynamic/391deb99-0430-4a19-8a2d-b2bf62243266/raw.jsonl` | 16863304 | `9ff9ad5481d08d1d88653697fa6086b94965344ffd38feb7169e6c6801d20b8c` |

## P0 procedure

1. Read-only post-restart audit first:
   - confirm every path exists;
   - confirm file type is regular file;
   - confirm byte count equals the frozen value;
   - record free disk space and mount/device identity if available;
   - do not regenerate or overwrite any artifact.

2. Copy one artifact at a time with a resumable transfer method. Existing partial local files may be resumed only if the method verifies the resumed prefix/content; otherwise recopy to a temporary destination.

3. After each copy:
   - `stat` local byte count;
   - compute local SHA-256;
   - require exact equality with the frozen pre-shutdown SHA above;
   - only then mark `LOCAL_SHA_CLOSED`.

4. If local SHA does not equal frozen SHA:
   - do not overwrite the failed local copy;
   - compute remote SHA-256 for that artifact to distinguish remote corruption from transfer corruption;
   - record both values and fail closed;
   - do not delete either copy.

5. P0 acceptance is exactly `5/5 LOCAL_SHA_CLOSED`.

## P0 recovery receipt

Publish a compact receipt on an independent transfer/recovery branch, not the active scientific branch:

`POST_RESTART_RECOVERY_RECEIPT_V1.json`

Required fields per artifact:

- role
- remote_path
- frozen_remote_bytes
- frozen_remote_sha256
- post_restart_exists
- post_restart_remote_bytes
- local_path
- local_bytes
- local_sha256
- status = `LOCAL_SHA_CLOSED` or explicit fail-closed reason
- transfer_started_utc / transfer_finished_utc
- resumable_method_used

Top-level fields:

- active_scientific_head = `ef0d89b1ce297518f86c51cddce190abd47e7364`
- shutdown_manifest_blob/source identity
- p0_total = 5
- p0_local_sha_closed
- server_restart_observed = true
- no_remote_deletion = true

Commit and push this compact receipt after P0 is closed.

## P1 — Llama S0 supporting evidence

After P0 is 5/5, recover all remaining Llama S0 `COPYBACK_READY` evidence, in this order:

1. Llama S0 campaign G1 `.nsys-rep` and SQLite export.
2. Their export validation / runner / source manifests if not already local.
3. All 34 `MAPPED_EXACT` Route-B V2 static-map payloads.
4. Q2 Prefill/Decode parse manifests, receipts, whitelists, producer manifests, and fresh-map parent receipts not already copied with P0.
5. CUTLASS owner bounded-diagnostic raw/registries/parent receipts where present; compact Git publication alone is not a substitute if remote raw exists.

Discover exact P1 entries from the existing `COPYBACK_QUEUE` plus Git-published compact receipts. Do not infer paths from names when the queue already has exact paths.

Each P1 artifact must also close local size + SHA against its frozen remote authority before being marked local-complete.

## P2 — other scientific campaign evidence

After all Llama P1 items are locally closed, continue with:

1. Qwen0 S3 Prefill formal R6 raw + compact tree contents.
2. Qwen0 S3 successful R5/repro address-bearing raw/map/log evidence.
3. Qwen0/Qwen7 campaign G1 raw reports and SQLite artifacts.
4. Other `COPYBACK_READY` scientific artifacts by recency/uniqueness.

Do not spend time copying model packages, wheelhouses, or replaceable caches while unique scientific raw remains remote-only.

## GPU restart rule

Lane A must remain GPU-idle until P0 reaches 5/5 `LOCAL_SHA_CLOSED`.

After P0 closes, GPU work may resume only by explicit user decision. The current scientific state remains:

- Q1 PASS;
- Q2 Prefill/Decode dynamic address evidence remote-SHA-closed;
- Q2 Route-A structural bridge not closed because `C16_ROUTE_A_BRIDGE_REFERENCE_V1` is absent;
- CUTLASS actual-owner closure remains fail-closed;
- representative selection/canary/formal/Route-C remain blocked under the current coverage contract.

Recovery work must not silently weaken those gates.

## Expected Lane-B report

Report at minimum:

```text
POST_RESTART_REMOTE_AUDIT=PASS|FAIL
P0_TOTAL=5
P0_LOCAL_SHA_CLOSED=<n>
P0_FAILED=<n>
P0_COPYING=<role|none>
P1_DISCOVERED=<n>
P1_LOCAL_SHA_CLOSED=<n>
P2_DISCOVERED=<n>
P2_LOCAL_SHA_CLOSED=<n>
LOCAL_DESTINATION_ROOT=<existing canonical root>
REMOTE_DATA_FREE_BYTES=<n>
REMOTE_DELETION_COUNT=0
RECOVERY_RECEIPT_COMMIT=<sha-or-pending>
```

Do not declare recovery complete until P0 is 5/5 and the compact receipt is pushed.