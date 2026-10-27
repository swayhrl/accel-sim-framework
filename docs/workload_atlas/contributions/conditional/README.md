# Agent F - seven conditional workload audits

All seven source reports are complete for the inspected fixed source. They retain `UNRESOLVED` ordinary identity. Source read/verification is independent of input, historical ELF, full capture scope and measured runtime.

- [backprop](../../programs/other/backprop.md): two hybrid GPU phases, single CPU-controlled training step.
- [cfd](../../programs/other/cfd.md): four unique kernels,14003 source launches; five-kernel capture misses every time-step.
- [kmeans](../../programs/other/kmeans.md): transpose and assignment, CPU convergence, up to501 assignment iterations/trial.
- [nn](../../programs/other/nn.md): materially different streamed-character and all-at-once FP32 implementations.
- [nw](../../programs/other/nw.md): tiled DP wavefront,15 versus255 launches, kernel ABI difference.
- [pathfinder](../../programs/other/pathfinder.md): temporal halos, added3.1 synchronization and CLI/source mismatch.
- [streamcluster](../../programs/other/streamcluster.md): one GPU gain implementation controlled by CPU search; five-launch capture cannot be normal completion for fixed source parameters.

`SOURCE_MANIFEST.json` records per-file SHA256; the coordinator's root `SOURCE_BLOB_VERIFICATION.json` binds source bytes to fixed upstream commit. `TRACE_SCOPE.json` records every frozen candidate's metadata and all first-nine-line kernel headers. Historical whole-trace hashes are copied from existing authority, not rehashed; no trace body was scanned. `summary.json` is the integration array.

Source-based formulas, possible cache behavior and runtime observations are kept distinct. No build, native GPU run, capture, simulation, controller/registry mutation, raw-output processing, input promotion or historical science edit occurred.
