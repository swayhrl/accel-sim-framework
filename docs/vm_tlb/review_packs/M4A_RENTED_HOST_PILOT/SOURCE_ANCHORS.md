# Source anchors

- Repository/branch: `swayhrl/accel-sim-framework`,
  `hrl/llm-trace-prep-v0`.
- Required pilot handoff anchor: `d22dae1fc945b2c3d3167ffcbf52027dc306c817`.
- Initial remote checkout/P1 anchor: `d22dae1fc945b2c3d3167ffcbf52027dc306c817`.
- P3 environment/build anchor: `caaaf5079f9c6b9e7301a07e585db728c20e2247`.
- P4 and closeout anchor: `ac9f42f824abb325acec0846b0da6cce78849d56`.

The remote image could reach PyPI but GitHub download/fetch stalled. The main
development host fetched the official NVBit 1.7.6 archive, verified
`dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f`, and
rsync-staged it. The project bootstrap verified that same digest before use.
Subsequent source synchronization used Git bundles fetched into remote refs;
no source files were copied outside Git provenance.

Pilot-local fixes were limited to verified-archive reuse, cu126 package
metadata acceptance plus selected-toolkit runtime PATH, and a P4-only Gloo
diagnostic to avoid a NCCL watchdog during NVBit's one-time CUDA module
instrumentation. They did not change GPU class/count, driver, NVBit version,
trace format, model identity/revision, TP meaning, ROI policy, or simulator
semantics.
