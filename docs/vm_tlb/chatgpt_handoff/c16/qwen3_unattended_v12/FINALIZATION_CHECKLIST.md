# Qwen3 Unattended V12 — Finalization Checklist

Use this only after 174-new V12 returns. The draft must not be released to node109 until every required item below is resolved.

## A. Bind exact 174-new authority

Replace every `PENDING_174NEW_V12` / `PENDING_*` field with:

- exact 174-new branch/HEAD;
- exact final decision;
- `QWEN3_EXECUTION_AUTHORIZATION.json` path and SHA256;
- V2 canonical validation artifact path and SHA256;
- exact Qwen3 S2 canonical token-sequence SHA256;
- exact Qwen3 S2 payload SHA256;
- execution-mode authorization;
- target-selection/max-target policy;
- S3 continuation policy;
- any extra STOP conditions.

Authorization must be PASS-derived and internally consistent before the draft status is removed.

## B. Resolve asset staging semantics

The final Goal should prefer already-local exact assets. If node109 lacks them but V12 identifies a durable hash-closed node164 authority, allow only a repository-documented/approved transfer of the exact assets, followed by complete post-transfer hash verification. Do not use network model re-download or same-name replacement as a fallback.

If no approved transfer path exists, fail closed with a concrete asset blocker.

## C. Resolve ADDRESS_CONTEXT policy exactly

Do not overstate V11 FM07.

- same-process `ADDRESS_CONTEXT` is mandatory for promoting object roles;
- absent context means `UNKNOWN_RUNTIME`, never inferred object identity;
- make absence a formal-campaign blocker only if the final V12 authorization explicitly requires object attribution/context as a required target gate.

Update both the Markdown handoff and stage-contract JSON accordingly.

## D. PASS_WITH_SCOPED_EVIDENCE boundary

Final text must state explicitly:

`PASS_WITH_SCOPED_EVIDENCE` cannot hide failure of a required S2 gate.

It is allowed only for authorization-designated optional evidence, for example:

- optional second attention/KV target not selected because not materially distinct;
- authorized S3 extension not run for a policy-supported reason;
- optional non-comparable NCU field while the required baseline metric/evidence remains closed.

A failed required S2 authority/state/replay/signature/path/formal/ACK gate must produce BLOCKED, not scoped PASS.

## E. Execution-mode semantics

Check that capacity is treated as an execution-mode selector, not automatically a blocker:

- `NATIVE_FULL_RESIDENT` only if proven feasible and authorized;
- otherwise `EXACT_SEMANTIC_LAYER_STREAMING_REPLAY` if authorized;
- no precision/quantization/backend/model substitution;
- streamed execution must never be described as full-resident native deployment.

## F. Validate executor integrity requirements

Final handoff must still require:

- no `FRAMEWORK_ONLY`/`PLAN_ONLY` scientific PASS;
- contiguous hash-valid resume chain;
- immutable attempt receipts;
- authorization-aware SKIPPED handling;
- signal-safe partial state;
- shard-resumable formal capture;
- serial formal admission + ACK;
- executable self-test before Qwen3.

## G. Final branch/package cleanup

Before handing to node109:

1. rename or replace `CODEX_109_QWEN3_UNATTENDED_CAMPAIGN_V12_DRAFT.md` with the final executable handoff;
2. rename/finalize `QWEN3_UNATTENDED_STAGE_CONTRACT_DRAFT.json`;
3. change `CURRENT_SCOPE_AND_GATES.md` status from DRAFT to final authority-bound state;
4. verify no `PENDING_` token remains;
5. verify branch HEAD and file hashes;
6. provide node109 with one concise launch message containing coordination branch, expected HEAD, final handoff path and suggested execution branch.