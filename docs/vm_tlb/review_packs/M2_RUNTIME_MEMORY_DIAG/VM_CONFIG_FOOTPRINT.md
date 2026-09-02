# D2/D3 effective configuration and footprint

The runtime-parsed values were: 46 SMs, 64 KiB page, L1 32 entries/32-way/one
port per SM, shared L2 768 entries/16-way/one port, MSHR 32, PWQ 32, walkers
16, and fixed walk latency 5 cycles.  `threads_per_sm=1536` and `warp_size=32`
were also verified while diagnosing the unrelated cluster allocation.

`translation_controller` allocates 46 L1 TLBs and one L2 TLB at construction;
the MSHR/PWQ/walker vectors are initially empty.  Conservatively charging 64 B
per entry gives `(46 * 32 + 768) * 64 = 143,360 B` (140 KiB), before small
vector/object overhead; this is well below 256 KiB.

The standalone production-size controller test constructed this exact setup,
asserted invariants, and completed with RSS below `/usr/bin/time`'s 1 KiB
reporting granularity.  Evidence: `/tmp/m2d-runtime-memory/D3_CONTROLLER.log`.
