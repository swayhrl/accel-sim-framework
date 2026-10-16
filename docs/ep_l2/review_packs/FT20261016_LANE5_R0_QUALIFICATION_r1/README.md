# Lane 5 independent R0 qualification r1

**INDEPENDENTLY_QUALIFIED: B16_BANKED and U_WB16 only.**

Review authority: aec01450d3c527524ee09ee59242f582fafe5354 (review_r2 only).
Producer publication: 02982b65e87f170103b44c6dbd562a8ffb03841e.
Producing Core: 126394be46b15f55b9756d43eb9ca9a9baae1c84.
Producing Framework: 37dec04d223ae65167c5584e56887c74f6540d27.
Frozen application binary SHA256:
0b504f5573ea0721709bc3439334f7f97a177286eaf73a36876403c7c9228698.

## Independently executed/audited

- Executed the pinned directed binary and four real-partition configurations:
  12 production groups PASS, including actual cache admission/copy/lower/fill/
  response, finite staging, no-pre-mutation refusal, same-bank exhaustion,
  WAD128, response pins and sector-version reference.
- Four invalid combinations rejected with expected SIGABRT.
- All eight frozen terminal parser tests PASS.
- Reused three old/new all-OFF application pairs without rerunning a simulator.
  Independently hashed six raw logs/binaries, complete input traces, ordered
  config/environment manifests and seven scientific CSVs per row; 21 pairwise
  CSV comparisons match. Native cycles/instructions and all 64 terminal resource
  invariants independently checked for every row.
- Fixed runner acceptance of native multiline quoted DRAM config without changing
  producing bytes; all 40 tooling tests PASS. A narrow invalid-mode message check
  was corrected against preserved exact rejection output, not a model failure.

Real partition cases reach actual L2interface acceptance and true set_done.
Reduced-geometry pressure results are correctness/progress evidence, never
application capacity benefit or speedup evidence.

## Scope

Data correctness is symbolic 32B-sector versions plus request/token/resource
lifetime correctness in this simulator model. Independent versions are compared
through production store/WB/lower/fill/response. Dataless SASS cannot establish
full-byte/atomic numerical application output; none is claimed or required.
R0 attached fills cannot replace pending/pinned payloads and check ID/generation.
This does not qualify future detached RO/TVD behavior. All those bits stay OFF.

Both arms have 1168x128B/slice, 4x292 single-op banks, plus the same separately
accounted 128B copy latch. OLD_D512_STATIC is not their performance baseline.
The executable certificate is lane5/R0_INDEPENDENTLY_QUALIFIED.json in the
codex_handoff directory. It binds exact source/binary and feature vectors.
Runtime config hashes 29995661... / 5d4dd903... remain producer-exact.

Qualification launches no main application; the rolling five-pair campaign
follows immediately. Future R1 ideal binaries need their own matched baseline.
