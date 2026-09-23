# SG3 V4 bounded cap-validation closure V1

Snapshot time: `2026-09-23T16:41:05Z`.

## Evidence boundary

All cells below are fresh, natural-exit, strict-PASS observer-ON receipts with
the recorded authority instruction identity.  The GESUMMV IO baseline and IO
`cap=2048` receipts are indexed in `SG3_EXECUTION_DATA_SNAPSHOT_V6.tsv`; the
other completed GESUMMV and positive-control receipts are indexed in V5.
The historical SG3/SG5 `-9` attempts remain preserved non-scientific failures
and contribute no result.  No capacity or MSHR GESUMMV row is used here.

## Predeclared cap result

The percentages are cycle changes versus each workload/mode's own `cap=base`
observer-ON baseline; negative is faster.

| Workload | Mode | base cycles | cap=512 | change | cap=2048 | change |
|---|---:|---:|---:|---:|---:|---:|
| BICG | IO | 93,942,704 | 24,422,555 | -74.0% | 59,803,803 | -36.3% |
| BICG | OO | 47,231,655 | 18,938,635 | -59.9% | 35,141,974 | -25.6% |
| GESUMMV | IO | 210,667,785 | 114,583,629 | -45.6% | 173,881,517 | -17.5% |
| GESUMMV | OO | 143,059,605 | 86,671,612 | -39.4% | 118,050,940 | -17.5% |

The independently predeclared cap=512 positive controls go in the opposite
direction: Btree is +9.6% (IO) and +44.1% (OO), while 2DConvolution is
+182.2% (IO) and +208.5% (OO).  Their cycle identities are likewise exact.

## Bounded conclusion and stop decision

The BICG injection/oversubscription classification has independent GESUMMV
support at the predeclared cap points: stronger throttling (`cap=512`) is more
beneficial than `cap=2048` in both modes.  The Btree and 2DConvolution positive
controls show that this is not a universally beneficial throttle.  This is
sufficient for the bounded paper claim that the response is workload-specific
and is consistent with DTC injection pressure for BICG/GESUMMV.

This result does not assert a unique physical L2 root cause, does not turn any
merge-tag identity-guard retry into a resource statistic, and does not
generalize the BICG MSHR conclusion beyond BICG.  The predeclared conditional
GESUMMV capacity/MSHR and service expansions are therefore not triggered:
they are unnecessary to support the bounded claim and would only fill an
unneeded matrix.
