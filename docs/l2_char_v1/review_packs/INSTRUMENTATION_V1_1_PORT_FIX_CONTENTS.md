# Instrumentation v1.1 port-sampling review pack

`instrumentation_v1_1_port_fix.tar.gz` is a reproducible closeout bundle for
the `STOP_AND_FIX` instrumentation revision.  It contains:

* `INSTRUMENTATION_V1_1_CLOSEOUT.md`
* Core diff from `c71c18a4` to `32f9b8d5`
* Framework diff from `9a498d9` through the closeout revision
* C1/C2 equivalence logs and host profiles
* C4 DataPort and C8 FillPort directed evidence
* the two bounded natural validation outputs (`summary.csv`, `slice.csv`,
  `window.csv`, `manifest.json`, raw logs, and host profiles)
* parser test output, SHA256 sums, source-tree status, and `git diff --check`
  output

It does not contain any pre-fix campaign result as formal characterization
data.  Those results remain available only as `PRE_FIX_DIAGNOSTIC` source
material.
