"""E2 explicit resource-only formal concurrency. No registry/global policy writes.

Only the E campaign's new formal simulation admissions skip fixed run counts.
Original resource arithmetic, policy validation, exclusivity and safety stay.
The old Registry.admission and host/final_intake policies are never modified.
"""
import hashlib
from pathlib import Path

CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1'
FIELD='mechanism_study_20261019_v1'
SCHEMA='E2_FORMAL_SIMULATOR_CONCURRENCY_AMENDMENT_V1'
APPROVAL_SHA256='a0d6eeb7b7f19f26c1d79bc42e9fe63521400f013d527b6d062a63f7986f5ab2'
APPROVAL_PATH=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/concurrency_amendment/USER_APPROVAL.json')
STATUSES={'ADOPTED_PENDING_SAFE_CONTROLLER_SOURCE_SWITCH','APPLIED'}

def require(ok,message):
    if not ok:raise ValueError(message)

def active(item):
    """Exact approval/ledger binding. Reads immutable approval, never writes."""
    if item is None or 'formal_simulator_concurrency' not in item:return False
    require(item.get('campaign_id')==CAMPAIGN,'resource-only concurrency is exact E2 campaign scope')
    row=item['formal_simulator_concurrency']
    require(row.get('schema')==SCHEMA and row.get('mode')=='RESOURCE_ONLY' and row.get('status') in STATUSES,
            'invalid E2 resource-only concurrency record')
    require(row.get('non_count_resource_limits_unchanged') is True and row.get('other_project_policies_unchanged') is True,
            'resource-only concurrency cannot waive physical or other-project rules')
    evidence=row.get('approval',{})
    require(evidence.get('path')==str(APPROVAL_PATH) and evidence.get('sha256')==APPROVAL_SHA256,
            'resource-only concurrency approval binding changed')
    require(hashlib.sha256(APPROVAL_PATH.read_bytes()).hexdigest()==APPROVAL_SHA256,
            'resource-only concurrency approval bytes changed')
    return True

def resource_only(item,kind='simulation'):
    # Screens, builds and native tests keep every original admission rule.
    return kind=='simulation' and active(item)

def admission(data,item,host,cpu,memory,scan,kind,resources):
    """Original Registry.admission non-count guards for this approved E call.

    Exact old source remains pinned by Coordinator.tooling_binding(). These
    copied guards intentionally omit only final-intake and host simulator counts.
    No synthesized host/final-intake quota, hidden run or alternate lock exists.
    """
    require(resource_only(item,kind),'non-count admission requires approved E formal simulation scope')
    # Lazy import: Coordinator inserts the pinned original Registry directory.
    from registry import ACTIVE,final_intake_policy,unwritten_simulation_growth
    policy=data['hosts'][host]
    intake=final_intake_policy(data)  # original strict final-intake validation
    live=[r for r in data['runs'].values() if r['host']==host and r['status'] in ACTIVE]
    leases=[r for r in data.get('resource_leases',{}).values() if r['host']==host and r['status'] in ACTIVE]
    all_live=live+leases
    if any(r.get('kind')=='ENGINEERING_PILOT' for r in leases):
        raise ValueError('exclusive engineering pilot active; ordinary heavy admission blocked')
    if kind=='simulation':
        # Only len(live) >= final-intake3 / host4 count guards are removed.
        if policy['scan_exclusive'] and (scan and live or any(r['scan'] for r in live)):
            raise ValueError('scan needs exclusive EP-L2 simulator slot')
    if sum(r['cpu_units'] for r in all_live)+cpu>policy['max_cpu_units']:
        raise ValueError('shared CPU quota full')
    if sum(r['memory_bytes'] for r in all_live)+memory>policy['max_reserved_memory_bytes']:
        raise ValueError('shared memory reservation quota full')
    if resources['available_memory_bytes']-memory<policy['min_available_memory_bytes']:
        raise ValueError('available memory safety floor')
    if resources['disk_free_bytes']<policy['min_disk_free_bytes']:
        raise ValueError('workspace free-space safety floor')
    if resources.get('share_disk_free_bytes',2**60)<40*2**30:
        raise ValueError('Share free-space safety floor')
    if kind=='build' and cpu>policy['max_build_jobs']:
        raise ValueError('build jobs exceed shared policy')
    if kind=='build' and intake and intake['producer_build_pending']:
        if resources['disk_free_bytes']-unwritten_simulation_growth(data,policy)-intake['producer_workspace_reserve_bytes']<policy['min_disk_free_bytes']:
            raise ValueError('producer50GiB gate plus existing simulation growth cannot fit')
