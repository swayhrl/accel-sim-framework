# Final decision

Status: **PREL1_COALESCER_INDEPENDENT_SERVICE_SUPPRESSION_GENERALIZED**

Claim classification:

- `INDEPENDENT_CORRECTNESS`: **PASS**
- `INDEPENDENT_COALESCING_OPPORTUNITY`: **PRESENT**
- `INDEPENDENT_PHYSICAL_SERVICE_SUPPRESSION`: **SUPPORTED**
- `INDEPENDENT_WAIT_SAFETY`: main wait count 105, mean
  155.857143,
  p95 991,
  p99 995,
  max 996,
  head-block 0 cycles.
- `INDEPENDENT_PERFORMANCE_RESPONSE`:
  main 7,716 cycles (+0.000000% versus OFF);
  +1-cycle 7,724 cycles (+0.103681% versus OFF).

The new AT_NATIVE_REDUCE family supplies 105 exact followers. Main L1 physical
launches fall from 130 to
10, while all correctness and quiescence gates
pass. This independently generalizes the service-suppression mediator. The
equal cycle response is reported as observed; it is not upgraded into a claim
of universal speedup.

Frozen mechanism/source/binary and parameters were not modified. No fallback,
control, sweep, ideal, 0/80, other kernel, repeated measurement or Observatory
run was performed.
