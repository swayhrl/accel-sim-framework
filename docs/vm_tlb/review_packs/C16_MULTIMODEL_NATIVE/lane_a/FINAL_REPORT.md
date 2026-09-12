# C16 A local prep and integration closeout

Final status: `C16_LOCAL_PREP_AND_INTEGRATION_PARTIAL_READY_FOR_FINAL_REVIEW`.

Lane A completed the available C15 metadata/provenance closeout and C16 local
pre-rental preparation.  The C15 A/B/C baselines are separately commit- and
manifest-hash-bound; model/deployment roles, tokenizer revisions, actual token
IDs, and S0–S4 identities are frozen.  The C16 stage-by-stage execution and
scientific status is the one-row-per-stage `C16_STAGE_STATUS.tsv`.

What is ready:

- C16-0.0, 0.1, 0.2, 0.6, and 0.7 passed their local/provenance acceptance
  scope.  Llama's existing checkpoint and every downloaded metadata/tokenizer
  file have local SHA-256 values.  Every absent non-Llama checkpoint shard has
  a fixed remote LFS SHA-256 and size, without downloading its content.
- All 84 stored token receipts are actual CPU tokenizer outputs over three raw,
  hash-bound input classes and four exact prefill lengths.  No input is inferred
  from a model family or copied from a live producer worktree.
- C16-5.4, 6.2, and 6.3 are explicitly not qualified rather than filled with
  static or historical substitutes.  No common pattern, behavior class, cost
  reduction, timing, cache/TLB result, or MoE routing result is claimed.
- Fixed G and C releases are now hash-validated in `integration/`: G provides
  only offline C16-0.3/0.4 infrastructure closure, and C provides only offline
  C16-0.8/3.x/6.1 boundaries.  Neither is promoted to native evidence.

What blocks the remaining work:

- H commit `65b5357400db3b4c77f8a60e575091e22fb081ee` lacks a publish manifest
  or equivalent payload-hash release.  A rejected it as an input rather than
  reading a live partial.  This blocks C16-0.9 GPU package publication and all
  native/fingerprint synthesis.
- Non-Llama full weights are intentionally not local.  The asset manifest makes
  the exact file set hash-addressable, but a transfer cannot begin until the
  complete package, G environment lock, and C/H offline-gate artifacts are
  published and a fresh authorization permits it.

No GPU, CUDA model execution, profiler, NVBit, simulator, SASS, or full-ROI
task was started.  The three bounded future high-fidelity requests in
`NEXT_HIGH_FIDELITY_REQUESTS.md` require new authorization and are not queued
for automatic execution.
