# C10-B build and runtime validation

Final status: `C10B_HARD_BLOCKER_WITH_EVIDENCE`.

All implementation and validation gates C10B-0 through C10B-5 passed on the
current Window-C sources. This pack does **not** authorize or contain a C5
replay. C5 preflight found that decode1 has a C10 V2 privileged registration,
whereas prefill has only the historical identity-like V1 segment map and no
immutable C-side trace-list provenance. C9 forbids deriving a formal V2 PA
mapping from either the V1 range or the telemetry object map. That immutable
provenance gap is the sole final blocker; it is not a resource, compile,
standard-regression, or architecture-implementation failure.

Retained labels: `SPECULATIVE_CANDIDATE` and
`REFERENCE_APPROX_SUBENTRY_16`.

No C5, KV segmentation, 12K workload, M5 work, Window-A/B worktree, or
historical Window-A result was operated by this Goal.
