# C3 final status

`C3_FINAL_STATUS = TERMINAL_PASS`

At `2026-09-08T00:22:10Z`, a fresh, non-overwriting execution of
`summarize_m4c_runs.py --require-level 2` over the frozen C3 root produced
eight `PASS` rows. It revalidated each manifest's `simulator_exit_status=0`,
the immutable expected-kernel count, `Processing kernel` markers, and
`m4c_telemetry_schema` records. For each generic/paper arm it also revalidated
PTE request/response equality, zero response misassociation, waiter
registration/wakeup equality, and object-attribution conservation.

The fresh summary SHA-256 is
`6f7538f62a85e5489d54e08eaa41ffaf3aa2012730b2261ab1d832019b5158a4`.
It has the same content hash as the frozen v3 C4 summary input; it was written
to a distinct publication-check directory and did not overwrite prior C3
evidence.

`prefill-paper`: exit `0`; marker/expected `692/692`; telemetry/expected
`692/692`; final cycles `62173001`; final IPC `296.7948`.

The original Framework split is preserved: decode disabled/ideal/generic use
`7709376eb7c7358247e1868f80a143edb54ce69d`; decode paper and all prefill
arms use `a7c0759be7f293ed0d5e2179c62094b6de49c1e8`. All use Core
`0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` and the frozen binary recorded
in the provenance table. No C3 simulator remains active.

This status does not claim C4 completion, locality completion, or host
readiness for another window.
