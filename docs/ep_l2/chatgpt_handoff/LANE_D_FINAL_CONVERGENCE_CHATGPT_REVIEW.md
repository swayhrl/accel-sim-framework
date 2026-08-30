# EP-L2 Lane D Final Calibration Convergence — ChatGPT Review

Date: 2026-08-30

Review status: **PASS — SCIENTIFIC CONVERGENCE ACCEPTED**

Archival follow-up: record the final convergence analysis branch SHA and explicit `git diff --check` evidence in the Lane-D pack before long-term archival. These are packaging/reproducibility cleanups and do not block the scientific decision below.

## Scope reviewed

Reviewed:

```text
docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1/
Lane-D analysis branch hrl/ep-l2-cal-analysis-v0
```

The accepted primary matrix contains exactly the six promoted, contract-bound cells:

```text
D256_BASE       26 rows
D512_BASE       26 rows
D256_META_HR     7 rows
D256_BANK_HR     7 rows
D512_META_HR     7 rows
D512_BANK_HR     7 rows
                 -------
                  80 rows
```

Lane-E Line-MSHR sensitivity remains a separate controlled supplement and is not conflated with the main factorial matrix.

## 1. Input provenance / V2 contract binding — PASS

All six cells have `EP_L2_CALIBRATION_CONTRACT_V2` contracts and PASS config-delta/equivalence evidence. Direct D256/D512 base inputs use exact per-run runtime audit; Lane-C compact evidence is explicitly identified as review-pack-bound rather than being silently presented as a direct raw-run audit.

The post-V3 compatibility repair in `lane_d_analysis.py` is semantically correct: runtime configuration digest lookup now checks the per-run `run_status.audit` first, then retained manifest/campaign evidence, and still rejects missing or contract-mismatching hashes. It does not introduce a fallback/default hash.

## 2. 13-workload archetype checkpoint — PASS

All 13 workloads appear exactly once and each characterization dimension carries an evidence status (`MEASURED`, `CONTROLLED_SENSITIVITY`, `INFERRED`, or `UNKNOWN_NEEDS_TELEMETRY`).

Accepted representative development set:

```text
convolutionSeparable  structural bottleneck substitution
scan                  sustained descriptor/lower/high-BW
vectorAdd_4M          sustained throughput/high-BW
spmv                  per-address / near-MSHR
FWT_7_21              bursty descriptor/WAD/lower
cfd_097k              true bank-service contention
dwt2d                 dirty-victim/WAD lifetime candidate
sad                   low-pressure negative control
```

The pack correctly leaves Unified payload, RO eligibility/avoidable lifetime, and TVD releasable payload opportunity as `UNKNOWN_NEEDS_TELEMETRY` where current evidence does not directly measure them.

## 3. D256 -> D512 calibration conclusion — PASS

D256 descriptor capacity is a real structural admission throttle in multiple workloads. D512 removes that ceiling across the promoted breadth at a bounded metadata cost (2–4 KiB/slice, 128–256 KiB/chip, about 1.39–2.78% of the frozen payload-byte budget).

D512 does not broadly improve cycles; in descriptor-heavy workloads the response is generally near-tie or small slowdown. Therefore the accepted interpretation is **bottleneck substitution**, not a D512 performance claim.

D512 is nevertheless a better **research/calibration baseline** because it avoids an inexpensive metadata ceiling prematurely truncating the L2 concurrency/resource chain that EP-L2 is intended to study.

The rationale explicitly rejects “choose D512 because it makes MSHR the bottleneck.”

## 4. L1 baseline decision — PASS

Promoted Lane-C META-HR/BANK-HR results show no broad material (>5%) response. Most changes are below ~2%; btree remains a small local sensitivity/control.

Therefore retain the primary L1 configuration:

```text
64 KiB/core
4 sets x 128 ways x 128 B
4 banks
20 cycles
L1 MSHR 512
merge cap 8
MissQ 16
```

Do not enlarge L1 resources merely to suppress large retry counters.

## 5. Line-MSHR baseline decision — PASS

The controlled convolution result is represented correctly:

```text
D256/M128  290,308
D256/M256  290,308
D512/M128  292,211, Line-MSHR-full 931,416
D512/M256  291,108, Line-MSHR-full 0
```

Eliminating all exact D512 Line-MSHR-full events yields only ~0.38% cycle improvement while pressure shifts to MissQ/WAD/lower-path resources. This is strong evidence that MSHR128 is a real admission ceiling in that regime but not the final performance ceiling.

Therefore keep **Line-MSHR=128** in the calibrated research baseline. MSHR256 remains sensitivity evidence only.

## 6. DRAM / temporal semantics — PASS

The convergence retains Lane-D V3 semantics:

```text
lower_admission_byte_rate_norm != physical DRAM utilization
native physical DRAM utilization = final complete 32-channel snapshot
per-5K physical bus utilization = NOT_RETAINED unless a new producer is added
```

Base cells retain exact 64-slice / 32-channel temporal semantics. Compact Lane-C tables explicitly label unavailable native distributions `NOT_RETAINED_IN_COMPACT_L1_REVIEW_TABLE` rather than inventing zeroes.

## 7. Workload/mechanism map — PASS

The mechanism target map correctly refuses to infer functional opportunity from nonzero counters alone:

- Unified payload: unknown until a real non-resident role/lifetime and time-aligned slack are measured.
- RO pending-state: secondary target; exact MSHR blocking exists, but controlled performance sensitivity is weak and safe RO eligibility/lifetime is unmeasured.
- TVD: WAD-active workloads exist, but dirty-victim payload hold time and storage-neutral reuse opportunity remain unmeasured.
- Cross-resource elasticity / generic M0+M1: strongest immediate target because descriptor relief has already demonstrated natural bottleneck substitution.

## 8. Performance-headroom candidates — PASS as future sensitivity

Accepted first candidates, not yet authorized runs:

```text
H-SCHED 128->256 : scan, vectorAdd, convolution, FWT7
H-L2D   128->256 : scan, vectorAdd, convolution, spmv
H-BW 850MHz->1GHz: scan, vectorAdd, spmv
sad               : negative control
```

A downstream-masking claim will require a mechanism x headroom interaction, not merely headroom speedup.

## 9. Calibrated primary research baseline — ChatGPT decision

**BASELINE_DECISION_PASS**

Freeze the next mechanism-development baseline as:

```text
Descriptor pool        512
Line MSHR              128
per-address cap         32
L1                     BASE (512 MSHR / merge8 / MissQ16 / 4 banks / 20 cycles)
WAD                     128
payload physical budget 1152 x 128 B / slice
payload banks           4 x 288, one arbitrary op/bank/cycle
L2->DRAM queue          128
FR-FCFS scheduler       128/channel
ReturnQ                 192/channel
DRAM clock              850 MHz primary
```

This is a **calibrated research baseline**, not a claim that D512 is faster than D256. Historical formal D256 evidence remains immutable and valid as calibration provenance.

Future feature comparisons must hold this base-resource configuration fixed and use the same-source/binary feature-switch contract.

## 10. Reproducibility packaging follow-up

Before Lane D is archived, add to the final pack:

1. exact final analysis source SHA (current reviewed branch tip during this review: `aa44f9e8d685b6f9bbe410b996e07ef185a8de96`, or the exact producing commit if different);
2. explicit `git diff --check` result for that source state.

No simulator rerun or scientific re-analysis is requested.

## Final disposition

```text
FINAL_CALIBRATION_CONVERGENCE       PASS
BASELINE_DECISION                  PASS
PRIMARY RESEARCH BASELINE          D512 / L1 BASE / Line-MSHR128
FUNCTIONAL UNIFIED/RO/TVD          NOT YET AUTHORIZED
NEXT ENGINEERING                   M0 opportunity telemetry + M1 static-equivalent substrate
```
