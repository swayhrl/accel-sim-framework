# EP-L2 C5–C7 Production Closeout

Status: closeout in progress; this document does not authorize workload characterization.

## Frozen scope

The implementation keeps the B0 contracts unchanged: 1024 static resident
payload slots, 128 static bypass slots, no borrowing, no RO-no-MSHR path, no
replaceable RO-pending state, no TVD functionality, and no graphics borrowing.

## Production integration

* C5 uses independent resident and bypass 1R1W ports.  In target mode the
  historical DataPort and FillPort do not become a second admission gate.
* Resident identity is assigned at miss allocation, carried with every sector
  lower transaction, and validated on return.  A multi-sector line keeps one
  payload ID/generation until all fills land.
* C6 retains 1024+128 static ownership and uses per-bank pending operations
  with sequence-number oldest-ready grant.  A denied request remains pending;
  no request is dropped or duplicated.
* C7 emits a separate `EPL2B0V1` family.  Application records are cumulative;
  kernel records are completion deltas.  `overlap_detected=1` means that a
  record is a shared-resource interval measurement and is not exclusive kernel
  attribution.

## Analysis contract

`util/ep_l2/parse_epl2_b0.py` creates only the target artifacts:

* `target_summary.csv`
* `target_slice.csv`
* `target_kernel.csv`
* `target_bank.csv`
* `manifest.json`

The parser never redefines or consumes `L2CHARV1`.  Its manifest states that
characterization has not started.

## Closeout gates

Before this document can be marked PASS: run C3–C7 directed regressions,
the parser regression, a Release build, instrumentation OFF/ON timing-neutral
fixture, and package the exact logs and source revisions into a review pack.
