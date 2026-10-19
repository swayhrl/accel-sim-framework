# A common build/native entry — source prepared, no compute admission

The formal common entry is util/ep_l2/mechanism_study/build_common_a.py,
with exact source/hash/budget in COMMON_BUILD_ENTRY_r12.json and
COMMON_NATIVE_BUILD_SPEC_r1.json. R1 build_a.py stays R1-only and is preserved.
Default invocation only prepares a fresh finite plan. No application command
or automatic retry/watcher is implemented. Do not invoke raw CMake to bypass it.

The common test set is55 required main invocations and9 separately qualified
diagnostics, selected by affected shared invariants rather than concatenating
old55+21+25. The default main set covers shared atomic/host/clock/stale paths,
S/U observer equivalence, C13 actual combined cases + new shared RESPONSE mux,
RO modules, full-F observer equivalence, warm native DRAM/physical P1 with and
withoutV,64slice GPU epoch APIs, actual victim versions/UID/sector/dirty/pin/
bypass, real dirty boundaries and bounded arbiter identity. It is NOT the old
R1 suite despite the same count. Facade/reference/tiny geometry/full1024Tag/
nativeDRAM scopes are labelled. SASS numerical/application correctness is not
inferred from these directeds. All native invocations remain UNRUN.

Plan inputs are copied from exact frozen C artifacts, local paths rebound and
hashes/whole-commandlist/range bindings checked. A source-owned semantic signature
allows observer0/1 comparison for actual S/U/F cycles/values/counts. The readonly
partition's after-epoch prefill assertion now matches the already-implemented V2
closed/quiescent initialization rule and the GPU API test. Active certified
updates still reject. Those are new uncompiled regression-source changes.

Execution always uses E's current published/hash-pinned API and one central
mechanism_A lease plus A_BUILD.lock. Ordinary combined work requires48GiB plus
3GiB build+256MiB output growth, Share40GiB, availableRAM64GiB after reservation,
2CPU/8GiB RAM. All temporaries/user-cache redirection remain in the admitted
build root and count toward3GiB; no HOME change or old-data cleanup. Native-only
resume uses a new ordinary test lease (1CPU/8GiB,256MiB output), never a build.

User's later single named-build disk draw is implemented ONLY through E's
canonical READY record, exact source_identity/build_identity, host/boot/API,
CPU/RAM/growth/output/expiry and atomic single-use consume. No record is created
by this entry. The CLI --disk-authorization-id is legal ONLY with --phase build.
Only that reviewed compile task may use its bounded floor (no lower than44.5GiB,
max3.5GiB draw); an extra128MiB monitor/termination reserve is held above the
record floor. Global ordinary48GiB and app policies remain. E's backend still
rechecks current physical resources/exclusivity/budgets when consuming the ID.

Successful build-only seals BUILD_ONLY_RECEIPT.json with source/driver/spec,
assertion flags, binary/test executable/dynamic-library SHA256 and build logs,
then releases the lease WITHOUT RUNNING A NATIVE TEST. After ordinary48GiB is
restored E can approve --phase native --build-receipt PATH against the same
retained build; no recompilation or object reuse from another source occurs.
That resume's positive native path has NOT been exercised. Build plus tests
may instead run together under a normal exact E admission and ordinary floors.

main and all are valid build/combined suites; diagnostics is native-resume only.
Compile all64 fixture targets in the one named build when E approves so later
nine diagnostic checks need no second build. Native main seals its own producer
checkpoint before optional diagnostics. Tests assert actual exit plus exact
terminal and record actual native PID/raw log/executable identities. A wrapper
limits each raw native output to16MiB; the original supervisor enforces total
output, memory, expiry, source/config/tool hashes, owned process groups and
resource floors. It stops only its own work. A producer checkpoint is pending
independent E qualification, never an automatic app release.

Actually executed controls: plan(main55), plan(build-all64), missing ordinary
E admission refusal, absent named-record refusal and named-native scope refusal.
All created0 compilers/native/leases/builddirectories; registry bytes were
unchanged. One initial filename-hyphen preparation error is retained/fixed.
No successful build, native resume, linked library report or binary exists yet.
See COMMON_ENTRY_CONTROL_VERIFICATION_r2.json. E's127 controls are reused as
policy evidence, not rerun or described as native proof.
