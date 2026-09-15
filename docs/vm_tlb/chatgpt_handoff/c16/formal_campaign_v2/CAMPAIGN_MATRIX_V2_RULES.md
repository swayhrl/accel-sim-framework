# CAPTURE_CAMPAIGN_V2 Rules

## Principle

`CAPTURE_CAMPAIGN_V1.tsv` is frozen historical evidence. Do not edit it in place.

Create `CAPTURE_CAMPAIGN_V2.tsv` as a living-but-checkpointed execution matrix for the recovery campaign.

## Required columns

```text
target_id
deployment_id
scenario
phase
decode_step
semantic_stratum
scientific_role
target_function
code_object_sha256
launch_selector
static_mref_set_sha256
capture_method
shard_selector
object_map_sha256
ncu_evidence
resource_admission
readiness_state
formal_evidence_class
supported_analyses
unsupported_claims
fallback_target_id
attempt_count
last_result
pipeline_run_id
pipeline_ack_status
```

## Readiness states

Use actionable states rather than one binary gate:

```text
READY_EXACT_FULL_LAUNCH
READY_CTA_SHARD
READY_MREF_SHARD
RECOVER_STATIC_MAP
RECOVER_OBJECT_MAP
RECOVER_CAPTURE_TOOL
RECOVER_BACKEND
RECOVER_MEMORY
CONTROL_ONLY
DEFER_RESOURCE
REJECTED_WITH_EVIDENCE
FORMAL_ACCEPTED
```

A recoverable state is an instruction to continue work, not permission to stop the campaign.

## Promotion rules

A target can be promoted to formal when its chosen evidence class has enough evidence for the analyses claimed.

Examples:

- object map with some `UNKNOWN_RUNTIME` is acceptable if the mapping procedure is hash-bound and unknowns are preserved;
- NCU is supportive, not universally mandatory;
- semantic label may remain `GEMM_HEAVY_UNRESOLVED_SEMANTIC` if the kernel role cannot be proved more specifically;
- `CTA_SHARDED_ALL_MREF` does not need full-launch terminal closure;
- `MREF_SHARDED_COMPLETE_SET` does not need cross-group ordering.

## Fallback policy

Each important semantic stratum should have an ordered fallback list.

A fallback is valid only when it belongs to the same scientific role/stratum or is explicitly labeled as a replacement with different scope.

Do not replace Attention with an arbitrary indexSelect or easy-PC kernel simply because it traces easily.

## Controls

Single-MREF traces, tiny canaries, and mechanism diagnostics stay `CONTROL_ONLY` unless their scientific role is explicitly only to validate mechanism/identity.

## Matrix closure

At goal end, every row must be one of:

```text
FORMAL_ACCEPTED
CONTROL_ONLY
DEFER_RESOURCE
REJECTED_WITH_EVIDENCE
```

No unexplained PENDING rows.
