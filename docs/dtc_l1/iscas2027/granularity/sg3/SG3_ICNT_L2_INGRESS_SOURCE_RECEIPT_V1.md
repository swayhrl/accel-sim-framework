# SG3 R5.0 ICNT-to-L2 ingress source receipt

Authority: `c055d817b009cbe6a59c7f8ac7af1081f86ec6e8`; execution R5 handoff on
master `75684c33a768ec18a9f41f4d67c71a114b840782`.

Source inspection of the frozen DTC Core records the following.

1. `l2cache.cc:488-497` parses `gpgpu_L2_queue_config` as
   `icnt_L2:L2_dram:dram_L2:L2_icnt`, and constructs four FIFOs in exactly
   that order.  The framework base config supplies `64:64:64:64`.
2. `l2cache.cc:708-710` forwards `full(size)` to the ICNT-to-L2 FIFO's
   finite-capacity size admission check.  `gpu-sim.cc:2324-2331` calls it
   with `SECTOR_CHUNCK_SIZE`, the worst-case four-sector expansion.
3. That same block increments `gpu_stall_icnt2mem` only when the ingress
   admission test is true *and* `icnt_has_packet(...)` is true.
4. `gpu-sim.cc:1730` prints that counter with legacy text
   `gpu_stall_dramfull`; it is not a DRAM-full counter.
5. R5 changes only the first queue field to 256.  Thus it leaves L2 capacity,
   MSHR/miss queue, the other three partition queues, scheduler/return queues,
   channels, mapping, DTC semantics, trace, Core, and runtime identity fixed.

This receipt authorizes only the registered G/H BICG rows.
