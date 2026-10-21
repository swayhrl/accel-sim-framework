"""Explicit ten-start amendment of the original E ledger, not a new campaign.

Pure transformations/checks. Coordinator owns original REGISTRY.lock and writes.
No qualification, source build, app launch, retry or resource waiver is granted.
"""
import copy
import hashlib
import json
from pathlib import Path

AUTHORITY='49343880865edb22a17523790fc32dd55975966c'
CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1'
BUCKET='five_input_capacity_diagnostic_user_approved_20261021'
MASTER='-gpgpu_ep_l2_diag_l2_large_capacity'
OFF='S'
ON='S_L2_DATA_FREE_LARGE_CAPACITY'
MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
GIB=2**30
LIMITS=dict(maximum_actual_starts=46,additional_results_max_bytes=10*GIB,
 old_plus_new_results_max_bytes=24*GIB,start_deadline_unix=1792663200,intake_deadline_unix=1792677600)
ORIGINAL_LIMITS=dict(maximum_actual_starts=40,additional_results_max_bytes=6*GIB,
 old_plus_new_results_max_bytes=20*GIB,start_deadline_unix=1792576800,intake_deadline_unix=1792591200)
APPROVAL_SHA='1eff2669e129328ef79710be077f273ce45318bbd015edfa207ba1fe3374b2e8'
INPUTS={
 'convolutionSeparable':('D_V1_convolutionSeparable','620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f',714547200),
 'cfd_097k':('D_V2_cfd_097k','6d5eb92fbe5391b3811dc08fcaaacb891ec8a69639512b99f68d224b6a921e66',143129372),
 'dwt2d':('D_V1_dwt2d','5df26bc18e344ec381ce8cae8acd93a0e8b2266d5def861dd575a7061a303fc9',148684429),
 'sad':('D_V2_sad','c0a36352a791331237f6c293c39bbf4017c930ae3871860618a92685381d6b01',157583646),
 'vectorAdd_4M':('D_V2_vectorAdd_4M','138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940',56000000)}
GATES={'capacity_master_off_equivalence','capacity_scaled_geometry_role_bounds',
 'capacity_effective_values_and_default_off','capacity_real_copy_fixed_latch_and_data_identity',
 'capacity_requester_stale_sector_wad_wb_drain','capacity_bank_free_on_p1_off',
 'capacity_reject_contradictory_settings','capacity_highwater_refusal_coverage'}

def check(ok,message):
 if not ok:raise ValueError(message)

def active(item):return 'capacity_diagnostic_amendment' in item

def effective_limits(item):
 if not active(item):
  check(item.get('maximum_actual_starts') in (24,40),'unamended campaign counter changed')
  check(item.get('start_deadline_unix')==ORIGINAL_LIMITS['start_deadline_unix'] and
        item.get('additional_results_max_bytes')==6*GIB and item.get('old_plus_new_results_max_bytes')==20*GIB,
        'unamended campaign deadline/result policy changed')
  result=ORIGINAL_LIMITS.copy();result['maximum_actual_starts']=item['maximum_actual_starts'];return result
 record=item['capacity_diagnostic_amendment']
 check(record['authority_commit']==AUTHORITY and record['approval_sha256']==APPROVAL_SHA,'invalid capacity authority')
 check(all(item[k]==v for k,v in LIMITS.items()),'capacity approved bounded limits changed')
 check({k:v for k,v in item['reservations'].items() if k!=BUCKET}==record['original_reservations'],
       'old allocation history changed')
 check(item['reservations'].get(BUCKET)==10,'capacity diagnostic bucket is exactly ten')
 check(item['no_new_full_application_after']=='2026-10-22T18:00:00+08:00' and
       item['result_intake_freeze']=='2026-10-22T22:00:00+08:00','capacity deadline display differs from bounded Unix cutoff')
 check(item['full_system_matrix']['sha256']==record['original_matrix_sha256'] and
       item.get('final_source_identity')==record['original_source_identity'],'legacy matrix/source identity changed')
 return LIMITS.copy()

def matrix():
 return dict(authority_commit=AUTHORITY,campaign_id=CAMPAIGN,conditions=[
  dict(condition_id='V3_CAPACITY_'+work+'_'+('S_OFF' if profile==OFF else 'S_ON'),workload=work,
    selection_id=selection,trace_content_sha256=trace,expected_full_instructions=insn,
    profile=profile,master_requested=int(profile==ON),comparison_group='CAPACITY_DIAGNOSTIC_'+work,
    budget_bucket=BUCKET) for work,(selection,trace,insn) in INPUTS.items() for profile in (OFF,ON)])

def amend(item,approval_path,at_unix):
 raw=Path(approval_path).read_bytes()
 check(hashlib.sha256(raw).hexdigest()==APPROVAL_SHA,'approved bytes changed')
 approval=json.loads(raw)
 check(approval['status']=='USER_APPROVED_FOR_A_E_IMPLEMENTATION_AND_EXECUTION_AFTER_QUALIFICATION',
       'not the approved execution revision')
 if active(item):effective_limits(item);return False
 check(item['campaign_id']==CAMPAIGN,'wrong campaign')
 check(all(item.get(k,v if k=='intake_deadline_unix' else None)==v for k,v in ORIGINAL_LIMITS.items()),'unexpected prior limits')
 check(item['controller']['state']=='STOPPED','adopt only at original controller safe boundary')
 check(not any(a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED') for a in item['attempts']),
       'active or uncertain application prevents adoption')
 check(sum(a.get('actual_start') is True for a in item['attempts'])==item['actual_starts']==36,
       'adoption must preserve exact charged36 boundary')
 original=copy.deepcopy(item['reservations'])
 check(sum(original.values())==40 and original.get('contingency')==8,'original32+8 allocation missing')
 check(BUCKET not in original,'unrecognized preexisting capacity bucket')
 record=dict(authority_commit=AUTHORITY,approval_path=str(Path(approval_path).resolve()),approval_sha256=APPROVAL_SHA,
   adopted_unix=at_unix,actual_starts_at_adoption=36,old_limits=ORIGINAL_LIMITS.copy(),new_limits=LIMITS.copy(),
   original_reservations=original,additional_bucket=BUCKET,additional_actual_starts_maximum=10,
   previous_deadline_strings={k:item.get(k) for k in ('no_new_full_application_after','result_intake_freeze')},
   original_matrix_sha256=item['full_system_matrix']['sha256'],original_source_identity=copy.deepcopy(item.get('final_source_identity')),
   old_attempts_refunded=False,separate_campaign_counter=False,new_runtime_qualification_inherited=False,
   original_unstarted_four_frozen_for_this_batch=True)
 item['capacity_diagnostic_amendment']=record
 item['capacity_diagnostic_matrix']=matrix()
 item['reservations'][BUCKET]=10
 item.update(LIMITS)
 item['no_new_full_application_after']='2026-10-22T18:00:00+08:00'
 item['result_intake_freeze']='2026-10-22T22:00:00+08:00'
 item.setdefault('policy_amendments',[]).append(copy.deepcopy(record))
 effective_limits(item)
 return True

def is_capacity_spec(spec):return spec.get('budget_bucket')==BUCKET

def qualification(q,digest):
 contract=q.get('capacity_diagnostic')
 check(contract is not None,'new capacity qualification contract missing')
 check(contract['authority_commit']==AUTHORITY and contract['master_option']==MASTER,
       'capacity qualification authority/master changed')
 check(q['source_identity']['binary_sha256']!=MAIN61,'main61 qualification cannot be inherited')
 check(q.get('full_system_v2') is None,'capacity S qualification cannot masquerade as full-design V/RO')
 check(set(q['supported_profiles'])=={OFF,ON},'exact two new-runtime OFF/ON profiles required')
 check(contract.get('common_capacity_vector') and contract.get('native_cache_geometry'),
       'A/E exact common finite vector/native geometry missing')
 for name in GATES:
  gate=q['gates'][name]
  check(gate['status']=='PASS' and gate['production_driven'] is True and
        digest(gate['evidence_path'])==gate['evidence_sha256'],'missing/changed new-runtime capacity gate: '+name)
 for name,p in q['supported_profiles'].items():
  check(p['research_switches']==dict(W=0,V=0,T=0,M=0),'capacity matrix requires traditional S only')
  options=p['effective_options']
  check(options[MASTER]==str(int(name==ON)),'wrong explicit master request')
  check(all(options.get(k)=='0' for k in
    ('-gpgpu_ep_l2_diag_copy_free','-gpgpu_ep_l2_diag_l2_data_free','-gpgpu_ep_l2_ideal_meta',
     '-gpgpu_ep_l2_ideal_read_hit','-gpgpu_ep_l2_ideal_wb','-gpgpu_ep_l2_mq2','-gpgpu_ep_l2_rg1',
     '-gpgpu_ep_l2_feature_unified_payload','-gpgpu_ep_l2_feature_ro_pending_state',
     '-gpgpu_ep_l2_feature_tvd','-gpgpu_ep_l2_feature_adaptive_policy','-gpgpu_ep_l2_tvd_clean',
     '-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_tvd_fixed_entries','-gpgpu_ep_l2_ro_tag_detach',
     '-gpgpu_ep_l2_ro_line_mshr_bypass','-gpgpu_ep_l2_static_s64','-gpgpu_ep_l2_wb_local_cap')) and
     options.get('-gpgpu_ep_l2_ft_mode')=='1' and options.get('-gpgpu_ep_l2_payload_mode')=='2',
     'contradictory flags or nontraditional S')
  check(set(p['comparison_variable_options'])=={MASTER},'only master switch varies in this diagnostic pair')
  check(p['hardware_P1_throughput_eligible']==int(name==OFF),'incorrect hardware P1 eligibility label')
  check(all(not p['feature_vector'].get(k,False) for k in
       ('tvd','unified_wb','ro_tag_detach','ro_line_mshr_bypass','adaptive_policy','static_s64')),
       'feature-vector V/RO/W/static contradiction')
  check(all(p['ideal_vector'].get(k) is False for k in ('copy_free','meta','read_hit','wb','mem_all_data')) and
        p['ideal_vector']['l2_data_free']==bool(name==ON),'ideal-vector service contradiction')
  check(p['labels']['subset'] in (False,None) and p['labels']['oracle'] is False,'capacity scope is full-input diagnostic, no RO oracle')
  if name==ON:check(p['labels']['diagnostic'] is True,'ON must retain diagnostic label')
 off=q['supported_profiles'][OFF]['effective_options'];on=q['supported_profiles'][ON]['effective_options']
 check(set(off)==set(on) and {k for k in off if off[k]!=on[k]}=={MASTER},
       'OFF/ON configs must differ only in the single master option')
 return contract

def condition_check(item,spec,digest):
 effective_limits(item)
 check(active(item),'explicit capacity amendment not adopted')
 check(item.get('capacity_diagnostic_matrix')==matrix(),'approved exact ten-condition matrix changed')
 row=next((r for r in matrix()['conditions'] if r['condition_id']==spec.get('condition_id')),None)
 check(row is not None,'unapproved capacity condition')
 check(all(spec[k]==row[k] for k in ('selection_id','profile','comparison_group','budget_bucket')),
       'capacity condition/profile/bucket changed')
 check(spec['identity']['workload']==row['workload'] and spec['identity']['trace_content_sha256']==row['trace_content_sha256'],
       'capacity exact full-input identity changed')
 check(spec['identity']['epoch_range']=={'epochs':'all','scope':'full_application'},'capacity requires complete application')
 check(not spec.get('retry_previous_attempt') and not spec.get('retry_reason'),'capacity automatic retry not authorized')
 qrow=item['qualifications'][spec['qualification_id']]
 check(digest(qrow['path'])==qrow['sha256'],'capacity independent qualification changed')
 q=qrow['qualification'];qualification(q,digest)
 check(item.get('capacity_diagnostic_runtime')==q['source_identity'],'new common capacity binary not frozen')
 check(spec['profile_semantics']==q['supported_profiles'][spec['profile']],'capacity profile semantics changed')
 check(all(spec['identity'][k]==q['source_identity'][k] for k in
       ('core_source_commit','framework_source_commit','binary_sha256')),'wrong capacity runtime')
 check(spec['timeout_seconds']==10800,'capacity per-end timeout remains10800s')
 check(0<spec['maximum_result_bytes']<=384*2**20,'capacity endpoint result cap exceeds384MiB')
 return row

def bucket_guard(item,spec):
 """New ten cannot enlarge any original bucket or supply original contingency."""
 if not active(item):return
 effective_limits(item)
 attempts=item['attempts']
 charged=lambda a:a.get('actual_start') or a['state'] in ('RESERVED','START_INTENT_UNRECONCILED')
 capacity=sum(a.get('budget_bucket')==BUCKET and charged(a) for a in attempts)
 legacy=sum(a.get('budget_bucket')!=BUCKET and charged(a) for a in attempts)
 if is_capacity_spec(spec):check(capacity<10,'capacity ten actual-start allowance exhausted')
 else:
  check(legacy<40,'old campaign40 allowance cannot borrow new diagnostic slots')
  check(False,'old unstarted four frozen: approved batch authorizes capacity conditions only')
