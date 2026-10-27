# Shared GPU Workload Source & Behavior Atlas V1

This atlas explains the source and declared trace scope of all 35 frozen ordinary DTC workloads, preserves seven conditional workloads, and maps independently inherited EP-L2 inputs. It is a source audit, not a new performance experiment or numerical correctness certificate.

Start with [WORKLOAD_INDEX.tsv](WORKLOAD_INDEX.tsv), then the individual reports under `programs/`. Read [SOURCE_AUTHORITY.md](SOURCE_AUTHORITY.md) before interpreting a source observation as a capture-time fact. [INPUT_TRACE_BINDINGS.tsv](INPUT_TRACE_BINDINGS.tsv) retains all 72 inherited input identities, including alternates and derived inputs. [CROSS_PROJECT_MAPPING.md](CROSS_PROJECT_MAPPING.md) explains EP-L2 member identity independently of DTC input-digest naming.

[ARCH_FEATURE_MATRIX.tsv](ARCH_FEATURE_MATRIX.tsv) provides evidence-bearing features rather than performance-derived labels. [EVIDENCE_GAPS.md](EVIDENCE_GAPS.md) and [REVIEW_STATUS.md](REVIEW_STATUS.md) disclose limitations and actual review coverage. [CROSS_REVIEW.md](CROSS_REVIEW.md) contains independent address and scope checks.

Project entry points: [DTC-L1](project_views/DTC_L1.md), [EP-L2](project_views/EP_L2.md), [AWMA](project_views/AWMA.md), [AI-ARCH](project_views/AI_ARCH.md).

## Evidence dimensions

| Dimension | Meaning |
|---|---|
| SOURCE_VERIFIED | The inspected source bytes are fixed by a recorded content hash / repository commit. This does not establish capture-time source identity. |
| INPUT_BOUND | The inherited input digest, parameters and trace-bundle/member metadata are identified within that project's contract. Original raw data or generator seed may remain unknown. |
| BINARY_BOUND | Capture-time executable identity is linked to the inspected source and build. A current ELF hash alone is insufficient. |
| TRACE_SCOPE_BOUND | The declared launch sequence/geometry is compared to the selected source path. Header compatibility alone cannot certify complete trace bodies or complete application execution. |
| RUNTIME_MEASURED | A particular claim has a specific valid historical measurement. No measurements were created by this audit. |
| UNRESOLVED | The corresponding dimension lacks evidence or contains an explicit conflict. |

Each dimension is independent. A frozen identity is not a full-application certificate, simulator termination is not numerical correctness, and a static repeated address is not a measured hit or pending-request merge.

## Boundaries

Only `docs/workload_atlas/` is written in isolated branch `hrl/shared-gpu-workload-atlas-v1`, worktree `/root/workspace/shared-gpu-workload-atlas-v1`, based on `3b28d3064`. Existing experiment manifests, controllers, registries, raw data, results, budgets, manuscript v0.23 and EP-L2 paper remain outside the write scope. No benchmark build, native workload execution, capture, simulation, GPU access or model/dataset/trace download is part of this work. Lightweight source hashing and metadata/formula validation are CPU-only audit operations.

The DTC authority remains `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at the recorded base; derived b+tree and hotspot do not become ordinary representatives. The L2 exploration anchor `5178408bc28819140d01520f339af76b71f61489` is contextual evidence, not a source certification.


## V1R1 evidence and phase overlay (separate non-destructive revision)

Use [EVIDENCE_SCHEMA_V1R1.md](EVIDENCE_SCHEMA_V1R1.md) and [EVIDENCE_BINDINGS_V1R1.tsv](EVIDENCE_BINDINGS_V1R1.tsv) instead of interpreting the legacy `INPUT_BOUND`/`BINARY_BOUND` as one universal certificate. This separates registered trace, raw source input, capture ELF, and simulator binary. [PROJECT_SCOPE_ADVISORIES_V1R1.md](PROJECT_SCOPE_ADVISORIES_V1R1.md) records application-vs-ROI concerns without revising historical results. [KERNEL_PHASE_FEATURES_V1R1.tsv](KERNEL_PHASE_FEATURES_V1R1.tsv) indexes source-candidate GPU phases with their evidence limits. V1 original evidence files are preserved unchanged.
