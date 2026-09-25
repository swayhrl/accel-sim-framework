# Memory queue-chain and DRAM-headroom review pack

Status: `CLOSED_ALL_REGISTERED_ROWS_STRICT_PASS`.

This pack records the bounded continuation authorized by the current
`chatgpt_handoff`.  It starts from accepted BICG queue=128 evidence and the
retained (but non-discriminating) 16-to-32-B bus-width diagnostic.  The only
new numerical question is whether source-supported memory-side queue-chain
headroom and/or detailed-DRAM service timing can convert default-cap=8192 DTC
concurrency headroom into performance.

The registered work is deliberately small:

1. Twelve BICG R1 rows: six source-defined queue-chain/DRAM configurations
   for both IO and OO.
2. At most two GESUMMV configuration pairs, selected by a predeclared BICG
   5% eligibility gate and fixed priority `F, E, D, A, B, C`.
3. Two BICG R4 all-headroom ceiling rows only after F qualifies.

Every numerical result natural-exited and strict-PASSed in its own immutable
directory.  R1 establishes that queue-chain buffering alone is not beneficial
for BICG, whereas the predeclared detailed-DRAM 2x time-domain service probe
is strongly beneficial; R3 confirms that bounded direction on GESUMMV for the
two fixed-priority eligible configurations.  R4 is a paired 20MiB ceiling
check only, not a capacity sweep.  These are simulator-model counterfactuals,
not a claim about a physical GPU clock or a unique universal bottleneck.

Start with [R0_AUDIT_INDEX.md](R0_AUDIT_INDEX.md),
[R1_BICG_MATRIX.md](R1_BICG_MATRIX.md), [SOURCE_ANCHORS.md](SOURCE_ANCHORS.md),
and [OPEN_ISSUES.md](OPEN_ISSUES.md).
