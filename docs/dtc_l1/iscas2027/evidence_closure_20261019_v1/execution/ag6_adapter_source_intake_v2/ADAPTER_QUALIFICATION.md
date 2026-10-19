# AG6 adapter CPU qualification outer entry

**SOURCE_PREPARED_NOT_EXECUTED.** `qualify_adapters_v2.py` is prepared for an
unchanged copy into the parent's `execution/prepared_ag6/`. It deliberately
refuses execution from this COV directory. No import, AST/syntax check, test,
identity call, map scan, raw read, resource sample, target/root launch or
simulation was performed for this handoff. The original parser, four-case
source, ACK wrapper, controllers and39-file CPU engine closure are unchanged.

Inspected parent source is
`7268d0fb46f951ae51b9879988b89dd35c8dc9c4`: current CPUAdmission uses
`admission.disk_floor_exclusive_bytes`, and close_attempt_v2 exports
`close_mapping(engine, mappings, purpose='CPU_FIXTURE')`. The new postclose
function has not been executed by this worker. Existing actual shared PASS
data is a future input to this source, not a qualification obtained here.

## Fixed entry and publication

The executable form after parent freeze is exactly:

```text
/usr/bin/env -i PATH=/usr/bin:/bin LANG=C LC_ALL=C /usr/bin/python3.10 -I -B PARENT_EXECUTION/prepared_ag6/qualify_adapters_v2.py
```

cwd must be the exact parent Framework worktree. Parent must fill and publish
`execution/AG6_CPU_ADAPTER_REGISTRATION_V2.json`; the adjacent schema is a
nonexecutable field illustration with placeholders. The role is exactly
AG6_CPU_ADAPTER_QUALIFICATION_V2 and its source hashes equal the registration's
complete source/import closure. It includes this entry, parser, four-case
entry, identity and close modules plus the necessary unchanged CPUAdmission /
shared authority / ownership / frozen reviewer imports. All those files and
the registration must be in the readback receipt's files map with actual
SHA256 and Git blob. This self role cannot grant model dispatch.

The fixed raw publication path is
`/workspace/dtc-evidence-closure-20261019-v1/coordinator/ag6-v2/cpu-adapter-qualification-v1-prereg/PUBLICATION_READBACK.json`.
The entry checks actual origin branch HEAD, its exact clean local HEAD/tree,
the dedicated `refs/dtc-closure-readback/ag6-cpu-adapters-v2`, fetched commit/tree,
each file's bytes/blob and full source closure. Only fixed read-only Git
commands spawn tooling children; there is no target Popen/fork/ptrace or new
fixture root. Publication checks run before admission, after admission and
before successful terminal. Remote or source advancement fails closed.

## Fresh gate and bounded work

There is no outer timeout supervisor/control process. The entry first rejects
an existing ITIMER_REAL, installs only its own SIGALRM handler raising
TimeoutError and sets a90s total alarm before publication/preflight. Finally
it cancels that timer and restores the prior handler. It never calls os.kill,
pidfd signaling, group signals or a foreign-process cleanup API. The ordinary
Python signal bound does not make a real-time guarantee for uninterruptible
kernel I/O or terminal receipt writes.

Only the necessary frozen CPUAdmission bootstrap imports occur before the
gate. The unchanged full admission checks both fresh host/cgroup samples,
>=10s separation, both>=32GiB memory, memory full<=1, IO full<=25, no new OOM,
original174, current exact execution authority and disk **>5GiB**. No10GiB
threshold or skipped second sample is introduced. Gate failure yields
WAIT_RESOURCE_OR_AUTHORITY_ZERO_ADAPTER_WORK and0 parser cases /0 identity
calls /0 mapping calls. It neither imports payload modules nor retries.

After a successful gate, actual parser/targeted/identity/close module __file__
and source SHA are checked against the published closure. Then exactly:

1. Call the existing four pure targeted cases once, using the four exact-hash
   immutable metadata files; preserve the report and require all4 PASS.
   Fixtures remain declared synthetic, not AG6 performance/guard evidence.
2. Call actual validate_identity(binding, 'AE_GEMM') once. Require prelaunch
   scope,511 trace stat checks,702 source hashes,12 runtime files and0 trace
   body bytes. This is actual filesystem identity preparation, not a model
   launch, fresh body hash or observed runtime mapping.
3. Call the unchanged parent's close_mapping on the two already closed
   registered root0/root1 paths, purpose CPU_FIXTURE, with the exact original
   CPU manifest. No guard or fixture is started again. Require58 retired/exit
   instances and1882 map payloads per root, shared event-digest/root join and
   terminal ownership drain. Hash actual closed map payloads through the
   parent's postclose method; retain only compact counts/bytes/event hash and
   canonical SHA of the returned payload index. Do **not** write the big index.

The committed registration must bind the actual shared PASS copy, original
source-registration SHA and39-source dictionary, original CPU manifest SHA,
and each root's TERMINAL/START/CHILD/FORK_CHILD/MAP_EVENTS SHA. Parent fills
these from actual closed receipts; this worker read no raw root files. The
shared PASS's registration/source/manifest values and original requests must
join exactly; published shared/source-registration copies are required in the
same readback files map. Root receipts are rehashed before/after each close;
shared provenance is rechecked before terminal. Event/retired ancestry checks
are delegated to the actual frozen close function, not invented status rows.

## Receipts and remaining scope

Exclusive output is fixed at `coordinator/ag6-v2/cpu-adapter-qualification-v1`.
ENTRY_START, SOURCE_PUBLICATION_BINDING, admission FIRST/SECOND/ADMISSION,
PARSER_TARGETED, PRELAUNCH_IDENTITY, two compact CPU_MAPPING_ROOT receipts and
ENTRY_TERMINAL preserve source/publication/admission and actual attempted-call
counts. Intermediate work stops on failure and status never promotes to PASS
without every step. Entry refuses an existing output directory, never erases
or resumes a prior attempt. Invalid argv/environment/preexisting-timer refusal
occurs before creating a new output; the parent's command receipt retains it.

The entry's **aggregate compact payload receipts** are bounded to1MiB, with
128KiB retained for terminal; stdout is one compact summary line. The unchanged
CPUAdmission FIRST/SECOND files are separate existing resource evidence and
are not silently truncated. Parent must retain their existing write allowance
in its published disk assessment. The index hash canonicalization is UTF-8
JSON, sort_keys=True, separators=(',', ':'), ensure_ascii=True, without newline.
Terminal records the descriptor receipt hashes and CPU-only map summaries.

A successful status is PASS_AG6_CPU_ADAPTER_INTERFACES_ONLY. It proves only
the admitted synthetic parser interface cases, actual prelaunch identity call
and actual read-only postclose of existing shared CPU fixtures. It is not a
simulation or AG6 scientific/performance result, does not qualify production
postclose on unseen simulator output and grants no new-root or dispatch right.
All runtime qualification remains pending parent source review/freeze,
publication/readback, registration and actual successful fresh R2.
