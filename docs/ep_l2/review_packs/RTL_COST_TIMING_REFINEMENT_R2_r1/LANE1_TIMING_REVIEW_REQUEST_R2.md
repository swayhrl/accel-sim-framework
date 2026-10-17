# Lane1 R2 handoff: exact changed path and remaining timing work

Canonical RTL f54d3c054; finite protocol Core9bd30ed9; all five cost RTL blobs
match every final mapping/function receipt. No official Core patch or app rerun.

|Mode|Primary WNS(ns)|Worst FF data arrival(ns)|FF data slack(ns)|
|---|---:|---:|---:|
|B16|-1.413025|2.162542|-1.356225|
|S64|-1.400875|2.207192|-1.400875|
|UNIFIED|-1.700971|2.505711|-1.699394|

Primary failures retain real reset timing and design rules. Additional register
path filters do not change WNS/TNS, constraints or library. Earlier v2 B16/S64 primary reset
fanout was thousands of actual sinks; large cap/slew was outside normal cell-table
operation and is not a silicon Fmax estimate. The final variant includes real reset buffer distribution and Tag-map data masks. Further buffer distribution
and load-aware hierarchy handling are required, not false/reset exceptions.

The ordinary data path remains unclosed independently of reset. Real path reports
include bank arbitration/grant/native-commit and local32-bit generation update.
Inspect exact mapped start/end and raw path before attributing cycle cost; a
reference-library prototype cannot prove a required fixed number of GPU cycles.
Further carry/select optimization and global library buffering should precede any
pipeline proposal. Static fixed-owner selectors can also benefit from cross-module
constant propagation; this source is not claimed area-minimal.

R2 changed combinational selection/distribution, generation prefix, real reset buffers and proved redundant state.
Frontend readII4/writeII3, serialized static copy, synchronous RAM assumption,
response/WB holding phases, round-robin bank arbitration and held native approval
remain the R1 implementation. A throughput-matched frontend needs actual queued
descriptors/return resources and review of the native Tag/MSHR/NoC boundary. Do
not silently add a blanket hit cycle or use current Lane5 numbers as this RTL speed.

Explicit future proposal for Lane1 only: first close genuine global fanout and
real macro/library binding; then choose an actual bank-local allocator/generation
pipeline and frontend throughput contract if necessary. Any extra allocation or
return stage must retain reservation/rollback, simultaneous grants, ref/WAD release
and same-head progress, have exact SIM/RTL timing disclosure and a new qualified
official release. No such change is authorized or performed by this R2 pack.

Native interface integration risks: static Tag handle/owner/role proofs require
that native Tag cannot relocate/rebind behind this controller. RO/TVD or another
owner must re-establish these invariants before sharing the pool. The metadata
word install_generation input became install_old_live; STATIC_RESIDENT is valid
only for B/S fixed resident slots. New helpers live in the existing metadata file
and are covered by the same filelist. Full-pool capacity/bank/lifecycle semantics
and the same-edge pin race exclusion are retained; three TVD tests remain UNRUN.

SameRTL DC entrance/filelist/SDC/library/unit/PVT paths are ready but DC UNRUN.
Four SRAM boundaries146KiB plus native Tag/LRU/MSHR/dirty-byte/NoC/lower costs remain
UNKNOWN. No whole-slice PPA or net performance/area benefit can be claimed.

The reset network uses real kept noninverting2xINV stages:2 root groups,
at most19 mid groups and292 four-word leaves. Active static bypass groups
are pruned fairly. All buffer gates are counted; same source/Liberty/PVT/SDC
for all modes. No reset constraint was removed and no clock stage was added.
The generation prefix is exact modular add1/2, with all GEN32 FF retained.
Tag-map masked data is unobservable unless targetTag matches write enable;
its all-target/all-landing inductive proof is delivered.
