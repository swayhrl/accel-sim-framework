# M4I-3 final-Core admission

Status: `PASS`.

The isolated Framework checkout was cold-built against isolated Core
`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d` using the latter as
`GPGPUSIM_ROOT`; the release build of `gpu-simulator/bin/release/accel-sim.out`
completed with exit status zero.  The Core branch has no semantic source change
relative to that accepted anchor.

All compact final-Core directed regressions compiled with `-std=c++11 -Wall
-Wextra` and passed:

`vm_core_m1_test`, `vm_m2_g2_{1,2,3,4}_test`,
`vm_m2_rf_pending_retry_test`, `vm_m3_g3_{1,2,2b_width,2c_hierarchy,3_pwc,
4a_page_size,4b_tlb_timing,5_latency_accounting}_test`.

This covers disabled/ideal identity semantics, pending-waiter no-reprobe,
bounded TLB/MSHR/PWQ/walker behavior, non-recursive PTE association, PWC,
page-size and lookup no-polling behavior, and the G3-5 latency accounting
invariant.  Fresh staged inputs did not include the historical Rodinia LUD/BFS
corpus; final-Core functional integration was therefore additionally checked
on fresh formal LLM compute samples (prefill and decode1) rather than treating
an unavailable historical log as a current run.  The historical LUD/BFS formal
evidence remains frozen in `M1_M3_VM_BASELINE_CLOSEOUT` and was not rerun or
modified.
