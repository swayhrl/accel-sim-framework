# M4R bounded real-trace throughput pilot

Status: `PASS` — progress healthy.

The first decode1 COMPUTE trace (`kernel-1464-ctx_0x55d98da1ddf0.traceg.xz`)
ran to normal exit using the exact M4R 49-bit, real-PTE configuration.  It
completed 2,019,328 simulated instructions and 17,390 cycles in 2.62 seconds
at 196,608 KB RSS.  VM work was nonzero and quiescent: 1,568 lookup launches
and completions, 2 MSHR allocations / 30 merges, 2 walks, 7 PTE requests and
responses (all DRAM), zero PTE response misassociations, and zero final active
MSHR/PWQ/walkers.

The pilot demonstrates both real-PTE progress and the expected nonzero TLB
path; it is not a replacement for formal full-list replay.  A naive linear
extrapolation from this small 2.0M-instruction trace is only a loose upper
bound, so later full-run scheduling records measured progress rather than
substituting a sampled result.
