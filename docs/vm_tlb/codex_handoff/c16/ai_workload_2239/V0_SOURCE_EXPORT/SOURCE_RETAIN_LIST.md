# Source retain list

The following stays in the source environment after any future copy.  V0 made
no copy, move, or cleanup.

- `/root/share/c16_recovery_v3` in full: historic RTX3090 recovery and closeout
  endpoint, including excluded archival material and the 17 unresolved local
  items listed in `UNKNOWN_PROVENANCE.md`.
- Every `/data/c16` asset named by a 4080 receipt, including the N1 `.ncu-rep`,
  CSV, U8 raw-root, userspace runtime, wheelhouse, and any R5 raw payload.  The
  current container cannot access that path, so this is a retain policy rather
  than an existence claim.
- Source Docker’s decouple-L1/L2, L2, and other non-AI architecture work.
- Host-private `/home/...` / `/etc/...` administrative records and any secret
  material.  These are not Git or artifact-transfer inputs.

Future operations are copy-not-move and must close source size/SHA to
destination size/SHA per artifact.
