"""Exactly four approved main61 starts in the original locked campaign.

Pure guards and transformations only. Coordinator owns the permanent registry
lock. Full-spec bindings may be appended after independent qualification; they
never grant qualification, alter old buckets, or refund a prior attempt.
"""
import copy
import detach_diagnostic_policy as detach_policy
import hashlib
import json
from pathlib import Path

CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1'
FIELD='workload_pipeline_batches'
SCHEMA='E2_EXACT_MAIN61_WORKLOAD_BATCH_ADOPTION_V1'
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PACK=ROOT/'docs/ep_l2/review_packs/MS20261022_E2_WORKLOAD_PIPELINE_PROPOSAL_r1'
PROPOSAL_PATH=PACK/'PROPOSAL.json'
PROPOSAL_SHA256='1a305c7ac8492f0771e1fcebbc4092d3d3b87c2697679c02f8071e0da77416aa'
PROPOSAL_COMMIT='9c2d9c1b137dd9b282dc3e3a48c8b89c849b4637'
APPROVAL_PATH=PACK/'USER_APPROVAL.json'
APPROVAL_SHA256='529ca37c4f649f8a2a786324861a1b6e7ab0305c392d78e17bc463fdaa3eb47d'
APPROVAL_COMMIT='92e3cd50cb30fd245e107ad674a7be249fce4929'
MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
SOURCE={'core_source_commit':'d010911e3174a3764791183cd108fe4664ba8731',
 'framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
 'vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b','binary_sha256':MAIN61}
ARCHIVE_SHA256='3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8'
FWT_BATCH='EPL2_MAIN61_FWT_RESTORATION_20261022_r1'
SGEMM_BATCH='EPL2_MAIN61_SGEMM_EXPLORATORY_20261022_r1'
CONDITIONS={
 'V4_FWT_MAIN61_RESTORE_S':(FWT_BATCH,'S','D_V1_FWT_7_21','FWT_7_21','V2_MAIN_FWT_7_21','E011_618407f0'),
 'V4_FWT_MAIN61_RESTORE_F':(FWT_BATCH,'F','D_V1_FWT_7_21','FWT_7_21','V2_MAIN_FWT_7_21','E012_63be0bb4'),
 'V4_SGEMM_MAIN61_EXPLORATORY_S':(SGEMM_BATCH,'S','D_EXP_SGEMM_MEDIUM_20261022_r1','sgemm','V4_EXP_SGEMM_MAIN61_SF',None),
 'V4_SGEMM_MAIN61_EXPLORATORY_F':(SGEMM_BATCH,'F','D_EXP_SGEMM_MEDIUM_20261022_r1','sgemm','V4_EXP_SGEMM_MAIN61_SF',None)}
TRACES={'FWT_7_21':'f3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460',
 'sgemm':'694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb'}


def require(ok,message):
    if not ok:raise ValueError(message)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def approval_ref():
    return dict(path=str(APPROVAL_PATH),sha256=APPROVAL_SHA256,publication_commit=APPROVAL_COMMIT)


def authority():
    raw=PROPOSAL_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==PROPOSAL_SHA256,'exact approved proposal changed')
    proposal=json.loads(raw)
    require(proposal['proposal_id']=='EPL2_WORKLOAD_PIPELINE_PRIMARY_FOUR_20261022_r1','wrong proposal')
    require({r['condition_id'] for r in proposal['conditions']}==set(CONDITIONS),'approved four IDs changed')
    raw=APPROVAL_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==APPROVAL_SHA256,'exact workload user approval changed')
    user=json.loads(raw)
    require(user.get('schema')=='E2_MAIN61_WORKLOAD_PIPELINE_USER_APPROVAL_V1' and user.get('status')=='USER_APPROVED_ONLY_EXACT_FOUR_AFTER_QUALIFICATION','workload proposal not approved')
    require(user.get('approved_proposal')==dict(path=PROPOSAL_PATH.relative_to(ROOT).as_posix(),sha256=PROPOSAL_SHA256,commit=PROPOSAL_COMMIT,repo='swayhrl/accel-sim-framework'),
            'approval must bind exact published proposal')
    require(set(user.get('approved_condition_ids',[]))==set(CONDITIONS) and len(user.get('approved_condition_ids',[]))==4 and user.get('maximum_new_actual_starts')==4,
            'approval must bind four starts only')
    require(user.get('source_identity')==SOURCE and user.get('archive_sha256')==ARCHIVE_SHA256,
            'approval exact main61/source/archive required')
    require(user.get('baseline_actual_starts')==46 and user.get('T0')==1792414193 and
      user.get('endpoint_result_cap_bytes')==384*2**20 and user.get('batch_application_result_cap_bytes')==1536*2**20,
            'approval old count/T0/result bounds differ')
    require(user.get('effective_timeout_seconds') is None and
      user.get('automatic_retry_or_extra_condition_approved') is False,
            'no automatic extra/retry or implicit timeout')
    return proposal


def is_workload_spec(spec):
    return spec.get('condition_id') in CONDITIONS or spec.get('budget_bucket') in (FWT_BATCH,SGEMM_BATCH)


def operational_override(spec):
    return dict(schema='E2_WORKLOAD_OPERATIONAL_LIMITS_OVERRIDE_V1',approval=approval_ref(),
      proposal_sha256=PROPOSAL_SHA256,condition_id=spec['condition_id'],effective_timeout_seconds=None,
      effective_start_deadline_unix=None,effective_intake_deadline_unix=None,
      frozen_termination_contract_preserved=True,no_automatic_retry=True)


def spec_sha(spec):
    # Inspector attaches content audit in-place. All execution/science fields,
    # paths, ordered configs, parser, full identity and qualification remain bound.
    return canonical_sha({k:v for k,v in spec.items() if k not in ('input_audit','operational_limits_override')})


def active(item):
    if FIELD not in item:return False
    authority();row=item[FIELD]
    require(row['schema']==SCHEMA and row['approval']==approval_ref(),'workload adoption authority changed')
    require(item['campaign_id']==CAMPAIGN and item['t0_unix']==row['t0_unix'],'original campaign/T0 changed')
    for key,value in row['immutable_original'].items():
        require(item.get(key)==value,'workload adoption cannot rewrite old '+key)
    require(len(item['attempts'])>=46 and canonical_sha(item['attempts'][:46])==row['old46_attempts_sha256'],
            'old46 attempts cannot be changed or refunded')
    for group in ('accepted_results','accepted_pairs','scientific_holds'):
        require(all(item.get(group,{}).get(k)==v for k,v in row['original_scientific_records'][group].items()),
                'old scientific record changed: '+group)
    require(set(row['batches'])=={FWT_BATCH,SGEMM_BATCH},'exact two workload batches required')
    require(set(row['bindings'])<=set(CONDITIONS),'extra binding denied')
    if len(item['attempts'])>50:
        require(detach_policy.active(item),'post50 requires exact new observer adoption')
    attempts=item['attempts'][46:50]
    require(len(attempts)<=4,'at most four new reservations/starts; failed attempts not refunded')
    all_ids=[]
    for batch,entry in row['batches'].items():
        require(entry['maximum_new_actual_starts']==2 and len(entry['attempt_ids'])<=2,'two starts per batch')
        actual=[a for a in attempts if a.get('budget_bucket')==batch]
        require(entry['attempt_ids']==[a['attempt_id'] for a in actual],'batch append-only accounting mismatch')
        all_ids.extend(entry['attempt_ids'])
    require(len(all_ids)==len(set(all_ids))==len(attempts),'unapproved post46 attempt or duplicate charge')
    for a in attempts:
        cid=a.get('condition_id')
        require(cid in CONDITIONS and a['budget_bucket']==CONDITIONS[cid][0],'new attempt exact condition missing')
        require(a.get('workload_spec_sha256')==row['bindings'][cid]['spec_sha256'],'attempt/spec binding changed')
        require(a['identity']==row['bindings'][cid]['identity'],'new attempt identity changed')
    require(len({a['condition_id'] for a in attempts})==len(attempts),'new condition attempted twice')
    return True


def basic_spec(spec):
    cid=spec.get('condition_id');require(cid in CONDITIONS,'unapproved workload condition')
    batch,profile,selection,work,group,prior=CONDITIONS[cid]
    require(all(spec.get(k)==v for k,v in dict(budget_bucket=batch,profile=profile,selection_id=selection,
      comparison_group=group,campaign_id=CAMPAIGN,launch_owner='E').items()),'wrong workload profile/batch/selection/group')
    identity=spec['identity']
    require(identity.get('workload')==work and identity.get('trace_content_sha256')==TRACES[work],
            'wrong full workload input')
    require(identity.get('epoch_range')=={'epochs':'all','scope':'full_application'},'full input required')
    require(all(identity.get(k)==SOURCE[k] for k in ('core_source_commit','framework_source_commit','binary_sha256'))
      and spec.get('vendor_pybind11_commit')==SOURCE['vendor_pybind11_commit'],'exact main61 source required')
    require(spec.get('retry_previous_attempt')==prior,'exact old retry ID required; SGEMM is not a retry')
    require(bool(spec.get('retry_reason')) if prior else not spec.get('retry_reason'),'retry reason scope mismatch')
    require(spec.get('timeout_seconds') is None and spec.get('operational_limits_override')==operational_override(spec),
            'exact approved null operational timeout override required')
    require(type(spec.get('maximum_result_bytes')) is int and 128*2**20<=spec['maximum_result_bytes']<=384*2**20,
            'hard endpoint result cap exceeds384MiB')
    require(spec.get('memory_bytes',8*2**30)==8*2**30,'exact8GiB memory reservation')
    require(identity.get('termination_contract',{}).get('timeout_seconds')==10800,
            'frozen scientific termination identity must remain10800')
    p=spec['profile_semantics']
    require(p['research_switches']==dict.fromkeys(('W','V','T','M'),int(profile=='F')),'finite main61 switch vector')
    require(not any(identity.get('ideal_vector',{}).values()),'no ideal diagnostic flag in finite S/F')
    require(identity['feature_vector'].get('payload_capacity_per_slice')==1168 and
      identity['feature_vector'].get('ops_per_bank_cycle')==1,'finite1168 physicalP1 required')
    require(spec['labels']==p['labels'] and spec['labels']['diagnostic'] is False,'exact qualified finite profile labels required')
    return cid


def scope_allowed(item,spec):
    if not active(item) or not is_workload_spec(spec):return False
    try:cid=basic_spec(spec)
    except (ValueError,KeyError,TypeError):return False
    binding=item[FIELD]['bindings'].get(cid)
    return binding is not None and binding['spec_sha256']==spec_sha(spec)


def effective_timeout(item,spec):
    require(scope_allowed(item,spec),'workload timeout scope not bound/qualified')
    return None


def batch_guard(item,spec):
    require(scope_allowed(item,spec),'exact approved workload scope required')
    row=item[FIELD];batch=spec['budget_bucket']
    require(len(row['batches'][batch]['attempt_ids'])<2 and len(item['attempts'][46:])<4,'workload start batch exhausted')
    require(not any(a.get('condition_id')==spec['condition_id'] for a in item['attempts'][46:]),
            'workload condition already attempted; no implicit retry/refund')


assert_condition_unstarted=batch_guard


def condition_check(item,spec,digest):
    require(scope_allowed(item,spec),'unbound workload condition')
    qrow=item['qualifications'][spec['qualification_id']]
    require(digest(qrow['path'])==qrow['sha256'],'independent workload qualification changed')
    q=qrow['qualification']
    require(q['source_identity']==SOURCE and q['status']=='INDEPENDENTLY_QUALIFIED','independent exactmain61 qualification')
    require(spec['profile_semantics']==q['supported_profiles'][spec['profile']],'wrong separately qualified profile')
    require(q['input_selection_id']==spec['selection_id'],'own input-specific qualification required')
    return dict(condition_id=spec['condition_id'],group='MAIN_RESTORATION' if spec['budget_bucket']==FWT_BATCH else 'EXPLORATORY')


def bind_condition(item,spec,digest):
    require(active(item),'workload adoption absent')
    cid=basic_spec(spec)
    require(not any(a.get('condition_id')==cid for a in item['attempts'][46:]),'cannot change started binding')
    qrow=item['qualifications'][spec['qualification_id']];q=qrow['qualification']
    require(digest(qrow['path'])==qrow['sha256'] and q['status']=='INDEPENDENTLY_QUALIFIED','own current qualification required')
    require(q['source_identity']==SOURCE and q.get('input_selection_id')==spec['selection_id'],'wrong input/main61 Q')
    require(q['supported_profiles'].get(spec['profile'])==spec['profile_semantics'],'wrong own profile Q')
    chosen=item['input_selections'][spec['selection_id']]
    require(digest(chosen['path'])==chosen['sha256'] and
      chosen['selection']['full_input_identity']['trace_content_sha256']==spec['identity']['trace_content_sha256'],
      'exact registered D input required')
    prior=CONDITIONS[cid][5]
    if prior:
        old=next((a for a in item['attempts'][:46] if a['attempt_id']==prior),None)
        require(old is not None and old['state']=='INCOMPLETE' and old['identity']==spec['identity'],
                'FWT restoration must preserve exact previous INCOMPLETE identity')
    record=dict(spec_sha256=spec_sha(spec),identity=copy.deepcopy(spec['identity']),qualification_id=spec['qualification_id'],spec_fields=copy.deepcopy({k:v for k,v in spec.items() if k not in ('input_audit','operational_limits_override')}))
    old=item[FIELD]['bindings'].get(cid)
    require(old is None or old==record,'append-only immutable spec binding')
    item[FIELD]['bindings'][cid]=record
    condition_check(item,spec,digest)
    return record


def record_reservation(item,spec,attempt):
    # Called immediately before appending attempt under the same registry lock.
    batch_guard(item,spec)
    attempt.update(condition_id=spec['condition_id'],workload_spec_sha256=spec_sha(spec))
    item[FIELD]['batches'][spec['budget_bucket']]['attempt_ids'].append(attempt['attempt_id'])


def amend(item,approval_path,at_unix):
    require(Path(approval_path).resolve()==APPROVAL_PATH,'wrong exact workload approval path')
    authority()
    if FIELD in item:active(item);return False
    require(item['campaign_id']==CAMPAIGN and item['controller']['state']=='STOPPED','adopt at original stopped controller')
    require(len(item['attempts'])==46 and sum(a.get('actual_start') is True for a in item['attempts'])==46,
            'exact charged46 history required')
    require(not any(a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') for a in item['attempts']),
            'active/uncertain task prevents adoption')
    immutable=('reservations','full_system_matrix','capacity_diagnostic_matrix','final_source_identity',
      'capacity_diagnostic_runtime','capacity_diagnostic_amendment','start_and_time_limit_removal',
      'maximum_actual_starts','start_deadline_unix','intake_deadline_unix',
      'additional_results_max_bytes','old_plus_new_results_max_bytes')
    item[FIELD]=dict(schema=SCHEMA,approval=approval_ref(),proposal_sha256=PROPOSAL_SHA256,
      adopted_unix=at_unix,t0_unix=item['t0_unix'],old46_attempts_sha256=canonical_sha(item['attempts']),
      immutable_original={k:copy.deepcopy(item.get(k)) for k in immutable},
      original_scientific_records={k:copy.deepcopy(item.get(k,{})) for k in ('accepted_results','accepted_pairs','scientific_holds')},
      bindings={},batches={b:dict(maximum_new_actual_starts=2,attempt_ids=[]) for b in (FWT_BATCH,SGEMM_BATCH)})
    active(item);return True


def adopt_selection(item,path,raw,selection,digest):
    require(active(item),'workload adoption absent')
    require(selection.get('campaign_id')==CAMPAIGN and selection.get('selection_id')=='D_EXP_SGEMM_MEDIUM_20261022_r1',
            'only approved independent SGEMM selection adoption')
    require(selection.get('selected_by')=='E' and selection.get('adoption_kind')=='E_ADOPTION_OF_PRIOR_D_PREREGISTRATION',
            'E adoption cannot impersonate new D decision')
    require(selection.get('approval')==approval_ref(),'selection adoption must bind exact approval')
    origin=selection.get('original_D_preregistration',{})
    require(origin.get('publication_commit') and origin.get('path') and origin.get('sha256'),
            'original published D preregistration reference required')
    require(digest(origin['path'])==origin['sha256'],'original D preregistration bytes changed')
    original=json.loads(Path(origin['path']).read_text())
    require(origin.get('publication_commit')=='6825d1cd0c87d8b0122e03a9dff5253c873b747b' and origin.get('sha256')=='2d2902905605a93193c3129be8cf765e48fe71e8b205ac12028d179e41f99f26', 'exact published D exploratory proposal required')
    require(original.get('schema')=='D_PROPOSED_TRACE_INPUT_FOR_E_REVIEW_NOT_REGISTRATION' and original.get('workload')=='sgemm' and original.get('expected_full_instructions')==1658916864 and original.get('kernel_count')==1 and original.get('selected_before_new_candidate_S_F_performance') is True and original.get('candidate_new_speedup_inspected') is False,'original independent D preregistered selection scope required')
    original_input=original
    chosen=selection['full_input_identity']
    require(original_input.get('trace_content_sha256')==chosen.get('trace_content_sha256')==TRACES['sgemm'],
            'exact original preregistered SGEMM input required')
    require(chosen.get('expected_full_instructions')==1658916864 and
      chosen.get('comparison_groups')==['V4_EXP_SGEMM_MAIN61_SF'] and chosen.get('runtime_independent_input_source'),
      'exact full SGEMM input/comparison scope required')
    require(selection.get('rationale') and selection.get('original_MAIN_roster_replacement') is False,
            'separate exploration only; preserve original MAIN')
    row=dict(path=str(Path(path).resolve()),sha256=hashlib.sha256(raw).hexdigest(),selection=selection)
    old=item['input_selections'].get(selection['selection_id'])
    require(old is None or old==row,'registered selection cannot be rebound')
    item['input_selections'][selection['selection_id']]=row
    return row
