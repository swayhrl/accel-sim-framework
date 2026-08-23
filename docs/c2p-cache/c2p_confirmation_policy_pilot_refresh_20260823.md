# C2P+ matched-policy pilot refresh

The historical pilot root
`hw_run/c2p-confirmation-policy-v2-pilot-20260823` is retained as diagnostic
evidence only.  It used backend commit `099046a7`; the final matched 64 x 4
x 3-bit policy matrix uses `9b724500`.  The older build also predates the
explicit initial-score/forced-small-candidate configuration lines and the
`c2p_adaptive_package_start_forced` counter.  It must not be used to qualify
the final matrix.

The replacement pilot ran at:

`hw_run/c2p-confirmation-policy-v2-pilot-refresh-20260823`

It reran B+tree, BFS, and LPS with the fixed final binary and the three
matched policies (exhaustive control, PC-hash, AddrTopo).  All nine replays
passed the strict matrix analyzer: normal exit, matched triplet
provenance/configuration, remote-hit equals L2-avoidance, and all
probe/continuation/package/residual conservation checks.

The refreshed pilot and the running final matrix have the same identities:

- backend commit `9b7245008ca12c5acb3c62fa269df29b1729c3d3`;
- simulator SHA-256 `ae8ee5113bded602d30802b8264ff6e98187dff3055a5961405e87cae13a7df8`;
- `libcudart` SHA-256 `220dbb275a3ae387c7631a6fd5e693450294e140aa93687420a8953156db635b`.

The finalizer consumes this refreshed root, rather than the historical root.
