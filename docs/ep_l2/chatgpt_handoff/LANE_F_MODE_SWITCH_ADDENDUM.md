# Lane F Addendum — Baseline / Mechanism Mode-Switch Design

Status: **applies to the currently running Lane-F source-audit task; no restart required**.

Read:

```text
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md
docs/ep_l2/project_spec/decisions/ADR-004-experiment-mode-switch.md
```

## Additional Lane-F requirement

The M1/M2 source design must explicitly define how future experiments switch between the accepted baseline and EP-L2 mechanisms.

Do not implement the switches in Lane F; design and source-map them.

The design must preserve these principles:

1. Calibrated base resources (Descriptor D256/D512, MSHR, L1, lower queues, DRAM clock) are a separate configuration layer from mechanism enable/disable state.
2. The final functional source/binary family should be able to run baseline and mechanisms through explicit configuration rather than branch checkout/source edits.
3. All mechanism features OFF must reproduce the accepted parent baseline.
4. Prefer orthogonal feature switches suitable for ablation/composition over one opaque mode that encodes every combination.
5. Human-readable runner mode labels may map to an explicit authoritative feature vector.
6. Every run manifest must record the effective feature vector and base resource configuration.
7. Unsupported/unsafe combinations must fail closed.
8. Result roots/manifests must be collision-free across modes.

## Add to Lane-F deliverables

Extend the existing review pack with:

```text
EXPERIMENT_MODE_SWITCH_DESIGN.md
```

It should contain:

```text
existing config plumbing/source locations
recommended simulator-facing option(s)
recommended orthogonal feature vector
baseline/default semantics
M1 static-compatible mode
M2 enable path
future M3/M4 switches
illegal-combination checks
runner overlay mapping
manifest/provenance fields
old-mode equivalence test plan
ablation/composition matrix
```

Also reflect the mode-switch interface in:

```text
M1_ELASTIC_SUBSTRATE_DESIGN.md
MODIFICATION_SEQUENCE.md
RISK_AND_INVARIANT_MATRIX.md
CHANGED_FILES_EXPECTED.md
```

Do not hard-code D256 or D512 as the final primary baseline; the switching layer must sit above the later `BASELINE-DECISION`.
