# Source diff summary

The runtime source starts from frozen ideal-control V3
`5e59fbcf7e5217e91d40e5ff2e38dfd3f48a97f8`.

Final unified binary SHA-256:
`875e89e1a6d2a1dd350954f050b0cc5dd9d26fd847b372bab5308e79e5760b05`.

New centralized source:

- `src/gpgpu-sim/bottleneck_observatory.h`
- `src/gpgpu-sim/bottleneck_observatory.cc`

Read-only hooks are placed at existing decisions in:

- `shader.cc`: scheduler predicates, instruction completion, translation READY,
  successful downstream admission, L1D status, and LDST stall enum;
- `gpu-sim.cc`: configure/reset/print lifecycle and CTA completion;
- `l2cache.cc`: L2 status, partition queues, and data DRAM return;
- `dram.cc`: source scheduler queue occupancy.

No translation controller, cache lookup/replacement, arbitration, scheduler
selection, issue decision, queue mutation, address, request, READY ownership, or
memory-partition mapping is changed.  The module has one public flag family and
does not retain the T1-specific public diagnostic flag.

OFF performs no large dynamic allocation, no observer-only traversal, and no
logging.  Level 2 uses bounded online aggregation.  Level 3 alone allocates exact
cycle progress storage and the live READY map; those costs are measured in the
overhead matrix.
