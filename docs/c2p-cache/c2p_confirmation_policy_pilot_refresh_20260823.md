# C2P+ matched-policy pilot refresh

The historical pilot root
`hw_run/c2p-confirmation-policy-v2-pilot-20260823` is retained as diagnostic
evidence only.  It used backend commit `099046a7`; the final matched 64 x 4
x 3-bit policy matrix uses `9b724500`.  The older build also predates the
explicit initial-score/forced-small-candidate configuration lines and the
`c2p_adaptive_package_start_forced` counter.  It must not be used to qualify
the final matrix.

The replacement pilot is run at:

`hw_run/c2p-confirmation-policy-v2-pilot-refresh-20260823`

It reruns B+tree, BFS, and LPS with the fixed final binary and the three
matched policies (exhaustive control, PC-hash, AddrTopo).  Qualification is
only granted if the strict matrix analyzer reports normal exit, matched
triplet provenance/configuration, remote-hit equals L2-avoidance, and all
probe/continuation/package/residual conservation checks.

The finalizer consumes this refreshed root, rather than the historical root.
