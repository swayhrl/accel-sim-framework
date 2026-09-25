# Claims and boundaries

Paper-safe claim: under this frozen BICG identity, increasing only the
ICNT->L2 FIFO from 64 to 256 does not materially improve performance, either
at default detailed-DRAM service or as an increment over the accepted DRAM2x
probe.  The large ingress-pressure count therefore behaves as pressure, not a
demonstrated dominant FIFO-capacity limit.

Forbidden overclaims: no cross-workload conclusion; no physical-GPU queue
capacity claim; no attribution to NoC, L2->ICNT, ROP, DRAM timing, or a unique
hardware bottleneck.  This closure authorizes no queue >256, GESUMMV, NoC,
L2 capacity/MSHR/miss-queue, DTC-cap, or additional DRAM experiment.
