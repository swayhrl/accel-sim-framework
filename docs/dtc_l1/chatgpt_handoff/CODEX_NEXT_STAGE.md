# CODEX_NEXT_STAGE

## Status

**ACTIVE — FINAL ICNT->L2 INGRESS-QUEUE CHECK**

This is a four-row bounded extension of the accepted SG3 study. Do not restart prior stages.

## Source anchors

Before work:

1. `git fetch origin`.
2. Verify actual remote heads.
3. Never reset an advanced branch.

Expected coordination/master ancestry contains the current handoff update.

Accepted SG3 authority:

`c055d817b009cbe6a59c7f8ac7af1081f86ec6e8`

Execution/evidence branch:

`hrl/iscas2027-dtc-sg3-downstream-localization-v0`

Read in order:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. this file
4. `docs/dtc_l1/review_packs/MEMORY_QUEUE_CHAIN_DRAM_HEADROOM_V1/`
5. `SG3_MEMORY_QUEUE_CHAIN_SOURCE_MAP_V2.tsv`
6. `SG3_BICG_MEMORY_QUEUE_CHAIN_TELEMETRY_V2.tsv`

Treat all existing A-F/R3/R4 results as immutable accepted evidence.

---

# R5.0 — zero-simulation source confirmation

Before launching, commit a compact source receipt confirming:

1. `gpgpu_dram_partition_queues` field order is:
   - ICNT->L2
   - L2->DRAM
   - DRAM->L2
   - L2->ICNT
2. default ICNT->L2 queue is 64/subpartition.
3. `memory_sub_partition::full(SECTOR_CHUNCK_SIZE)` checks whether the ICNT->L2 FIFO lacks room for the worst-case sector expansion.
4. `gpu_stall_icnt2mem` increments only when that ingress-capacity condition is true and ICNT actually has a packet waiting.
5. terminal label `gpu_stall_dramfull` is legacy text and must not be interpreted as a DRAM-full counter.
6. enlarging only the first queue field does not change L2 capacity/MSHR/miss queue, DRAM queues, scheduler, return queue, channel count, mapping, DTC semantics, or trace identity.

Deliver:

`docs/dtc_l1/iscas2027/granularity/sg3/SG3_ICNT_L2_INGRESS_SOURCE_RECEIPT_V1.md`

and a registered four-row execution TSV before simulation.

---

# R5.1 — four authorized BICG rows

Run exactly:

## Family G — ingress queue only

Overlay:

`-gpgpu_dram_partition_queues 256:64:64:64`

Rows:

- BICG IO
- BICG OO

Everything else remains at the exact accepted default-cap=8192 configuration.

## Family H — ingress queue + accepted DRAM2x service probe

Overlay:

- `-gpgpu_dram_partition_queues 256:64:64:64`
- `-gpgpu_clock_domains 1410.0:1410.0:1410.0:1700.0`

Rows:

- BICG IO
- BICG OO

Everything else matches accepted E except the first partition-queue field.

Total new simulator rows: **4**.

These may all be rolling-launched after R5.0 is committed.

---

# R5.2 — required analysis

For G compare against exact default.

For H compare against:

1. exact default;
2. accepted E/DRAM2x:
   - IO 50,713,356 cycles
   - OO 29,933,876 cycles.

Report at minimum:

- cycles;
- cycle delta/speedup;
- `gpu_stall_icnt2mem`;
- `gpu_stall_mem2icnt`;
- mean memory-fetch latency;
- mean ICNT->memory latency;
- mean MRQ latency;
- DTC lower outstanding average/peak if available;
- L2 miss-queue pressure;
- DRAM `mrqq` max/avg;
- exact resolved queue config and clock config.

Do not interpret the legacy printed name `gpu_stall_dramfull` literally.

## Decision labels

Use one bounded final label:

- `ICNT_L2_INGRESS_HEADROOM_SUPPORTED`
- `ICNT_L2_INGRESS_DRAM_INTERACTION_SUPPORTED`
- `ICNT_L2_INGRESS_PRESSURE_NOT_CAPACITY_LIMITED`
- `ICNT_L2_INGRESS_HEADROOM_PARTIAL`

No cross-workload generalization from these four BICG rows.

---

# Explicitly forbidden scope

Do NOT launch:

- GESUMMV for R5 without a new review;
- ICNT->L2 >256;
- L2->ICNT changes;
- interconnect buffer/routing/bandwidth sweeps;
- NoC sweeps;
- ROP sweeps;
- new L2 miss-queue/capacity/MSHR points;
- new DTC cap points;
- additional DRAM frequencies;
- DRAM timing-string sweeps;
- busW experiments;
- new mechanisms.

---

# Acceptance requirements

Each new row requires:

- fresh UUID;
- immutable run directory;
- exact Core/runtime/config-chain/trace identity;
- START receipt;
- natural terminal receipt;
- strict validation;
- terminal drain / observer closure.

Preserve every failure; never overwrite.

---

# Deliverables

Create/update:

`docs/dtc_l1/review_packs/ICNT_L2_INGRESS_HEADROOM_V1/`

with:

- `README.md`
- `SOURCE_ANCHORS.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- R5.0 source receipt
- four-row registry/results
- exact paper-safe claims
- forbidden overclaims
- raw-log index

Update:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

with the final branch SHA and bounded conclusion.

---

# STOP boundary

Complete R5.0, all four R5.1 rows, R5.2 analysis, review pack, handoff, commit and push.

Then STOP.

Do not automatically continue to NoC or any other resource family regardless of result.
