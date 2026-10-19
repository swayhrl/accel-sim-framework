# Reused lifecycle engine and isolated CPU roots

**PREPARED_NOT_TESTED. DO NOT EXECUTE WHILE AG4 AUTHORITY GATE IS CLOSED.**

This is concrete post-gate runtime preparation, not a passing qualification,
performance runner, scheduler or deferred dispatcher. No file in this directory
has been imported, compiled or invoked during preparation. The coordinator's
published source/authority contract governs execution; a JSON status string is
not evidence that the real gate has opened.

`ENGINE_SOURCE_BINDING.json` binds the upstream AG4 source commit and exact
Git blobs. `mapping_roles.py`, `ownership.py` and `oom_watchdog.py` are copied
byte-for-byte. `guarded_process.py` changes the CPU fixture path/prefix and now repairs the
retired-PID wait-dispatch gap reported by AG4 terminal d8d0401. Retired owned,
image and parent memberships are removed in normal and cleanup exit branches;
every resume requires a currently confirmed instance and fresh start_ticks.
These local changes are PREPARED_NOT_TESTED; AG4 files remain unchanged.
`authority_cpu.cc` changes only its two project data paths and retains the
original CPU-only stdout markers. No AG4 path is written or executed. The
minimal local `common.py` exports only output and timestamp helpers used by
the engine; it does not carry historic write paths or old-run dispatch APIs.

`cpu_guard_entry.py` invokes one inherited engine in a separate OS process.
It admits only purpose CPU_FIXTURE, exact request/source/manifest hashes, and an
isolated output destination. It has no simulation capability. Interrupt signals
become observer stop requests so the reused engine can perform event-proven
cleanup; they do not trigger adoption or broad signalling of foreign jobs.

`multi_root_cpu.py` has no CLI. Its single entry accepts exactly two already
registered CPU requests, launches separate guards and records an observation
where both real event-confirmed roots are live simultaneously. Root identity
uses PID/start_ticks, the real guard parent and fresh `/proc/stat`; an old active
file alone cannot prove overlap. Final results require both engines' natural
exit/identity closure, no owned live children and no unresolved pending proof.
Direct guard children are signalled only through instance-bound pidfds (or the
unreaped direct Popen handle if pidfd setup failed), never by a historical PID.
Unresolved cleanup is reported as incomplete, not zero live children.

## Post-release use and remaining integration

After consuming AG4's immutable terminal publication and exit/lock receipts,
register exact qualifier/compiler/helper/worker roles and resources. Build the
reused CPU fixture in the isolated coordinator build directory, with its exact
source/compiler/flags/binary SHA. Create helper-data containing the original
`AG4_HELPER_OK` marker and an unregistered-data negative fixture. Use the accepted
static dependency/mapping manifest procedure to freeze the actual CPU target,
dash and cat before either root starts. Do not treat the C++ source alone as a
runtime ELF manifest or assume a node's libc/loader identities.

Fix the two CPU request JSONs and all engine/source hashes before invoking the
library. A request carries purpose, post-release role-registration state, exact
argv and environment, timeout<=60s, distinct isolated destination, manifest
path/SHA and prepared_source_sha256. Use the fixture's `long` mode for overlapping
thread/fork/dash/cat lifecycles. There is no executable request or generated
CPU result in this preparation publication.

This deliberately does **not** claim production multi-root authority PASS.
The later qualification must connect the exact shared-role observer, reject
an unregistered root/helper and wrong PID instance, confirm PENDING never
becomes PASS, preserve ownership/cleanup negatives from AG4, and admit the
three external worker CPU roles. It must check real helpers in MAP_EVENTS and
ownership proof, not infer helper coverage merely from exit0. CPU fixture
markers, map closure and overlap are necessary but insufficient evidence.
The global resource/authority observer and matrix/ledger publication gates are
still prerequisites for the sole full-simulation coordinator. No existing
AG4 checker is changed, and no directory wildcard or filename exemption is
introduced.

AG4 terminal intake is now available and its own authority is released. The
prior local inherited copy was never executed. Its newly identified production
dispatch gap must be reproduced on the frozen source and rejected on the
repaired actual dispatch AST, then qualified through real helper/multi-root
lifecycles. Source review alone does not open new simulation authority.
