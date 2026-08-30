# EP-L2 Experiment Mode / Baseline Switch Contract

Status: **canonical cross-cutting implementation requirement**.

## Purpose

EP-L2 experiments must be easy to reproduce and difficult to misconfigure. A researcher must be able to run the calibrated baseline, one mechanism, or a mechanism combination from the **same functional source/binary family** using explicit configuration, without checking out another implementation branch or editing source code.

The switching interface is therefore part of the architecture implementation, not an afterthought in the runner.

## 1. Separate baseline resources from mechanism features

Do not encode a calibrated resource choice and a functional mechanism into one opaque mode number.

Conceptually keep two independent layers:

```text
BASE RESOURCE CONFIGURATION
  descriptor capacity       D256 or D512, as selected by BASELINE-DECISION
  Line MSHR                 calibrated value
  L1 / WAD / lower queues   calibrated/frozen values
  payload storage/banks     frozen physical budget
  DRAM clock                primary value

MECHANISM FEATURE VECTOR
  elastic-substrate behavior change     0/1 (M1 itself should be behavior-preserving)
  unified-payload allocation            0/1
  RO/pending-state decoupling           0/1
  TVD/victim-payload decoupling         0/1
  later policy/adaptation               0/1
```

The exact option names are a source-design decision, but the semantic separation is mandatory.

## 2. One source SHA should run baseline and mechanism modes

After a functional mechanism is integrated, the preferred experiment model is:

```text
same Core SHA
same Framework SHA
same binary
same trace
same base resource configuration

feature vector = all OFF   -> baseline/reference behavior
feature vector = M2 ON     -> Unified Payload
feature vector = M3 ON     -> RO pending-state
feature vector = M4 ON     -> TVD
feature vector = selected combination -> integrated EP-L2
```

This removes source-version differences from the mechanism comparison.

A phase may initially be developed on a feature branch, but before formal mechanism evaluation the branch must expose an explicit OFF path that reproduces the accepted parent baseline.

## 3. Default must fail safe to baseline

If new mechanism options are omitted, the simulator must not silently enable an experimental feature.

Required property:

```text
unspecified/zeroed feature vector => accepted baseline semantics
```

If a configuration requests an unsupported or unsafe feature combination, fail closed with a clear configuration error rather than silently falling back to another behavior.

## 4. M1 static-compatible mode is the first proof point

M1 refactors allocator/state plumbing but must provide an explicit static-compatible mode that still enforces the accepted baseline behavior, including the current payload role partition where applicable.

M1 acceptance requires representative old-vs-new equivalence at the original feature vector:

```text
cycles identical
existing parsed telemetry identical where deterministic
terminal invariants identical
no new ownership/resource leaks
```

Only after this OFF/static mode passes may M2 functional borrowing be enabled.

## 5. Prefer independent feature bits over a single monolithic enum

A human-friendly runner may expose labels such as:

```text
BASE
M1_STATIC
M2_UNIFIED
M3_RO_PENDING
M4_TVD
M2_M3
M2_M4
M3_M4
M5_INTEGRATED
```

but the simulator-facing effective configuration should remain an explicit feature vector wherever practical. This is required for clean ablation and composition experiments.

The runner label is descriptive; the feature vector is authoritative.

## 6. Every run records the effective mode in provenance

Every mechanism run manifest/review row must record at minimum:

```text
semantic_base_id
runtime Core SHA
runtime Framework SHA
runtime_config_composite_sha256
base resource configuration
human-readable experiment_mode label
explicit EP-L2 feature vector
effective mechanism-specific parameters
trace identity
```

Do not infer mechanism state later from branch names or filenames.

Recommended machine-readable representation:

```json
{
  "experiment_mode": "M2_UNIFIED",
  "ep_l2_features": {
    "unified_payload": true,
    "ro_pending_state": false,
    "tvd": false,
    "adaptive_policy": false
  }
}
```

Exact field names may differ, but equivalent information is mandatory.

## 7. Config overlays must be deterministic and reviewable

For formal comparisons, use small config overlays/diffs rather than copy-pasted full configs whose hidden differences are difficult to audit.

For each experiment pair, review tooling must prove:

```text
base resource config equal
trace equal
source equal
only authorized feature/parameter fields differ
```

The generated effective-config hash must be stored with the run.

## 8. Runner/result-directory convention

The runner should accept an explicit mode/feature specification and create deterministic isolated result roots. Example concept:

```text
results/<campaign>/<workload>/<variant>/<mode>/
```

or another collision-free equivalent.

Never let two modes write to the same output directory.

A campaign manifest should enumerate all expected `(workload, variant, mode)` keys before launch and reject duplicates.

## 9. Ablation and combination are first-class requirements

M5 integrated EP-L2 must not require rebuilding separate binaries to produce ablations.

The same implementation should support at least:

```text
all mechanisms OFF
M2 only
M3 only
M4 only
selected two-way combinations
integrated enabled set
```

if the mechanisms are architecturally composable.

Unsupported combinations must be documented and rejected explicitly.

## 10. Telemetry must identify active mode

Mechanism-specific telemetry must be interpretable together with baseline telemetry. The parser/manifest should expose the active feature vector without changing the meaning of existing C7e/Lane-D fields.

Do not overload an existing counter with different semantics when a mechanism is enabled. Add a new field/version when semantics genuinely differ.

## 11. Storage/timing fairness gate

Switching a feature ON must not silently alter unrelated comparison dimensions.

Formal mechanism comparisons must audit:

```text
total L2 storage budget
payload bank count/service rate
base descriptor/MSHR resources
L1 configuration
lower queues/scheduler
DRAM clock
```

unless that dimension is explicitly the experiment under study.

## 12. Recommended engineering hierarchy

```text
source/config parser
    |
    +-- base resource configuration
    |
    +-- EP-L2 feature vector
            |
            +-- payload allocation policy
            +-- pending-state policy
            +-- victim/TVD policy

runner
    |
    +-- mode label -> explicit feature-vector overlay
    +-- effective config audit/hash
    +-- deterministic result root
    +-- manifest
```

## 13. Phase acceptance implication

Every functional mechanism stage after M1 must demonstrate both:

```text
FEATURE OFF:
  accepted parent baseline equivalence

FEATURE ON:
  mechanism-specific correctness/invariants
```

The OFF result is not optional cleanup; it is a required experimental control.

## 14. Baseline-decision compatibility

This contract intentionally does not hard-code D256 or D512 as the future primary baseline. `BASELINE-DECISION` selects the calibrated base-resource configuration; the mechanism feature-vector layer then sits above that selection.

Therefore changing the final calibrated descriptor capacity must not require redesigning the M2/M3/M4 enable/disable interface.
