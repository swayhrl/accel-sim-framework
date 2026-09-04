# M4B integrated execution report

Current stage: `M4R PASS / M4C NEXT`.

Fresh isolated branches were created at the authorization and Core anchors.
Track-B was path-scoped imported from `e21ffebce280e6b932fb4556ef75c609ff54c326`
with 87 source/destination blob-identical records in
`review_packs/M4I_AB_INTEGRATION/B_IMPORT_MANIFEST.tsv`.  Archives, semantic
derivatives, RF0 object-range safety, final-Core cold build/direct regressions,
49-bit admission, and final-Core parser smoke pass.  No B Core was imported,
no archive was changed, and no synthetic KV or Segmentation behavior exists
yet.  M4R selected compute-only as the primary replay policy because the
paper gives one tensor-parallel partition rather than a rank-complete replay
contract.  The policy and its bounded real-PTE pilots are frozen in
`review_packs/M4R_LLM_REPLAY_COMPAT/`; the representative decode COMPUTE
trace completed normally with nonzero, quiescent translation traffic.  The
full rank-complete list remains a sensitivity run, not an interchangeable
primary result.
