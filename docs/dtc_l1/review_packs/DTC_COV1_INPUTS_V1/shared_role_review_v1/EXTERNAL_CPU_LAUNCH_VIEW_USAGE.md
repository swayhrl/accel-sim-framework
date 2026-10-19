# Minimal implemented read-only launch view

Status: SOURCE_PREPARED_NOT_IMPORTED_NOT_TESTED. Parent source context is
25cf0ab03d6cc68f964eeb03f42347452ac23abb. No tests, import/compile, process
inspection, ptrace, resource polling, subprocess or simulator was run for this
implementation. Existing CPU admission failure remains a WAIT, not permission.

`external_cpu_launch_view.py` adds only ExternalCPULaunchView.observe(). It has
no CLI, launch, wait, signal, ptrace, registration writer, /proc scan, ownership
object or local.confirmed access. Import defines functions/classes and stdlib
imports only; construction copies fixed JSON-like trust/admission data without
calling providers/readers/clock. File/process reads happen only in observe().
Three declared-data examples in `test_external_cpu_launch_view.py` are source
only, not executed. Actual rejection against the same live role remains for
the parent's later single directed query.

## Small schema

Pass independently pinned coordinator values to the constructor, never values
learned from a launch row:

- `trusted.release_sha256`, `role_contract_sha256`, `admission_policy_sha256`,
  `manager_role_sha256`: lowercase64-character SHA256 digests of the fixed
  published release, role contract, CPU admission policy and sole-manager role.
- `trusted.manager`: exact `instance`, `argv`, `cwd`, `executable`,
  `executable_sha256`, `source_sha256`. Include the source that implements the
  registered provider in this pinned manager closure. `instance` supplies
  boot_id,pid,start_ticks,tgid from the parent's actual direct launch.
- `trusted.roles`: only the three existing COV/SEM/ROB role names, or a subset.
  Each has exact cwd/executable/executable_sha256/source_sha256 and `phases`.
  Each phase fixes argv,max_runtime_ns,output_bound_bytes. Source paths and
  executable/cwd should be the absolute registered paths. `tracer_pid` defaults
  to0 for these external controls; any other tracer requires a fixed explicit
  contract rather than discovery or adoption.
- `admissions[role][phase]`: independently validated actual receipt_sha256,
  policy_sha256,status=PASS,scope=CPU_ONLY,valid_from_monotonic_ns and
  valid_until_monotonic_ns. The policy/receipt must cover the declared active
  phase deadline. These are fixed trusted inputs; a provider's own claimed
  status or policy cannot validate itself. This module evaluates no PSI/OOM/
  disk samples and does not create or renew a resource lease.

The source-bound sole-manager `provider()` returns one current snapshot:
`{manager_instance,manager_role_sha256,launches}`. Each launch has:
`role_name,phase,actual_launch_id,instance,manager_instance,state,release_sha256,
role_contract_sha256,admission_policy_sha256,admission_sha256,argv,cwd,executable,
launched_monotonic_ns,deadline_monotonic_ns,output_bound_bytes`.

`instance` has boot_id,pid,start_ticks,tgid. A row must originate from that sole
manager's actual Popen result; the manager may retain its own wait handle, but
must export only data. Do not synthesize rows from /proc discovery, parent PID,
path/name matching or controller self-assertions. A data-only module cannot
prove how a producer obtained a tuple: the parent's published provider/manager
source and direct-launch registration are the trust boundary. No alternate
provider factory or arbitrary registry path loader is supplied here.

## Injection and parent integration

Construct the view only after the parent verifies the exact module/provider/
manager source closure, fixed release and resource receipts:

    view = ExternalCPULaunchView(
        trusted=fixed_parent_contract,
        admissions=validated_fixed_admissions,
        provider=registered_sole_manager_popen_view,
        identity_reader=current_full_instance,
        process_reader=current_full_process,
        monotonic_ns=parent_monotonic_ns)

`identity_reader(pid)` must return current boot_id,pid,start_ticks,tgid,state,
ppid,tracer_pid. `process_reader(pid)` returns those fields plus current argv,
cwd,exe. Both are fresh readers, not lookup of the saved launch row. Missing
process may return None or raise FileNotFoundError/ProcessLookupError. Existing
parent AG5 identity may need a small adapter adding the independently verified
current boot_id; the process reader remains the parent's current full reader.
Default file_sha256_reader hashes only the fixed registered files. Its injection
exists for declared-data examples; production must not use a fake hash reader.

In bind_current_review/review_with_exact_roles, after finding the exact CPU
role candidate and before filtering it out of legacy classification, call:

    row = view.observe(role_name, process, callback_sample_id=current_sample_id)

Filter only `classification=EXACT_EXTERNAL_CPU_CONTROL_OBSERVED` with
`live_observation=True`. `dict(row)` is JSON serializable; all values are scalar
or immutable tuples. The mapping itself cannot be written. Log it in the
existing callback result without adding it to local or peer confirmed owners.
Keep the original all-project resource snapshot unchanged. Observer/manager
self registration is still required in the parent caller.

The view independently matches the sole manager's current attributes/source,
exact row-to-fixed release/role/admission bindings, phase/ACTIVE deadline,
actual direct-child ppid, full boot/PIDticks/Tgid instance and current attributes,
and source/executable hashes. Full current process reads are bracketed by
identity reads and repeated after hashing. The candidate's saved argv/cwd/exe
is never sufficient. An is_simulator candidate cannot be accepted as CPU role.

## Outcomes and remaining scope

- `EXACT_EXTERNAL_CPU_CONTROL_OBSERVED`: one live admitted current-instance
  observation; ownership_granted and simulation_permission are always false.
- `NOT_CURRENT` / `TERMINAL`: natural absence, process exit during fresh reads,
  or the sole-manager's retired/reaped record. live_observation is false.
  These are not authority-release proof or a replacement for the actual Popen
  owner's terminal/reap receipt. Never recover a cached START into a live row.
- `ExternalCPUReject`: changed PIDticks/full identity, source/image, phase,
  release/admission binding, unregistered manager/parent/tracer, expired ACTIVE
  deadline, duplicate/missing launch, malformed evidence or read permissions.
  The caller preserves its existing fail-closed policy; this module cleans up
  nothing. Metadata mismatches are checked before any terminal disposition.

The parent alone registers the executable cohort and the provider's real
launching source. This module does not supply the Popen producer, rendezvous,
resource evaluator, observer scheduler, synthetic pending permission, AG5
state machine, production qualification or simulation dispatcher. Completed
SEM configure is not repeated. The current phase list is frozen from actual
pending work at release time, not from this source-only usage example.

Direct-launch restriction is deliberate: the manager's Popen must identify the
actual Python controller (an exec-only env step may retain that instance).
Do not publish a forking timeout wrapper PID as the role or discover its child
from /proc. Use the registered manager's own finite deadline for that direct
child, or publish a different source-bound ownership contract first; this
module does not relax its direct-manager-child check to accommodate wrappers.
