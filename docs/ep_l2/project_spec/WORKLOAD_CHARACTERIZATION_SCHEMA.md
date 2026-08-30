# EP-L2 Workload Characterization Schema

Status: long-lived classification contract.

## Purpose

Characterization is not a list of counters. It should tell mechanism design **which resource/lifetime coupling matters for which workload and during what phase**.

Every target workload must be classified along the same dimensions so that future mechanism experiments can choose representative workloads instead of repeatedly running the full suite.

## Evidence labels

Every classification cell must carry one of:

```text
MEASURED
CONTROLLED_SENSITIVITY
INFERRED
UNKNOWN_NEEDS_TELEMETRY
```

`INFERRED` must point to the measured evidence that motivates the inference.

Never promote `UNKNOWN_NEEDS_TELEMETRY` to a mechanism opportunity without new evidence.

## Required dimensions

### 1. Request/admission metadata

```text
descriptor need / block / avg / p95 / max
Line-MSHR need / block / avg / p95 / max
per-address cap check / block
tag-way need / block / all-reserved set pressure
```

Classify descriptor and MSHR pressure as:

```text
NONE
BURSTY
SUSTAINED
NEAR_CAPACITY
EXACT_FULL_BLOCKING
```

using exact block counters plus 5K temporal distributions.

### 2. Payload and victim state

```text
resident payload occupancy
bypass/pending payload occupancy when available
payload capacity denial
payload service denial
WAD occupancy/full/hazard/wait
```

For unified-payload design, additionally ask whether resident and bypass roles have **complementary slack in the same phases**. If current telemetry cannot establish this temporally, mark `UNKNOWN_NEEDS_TELEMETRY` rather than assuming borrowing opportunity.

### 3. Bank/service pressure

```text
logical operations
grants
true conflicts
wait cycles
per-bank imbalance
```

Distinguish capacity pressure from service-port/bank pressure.

### 4. L1 causal sensitivity

Use the controlled Lane-C META-HR and BANK-HR cells.

Classify:

```text
L1_NOT_CAUSAL
L1_WEAK_LOCAL_SENSITIVITY
L1_MATERIAL_LOCAL_SENSITIVITY
L1_MASKS_L2
```

Do not classify from raw L1 retry counts alone.

### 5. Lower path / memory

```text
L2->DRAM queue occupancy/full
scheduler occupancy/full-cycle/causal block
ReturnQ / DRAM->L2 return pressure
read/write bytes
native physical DRAM data-bus utilization
traffic-conditioned channel imbalance
```

Classify the primary downstream regime:

```text
LOW_DOWNSTREAM_PRESSURE
QUEUE/SCHEDULER_PRESSURE
HIGH_BW
BURSTY_CHANNEL_LOCAL
RETURN_PATH_PRESSURE
```

### 6. Temporal regime

Classify the dominant resource pressure as:

```text
SUSTAINED
BURSTY
PHASE_SEPARATED
LOW_ACTIVITY
```

Use 5K-window distributions and longest-high-average-window runs. A zero-minimum does not by itself imply burstiness; use the full distribution and phase persistence.

### 7. Bottleneck-substitution chain

When controlled experiments exist, write an ordered chain, for example:

```text
Descriptor256 -> Line-MSHR128 -> MissQ/WAD/lower path
```

Only arrows backed by an actual controlled change may be labeled `CONTROLLED_SENSITIVITY`.

### 8. Mechanism relevance

For each mechanism family:

```text
Unified Payload Borrowing
RO Pending-Tag / no-traditional-MSHR
WAD-backed TVD
Generic cross-resource elasticity
```

assign:

```text
STRONG_TARGET
SECONDARY_TARGET
CONTROL
UNKNOWN_NEEDS_TELEMETRY
```

and state exactly which evidence is missing before implementation/evaluation.

## Required output columns

At minimum the machine-readable workload table should contain:

```text
workload
primary_archetype
descriptor_regime
line_mshr_regime
per_address_regime
tag_regime
wad_regime
payload_regime
bank_regime
l1_causal_regime
lower_path_regime
dram_bw_regime
temporal_regime
bottleneck_substitution_chain
unified_payload_relevance
ro_pending_tag_relevance
tvd_relevance
headroom_axis_candidate
confidence/evidence_status
notes/evidence_paths
```

## Representative-set rule

After all 13 workloads are classified, select a minimal representative set that covers distinct mechanisms/regimes. Prefer one or two workloads per archetype plus one low-pressure control.

This representative set is for fast mechanism development and screening. Final paper evaluation may later return to the full suite.
