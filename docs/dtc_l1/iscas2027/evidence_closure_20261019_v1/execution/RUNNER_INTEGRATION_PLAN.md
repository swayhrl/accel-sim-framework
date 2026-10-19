# Minimal runner integration after AG4 release

Status: PREPARED_NOT_TESTED. This is a source-reviewed integration plan, not executable admission or a new dispatcher. No code here is invoked against active AG4.

## Reuse the accepted lifecycle engine

Reviewed immutable source: AG4 Framework `9ece18f6fdb6de16ee95f35caa6fad1fec765fc9`, pack `docs/dtc_l1/review_packs/DTC_LANE_AG4_AUTHORITY_AE_AD_V1/`. Preserve guarded_process.py's event-proven ownership, ownership.py's 2.0s confirmation window, 256-event finite drain batch, per-exec mapping epochs, exact mapping-role identity and content checks, and the independent 0.25s OOM watchdog. PENDING remains non-PASS with no resume or signal absent parent-event proof. STOP cleanup requires exact confirmed unreaped instances and reports unresolved ownership. Never adopt a process by path, PPID, or historical PID.

Only the new plan's isolated paths, exact registered CPU fixture target identities, explicit external worker roles, complete family manifest, ledger and dispatcher ownership need adaptation. AG4 files, source, checker, locks, contract and UUIDs are immutable. Its strict failure/zero-retry contract does not become this plan's replacement policy; new ordinary wrapper failures use MASTER_PLAN's bounded two-replacement allowance, with original failure retained and new start counted. Model, identity, value, and unexplained numerical failures cannot use this allowance.

## Two roots require isolated guard processes

The existing engine uses `waitpid(-1)` and a root-local ownership set. Two simultaneous `run_guarded` calls in one OS process would share the wait queue and can consume each other's child events. Do not parallelize that engine with threads. Prepare one guard process per admitted simulation root so each wait queue contains only that root's descendants; the sole coordinator owns all launch permissions and records every start. A guard is a restricted executor of one exact registered attempt, never a second matrix scheduler.

Before using two roots, a small real CPU qualification must demonstrate two concurrent isolated guards with reader helpers, root and child exit accounting, pending/foreign-instance rejection, and cross-root classification. The observer must recognize the exact other registered guard/root/helper identities rather than classify them as foreign DTC authority. Do not weaken ownership checks or add directory/name wildcard exemptions. Register COV1, SEM1 and ROB1 exact external CPU entry files, hashes and roles once; their role permits only the specified local task, never simulator spawning. Their CPU/RSS/I/O counts against global headroom.

These are unexecuted requirements. No CPU qualification or max-worker claim is made. Default future simulation ceiling is two. Four requires prior published resource and authority qualification and a frozen ceiling before the first simulation; it is not enabled during a live cohort.

## Admission and scientific boundaries

Retain R2 minima and persistence rules from the source pack. In brief, two prelaunch samples at least 10s apart require host available and cgroup headroom >=32GiB, disk >=10GiB, memory-full PSI avg10 <=1%, IO-full <=25%, and no new OOM. Runtime new OOM/oom_kill stops immediately; available/headroom <8GiB or disk <2GiB stops; memory-full >10% or IO-full >25% requires three samples >=30s apart; swap growth >=16MiB requires three observations >=10s apart. Full samples normally 10s, WARN 5s; isolated swap pages are contextual warnings. Preserve exact reviewed policy implementation and count other projects.

Publish and read back every family before any member starts: all inputs and denominator, full input identities, scientific configuration/source/Core/binary/runtime closure, effective options, comparable BASE/C+ provenance and scope, timeout, statistics/strict definitions, fresh UUIDs and budget source. Reserve a conservative counted start immediately before the sole permitted fork/exec; failed initialization/timeouts count. Do not manufacture RUN_START for imported results. Input qualification may use an accepted shared hash/body index rather than repeat large scans.

Whole-input natural exit and all kernel/command/CTA/instruction boundaries remain mandatory. Historical full results can be imported only with a qualified reuse dossier. Do not substitute ROI, copied CTAs, concatenated traces or ISA aliases. The complete P/F-C+ family can proceed independently of blocked N inputs only after all its own prerequisites are satisfied. An affected SEM1 semantic family remains restricted without stopping unrelated limited-model research.

## Required next artifacts

1. AG4 immutable terminal intake and exit/lock receipt verification; then final candidate selection or explicitly provisional O.
2. Immutable COV1 input/reuse index, SEM1 per-input scope and ROB1 actual-source control requests.
3. Only necessary runner adaptation and role registry, then targeted CPU qualification after the authority gate opens.
4. The unique executable MASTER_MATRIX.tsv, family publication/readback and fresh resource/authority admission.

All remain prerequisites, not completed tests. No automated waiting dispatcher is created during preparation.
