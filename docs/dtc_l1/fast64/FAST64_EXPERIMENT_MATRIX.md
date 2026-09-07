# DTC FAST64 Experiment Matrix

Status: **APPROVED PLAN — EXECUTE ONLY THROUGH STAGE GATES**

Authority:

- `FAST64_RESEARCH_SCOPE.md`
- `FAST64_PLATFORM_CONTRACT.md`
- `FAST64_WORKLOAD_MANIFEST.tsv`
- `FAST64_ACCEPTANCE_CONTRACT.md`

## FAST64.0 — Pivot and evidence freeze

No performance runs.

Required outputs:

- pivot handoff recording parent Framework/Core SHAs;
- mapping of retained M5 evidence into Tier A/B/C;
- explicit `DEFERRED_HEAVY_AUXILIARY` disposition for 2MM and SYR2K primary-path work;
- existing long 80-SM ATAX marked background auxiliary stress only;
- no deletion of scientific artifacts.

## FAST64.1 — Platform and payload lock

### Platform bring-up

Create resolved configurations:

- `FAST64_BASE`
- `FAST64_IO`
- `FAST64_OO`

Use two cheap smoke payloads:

- `nn`
- `bicg`

Run each mode to natural termination where practical. The bring-up may use a
single representative payload first to resolve configuration defects before
running the full smoke pair.

### Payload lock

For every FAST12 row freeze:

- source suite/workload/input label;
- exact trace root;
- `kernelslist`/`kernelslist.g` SHA-256 as applicable;
- ordered `.traceg` member list;
- per-member SHA-256;
- set hash over ordered members;
- trace format/frontend identity;
- exact byte total.

No IO/OO benefit may be consulted to alter membership or inputs.

### Lower-cap non-binding qualification

At minimum run:

- BICG IO: cap candidate vs high cap;
- BICG OO: cap candidate vs high cap;
- one second workload chosen pre-performance from `{btree, gesummv}` using
  Base/trace characteristics only, IO and/or OO as needed.

Candidate starts at 8192.

## FAST64.2 — Repair qualification

### Normal natural-terminal triplet

Use a small/medium FAST12 payload, default `bicg`, under the frozen FAST64
platform:

- Base
- IO
- OO

### Forced lower-create-queue stress

Create a separate diagnostic-only overlay that intentionally makes lower
candidate capacity/credits tight enough to produce:

`DTC_L1_*_lower_create_queue_full_stalls > 0`

The diagnostic may use BICG or ATAX, whichever reaches the target event faster
without changing source/input.

It is not a performance point.

It may be acquired in an isolated namespace before FAST64.1 logical PASS only
as `PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE`.  The overlay
uses a high/non-binding global lower cap and reduces only the relevant
lower-create candidate-queue/headroom control; it is never an aggregate row.

The existing large 80-SM ATAX recovery triplet may continue independently but
is no longer a FAST64 gate after this stage passes.

## FAST64.3 — Base-only characterization

Run exactly one valid `FAST64_BASE` row for each FAST12 workload: **12 rows**.

Collect at minimum:

- `gpu_tot_sim_cycle` and dynamic instructions;
- source-domain Load/Store/Atomic/FENCE_OP counts when available;
- PIB occupancy/peak/full cycles;
- true Tag/cacheline allocation failures;
- MSHR entry/merge pressure;
- lower/miss-queue/downstream capacity pressure;
- common live-miss avg/peak/create/complete;
- L1/L2 accesses, misses/hits where parser-supported;
- NoC/DRAM/traffic fields already supported by the M5 parser;
- host wall/user/sys time, cycles/s, instructions/s, RSS;
- terminal/drain/accounting status.

Purpose: correctness, workload classification, runtime planning, and Base
structural-pressure evidence. It is **not** a selection round; all valid rows
remain in FAST12 regardless of pressure.

Before FAST64.1/2 close, isolated Base@8192 acquisition is allowed only as
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`.  Such rows become FAST64.3 results
only after their complete stage identity/accounting gates pass.

## FAST64.4 — Primary Base/IO/OO matrix

Primary matrix membership is fixed at 12 workloads x 3 modes = **36 rows**.

Reuse the valid FAST64.3 Base rows. Launch the missing **24 IO/OO rows**.
After FAST64.2 PASS these may be physically acquired before FAST64.3 logical
PASS as `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, but cannot affect FAST12
membership, inputs, or Base characterization before that PASS.

Scheduling:

- dynamic worker pool;
- no workload-by-workload serialization;
- one triplet uses one payload identity and one common observer identity;
- negative/zero speedup does not trigger removal or retuning.

Primary metrics:

`speedup_IO = cycles_BASE / cycles_IO`

`speedup_OO = cycles_BASE / cycles_OO`

Aggregate:

`GM-FAST12` over all 12 valid primary members.

## FAST64.5 — Causal analysis and paper-facing primary outputs

Generate at least these compact datasets/figures:

1. **Base structural pressure**
   - PIB full;
   - Tag/cacheline allocation failure;
   - MSHR capacity failure;
   - MissQueue/lower/downstream failure;
   - keep Tag-bank arbitration separate.

2. **Base/IO/OO performance**
   - Base normalized to 1.0;
   - IO/OO bars;
   - `GM-FAST12`.

3. **Concurrent live misses**
   - Base/IO/OO average per SM;
   - peaks in audit table.

4. **Causal relationship**
   - Base structural pressure;
   - live-miss change;
   - performance change;
   - classify outliers/weak/negative rows.

5. **IO versus OO mechanism evidence**
   - IO HOL ready-younger evidence;
   - OO out-of-order retire;
   - active Ref/reclaim;
   - explain where OO adds value and where it does not.

Every workload receives a causal class; no unresolved implementation defect may
be hidden as a workload result.

## FAST64.6 — Bounded sensitivity

Freeze the sensitivity roster before inspecting FAST64.4 IO/OO benefit:

- `bicg`
- `gesummv`
- `btree`

### Logical capacity

Candidate points:

- 16 KiB
- 32 KiB
- 64 KiB

### Physical pool

Candidate DTC physical points:

- 16.5 KiB
- 24 KiB
- 32 KiB
- 40 KiB
- 48 KiB

Before launch, map each point exactly to representable whole-line physical
entries and document any necessary rounding. Do not invent fractional lines.

### PIB

Candidate DTC PIB points:

- 32
- 64
- 128
- 192
- 256

Do not blanket-run sensitivities across all FAST12 workloads.

Reuse matching FAST64.4 rows where identities match exactly.

## FAST64.7 — Final synthesis and closeout

Required final outputs:

- FAST12 summary table;
- structural-pressure table;
- live-miss table;
- traffic/pressure table;
- IO/OO mechanism table;
- sensitivity summaries;
- exact aggregate membership;
- limitations/boundary statement;
- Tier-A mechanism evidence index;
- Tier-C heavy auxiliary evidence index;
- raw-log index and result manifest.

Final conclusion must distinguish:

- mechanism correctness;
- FAST64 performance evidence;
- heavy auxiliary evidence;
- differences from the dissertation platform/workload set.
