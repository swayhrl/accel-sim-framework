# Validation summary

All scientific and correctness gates required before the S1 decision pass.

- handoff HEAD and exact scientific parent: verified;
- accepted B0/O2 summaries and immutable CONTEXT2 identities: hash verified;
- Stage A: exact 32-byte coalescing cross-check for kernels4-6;
- detailed availability ledger: 8,740,881 line/sector rows, gzip/hash valid;
- isolated S1 cold build and exact patch reproduction: PASS;
- S1 policy/resource directed checks: 24/24;
- source placement/resource checks: 18/18;
- accepted VM regressions: 3/3;
- accepted transient policy and O2 helper regressions: PASS;
- new-binary default OFF: exact accepted T2;
- new-binary explicit none: exact accepted T2;
- positive S1 smoke: read/write, exactly-once and full drain PASS;
- formal context: exact accepted cycle/instruction/CTA/L1D/L2/DRAM signature;
- formal S1: rc=0, stderr=0, 6/6 coverage and 56/56 gates PASS;
- duplicate application, semantic fail-closed counters and context service: 0;
- translation/controller/cache/interconnect/DRAM terminal state: quiescent;
- H1/FULL5 directories: absent as required by the failed S1 gate.

The completed formal raw needed postprocess-only recovery. The immutable receipt
binds the original command/log/rc/stderr hashes and proves no simulator rerun.
