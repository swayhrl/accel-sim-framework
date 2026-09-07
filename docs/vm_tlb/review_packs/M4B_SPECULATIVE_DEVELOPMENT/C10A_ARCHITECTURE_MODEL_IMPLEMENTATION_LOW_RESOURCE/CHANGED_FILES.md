# Changed files and ownership

Core commits are intentionally separated and were staged by explicit path.

| Commit | File | Change |
| --- | --- | --- |
| `5191bb5b` | `src/gpgpu-sim/vm_translation.h` | V2 descriptor interface and true-PA mapping fields. |
| `5191bb5b` | `src/gpgpu-sim/vm_translation.cc` | V2 parser, non-identity PPN arithmetic, ordinary-PTE consistency override, initial HIT_FIRST path. |
| `5191bb5b` | `tests/vm_c10a_registered_segment_test.cc` | initial non-identity registration focused test. |
| `c27bf0e2` | `src/gpgpu-sim/vm_translation.h` | access intent, local-replica state, telemetry ABI, fair sub-entry APIs. |
| `c27bf0e2` | `src/gpgpu-sim/vm_translation.cc` | local replicas, port/fallback/order telemetry, MISS_JOIN accounting, leaf/asid/global invalidation. |
| `c27bf0e2` | `tests/vm_c10a_registered_segment_test.cc` | controller cases for Segment-first, write fallback/PTE agreement, L1-first, G96/G32 geometry and invalidation. |
| `c27bf0e2` | `tests/vm_m4b_weight_segmentation_test.cc` | updates C3 expectations from wait-both to C10 HIT_FIRST. |
| C10-A Framework closeout | `configs/vm_tlb/M4B_C10A_FAIR_ARM_CONTRACT.tsv` | static F0--F9/H0 manifest contract. |
| C10-A Framework closeout | `util/vm_tlb/validate_c10a_fair_contract.py` | no-simulator arithmetic/guard validator. |
| C10-A Framework closeout | this review-pack directory | provenance, implementation and validation record. |

No Core or Framework path outside these explicit changes was staged by this
goal. No Window A/B worktree, scratch, binary, process, trace, object map or
configuration was touched.
