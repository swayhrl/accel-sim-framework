# R16 combined finite six-point correctness validation

All15 original failures and the two separate old observer-exit engineering
exceptions have been diagnosed. The original failures remain UNACCEPTED and
their old source/UUID/spent rows are preserved without refund. At the reported
old-R1 checkpoint,19 of23 repair validations were archived and four models were
still running; this is not an all-PASS or closure claim. In particular the two
old lavaMD attempts failed with std::bad_alloc under the16GiB hard cap. The
independent V2 metadata consumer continues old-R1 archive/closure without
overwriting canonical R14 ENGINEERING results or registered strict-V1 history.

R16 combines two separately finite new scopes under one sole parent lease:
LAVAMEM2 has two new cohorts,128GiB hard AS/process-tree RSS,96GiB estimated
physical admission RAM, and a1.5GiB future-write ceiling. Its strict per-scope
gate admits at most one live or DONE-but-not-restored point: the second waits
for the first archive/native restore even when physical RAM could hold both.
Late4 has four new cohorts,16GiB hard RSS/AS,4GiB initial RAM, and a3GiB write
ceiling. Both scopes retain the pinned source binaries, V100 geometry and all
270 simulator options from their corresponding repaired comparisons. No GPU
cache/device geometry is enlarged. Old original and ordinary old-R1 memory
policies remain intact. This is correctness validation, not a performance
promotion into the original288-point matrix.

The lava memory estimate is a source/population bound: actual64SM x9CTA gives
576 resident-CTA slots and2304 physical warp slots; actual record types are248
and264bytes. Complete20,776,255,925-byte trace SHA/header audit bounds vector and
heap capacity. Vector capacity is not measured RSS;96GiB is an estimate and128GiB
is a hard host-resource limit. New attempts must still satisfy fresh physical
headroom, cgroup clean-cache-credit, known-write and5GiB disk-floor gates. No
source/trace/raw payload is reread or changed merely to publish this package.

The published587c163 barrier was actually applied before this package: it
temporarily sealed35 admitted but unstarted original points while preserving
the prior historical HOLD/sealed set and every live model/spent identity. Its
published apply receipt, exact APPLIED fresh plan, and small preimage hash/count
summary are included as history. The full private native-registry/epoch
preimages remain at their retained canonical paths and are not copied into Git.
The historical applied plan is not a new plan/apply authorization. R16 releases
exactly barrier.added_cells during its own qualified activation, restoring the
prior HOLD set without unsealing it or refunding any consumed point.

The single R16 parent covers original40 plus new2 and new4. Existing old-R1
models remain alive and archive via their independent V2 consumer; no scientific
model is restarted, signalled or migrated by publication. New frontend routing
is Late4 -> LAVAMEM2 -> old-R1 -> original. R15 is an UNACTIVATED predecessor,
not a previous scientific run; its candidate bytes/supersession preimages are
preserved under the new metadata roots as historical evidence. Draft candidate
or old preimage filenames do not override final plan/request/authorization/SHA
bindings checked by the R16 total qualification. The unapplied once-marker
proposal and its qualifier are deliberately excluded.

The package contains final controller/driver/total-qualification sources, both
new roots' frozen Python and control metadata (including exact-byte compatibility
aliases), CPU/deep-prefork qualification, preserved R15 candidate history, memory
and late-failure evidence, source/build publication and runtime-recovery receipts.
It contains no binary/library/build tree, raw output, captured trace or archive
tar payload. Runtime receipts refer to independently restored assets rather than
installing anything over active canonical paths. Existing publication packs stay
byte-for-byte unchanged. Source manifest joins bind each copied file explicitly.

Publication and CPU qualification start no scientific model and mutate no real
authority, entry or receipt. Activation is a separate root action after exact
GitHub byte readback. Neither intact raw output nor a new validation fabricates
missing historical execution receipts; original full-matrix completeness remains
unclaimed. Fraction/trim inputs excluded from the original sweep remain excluded.
No formal performance result or paper master is promoted: English v0.23 remains
the last confirmed master.
