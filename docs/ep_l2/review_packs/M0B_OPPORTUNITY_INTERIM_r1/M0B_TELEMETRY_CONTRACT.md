# M0b Telemetry Contract

`-gpgpu_ep_l2_m0b_stats` defaults to `0`.  M0b data is only incremented or
printed when that sidecar switch is enabled.  It is not read by L2 admission,
payload allocation/replacement, tag replacement, bank arbitration, Line-MSHR
allocation/merge/retirement, WAD ownership/release, lower routing, scheduler,
or DRAM behavior.  All functional EP-L2 feature bits remain false and M1's
static payload policy remains zero.

M0a semantics carried into M0b documentation: `any_blocked` is an exact
once-per-observed-cycle total; reason fields are production-visible,
stage-primary counts, not an exhaustive simultaneous all-resource bitset.
Absence of a later reason does not prove availability when an earlier preview
stage stopped processing.
