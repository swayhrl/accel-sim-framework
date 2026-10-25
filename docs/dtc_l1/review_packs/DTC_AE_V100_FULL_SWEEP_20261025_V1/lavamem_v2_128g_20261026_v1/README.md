# lavaMD memory-cap validation V2 — separate two-point request

This exact-byte publication prepares a new finite two-point correctness
validation request after the two old repair attempts terminated with
std::bad_alloc under their 16GiB hard address-space/RSS cap. Their original DONE,
bad_alloc marker/hash summaries, archive receipts and spent identities are
preserved. This is a new pair of cohorts/attempts, with no refund or mutation of
old spent rows. Publication itself starts no scientific model and grants no
formal performance acceptance.

The new attempts use the same Core9eed / Framework027 binaries and V100 geometry
as the prior repaired runs. The same 270 simulator options and full input are
retained. The changes are host-side resource limits: 128GiB hard address-space
and process-tree RSS caps, with 96GiB estimated peak physical memory for admission.
They do not increase a simulated GPU cache, device RAM, or any simulated V100
geometry. Original and ordinary old-R1 requests retain their usual 4GiB initial
RAM floor and existing hard limits; the 96GiB estimate applies only to new2.

The memory evidence is source- and input-bound. The CPU audit read the complete
20,776,255,925-byte (about20.8GB) trace, verified its full SHA, and indexed all
1000 complete CTAs / 4000 warps / 420,346,376 warp records. Actual geometry bounds
resident CTA capacity at576 (64SM x9CTA). The compiled actual trace-record types
measure248bytes per inst_trace_t and264bytes per memory-info object. The
conservative vector-capacity upper bound is about68.77GiB, and the whole-grid
memory-object heap bound adds about6.04GiB. The 96GiB admission estimate includes
transient reallocation/runtime/allocator allowance; 128GiB hard AS adds virtual
mapping margin. These are conservative source/population bounds, not measured
new-run RSS. In particular, header173 at the old crash does not prove173CTAs
simultaneously resident, and vector capacity is not physical RSS.

Maximum new-model slots is2, but the fresh resource gate will normally admit
only one at a time under current memory capacity. It retains64GiB host available
and48GiB effective-cgroup headroom and all existing known-write/5GiB disk-floor
checks. A ready large model has resource-aware priority; no attempt is consumed
when admission lacks headroom. Two slots never imply authorization to bypass
the actual gate.

R15 is the sole parent for original40 plus independent new2. It preserves the
old-R1 live models, identities, claims, spent rows and authority fields. The old
23-point postprocess-V2 metadata consumer remains a separate closure path; it
is not replaced or misrepresented as registered V1 success. No existing model
is restarted, signalled or migrated by this publication. Zero-model controller
and deep pre-Popen CPU qualifications bind the final source/profile/plan/spec
and compatibility aliases; no qualification reconstructs missing historical
execution receipts or treats intact raw output as a recorded wait status.

This package includes only Python/C++ source, JSON/Markdown metadata, and the
small distribution index. It excludes simulator binaries, shared libraries,
build trees, audit executables, raw logs, archive tar files and trace payloads.
Old214/178/17-file packs remain unchanged. Prior source/build/publication/recovery
receipts are references to separately preserved exact assets, not a new runtime
installation. Aliases are copied as exact referent bytes with their original
link targets recorded in the manifest.

The original full performance matrix remains incomplete where historical
execution-receipt gaps persist. New correctness evidence is kept separate from
the original288 statistics, carries no accepted performance cycles, and does
not promote a formal performance result. The last confirmed paper master
remains English v0.23.
