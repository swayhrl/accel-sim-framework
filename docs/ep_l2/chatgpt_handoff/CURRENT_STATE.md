# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This is the authoritative high-level coordination state. Detailed historical rationale remains in the C7D/C7E discussion and closeout documents.

## 1. Frozen architectural facts

Primary Target Baseline remains:

```text
64 L2 slices
128 B line, 4 x 32 B sectors
Resident Tag: 64 sets x 16 ways = 1024 / slice
Resident payload: 1024 / slice
Bypass payload: 128 / slice
B0-Legacy: separate resident/bypass 1R1W
B0-Banked: 4 x 288 banks, bank=payload_id%4, static 1024+128 roles
Line MSHR: 128
Persistent shared requester descriptors: 256 in the current formal baseline
Per-address descriptor cap: 32
WAD: 128
ICNT->L2 64
L2->DRAM 128
DRAM->L2 64/slice
L2->ICNT 64
FR-FCFS scheduler 128/channel
internal DRAM ReturnQ 192/channel
850 MHz primary DRAM clock
L1D 64 KiB, 4 sets x 128 ways x 128 B, 4 banks, 20 cycles
```

C6d bank arbitration is frozen: idle first operation can grant same cycle; oldest pending priority is preserved; one arbitrary payload op/bank/cycle; true contention is separated from retry bookkeeping.

No Unified borrowing, functional RO no-MSHR, TVD, or 1GHz primary change belongs in the current baseline/calibration stage.

## 2. C7e / formal source state

The current formal campaign manifest declares the exact C7e pair:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

These are the source/config semantics used by the live formal Target-Baseline campaign. Publishing these exact existing commit objects to stable remote C7e branches is a required reviewability item; do not rebuild or create replacement source merely to publish them.

C7e provides the final characterization families needed for Tag/MSHR/descriptor/WAD/payload/bank/L1D/lower/DRAM/window analysis.

## 3. Formal Lane A status

Current final D256 Target-Baseline campaign:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
= 26 runs
```

Interim reviewed state:

```text
22/26 COMPLETE_VALID
missing/running: gemm Legacy/Banked and 3mm Legacy/Banked
status: CONDITIONAL PASS to continue
```

Review pack:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_INTERIM_22OF26_r1/
```

ChatGPT review:

```text
docs/ep_l2/chatgpt_handoff/INTERIM_22OF26_CHATGPT_REVIEW.md
```

Do not interrupt the four live formal runs.

## 4. Current scientific observations to test, not assume

The 22/26 data show:

```text
- strong global descriptor-256 pressure in multiple workloads
- Line-MSHR-full remains zero in those strong descriptor cases
- old fixed small per-MSHR merge fragmentation is largely removed
- Tag/set blocking is generally weak (scan is a small exception)
- WAD pressure is heterogeneous and real in scan/dwt/FWT/convolution/cfd
- payload capacity denial is measured zero in completed runs
- B0-Banked is timing-equal to Legacy in 10/11 completed pairs with zero true conflicts;
  cfd has real bank contention and ~2.37% slowdown
- substantial L1D retry/stall pressure exists in several workloads
- lower-path scheduler/L2->DRAM pressure is workload-dependent
- internal DRAM ReturnQ is not implicated in the completed subset
```

These observations motivate calibration; they are not yet all performance-causal conclusions.

## 5. Parallel calibration is now authorized

The project no longer waits serially for Lane A to finish before preparing calibration.

Shared plan:

```text
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Recommended lane ownership:

```text
Lane A — existing Codex window; finish formal D256 26-run only
Lane B — descriptor 256->512 calibration and speculative D512 mirror
Lane C — L1 causality/headroom factorial
Lane D — temporal/calibration analysis, descriptor hardware cost, opportunity scaffold
```

Use four Codex windows total (three new B/C/D windows).

## 6. Descriptor calibration question

Descriptor 512 is a high-priority candidate because 512 entries are considered practically provisionable, but calibration must not tune the system until MSHR becomes the bottleneck by construction.

Lane B asks:

```text
Does D256 create an unnecessarily tight/cheap metadata ceiling?
If D512 removes it, where does pressure naturally move?
```

Keep Line MSHR=128 and per-address cap=32 fixed while changing D256->D512.

## 7. L1 causality question

Large L1 blocker/retry counts do not by themselves prove L1 is the root cause; downstream L2/DRAM backpressure can extend L1 lifetimes and create retries.

Lane C therefore keeps L1 capacity/tag geometry fixed and tests only:

```text
META-HR: MSHR 512->1024, merge 8->32, MissQ 16->64
BANK-HR: banks 4->8
```

on selected B0-Banked workloads under both D256 and, after Lane B preflight, D512.

Interpret performance together with downstream pressure movement to distinguish L1-local bottleneck vs downstream symptom vs L1 throttling/masking L2.

## 8. Baseline decision gate

No lane independently chooses the final calibrated primary baseline.

After Lane A/B/C data and Lane D analysis converge:

```text
CAL-ANALYSIS
  -> BASELINE-DECISION
      -> choose/justify D256 or D512
      -> retain or recalibrate L1 baseline if evidence requires
      -> only then freeze opportunity-study baseline
```

If D512 naturally reveals Line-MSHR pressure, that strengthens RO no-MSHR motivation. If it instead exposes L1/lower/WAD limits, mechanism motivation must follow that evidence.

## 9. Shared update protocol

Codex updates execution/progress/evidence columns in:

```text
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

ChatGPT updates review/conclusion/next-action columns after inspecting pushed evidence.

Each parallel lane uses its own `codex_handoff/LANE_*_LATEST.md` to avoid write conflicts. Lane A owns the global `LATEST_REPORT.md` until formal closeout.