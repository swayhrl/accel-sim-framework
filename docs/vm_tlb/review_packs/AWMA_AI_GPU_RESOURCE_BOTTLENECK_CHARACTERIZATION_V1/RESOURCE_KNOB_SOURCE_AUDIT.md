# Resource-knob source audit freeze

This audit precedes every new scaling result. It applies to the frozen
WARP_VPN_DEDUP_REFERENCE binary (`ff43ee33257fac6171ddb31a81a561e10691b5c52d2127545719f6ba8709bef0`)
and RTX4080/V1 config (`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`).

The interventions are simulator diagnostics, not claims about physically
available RTX4080 resources. Instructions, CTA identity, trace records,
translation policy, and all non-selected config fields must remain constant.

## Audit conclusions

- Scheduler/front-end is observational only. Doubling scheduler count under
  sub-core mode would change warp partitioning and issue topology.
- The generic LDST-count option is rejected because its own option text says it
  is not hooked up. SP count alone is rejected because the frozen four-wide
  pipeline would remain a second cap.
- Specialized Tensor and SFU instance counts are finite source-created units;
  their latency and register widths remain fixed when count changes.
- Adaptive L1 capacity is rejected because shared-memory allocation can change
  associativity and occupancy. L1 latency, bank count, and MSHR entries remain
  separately identifiable.
- L2 capacity, MSHR entries, and data-port width are distinct fields. The
  baseline ROP latency is already zero and is not treated as an L2-hit knob.
- The configured local crossbar explicitly treats every packet as one flit.
  Neither `icnt_flit_size` nor buffer capacity is relabeled as ICNT bandwidth.
- DRAM bus width is rejected because it changes transaction atom size. The
  data-command frequency ratio is retained as a service diagnostic, with its
  coupled turnaround-timing change reported rather than hidden.
- Translation uses accepted sequential-vs-B1 results only; this stage does not
  rerun or redesign translation.

The machine had 512 logical CPUs, 349 GiB available memory, and no active
Accel-Sim process at the audit point. Durable outputs are placed on mnt164
because the root filesystem had only about 1.9 GiB free.
