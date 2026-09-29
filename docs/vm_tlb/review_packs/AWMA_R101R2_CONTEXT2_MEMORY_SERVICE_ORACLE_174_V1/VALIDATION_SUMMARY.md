# Validation summary

All required gates pass.

- input derivation: exact zero-based indices 3-8, six immutable samefile
  symlinks, 44 tiles, sidecar state/transition mapping and full opcode/address
  decode PASS;
- measured semantics: LDG/LDGSTS/STG only, ATOMIC/RED and unsupported target
  records zero;
- O2 policy/direct tests: 18/18 PASS;
- integration source-hook checks: 14/14 PASS;
- accepted VM regressions: 3/3 PASS;
- accepted transient-region policy regression: PASS;
- default absent and explicit none: exact accepted T2 cycles/instructions/CTA;
- positive dynamic smoke: real read/write O2, 29,280 transactions with exact
  schedule/ready/retire equality and clean terminal state;
- isolated cold build and O2 Core patch reproduction: PASS;
- formal B0/O2: rc=0, stderr=0, 6/6 coverage, all 54 summary gates PASS;
- context B0/O2: all registered L1D/L2/DRAM/cycle/instruction/CTA/lifecycle
  fields exactly matched;
- finalizer decision and repeat policy: PASS;
- raw index and node164 manifest verification: PASS.

The formal-at-run summarizer postprocessing issue is documented in
`ENGINEERING_FIXES.md` and each immutable recovery receipt.
