# AWMA P0 Gate Verification — 2026-09-20

Status:

`P0_PARTIALLY_CLOSED`

## 109

Verified remote pause branch:

`hrl/awma-109-moe-causal-closure-scale-20h-v1`

Remote HEAD:

`0e32ac01b0237d94b39e45b288263e87e1960ccf`

Remote commit contains:

- paused report;
- PAUSED_STATE.json;
- frozen 10-block x 22-condition schedule;
- degree-realization authority;
- admitted-condition index;
- SHA256SUMS.

Decision:

`109_P0_CLOSED`

The MoE side lane is frozen candidate evidence.

## 174

User/Codex reported:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED`

Independent GitHub verification does NOT confirm this.

Remote ref:

`hrl/awma-174-hitpath-v4-provenance-closeout-exec`

still resolves to:

`c8657cf637c5b54a0f40135248ff1eabcfd66696`

Direct remote reads return NOT_FOUND for:

- `RUNTIME_ACTIVATION_FORENSICS_HITPATH_174NEW_V4_REPORT.md`
- `REPAIRED_HIT_PATH_LATENCY_MATRIX_V4.tsv`
- `MODEL_VALIDITY_ENVELOPE.md`
- `RUN_RECEIPTS.json`
- `SHA256SUMS`

Decision:

`174_P0_NOT_CLOSED_REMOTE_PUBLICATION_MISMATCH`

No new 174 simulation may start.

## Mainline gate

Track-A and Track-B launch remains blocked until 174 publication is independently remote-readable.

Do not treat a local remote-tracking ref, worktree path, or local fetch-back as sufficient proof.

Required proof is that the pushed commit object itself contains the required paths and the remote branch points to that commit.
