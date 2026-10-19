# Source findings and minimum changes

Current source7e7bd82423f0f5807e2d89bb7fe779d21be13148 consumed. Baseline findings at69f22e88 are retained for traceability; R1 and R5 are source-fixed in7e7, not open requests. Source line numbers below
refer to that commit. No runtime counterexample is claimed from static review.

|ID|Source anchor|Concrete gap|Minimum change / evidence|
|---|---|---|---|
|R1|shared_authority.py:25–46|argv/cwd/exe match the older process row; the fresh read checks only ticks/state. An exec/chdir/argv change can retain PID/start_ticks.|Parent's planned fresh stat/status bracket around current cmdline/cwd/exe must re-match all fields, including Tgid/tracer and coherent current image. No stale row is accepted after a fresh read. Vanishing short roles become MISSED/TERMINAL, not an invented live row.|
|R2|shared_authority.py:122–165 and contracts|Exact source/argv currently removes the CPU control from legacy classification without checking the role contract's resource_admission_required or binding this run's release/admission/launch instance.|One read-only active-instance provider keyed by role,phase,boot_id,PID,start_ticks and launch ID, with exact release/role/admission hashes. Only a currently admitted ACTIVE row can be accepted. No second launcher or directory-wide exemption.|
|R3|qualify_shared_cpu_authority.py:37–87; registration requests|Both requests run closure-cpu-authority long. Three samples and a shared PASS containing two roots say nothing about an actual COV/SEM/ROB controller.|Keep existing result narrow. The same callback must emit accepted external role observations for the actual Python entry processes, with each exact role/phase/instance visible live. Actual work receipts and live classification are separate evidence.|
|R4|cpu_guard_entry.py observe,0.1s active update; external COV entry|The tiny process can finish before periodic snapshots. Its previous four-test PASS is a terminal mathematical result, not a live observer sample.|One immediate post-launch observation attempt may succeed. A missed instance is INCOMPLETE; do not inject a saved row, sleep the workload, rename it, or loop until success. If deterministic observation is necessary, preregister a bounded in-entry observation rendezvous and its new source hash before executing it.|
|R5|SharedOwnership.classify:81–107; verified_peer_view:168–203|The exported peer recognition consumes confirmed PID/ticks plus tracer and age, without explicit AG5 generation/retired precedence.|Consume canonical AG5 read-only generation snapshots. Retired wins over old confirmed records; current Tgid/tracer/instance/generation must match the live tuple. Preserve finite PENDING without promoting it. Do not maintain a second signal-capable ownership table.|
|R6|CPUContext.read_registry:32–55; peers:58–74|Peer argv and expected request hash are passed back from the same mutable registry row; trust depends on the exact manager source writing only its Popen returns. Terminal peers are silently omitted.|Derive expected guard argv/request hash from the immutable request contract, and bind each row to the actual current manager's direct-Popen launch receipt. Preserve terminal/reaped disposition and unresolved descendant status; omission alone is not authority-release proof. No new peer discovery by PPID/name/path.|
|R7|verified_peer_view:178–200; controller_roles:77–85|Guard image hash is checked, but the peer helper itself has no explicit expected cwd/exe-path check; manager/guard roles are metadata, not a live observation of an independent observer.|Use the same fresh exact process reader for manager, guards and observer. Register the observer's source/import closure, executable, argv, cwd, environment, release, resource admission and launch instance. Its own classifier exception is precise CPU control only.|
|R8|bind_current_review:224–247|CPU projection marks traced candidates is_simulator before exact role filtering; accepted CPU roles explicitly reject that flag.|Observe the three external controllers as their real external CPU controls. Do not put them under the fixture projection to manufacture visibility. If parent chooses an owning guard for a controller, explicitly resolve the projection/role ordering in a newly registered contract; an artificial is_simulator flag cannot authorize the controller.|
|R9|review_with_exact_roles return; qualifier observations|all_project_resource_population_unchanged=True is descriptive. Filtering three controllers from classification must not remove them, their compiler children, observer, guards or unrelated projects from admission/accounting.|Keep and return the original global resource snapshot independently. Record the current original population/sample identity, removed-for-classification role rows and unfiltered resource identity. Do not use classification_process_count for resource qualification.|
|R10|CPU_SHARED registration; cpu_guard_entry runtime observe; build controllers|The current shared contract budgets two60s roots/90s qualifier and128MiB output; SEM/ROB build controls can each run1200s with512MiB output. Runtime observe checks memory/disk but does not itself demonstrate paired host+cgroup PSI or OOM admission for later role starts.|Actual controller launches require their own fresh paired admission and aggregate overlap/output reserves. A90s observation-window PASS cannot claim whole-build lifecycle/continuous monitoring. The launch owners retain and wait all actual handles; any longer manager lifetime needs its own finite published bound.|

The parent specifically acknowledged R1 and canonical AG5 integration while
this review was in progress. They are requirements for the new source closure,
not requests to edit frozen AG4 or rerun the AG5 test program.

## The minimal read-only launch binding

Add one injected provider alongside the existing role contracts. It returns
only records from the current released launch owner's actual Popen result.
If the coordinator's existing manager launches the real controller, append
that direct-Popen record to its registry. If a worker remains the launch
owner, its exact released source-bound launcher must publish the same record;
`ps` discovery, a controller self-assertion alone, a PPID guess or a caller's
bare registered_source_and_launch_verified=true is insufficient. Pick one
owner for each phase before execution; never launch the same work twice.

One active record needs:

- Immutable role contract/release hash and phase, plus admission receipt hash
  and its fresh sample interval/applicable CPU scope.
- Actual launch ID, owner identity and boot_id/PID/start_ticks/Tgid from the
  direct launch, exact intended argv/cwd/executable/source closure and maximum
  lifetime/output. The current process is still re-read independently.
- State ACTIVE or TERMINAL_REAPED/RETIRED; only ACTIVE and the same live instance
  can be recognized. Preserve the completed record; do not recycle it for a
  new process. No adoption, signal, resume or wait rights are exported.

The exact-role matcher then uses the intersection of the immutable role,
current fresh process and current admitted launch record. Existence of the
source file is not a launch permit. For an expected launch-publication race,
allow only a specifically registered launch-in-progress to be finite PENDING;
it supplies no authority PASS. Do not add an unbounded source-path fallback.

Return an observation row containing role/phase, launch/release/admission hashes,
process tuple, actual argv/cwd/exe, observed hashes, timestamp and callback
sample identity. Use `EXACT_EXTERNAL_CPU_CONTROL_OBSERVED`, not ownership
`CONFIRMED`. It must remain outside local.confirmed and all signal selectors.

## Current source update:7e7bd82423f0f5807e2d89bb7fe779d21be13148

The current parent source was independently read after the baseline review.
R1's old-snapshot acceptance path is source-fixed: exact_cpu_role now uses
fresh_process for real observations, bracketing current cmdline/cwd/exe with
instance reads and matching those current attributes. The process_reader
injection is declared only for offline synthetic tests. R5's immediate
tracer/Tgid/retired checks are also source-fixed. cpu_guard_entry now publishes
ownership even when the original root has been reaped, retaining descendants'
current proof rather than suppressing the observer. Do not ask the parent to
implement those fixes again. No runtime PASS for them is asserted here.

Current `qualify_shared_cpu_authority_v2.py` still checks two actual long roots,
not the three external roles; it explicitly leaves their observation unfinished.
Its registration is `SOURCE_PREPARED_REQUIRES_POST_BUILD_MANIFEST_AND_RELEASE`,
with a missing new ELF publication marker. That is a valid non-executable gate,
not a release or an input for this reviewer to run. It also includes the parent's
new changed-interface checks; this plan does not add another whole negative
suite or repeat unchanged AG5/BASE qualification.

The remaining minimal work from this review is therefore R2/R3/R4/R7/R9/R10:
current release/admission/direct-launch binding, actual role evidence including
the short COV entry, observer-self registration and resource/lifetime scope.
R6 describes a caller-side binding hardening requirement when producing the
final instance provider; it is not a claim that a foreign registry mutation
was observed. The current CPUContext and multi_root_cpu sources remain unchanged
from the reviewed baseline. SOURCE_BINDINGS distinguishes both anchors.
