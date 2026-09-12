# C13 dependency snapshot

Read-only snapshots were taken after common audit, after P/N instrumentation,
and before final synthesis.  The first two resolved
`origin/hrl/vm-m4b-c13-diagnostics-v0` to
`889704ff6e8e7ed52c8aad8c5f414bc9fd743af3`; the final fetch resolved it to
`9ab1e0708af66a533d9327f35f1a3e63a34c4285`.

Final fetched status:
`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`.

- The nine original C13 mode=1 (`SUBENTRY_16`) results remain explicitly
  `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16` and are excluded from every C14
  scientific judgment.
- The repaired configurations explicitly use L2 mode 0.  C13 reports EQ1 and
  EQ2 exact for kernel markers, simulated cycles, and modeled `gpu_*`/`vm_*`
  counters (host-wall-clock-derived `gpu_total_sim_rate` excluded).  Its
  repaired results are therefore promoted.
- C13's closed Path-A report gives a Prefill L8 delta of `-1189116` cycles and
  L9 delta of `-206118` versus F0 (`9 < Lseg* < 10`, bracket only), plus a
  Decode L11 delta of `-24692` (`11 < Lseg* < 20`, bracket only).
- C13 explicitly leaves queue/DRAM/global-critical-path causality unresolved.
  This directly raises the priority of C14 N's bounded exposure observation;
  it does not reopen P, whose source/runtime `NO_GO_WITH_EVIDENCE` is
  independent of C13 timing.

No C13 worktree, branch, output directory, review pack, or raw artifact was
modified.  The only C14 interaction was read-only `git fetch`.
