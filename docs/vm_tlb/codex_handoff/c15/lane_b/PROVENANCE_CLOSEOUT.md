# C15 Lane B provenance-only closeout

Status: `C15_B_NATIVE_CAPTURE_CAPABILITY_LIMITED_READY_FOR_FINAL_REVIEW`.

This closeout changes provenance metadata only. It does not alter the native
capability determination, scientific evidence tier, C-selector decision, test
results, or any of the 21 data artifacts listed by the published manifest.

| Role | Immutable identity | Meaning |
|---|---|---|
| Planning authority | `9a755b14b01c5a77a6fc98c2547616e1c490e806` | C15 authorization and contract; retained as `planning_sha`. |
| Producer implementation | `8963919d608d05713e2caa22965d8895c728bc92` | The frozen producer-code anchor, not an artifact checkpoint. |
| Producer code | `util/vm_tlb/c15/lane_b/c15_lane_b.py` | SHA256 `731789f3e35108b4146859e0718876050559ecdb5d69a077e626f722e2e20c07`. |
| Artifact checkpoint | `57e2ef203befc96cfcefe00de2aaf8b0baab5d8b` | The commit containing the repaired `PUBLISH_MANIFEST.json`; this is the exact B artifact A must consume. |
| Final handoff HEAD | `refs/heads/hrl/vm-c15-native-capture-v0` | Resolve this branch after fetching to obtain the commit carrying the final handoff record; it is distinct from the artifact checkpoint and producer-code anchor. |

The repaired manifest changes `producer_source_sha` to the producer
implementation commit and adds `producer_code_commit`, `producer_code_path`,
and `producer_code_sha256`. Its `planning_sha` is unchanged. The manifest's
self-excluded file hash list remains the same 21 data artifacts; the closeout
documents live in the Codex handoff namespace rather than changing that
scientific/capability checkpoint.

Validation rerun for the repaired checkpoint passed unit tests, the synthetic
self-test, and manifest validation. No GPU, native model, profiler, capture,
simulator, or SASS process was started for this closeout.
