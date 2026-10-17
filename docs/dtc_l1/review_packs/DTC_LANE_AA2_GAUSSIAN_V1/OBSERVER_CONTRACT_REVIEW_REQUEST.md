# AA2-OBS-001: shared event observation qualification remains unresolved

Candidate Core is fixed at `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`; the exact source excerpts and hashes are in OBSERVER_CONTRACT_AUDIT.json and CANDIDATE_SOURCE_SHA256.tsv. This is a reviewable qualification issue, not an assertion that the OO invalidation implementation is incorrect.

The production option is `-gpgpu_dtc_l1_invalidate_on_source_event`, default0. When it is0, LDST invokes the original ordinary invalidate/cycle paths; no source-invalidation observer request/cycle bookkeeping or DTC_INVALIDATE_V1_SUMMARY printing runs. When it is1, the observer counts source requests, ordinary commits, mapping changes and retained/reclaimed states, and occupancy is sampled before immediate source-event reclamation. The existing debug-event limit remains0 in all four proposed configs; this disables detailed records, not K1 summary bookkeeping.

X explicitly declares zero extra **simulated** cycles for the logical sweep/observer. Host execution cost, emitted-counter availability and modeled GPU-cycle cost are different quantities. AA2 does not infer different GPU-cycle results merely from different host bookkeeping. It also does not silently promote that zero-cycle declaration into the user's required identical four-cell event observation contract/overhead qualification.

Before any full run, the exact Y2/source/observer scope must resolve whether this K1-only observation under one fixed binary satisfies the requested common observation contract. If qualified, K0's unprinted event fields must still be UNAVAILABLE, never measured0; the asymmetry and idealized modeled cost remain explicit. If not qualified, all four remain HOLD. AA2 requests no Core modification, second Core, new counters or extra experiments to resolve this issue.

Independently, the live foreign DTC dispatch authority and its fdinfo FLOCK already close current execution admission. An observer interpretation cannot waive that execution-rights barrier. No performance outcome has been read or used to select this issue or alter the fixed design.
