# C10B-0 resource-deferred blockers

1. Host `memory` and `io` PSI `full` totals must stop persistently increasing
   over the admission confirmation window before any compile is attempted.
2. Once healthy, compile current Core `12267bb7` without functional edits,
   serially (`-j1`), beginning with `vm_c10a2_static_model_test` and then
   `vm_c10a_registered_segment_test`.
3. Resample MemAvailable, SwapFree, swap-in/out, memory/io PSI full deltas and
   iowait before and after each compile/test. A renewed persistent PSI-full
   increase returns directly to `RESOURCE_DEFERRED` and forbids full link.
4. Simulator/full-link admission, C10B-1 and every later C10B gate remain
   unstarted. C5 remains prohibited.

No functional Core change was made, so no implementation failure has been
identified or repaired at this checkpoint.
