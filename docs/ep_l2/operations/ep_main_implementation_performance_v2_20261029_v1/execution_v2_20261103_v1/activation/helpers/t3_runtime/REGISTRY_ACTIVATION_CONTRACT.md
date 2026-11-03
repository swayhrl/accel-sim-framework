# T3 registry and activation contract ? Main only

This is engineering guidance derived from the current actual registry/epoch and `E/runtime_t` code. The helper performed no registry/native/model writes. `REGISTRY_ACTIVATION_READONLY_SNAPSHOT.json` records the point-in-time read; Main must read fresh while holding the registry update lock. Other owners are active and the old snapshot is not an installation source.

## Namespaces, exact paths and current state

- `E=/root/data/ep_l2_full_workload_performance_20261027_v1/execution_v2_20261103_v1`.
- Runtime modules: `E/runtime_t`; group ROOT: `E/t3` (not `E/t3/runtime_t`).
- `FRONTEND_GOAL` / frozen `spec.goal`: `EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1`.
- Fresh `GOAL`, `spec.science_request_id`, authorization goal, registry request key: `EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1`.
- Sole registry: `/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json`.
- Epoch: `/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json`.
- Snapshot: epoch2 ACTIVE, holder matches actual hostname; old EP227 consumed/remaining0; fresh T request absent. All existing foreign allowances and rows must stay untouched. Aggregate73 includes foreign budgets, not EP permission.

## Exact fresh request shape

The engine requires the following fields; metadata owner/project/source_keep/refund documents policy. Main creates this row only once after immutable actual specs and real user authorization exist.

```python
T = 'EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1'
# ref(path) returns EXACT two-field {path, sha256}; paths are absolute.
engine_ref = ref(E/'runtime_t/ep_perf_native_wv_modes_draft.py')
common_ref = ref(E/'runtime_t/ep_perf_common_v2.py')
cohorts = json.load(open(E/'helpers/t3_runtime/EXACT_COHORTS.json'))
assert len(cohorts) == len(set(cohorts)) == 6
specs = {c: ref(E/'t3/cases'/c/'control/FROZEN_SPEC.json') for c in cohorts}
q = dict(request=T, owner='EP-MAIN', project='EP_L2',
    budget=6, remaining=6, consumed={},
    admitted_specs={c:v['sha256'] for c,v in specs.items()},
    authorization_ref=ref(E/'t3/control/USER_AUTHORIZATION.json'),
    runtime_versions={engine_ref['sha256']:dict(engine_ref=engine_ref,common_ref=common_ref)},
    state='REGISTERED_NOT_STARTED', automatic_retry=False, refund=False,
    source_keep=True, resource_group_id=T, reserved_write_bytes=0)
assert T not in registry['registered_future_requests']
registry['registered_future_requests'][T] = q
```

Do not prepopulate consumed records, reuse old budget, reset a spent INTENT, silently replace specs, or put all six into running claims. Conditional ON starts are registered allowance, not permission to bypass the Main phase gate.

Real authorization minimum checked by runtime:

```python
auth = dict(goal=T, user_request_ref=ref(E/'t3/control/USER_REQUEST.txt'),
    owner='EP-MAIN', automatic_retry=False, refund=False,
    source_keep=True, approved_exact_cohorts=cohorts,
    authorization_scope='USER_20261103_W2_AND_T6_EXACT_STAGE_II')
```

Main supplies the actual user text/evidence; a TEST_ONLY approval-shaped object is not authority. The runtime compares `authorization.user_request_ref == ref(USER_REQUEST.txt)` exactly: adding a `bytes` field to that nested reference breaks equality.

## Locked registry/epoch update

Acquire `NATIVE/control/science_authority/REGISTRY_UPDATE.lock` with `fcntl.LOCK_EX`. Reread both files under the lock, checking `sha(REG)==epoch.native_registry_sha256`, epoch2 ACTIVE, holder `os.uname().nodename`. Keep all protected top-level fields, old source/qualification histories, all existing requests and prior charge records byte-semantically unchanged. Archive previous REG and EPOCH bytes by their exact SHA under request_history before writing. Add only the authorized fresh request(s), compute aggregate remaining from every request, then atomically fsync-write REG followed by EPOCH. Intermediate readers retry/HOLD on a hash mismatch.

```python
def remaining(v):
    if 'remaining' in v: return v['remaining']
    spent=v.get('consumed',0)
    return max(0,v.get('budget',0)-(spent if type(spent)is int else len(spent)))
registry['new_scientific_budget_remaining'] = sum(remaining(v)
    for v in registry['registered_future_requests'].values())
put(REG, registry) # existing exact fsync+atomic helper
# Preserve ALL other epoch fields; do not alter prepared/retirement identities.
epoch['native_registry_sha256']=sha(REG)
epoch['new_budget_remaining']=registry['new_scientific_budget_remaining']
epoch['request_revision']=dict(request_id=T,
    operation='MAIN_REGISTER_USER_APPROVED_FRESH_T3_EXACT6_NO_START', utc=now(),
    prior_registry_sha256=prior_REG_sha, prior_current_epoch_sha256=prior_EPOCH_sha)
put(EPOCH, epoch)
```

The relocated runtime `common.transaction()` implements subsequent single-request-only changes and protects foreign rows/top fields. It cannot be used to add W and T simultaneously because its protected-peer assertion allows mutations to its own GOAL only; Main either performs its audited two-row registration transaction or two separate scoped transactions. No epoch restart is needed.

## Native route installation, no stale overwrite

Current native starts with the foreign DTC padding amendment, followed by old generic EP_PERF route. The exact-eight Main prelude must come before both. Copy the **currently read complete native bytes**, SHA-pin them as `prior_entry_ref`, prepend the new exact-eight route, and verify resulting bytes end with those prior bytes. Never replace the live entry using an old accepted snapshot. Coordinate the shared mutation lock with current owner to prevent a lost peer update.

Exact generic shape (Main's final frontend has its own exact8 allowlist):

```sh
#!/bin/sh
set -eu
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:EXACT_COHORT_1|experiment:EXACT_COHORT_2) # enumerate actual8, no wildcard
   export EP_FULL_PERF_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /ABS/E/tools/native_stage2_frontend.py "$@"
   ;;
 esac
fi
# append every byte of current prior entry here, unchanged
```

Do not use this abbreviated placeholder shell as an actual route. Frontend must require exactly `experiment {prepare,inspect,run-native} COHORT --project EP_L2`; unknown operations/extra flags fail closed. New entry must not fall through to old EP_PERF frontend for one of the eight authorized cohorts.

Create `E/t3/control/NATIVE_ENTRY_ROUTE.json` with:

```python
route=dict(goal=T,status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',
    prior_entry_ref=ref(immutable_full_prior_native_file),
    own_prelude=exact_prepended_shell_text,
    frontend_ref=ref(E/'tools/native_stage2_frontend.py'),
    all_prior_bytes_preserved=True, scientific_starts=0)
```

Engine prepare checks prior SHA, `current_native.endswith(prior_bytes)` and own prelude containment; it does not require that no later peer prefix was added. `new_entry_ref` is optional historical evidence and can become stale on later peer additions. Do not change the old Main route receipt.

## Binding and claims required before run

`E/t3/control/dispatch_bindings/COHORT.json`:

```python
binding=dict(cohort=case, spec_sha256=sha(frozen_spec), host_cpu=chosen_available_int_cpu,
    selected_utc=now(), resolution='Main shared at-most-two scientific models; exact group binding')
```

Prepare alone does not read dispatch binding/claims; run-native requires both before admission/consume. The required binding fields are cohort, spec_sha256 and an integer host_cpu in current process affinity. It is a host-only binding and does not change immutable science options. Main must avoid the same CPU across W/T because CPU locks live in separate ROOTs.

`E/t3/control/DISPATCH_CLAIMS.json` initial `{'goal':T,'claims':{}}`; for each imminent authorized launch, under `E/t3/control/ADMISSION.lock`:

```python
claims['claims'][case]=dict(state='CLAIMED', spec_sha256=sha(frozen_spec),
    host_cpu=chosen_cpu,
    estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],
    remaining_write_bytes=s['limits']['result_bytes'] + 2*1024**2)
```

Fields required by admission are `state`, `spec_sha256`, `host_cpu`, `estimated_peak_RAM_bytes`, `remaining_write_bytes`. Model PID/start fields are absent until runtime obtains actual process maps. Runtime adds launcher/model PID, model_start_ticks, observed RSS/hot, output/uuid, then terminal state; archive removes own completed claim. No guessed PID or reused generation.

Group future-write carrier is sum of own remaining_write_bytes plus max(active case result_bytes) for **one** sequential restore window, plus2MiB metadata while claims exist. Do not add historical35GiB pool or duplicate Trace copies. Main's current resource adapter accounts foreign commitments and the other new group. It must exclude the current request when counting foreign guarantees, avoid double counting current RSS and budget ceilings, and honor all currently registered peer guarantees. Main controls at-most-two models globally; group engine has only per-CPU/per-case locks.

## Main HostQ relocation/signature

Copy the prior real Main HostQ to a **new immutable path**. Keep schema `EP_MAIN_NEW_SOURCE_T3_HOST_QUALIFICATION_V1`, status `HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED`, approved_by `EP-MAIN`, same Source5/16x8/three modes and observer scopes. Keep `application_permission=false`, `launch_permission=false`, `scientific_starts_authorized=0`, `application_NI=NOT_QUALIFIED`: user budget authorization is separate. Retain prior47native/39parser/283-echo evidence refs; add actual incremental runtime19controls and a Main review of relocation+phase gates+postprocess/archive/NI scope. This is operational qualification, not new model physics or application acceptance.

Replace `modules` with actual new refs covering at least engine/common/parser/mode. These four references must equal the corresponding spec refs as complete dictionaries (prefer exact2fields). Include archive/postprocess/NI/resource/front-end modules in Main's broader module inventory/evidence as appropriate. Update scope/native_route to truthful installed operational state only after install. Do not sign stale old hashes, synthetic approvals, new application NI, or free new hardware behavior.

`rebind_specs_for_main.py` accepts exact real HostQ/resource_module/resource_policy refs and stages6 specs with changed operational refs/pins only. Expected283 options, actual Source5/RO bytes/input/modes and geometry are unchanged; parser/mode/P1TP bytes remain frozen. Main then validates all6 with relocated `mode_contract.validate_static`, full host `spec_for` after registration, and native prepare once route/input/resource controls exist.

## Terminal and ON phase gates

Main invokes group postprocess only after actual natural DONE or technical terminal. Success validates current Source/spec/capsule/environment/maps/strace/gzip, exact283, all kernels/CTA/instructions/drain and64-slice P1 cost plus e986 TP geometry/invalid/overflow/closure. Then immutable archive to true164 and two native restores closes accepted/negative records. No refunds/retries.

Only after **all3 primary OFF are CLOSED_ACCEPTED** may Main sign `T3_DIAGNOSTIC_PHASE_MAIN_REVIEW_REF.json` pointing to the true Main phase review described by `MAIN_ACTIVATION_INTERFACE.json`. Then ON prepares/runs can proceed. Same-arm accepted OFF/ON `t3_application_ni.compare(off,on)` checks Source/input/options and compact semantics; ordered request trace, strict NEW and later UID chain remain NOT_INSTRUMENTED/NOT_MEASURED. A mismatch is a preserved negative with no automatic rerun.

## Pitfalls requiring explicit checks

1. A `module()` import shares the ordinary `ep_perf_common_v2` name. Run native operations in fresh processes or isolate sys.modules per group; otherwise W/T ROOT/GOAL can be cached incorrectly.
2. Old postprocess/archive use old common/Goal; only relocated runtime_t versions are valid for T.
3. Budget registration alone does not authorize ON before the phase gate.
4. HostQ engineering PASS is not application NI or acceptance; oldELF performance cannot fill a new-arm reference.
5. Additional native prefixes are compatible only if all previous bytes remain suffix and the new exact route still wins for its cohorts.
6. Registration and native installation must be fresh, locked, append-only operations preserving foreign DTC changes; a point-in-time hash read is not a lock.
