# SG3 busW 16->32 B probe reclassification

The accepted busW attempts and their PASS receipts remain immutable diagnostic evidence.  They are reclassified, not deleted or relabeled as failures.

For the dominant sector-read path, L2 issues a 32-B sector request.  At the default, `dram_atom_size = BL(2) * busW(16 B) * chips(1) = 32 B` (`gpu-sim.h:437-438`), and the detailed-DRAM transmission/return paths advance `txbytes`/`dqbytes` by exactly this atom (`dram.cc:298-301,570-592`).  A 32-B request consequently already completes in one detailed data step.  Raising `busW` to 32 B makes a 64-B atom but does not reduce the one-step count for such a request.

Therefore the prior null result does **not** test a meaningful 2x transfer-step reduction for the dominant 32-B sector-read path and cannot support the statement “2x DRAM service rate is insufficient.”  The formal R1 service-rate upper bound is instead DRAM clock 850->1700 MHz with core/ICNT/L2 clocks and DRAM timing cycle counts held fixed.  This is a config-only, source-defined time-domain upper bound, not a physical product-frequency claim.
