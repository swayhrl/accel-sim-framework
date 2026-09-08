# Open issues and scope boundary

- Object-specific DRAM channel/bank/row attribution is not available.
- `L1D_ACCESS_ATTEMPT_WINDOW` remains observation-only with its frozen
  access-attempt semantics; it is not an exact coalesced-transaction measure.
- The pre-correction/post-correction Framework manifest lineage is preserved
  explicitly in `C3_RUNTIME_PROVENANCE.tsv`; no historical manifest is edited.
- This package stops after C4.  No C5, M4B, or M5 execution is authorized here.
