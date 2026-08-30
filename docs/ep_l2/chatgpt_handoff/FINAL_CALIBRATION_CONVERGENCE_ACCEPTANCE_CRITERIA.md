# EP-L2 Final Calibration Convergence — Acceptance Criteria

Status: mandatory Lane-D self-gating contract.

## A. Input provenance

PASS only if every consumed cell is bound through `EP_L2_CALIBRATION_CONTRACT_V2` or an explicitly reviewed formal/supplemental evidence contract.

Required primary cells:

```text
D256_BASE
D512_BASE
D256_META_HR
D256_BANK_HR
D512_META_HR
D512_BANK_HR
```

Reject:

```text
wrong runtime config hash
wrong Core/Framework lineage
missing equivalence/config-delta PASS evidence
unpromoted speculative input
duplicate workload/variant/cell rows
trace/frequency mismatch
```

## B. No new simulation

PASS only if Lane D launches no simulator run and modifies no B/C/E runtime result root.

Analysis may read retained raw logs and parsed artifacts.

## C. Workload archetype completeness

All 13 target workloads must appear exactly once in the workload-level classification.

Every archetype dimension must carry evidence status:

```text
MEASURED
CONTROLLED_SENSITIVITY
INFERRED
UNKNOWN_NEEDS_TELEMETRY
```

Do not upgrade `UNKNOWN` to a mechanism opportunity.

The workload map must include both application-level and temporal evidence where available.

## D. Claim discipline

The final report must keep three evidence levels separate:

```text
L1: structural pressure/blocking
L2: service effectiveness / useful concurrency / lifetime movement
L3: end-to-end application performance
```

A reduction in blocker events must not be rewritten as speedup or latency reduction without direct evidence.

A high occupancy must not be called a causal bottleneck without exact blocking or controlled sensitivity.

## E. D256/D512 decision discipline

The baseline recommendation must include:

```text
D256 descriptor pressure removed by D512
D512 hardware metadata cost context
performance response
Line-MSHR/lower-path substitution
L1 sensitivity results
workload breadth
```

It must explicitly reject the rationale "choose D512 because it makes MSHR the bottleneck".

## F. L1 causal conclusion

Validate that the final promoted Lane-C results are used, not the old speculative snapshot.

If no workload crosses the defined material-response trigger, do not request one-at-a-time L1 decomposition retroactively.

Report small sensitivities such as btree separately from broad L1 baseline changes.

## G. Line-MSHR causal supplement

The convolution 2x2 must be represented exactly:

```text
D256/M128  290,308
D256/M256  290,308
D512/M128  292,211
D512/M256  291,108
```

and the D512 931,416 -> 0 Line-MSHR-full change must be paired with the ~0.38% cycle response and downstream-pressure movement.

The accepted classification may be `MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED`; do not turn it into a claim that MSHR capacity is irrelevant.

## H. Temporal/native-DRAM semantics

Use the approved Lane-D V3 semantics:

```text
lower_admission_byte_rate_norm != physical DRAM utilization
native physical DRAM utilization = final complete 32-channel native snapshot
per-5K physical DRAM utilization = NOT_RETAINED unless new producer evidence exists
```

Temporal cardinality/time-group integrity must remain fail-closed.

## I. Mechanism target map

For every proposed mechanism family, provide:

```text
evidence already available
scientific question
missing observation
best target workload(s)
primary L2-local success metric
secondary service metric
end-to-end metric
headroom axis if applicable
implementation risk/dependency
```

Do not recommend a mechanism solely because its required counter is nonzero.

## J. Reproducibility

The final pack must include:

```text
analysis source SHA
input contract paths
exact input result roots
record counts
workload/variant coverage
validation output
git diff --check
SHA256SUMS
```

Any Lane-D analysis code change after the reviewed V3 source must be isolated, tested, and explained as a bug fix or convergence-only tooling change.

## K. Completion state

PASS state is exactly:

```text
FINAL_CALIBRATION_CONVERGENCE_REVIEW_READY
```

This is not `BASELINE_DECISION_PASS` and does not authorize functional mechanism implementation.
