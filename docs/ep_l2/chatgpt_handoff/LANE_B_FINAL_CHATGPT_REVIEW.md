# EP-L2 Lane B D512 Calibration — ChatGPT Final Review

Date: 2026-08-30

Review status: **PASS FOR D512_READY / D512_MIRROR_COMPLETE; MINOR POST-CLOSEOUT PACKAGING FIXES REQUIRED BEFORE LANE-D INGESTION**

## Accepted scientific/execution state

The frozen D512 candidate is:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
runtime config composite SHA-256
a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

Accepted gates:

```text
D256 backward equivalence       PASS
D512 boundary/cardinality       PASS
D512 natural preflight          PASS
D512_READY                      PASS
D512 26/26 local completion     PASS
26/26 promotion                 PASS
D512_MIRROR_COMPLETE            PASS
```

`D512_PROMOTION_STATUS.json` reports 26/26 `PROMOTED_VALID_CALIBRATION`. These exact results may be consumed by Lane C/E without rerun.

## Final scientific interpretation

The corrected final findings are accepted:

- descriptor pool full blocking collapses to zero in all descriptor-heavy cases, including scan;
- cycle performance remains near-tie or slightly slower rather than improving materially;
- convolution develops 931,416 exact Line-MSHR-full events and scan develops 19 at D512;
- lower-path / scheduler pressure remains substantial in traffic-heavy workloads;
- D512 therefore removes a real admission ceiling but does not establish descriptor capacity as the ultimate performance ceiling.

This supports the classification that descriptor relief redistributes pressure rather than unlocking broad speedup.

## Non-blocking packaging corrections required before CAL-ANALYSIS

These do **not** invalidate D512_READY or the promoted 26 rows and do not require simulator reruns.

### 1. Fix D256 equivalence gate metadata

`D256_EQ_SCAN_GATE.json` still declares:

```text
promotion_dependencies = [D256_EQ_SCAN_PASS, D512_PREFLIGHT_PASS]
```

This is semantically wrong: the D256 scan equivalence gate is an independent PASS validation gate. It must not depend on itself or on D512 preflight.

Correct it to an independent equivalence-validation record. D512 descendants, not the equivalence gate, depend on D512 preflight.

### 2. Publish Lane-D V2 contract for D512_BASE

The coordination branch currently contains only `docs/ep_l2/calibration/contracts/D256_BASE.json`.

Before Lane D consumes D512 as an accepted calibration cell, publish:

```text
docs/ep_l2/calibration/contracts/D512_BASE.json
```

using schema `EP_L2_CALIBRATION_CONTRACT_V2` and binding at least:

```text
cell = D512_BASE
semantic_base_id = same formal C7e semantic base
base_core_sha = ece1a3a77c5628763e0a4605bfd1c639ee6a1495
base_framework_sha = f08d2ce857972fad73c4e1ab7162ba94c6336507
candidate_core_sha = 878f80869ce212e779df20b6421e4dc7f987825d
candidate_framework_sha = aae62b66685f15437cecf0193934f628e6fac6ae
runtime_config_composite_sha256 = a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
allowed_source_delta_class = telemetry/cardinality generalization proven D256-equivalent
equivalence_gate.status = PASS + evidence path
allowed_config_fields = [descriptor_pool_size]
effective_config = formal map with descriptor_pool_size=512
config_delta_gate.status = PASS + evidence path
```

The contract must point to the already-existing D256-equivalence and config-diff evidence; do not synthesize new simulator evidence.

### 3. Remove ambiguous bandwidth field naming in review-facing machine-readable tables

`D512_CALIBRATION_COMPARISON.csv` still uses columns named `d256_dram_bandwidth_util` / `d512_dram_bandwidth_util`.

The approved Lane-D V3 terminology is:

```text
lower_admission_byte_rate_norm
native_dram_data_bus_util_weighted_mean
```

For final review-facing analysis, rename/split these explicitly and recover the final-complete 32-channel native DRAM aggregate from retained raw logs where needed. Do not call C7e lower-admission normalization physical bandwidth.

## Handoff consequence

Lane C and Lane E may promote exact matching speculative descendants immediately because `D512_PREFLIGHT_PASS` is now established for the same parent candidate.

Lane D should wait only for the D512_BASE contract plus Lane-C cell contracts before emitting accepted joint calibration deltas.

No further Lane-B simulation or functional RO/TVD/Unified work is authorized.
