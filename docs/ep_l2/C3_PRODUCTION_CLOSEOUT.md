# EP-L2 C3 production closeout

Status: PASS (C1/C2 PASS; C3 conditional-pass action items closed by C3b).

## Verification contract

The Core fixture `tests/ep_l2/run_descriptor_mshr_integrated.sh` links the
current CMake build and drives one real memory partition. Its target fixture
uses one memory channel and one L2 slice, target descriptor settings
`128 line MSHRs / 256 global descriptors / 32 descriptors per line`, and a
real simple-DRAM return path.

| Review item | Production-path evidence |
|---|---|
| I1 descriptor lifetime | MissQ and L2→DRAM drain do not free it; a real return and fill make it ready; a full L2→ICNT FIFO retains it; real enqueue frees it and the line MSHR. |
| I2 different sector | `A+0` + `A+32`: one line MSHR, two descriptors, exactly two lower reads, two replies. |
| I3 same sector | `A+0` twice: one line MSHR, two descriptors, exactly one lower read, two replies. |
| I4 global exhaustion | 64 lines × four requesters reaches 256 descriptors while line entries remain 64 and chains remain four. Request 257 reports `DESCRIPTOR_POOL_FULL`; release then drains through production queues. |
| I5 exact reason | `l2_access_plan::ep_l2_mshr_block_reason` and target lower-read prediction are non-mutating observability fields only. |

## Deliberate non-scope

This closeout does not start C4 WAD, C5/C6 payload RAM/banking, Unified/RO/TVD,
graphics bypass, `EPL2B0V1`, or characterization. The next action requires a
separate authorization.
