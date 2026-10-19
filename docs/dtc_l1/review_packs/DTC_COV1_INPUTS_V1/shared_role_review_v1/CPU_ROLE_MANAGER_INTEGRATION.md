# Exact CPU manager: source handoff only

Status: **SOURCE_PREPARED_NOT_EXECUTED / NOT_RELEASED**. Baseline parent source is
`dada67f2a5b7f397423c7df5ace3c9978a6254b4`. No import, AST check, syntax compilation,
test, process launch, resource sample or live callback was performed for this
delivery. The existing three-case view test source remains unexecuted. This
adds no negative suite, rendezvous, simulator entry, registry or retry path.

`external_cpu_role_manager.py` exports one callable, `run_exact_cpu_roles`.
Import only defines code/constants. A frozen parent entry supplies the
registration path and its expected SHA256, four independent trusted hashes,
and the exact manager role object. It must import the parent's frozen modules
from a source-bound path before calling; this module never discovers imports
or inserts a path supplied by a launch row.

## Fixed work and completed phase preservation

The source contains only this sequential list, with at most one direct child:

| Phase | Actual Python controller | Manager phase ceiling |
| --- | --- | --- |
| SEM build | Existing SEM `bounded_cpu_build.py build`, clean three-key environment | 1230 s, including controller cleanup margin |
| ROB configure | Existing ROB `bounded_cpu_build.py configure`, same environment | 90 s |
| ROB build | Existing ROB `bounded_cpu_build.py build`, same environment | 1230 s |
| COV observe once, optional | Existing four-test `test_reference_algorithms.py -v`, existing five-key clean environment | 60 s |

The original controllers retain their own configure60/build1200 bounds and
child-group cleanup. SEM configure is absent from the list. Its existing
successful receipt must be imported by exact SHA256. Any other completed
phase may be imported and is preserved without launch. A receipt/log already
present without an exact completed receipt import stops the manager; it is
never overwritten or treated as permission to retry. ROB build requires the
actual successful ROB configure receipt. The worker source paths/cwd and
interpreter flags are constants, then checked against the independently
pinned role contract. No registration can supply another command.

The standalone entry has a2770s work alarm covering bootstrap, imports,
binding and all admissions, plus at most30s cleanup of one direct handle:
declared total2800s. It rejects an existing real timer and nondefault SIGCHLD
handling. No parallel builds or joint-three-live claim are implemented.

## Registration and fixed trust

`CPU_ROLE_MANAGER_PREREG_TEMPLATE.json` is deliberately invalid for execution:
its status and placeholders must not be construed as a release. Parent should
publish the final registration, independent entry arguments and source closure
together. Runtime registration status must be
`REGISTERED_FOR_EXACT_CPU_ROLE_MANAGER_ONLY`. Its admission object must exactly
equal the separately pinned policy object's `admission`; use the complete
actual parent policy, not the template's one-field illustration.

The independent entry's four expected hashes cannot be taken from a row or
from the just-read registration. Manager-role SHA256 is of UTF-8 JSON with
`sort_keys=True,separators=(",",":")`; release, registration, policy and role
contract hashes are of their actual file bytes. Role contract has `roles`
containing the three exact existing worker roles. Parent release status must
be `RELEASED_EXACT_CPU_ROLE_MANAGER_ONLY` and bind the exact role-contract,
admission-policy and manager-role hashes. Manager role/source closure must
include this module, the source-bound entry, CPUAdmission, launch view,
authority/ownership/frozen-review imports and their fixed contract artifacts.
Keep release/registration bytes outside a self-referential source-hash cycle.

The independently pinned manager role is an exact control role of its own:
fresh actual argv, cwd, interpreter/source hashes and current instance are
checked. It confers no observer cleanup or simulation rights. Actual launch
identity includes boot ID, PID, start ticks and Tgid from the parent's reader;
the provider exports only copied records produced immediately after this
manager's own successful `Popen`, never a discovered process or cached START.

## Fresh admission and one actual observation

Parent must freeze the announced
`CPUAdmission(registration, roles, external_launch_view_provider=None)` API
which forwards the provider into `bind_current_review`. The inspected dada67
CPUAdmission still takes two arguments; this delivery requires that pending
patch before any release. All stages share one CPUAdmission/provider binding,
including the empty launch set before the first start. Never disable the
binding to admit a later role.

Each unfinished actual stage calls the parent's full fresh R2 `admit` first,
retains its two actual samples/ADMISSION receipt, and refuses an admission
older than5s after source hashing. Only actual PASS creates a fixed-policy
admission lease ending at the phase deadline; this is initial admission, not
a claim of continuous resource sampling. The launch view is constructed with
the fixed parent hashes and this actual receipt hash. Launch rows cannot
validate themselves. All resources remain in the original all-project
snapshot; accepted exact CPU controls affect classification only.

After START, exactly one immediate invocation of that same actual
`gate.review(own)` records authority, original snapshot count/hash and whether
this exact worker instance was live accepted. Natural COV exit before that
callback is **INCOMPLETE**, even when its process exits0; no sleep, rendezvous,
second callback or extra run repairs it. A natural terminal view never becomes
live via cached START. A callback mismatch or exception stops subsequent work.

## Private cleanup and receipts

Only the local unexported Popen and pidfd can be used. Before sending one
pidfd TERM, the handle must remain unreaped and current boot/PIDticks/Tgid,
Python argv/cwd/exe and direct PPID must still match. No numeric PID signal,
process-group signal, ptrace, child discovery/adoption or post-reap signal is
available. TERM lets the existing SEM/ROB controller execute its own finally
cleanup; manager waits only its direct controller. Lost identity permits an
own-handle wait, never a fallback signal. Failure to reap within30s is explicit
UNRESOLVED and stops all later phases. No child handle is exported by provider.

Exclusive output files preserve MANAGER_START, actual per-phase admission,
START, OBSERVATION, TERMINAL and MANAGER_RESULT. Parent's bound entry must
preserve its own outer start/terminal for bootstrap failures occurring before
manager output exists. Exit0 is separate from live observation. Final
`PASS_PER_ROLE_CPU_OBSERVATIONS_ONLY` requires successful finite work and an
actual live observation of each of the three roles. Previously completed roles
are preserved, so such an import may leave this claim INCOMPLETE. No joint
three-role, continuous lifecycle, global simulation or scientific PASS follows.

## Remaining before actual release

- Freeze the parent API patch, exact entry/roles/source/import hashes, policy,
  completed-phase receipt digests and independent release arguments. Parent
  must check core/configuration/source identity behind imported successful
  controller receipts; exit0 alone is not native/object/decoder qualification.
- Parent must statically review this unexecuted source and register the exact
  actual run. No prior view synthetic result or old tiny test grants this run.
- stdout/stderr are ordinary files checked at terminal (16MiB each; COV1MiB
  combined), not hard streaming quotas. Existing worker controller limits
  remain; parent admission must budget the output and handle potential excess.
-2800s is an ordinary Python wall-clock alarm/cleanup bound, not a guarantee
  against uninterruptible kernel I/O or blocked receipt writes. Parent's outer
  receipt must report incomplete cleanup rather than infer that no child lives.
- Production live rejection/short-role observation and actual resource gates
  remain unexecuted. No extra negative suite or source-driven rerun is proposed.
