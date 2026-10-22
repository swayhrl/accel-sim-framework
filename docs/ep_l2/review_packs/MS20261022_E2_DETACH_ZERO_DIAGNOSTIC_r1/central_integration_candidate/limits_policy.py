"""Exact E2 numerical-start/time removal; no new scientific condition/retry grant.

Pure guards and an in-memory amendment; Coordinator owns original REGISTRY.lock.
JSON null means unlimited here. The ten approved condition identities stay finite.
"""
import copy
import detach_diagnostic_policy as detach_policy
import workload_policy
import hashlib
import json
import time
from pathlib import Path

CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1'
SCHEMA='E2_START_AND_TIME_LIMIT_REMOVAL_AMENDMENT_V1'
BUCKET='five_input_capacity_diagnostic_user_approved_20261021'
FIELD='start_and_time_limit_removal'
APPROVAL_PATH=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/limits_removal_r1/USER_APPROVAL.json')
APPROVAL_SHA256='ed94182c43f45591c1fa3b824f7eaac39e07e9838617174763dbdbdca6c5c943'
CONDITIONS=frozenset('V3_CAPACITY_'+w+'_'+p for w in
 ('convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M') for p in ('S_OFF','S_ON'))
REMOVED=('maximum_actual_starts','start_deadline_unix','intake_deadline_unix')
DISPLAYS=('no_new_full_application_after','result_intake_freeze')

def require(ok,message):
    if not ok:raise ValueError(message)

def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def approval():
    raw=APPROVAL_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==APPROVAL_SHA256,'start/time removal approval bytes changed')
    value=json.loads(raw)
    require(value.get('status')=='USER_APPROVED' and value.get('schema')=='E2_CAPACITY_START_AND_TIME_LIMITS_REMOVAL_USER_APPROVAL_V1',
            'start/time removal not exact user approval')
    require(all(k in value and value[k] is None for k in ('maximum_actual_starts','maximum_capacity_diagnostic_starts',
            'start_deadline_unix','intake_deadline_unix','formal_application_timeout_seconds')),
            'approval must explicitly remove count/time limits')
    return value

def active(item):
    if item is None or FIELD not in item:return False
    require(item.get('campaign_id')==CAMPAIGN,'start/time removal is exact E2 campaign scope')
    row=item[FIELD]
    require(row.get('schema')==SCHEMA and row.get('status')=='APPLIED','invalid start/time removal record')
    require(row.get('approval')==dict(path=str(APPROVAL_PATH),sha256=APPROVAL_SHA256),'start/time approval binding changed')
    approval()
    require(row.get('approved_condition_ids')==sorted(CONDITIONS),'start/time removal cannot grant more science')
    require(item.get('t0_unix')==row.get('t0_unix'),'original T0 cannot be reset')
    require(row.get('automatic_retry_authorized') is False and row.get('refunds_authorized') is False,
            'start/time removal cannot authorize retry or refund')
    require(row.get('non_time_resource_limits_unchanged') is True and row.get('other_projects_unchanged') is True,
            'start/time removal cannot waive resource/data/other-project rules')
    require(all(item.get(k) is None for k in REMOVED+DISPLAYS),'removed limits must be JSON null')
    require(item.get('maximum_capacity_diagnostic_starts') is None and 'maximum_capacity_diagnostic_starts' in item,
            'removed capacity start allowance must be explicit JSON null')
    require(item.get('per_end_timeout_seconds') is None and 'per_end_timeout_seconds' in item,
            'removed per-end timeout must be explicit JSON null')
    require(item.get('remaining_start_capacity') is None,'unlimited remaining capacity must be JSON null')
    require(item['additional_results_max_bytes']==10*2**30 and item['old_plus_new_results_max_bytes']==24*2**30,
            '10/24GiB result generation budgets unchanged')
    require(item['reservations']==row['original_reservations'],'historical budget buckets changed')
    require(item['capacity_diagnostic_matrix']==row['original_capacity_matrix'],'approved ten-condition matrix changed')
    require(item['full_system_matrix']['sha256']==row['original_legacy_matrix_sha256'],'legacy matrix changed')
    require(item.get('final_source_identity')==row['original_legacy_source_identity'],'legacy source changed')
    prefix=row['attempt_history_prefix_count']
    require(len(item['attempts'])>=prefix and canonical_sha(item['attempts'][:prefix])==row['attempt_history_prefix_sha256'],
            'pre-amendment attempts cannot be refunded or rewritten')
    return True

def scope_allowed(item,spec):
    if detach_policy.is_spec(spec):return detach_policy.scope_allowed(item,spec)
    if workload_policy.is_workload_spec(spec):return workload_policy.scope_allowed(item,spec)
    if not active(item):return False
    if spec.get('condition_id') not in CONDITIONS or spec.get('budget_bucket')!=BUCKET:return False
    row=next((r for r in item['capacity_diagnostic_matrix']['conditions'] if r['condition_id']==spec['condition_id']),None)
    if row is None:return False
    identity=spec.get('identity',{})
    return (all(spec.get(k)==row[k] for k in ('selection_id','profile','comparison_group','budget_bucket'))
      and identity.get('workload')==row['workload'] and identity.get('trace_content_sha256')==row['trace_content_sha256']
      and identity.get('epoch_range')=={'epochs':'all','scope':'full_application'}
      and all(identity.get(k)==item['capacity_diagnostic_runtime'][k] for k in
          ('core_source_commit','framework_source_commit','binary_sha256'))
      and not spec.get('retry_previous_attempt') and not spec.get('retry_reason'))

def has_start_capacity(item,spec=None):
    if active(item):return spec is None or scope_allowed(item,spec)
    return item.get('remaining_start_capacity',0)>0

def deadline_open(value,now=None):
    return value is None or (time.time() if now is None else now)<value

def operational_override(spec):
    return dict(schema='E2_CAPACITY_OPERATIONAL_LIMITS_OVERRIDE_V1',
      approval=dict(path=str(APPROVAL_PATH),sha256=APPROVAL_SHA256),condition_id=spec['condition_id'],
      frozen_termination_contract_preserved=True,effective_timeout_seconds=None,
      effective_start_deadline_unix=None,effective_intake_deadline_unix=None,
      scientific_scope_unchanged=True,no_automatic_retry=True)

def effective_timeout(item,spec):
    if detach_policy.is_spec(spec):return detach_policy.effective_timeout(item,spec)
    if workload_policy.is_workload_spec(spec):return workload_policy.effective_timeout(item,spec)
    if active(item) and spec.get('timeout_seconds') is None:
        require(scope_allowed(item,spec),'time removal cannot waive unapproved condition timeout')
        require(spec.get('operational_limits_override')==operational_override(spec),
                'null timeout requires exact approved operational override')
        return None
    require(type(spec['timeout_seconds']) in (int,float) and spec['timeout_seconds']>0,
            'bounded prior timeout or exact approved null override required')
    return spec['timeout_seconds']

timeout_seconds=effective_timeout

def assert_condition_unstarted(item,spec):
    if detach_policy.is_spec(spec):return detach_policy.batch_guard(item,spec)
    if workload_policy.is_workload_spec(spec):return workload_policy.assert_condition_unstarted(item,spec)
    if not active(item):return
    require(scope_allowed(item,spec),'numerical start removal is exact approved capacity scope')
    require(not any(a.get('budget_bucket')==BUCKET and a.get('selection_id')==spec['selection_id'] and
            a.get('profile')==spec['profile'] for a in item['attempts']),
            'approved condition already attempted: limit removal is not a retry grant')

def amend(item,approval_path,at_unix):
    require(Path(approval_path).resolve()==APPROVAL_PATH,'wrong exact start/time approval path')
    approval()
    if FIELD in item:active(item);return False
    require(item.get('campaign_id')==CAMPAIGN and 'capacity_diagnostic_amendment' in item,'original adopted capacity campaign required')
    require(item.get('controller',{}).get('state')=='STOPPED','adopt after original controller naturally stops')
    require(not any(a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') for a in item['attempts']),
            'active or uncertain applications prevent timing/source switch')
    require(item['maximum_actual_starts']==46 and item['start_deadline_unix']==1792663200 and
            item['intake_deadline_unix']==1792677600,'unexpected prior start/time contract')
    actual=sum(a.get('actual_start') is True for a in item['attempts'])
    require(actual==item['actual_starts'],'historical charge recount changed')
    row=dict(schema=SCHEMA,status='APPLIED',approval=dict(path=str(APPROVAL_PATH),sha256=APPROVAL_SHA256),
      adopted_unix=at_unix,actual_starts_at_adoption=actual,t0_unix=item['t0_unix'],
      old_limits={k:copy.deepcopy(item.get(k)) for k in REMOVED+DISPLAYS+('remaining_start_capacity',)},
      old_per_end_timeout_seconds=10800,old_capacity_start_allowance=10,
      pending_source_switch_reviews=copy.deepcopy([r for r in item.get('execution_control_reviews',[])
       if r.get('schema')=='E2_CAPACITY_LIMITS_REMOVAL_PENDING_SAFE_SOURCE_SWITCH_V1']),
      original_reservations=copy.deepcopy(item['reservations']),
      original_capacity_matrix=copy.deepcopy(item['capacity_diagnostic_matrix']),
      original_legacy_matrix_sha256=item['full_system_matrix']['sha256'],
      original_legacy_source_identity=copy.deepcopy(item.get('final_source_identity')),
      attempt_history_prefix_count=len(item['attempts']),attempt_history_prefix_sha256=canonical_sha(item['attempts']),
      approved_condition_ids=sorted(CONDITIONS),automatic_retry_authorized=False,refunds_authorized=False,
      non_time_resource_limits_unchanged=True,other_projects_unchanged=True,
      capacity_numeric_start_cap_removed=True,remaining_scientific_conditions_finite=True,
      operational_time_override='Frozen identity/Q termination fields retain their prior bytes as provenance; effective supervision timeout is null under this exact approval')
    item[FIELD]=row
    for k in REMOVED+DISPLAYS:item[k]=None
    item['remaining_start_capacity']=None
    item['per_end_timeout_seconds']=None
    item['maximum_capacity_diagnostic_starts']=None
    item.setdefault('policy_amendments',[]).append(copy.deepcopy(row))
    active(item)
    return True
