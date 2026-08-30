# Experiment Mode / Baseline Switch Design

This design incorporates the canonical `EXPERIMENT_MODE_SWITCH_CONTRACT.md` and ADR-004. It is a source-level plan only; Lane F implements no switches.

## Existing configuration plumbing

Core C7e initializes L2 configuration defaults in `src/gpgpu-sim/gpu-cache.h:566-581` and stores EP-L2 fields at `:919-928`. `src/gpgpu-sim/gpu-sim.cc:258-274` registers descriptor-pool, per-line cap, WAD, payload mode, and B0 stats options. The existing `-gpgpu_ep_l2_payload_mode` is a timing-model selector (`0=off, 1=Legacy, 2=Banked`), not an architectural mechanism selector and must remain separate from the proposed features. Framework target scripts currently form configuration by config text and source setup; a formal runner must add reviewable overlays/manifests rather than encode mode in a checkout path.

## Two independent configuration layers

```text
base_resource_config (selected later by BASELINE-DECISION)
  descriptor capacity, Line MSHR, L1, WAD/lower queues, payload budget/banks,
  DRAM clock and all other frozen resource/timing controls

ep_l2_feature_vector
  elastic_substrate, unified_payload, ro_pending_state, tvd, adaptive_policy
```

No option name or runner label may encode a D256/D512 choice together with a feature. A feature comparison holds the complete base-resource layer fixed and changes only authorized feature/parameter fields.

## Proposed simulator-facing interface

Keep `-gpgpu_ep_l2_payload_mode={0,1,2}` for off/Legacy/Banked service behavior. Add boolean (default `0`) feature options:

```text
-gpgpu_ep_l2_feature_elastic_substrate
-gpgpu_ep_l2_feature_unified_payload
-gpgpu_ep_l2_feature_ro_pending_state
-gpgpu_ep_l2_feature_tvd
-gpgpu_ep_l2_feature_adaptive_policy
```

Add `-gpgpu_ep_l2_payload_policy=static|shared_reserve` only where M1/M2 needs policy selection; parser validation derives its legality from the feature vector rather than silently enabling a feature. Required checks:

- `unified_payload` requires `elastic_substrate` and a supported shared policy.
- `adaptive_policy` requires the mechanism(s) whose state it controls.
- M3/M4 combinations are rejected until their composition contract exists.
- an unknown feature value, unsupported mode, or incompatible policy/bit pair exits with a clear configuration error.

All bits zero is the fail-safe baseline path. `elastic_substrate=1` plus `payload_policy=static` is `M1_STATIC`: behavior preserving. M2 turns on only `unified_payload` (and its M1 prerequisite), retaining the same source/binary and base resource config.

## Runner overlay and authoritative mode mapping

The runner may offer descriptive labels but must emit the full explicit overlay:

| label | authoritative feature vector |
|---|---|
| `BASE` | all OFF |
| `M1_STATIC` | elastic substrate only; static policy |
| `M2_UNIFIED` | elastic substrate + unified payload; shared-reserve policy |
| `M3_RO_PENDING` | M3 bit plus required declared prerequisite(s) |
| `M4_TVD` | M4 bit plus required declared prerequisite(s) |
| `M2_M3`, `M2_M4`, `M3_M4`, `M5_INTEGRATED` | explicit bit set only when parser marks it supported |

The runner must write to a deterministic isolated root such as `results/<campaign>/<workload>/<variant>/<mode>/`, pre-enumerate unique `(workload,variant,mode)` keys, and reject duplicates. It generates a merged effective config from a base config plus a minimal feature overlay, computes `runtime_config_composite_sha256`, and proves that paired comparisons have equal base config, source, and trace.

## Provenance and telemetry

Every manifest/review row records `semantic_base_id`, runtime Core/Framework SHA, effective-config SHA256, base resource configuration, mode label, complete feature vector, mechanism parameters, trace identity, and result root. Telemetry must print or associate the active vector with each mode. Existing C7e fields retain their semantics; a changed mechanism meaning gets a new versioned field, never a reinterpretation.

## Acceptance tests

1. Parser defaults: omitted all feature options resolves to all OFF.
2. Invalid vector/policy tests fail closed with diagnostic text.
3. M1 static equivalence: parent accepted baseline vs same post-M1 SHA/binary all-OFF and `M1_STATIC` as applicable; cycles, deterministic existing telemetry, and terminal invariants match.
4. For every functional feature: OFF reproduces accepted parent semantics; ON satisfies directed lifecycle/invariant tests.
5. Overlay/manifest test checks all required provenance keys, config-hash stability, pairwise diff authorization, and distinct result roots.
6. Composition matrix accepts only documented legal rows and rejects every unsupported row.

This interface deliberately sits above BASELINE-DECISION. It does not choose D256 or D512.
