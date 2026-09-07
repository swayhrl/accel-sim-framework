# C10-A2 named-blocker static closure

## Status and scope

Final status: `C10A2_STATIC_BLOCKERS_CLOSED_COMPILE_AND_RUNTIME_DEFERRED`.

This pack closes the source/static portions of C10-A blockers B2--B7. It is
not a build result, simulator result, replay result, or performance claim.
The retained labels are `REFERENCE_APPROX_SUBENTRY_16` and
`SPECULATIVE_CANDIDATE`.

The admitted inputs were Framework `d112714291ff789194ab335940f76243920b4404`
and Core `c27bf0e2fc5e24c54966426840bd56748ef92028`; see
`INPUT_PROVENANCE.tsv`. The resulting Core static-closure checkpoint is
`12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`. No Window A/B worktree, build,
link, simulator, C5, or large trace operation was used.

## Delivered static contracts

| Blocker | Static closure | Evidence |
| --- | --- | --- |
| B2 | V2 registration stages all descriptors and semantically rejects atomically to conventional paging. | `REGISTRATION_TRANSACTION_MODEL.md` |
| B3/B6 | Explicit `INACTIVE → INSTALLING → ACTIVE → REVOKING` local-replica lifecycle. | `SEGMENT_LIFECYCLE_MODEL.md` |
| B4 | Sole production caller derives READ/WRITE/ATOMIC from `warp_inst_t`. | `ACCESS_CLASS_INTEGRATION.md` |
| B5 | F0--F4/F6--F9 selector, geometry and emitted realized fields; F5/H0 hard blocked. | `FAIR_ARM_RUNTIME_PLUMBING.md` |
| B7 | ASID generation binds lookup/MSHR/fill; shootdown rejects stale completion. | `SUBENTRY_GENERATION_RACE_MODEL.md` |

`STATIC_VALIDATION.md` records only no-build checks. `REMAINING_C10B_BLOCKERS.md`
names every compile, runtime and F5 obligation that remains before C5 can be
considered.
