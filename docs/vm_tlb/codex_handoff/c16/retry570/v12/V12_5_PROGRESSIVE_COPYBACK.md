# V12.5 Progressive Copyback While Llama Remains Primary

## Decision

Primary GPU/science priority remains `Llama-3.2-1B / S0 / B1 / T128 / Decode4`.
Copyback now starts progressively in parallel, but it is subordinate to every GPU measurement window.
No copyback activity may delay, perturb, or overlap a Llama measurement.

The user alone decides whether/when the rented server is shut down.  This handoff only protects already-produced evidence and reduces shutdown risk.

## Transfer admission gate

Lane B may start one transfer batch only when all are true:

- `MEASUREMENT_ACTIVE=absent`;
- active GPU process count is zero;
- shared control says `transfer_slot_granted=true`;
- Lane B can acquire `GPU_IO_EXCLUSION.lock` without waiting on a measurement owner.

If any condition changes or Lane A announces a GPU-ready measurement, Lane B must finish/abort at a safe file boundary, release the lock, and yield immediately.
Do not hold the lock while idle, hashing unrelated trees, planning, or waiting.

## Copyback priority

### P0 — newest irreplaceable Llama dynamic evidence

Copy these first, one artifact group at a time, retaining the remote source until local SHA closure:

1. Q2 Prefill dynamic stream and its compact evidence:
   - raw JSONL: `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_prefill_dynamic/91e27027-eb2d-4572-a4b0-b9baf4fd34fb/raw.jsonl`
   - remote SHA256: `cf60a7e063524c080593cef9aea409da0af3e8cad9020a28ed3e416f88725667`
   - bytes: `729983913`
   - `PARSE_MANIFEST.json`
   - `Q2_PREFILL_RECEIPT.json`

2. Q2 Decode dynamic stream and its compact evidence:
   - raw JSONL: `/root/autodl-tmp/c16_retry570/recovery_v3_runs/llama32_1b/S0/route_b_q2_decode_dynamic/391deb99-0430-4a19-8a2d-b2bf62243266/raw.jsonl`
   - remote SHA256: `9ff9ad5481d08d1d88653697fa6086b94965344ffd38feb7169e6c6801d20b8c`
   - bytes: `16863304`
   - `PARSE_MANIFEST.json`
   - `Q2_DECODE_RECEIPT.json`

3. Q1 producer qualification raw and compact evidence:
   - raw JSONL under `/root/autodl-tmp/c16_retry570/route_b_q1_ac36cbdc/runs/q1_tiny_88168889_20260914T072246Z/raw.jsonl`
   - remote SHA256: `420ab3b009bcf20975bde9a38d3792f84882ee4977f8254464bdf8ca07fb1a0b`
   - bytes: `502744`
   - corresponding parse manifest / static map / whitelist / compact receipt.

For each P0 group, after copyback compute local SHA256 and require exact equality before marking `LOCAL_SHA_CLOSED`.  Never delete the sole remote copy merely because transfer completed.

### P1 — Llama campaign reconstruction evidence

Next drain the existing `COPYBACK_READY` queue entries for:

- Llama S0 G1 `.nsys-rep`;
- Llama S0 G1 SQLite export;
- G1 export validation / compact catalog dependencies if they are not already local;
- all 34 successful Route-B V2 exact-function static-map payloads and their map/owner receipts;
- any later Llama CUTLASS owner, Route-B canary, formal Route-B, or Route-C raw produced after this handoff.

New Llama artifacts automatically enter P0/P1 ahead of every non-Llama artifact.

### P2 — already valuable non-Llama scientific evidence

After P0/P1 are locally SHA-closed, progressively drain existing `COPYBACK_READY` evidence, beginning with:

- Qwen0 S3 Prefill formal R6 raw capture and compact tree manifest;
- Qwen0 S3 successful R5/reproduction artifacts needed to reproduce the R6 identity chain;
- other already-completed campaign G1 reports with real profiles/censuses.

Do not initiate new non-Llama GPU work merely to make copyback more complete.

## Transfer mechanics

Use the already-established Lane-B transfer destination and queue authority; do not invent a new destination or rewrite queue identity.

For each artifact:

1. Verify remote path exists and size matches queued/receipt metadata.
2. Verify or reuse the already-closed remote SHA256.  Do not recompute multi-GB remote hashes during an imminent GPU measurement unless the existing remote SHA is missing.
3. Acquire the shared I/O lock only for the actual copy/local-verification window.
4. Copy one artifact or one tightly related small group.
5. Compute local SHA256.
6. Require local SHA == remote SHA.
7. Atomically mark `LOCAL_SHA_CLOSED` in Lane-B transfer state/receipt.
8. Keep the remote source unless there is explicit later cleanup approval.
9. Release the lock immediately.

If transfer is interrupted, preserve partial local data where the established copy mechanism supports resume, but do not mark closure until a full local SHA matches.

## GPU preemption rule

Lane A has absolute priority.

When Lane A has a ready measurement (CUTLASS owner map, representative Route-B canary/formal capture, Route-C GPU step, etc.):

- Lane B must yield the I/O lock;
- no new copy starts;
- an in-progress large copy should stop at the nearest safe boundary if it materially delays the measurement;
- after the measurement closes and `transfer_slot_granted=true`, resume from the queue.

## Reporting

Lane B should periodically publish a compact transfer receipt/state with at least:

- `P0_TOTAL`, `P0_LOCAL_SHA_CLOSED`, `P0_COPYING`;
- `LLAMA_TOTAL_COPYBACK_READY`, `LLAMA_LOCAL_SHA_CLOSED`;
- `NON_LLAMA_TOTAL_COPYBACK_READY`, `NON_LLAMA_LOCAL_SHA_CLOSED`;
- current artifact path / bytes when copying;
- `REMOTE_DATA_FREE_BYTES`;
- lock state;
- last local/remote SHA equality result.

No Git commit is required for every copied file.  Commit/push only compact state/receipts when there is a meaningful checkpoint; raw payloads remain outside Git.

## Success condition

The immediate target is:

`P0_LOCAL_SHA_CLOSED = 3/3 groups`

while Lane A continues toward Llama representative Route-B canary/formal capture without waiting for copyback.
