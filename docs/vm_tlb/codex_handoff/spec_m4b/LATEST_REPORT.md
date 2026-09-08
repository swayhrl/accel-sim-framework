# Window C — SPECULATIVE M4B DEVELOPMENT current handoff

Status: `C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW` / `SPECULATIVE_CANDIDATE` /
`REFERENCE_APPROX_SUBENTRY_16`.

C11 has closed the full-ROI prefill/decode1 input and provenance gate.  This is a
review-ready precondition, **not C5 execution authorization**.  No C5 performance
replay has run.

## Frozen C11 execution identity

- Runtime/config Framework anchor:
  `d64408a97d76a320a6d49468653d416e33677af8`
- Core (including the common nonidentity PA backend):
  `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- Linked binary SHA-256:
  `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`

The C11 Core change ensures a V2 registered modeled PPN is shared by conventional
PTW fair arms and Segment fair arms.  It neither changes C9 architecture nor makes
`OBJECT_WEIGHT` a functional eligibility signal.

## C5 review inputs

The review pack is:

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C11_C5_PREFILL_PROVENANCE_CLOSURE/`

Start with `FINAL_REPORT.md`, then check `C5_ARM_MATRIX.tsv`,
`C5_COMMAND_MANIFEST.tsv`, `C5_ACCEPTANCE_MATRIX.md`,
`COMMON_PA_FAIRNESS_VALIDATION.tsv`, and `VALIDATION_RESULTS.tsv`.

- Prefill trace list: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
  (692 entries).
- Decode1 trace list: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
  (740 entries).
- Both use `C5_MODELED_PA_HIGH_UNUSED_BIT_V1`, explicitly `MODELED_DRIVER_PA`,
  never measured hardware PA.

The primary matrix is F0/F1/F2/F5/F9 plus F7/F8 at Lseg 5/10/20 for each ROI.
F6 remains an omitted diagnostic pending a separately approved 2-MiB driver PA
contract; H0 remains excluded.  C5 must receive a separate execution decision and
must revalidate all input hashes, resource admission, observables and conservation
conditions before any command is run.
