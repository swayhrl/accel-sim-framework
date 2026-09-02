# M2-RF changed files

Core commit `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b` changes four files:

| File | Change |
| --- | --- |
| `src/gpgpu-sim/vm_translation.cc` | detects a registered `(key, UID)` before TLB arbitration; emits new observability counters |
| `src/gpgpu-sim/vm_translation.h` | defines clean retry/lookup and MSHR occupancy, merge-depth, lifetime statistics |
| `tests/vm_m2_rf_pending_retry_test.cc` | exact non-reprobe/non-starvation test |
| `tests/vm_m2_rf_kernel_persistence_test.cc` | focused warm-translation boundary persistence test |

There is no changed VM configuration, resource limit, mapping policy, page
size, or G3-2/PTE-memory integration.  The Framework update for this repair
is documentation/evidence only.
