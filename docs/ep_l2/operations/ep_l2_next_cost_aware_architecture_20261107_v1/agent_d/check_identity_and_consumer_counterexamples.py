"""Finite metadata/consumer-shell negatives. No loader, model, dispatcher or ledger."""
from pathlib import Path
import json,copy,importlib.util
O=Path(__file__).resolve().parent
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,O/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
i=load('identity_contracts','identity_contracts.py');c=load('resource_tail','source_specific_resource_tail_consumer.py')
P=O.parents[2]
index=json.loads((P/'research/unified_memory_taxonomy_20261106_v1/agent_a/CURRENT_ENDPOINT_INDEX.json').read_text())
by={e['cohort']:e for e in index['endpoints']}
def point(e):
 p={k:copy.deepcopy(e[k])for k in['input_identity_sha256','literal_commandlist_sha256','ordered_commands_canonical_sha256','ordered_commands','ordered_kernel_identity','mode','geometry','clock_domains','observer_env','expected_kernel_launches','expected_instructions','expected_CTA','effective_option_count','effective_options']}
 p['source_identity']=e['source_identity_original'];p['expected_effective_options']=p.pop('effective_options');p['fullconfig_sha256']=e['effective_options_sha256'];return p
a=point(by['EP_PERF_PFV5_A_FWT_G32W8_WV_OFF_V1']);b=point(by['EP_PERF_PFV5_A_FWT_G32W8_WV_ON_V1'])
allowed={k for k in a['expected_effective_options'].keys()|b['expected_effective_options'].keys()if a['expected_effective_options'].get(k)!=b['expected_effective_options'].get(k)}
checks=[]
def check(n,f,reject=False):
 try:r=f()
 except Exception as e:
  if not reject:raise
  checks.append(dict(name=n,status='PASS_REJECT',reason=str(e)));return
 if reject:raise AssertionError('negative accepted '+n)
 if r is False:raise AssertionError('false positive '+n)
 checks.append(dict(name=n,status='PASS'))
check('actual_frozen_sameSource_sameInput_fullconfig_pair_identity_not_perf_endorsement',lambda:i.validate_pair(a,b,allowed))
for field in ['binary_sha256','core_source_commit','framework_source_commit','archive_sha256']:
 v=copy.deepcopy(b);v['source_identity'][field]='0'*len(v['source_identity'][field]);check('reject_cross_'+field,lambda v=v:i.validate_pair(a,v,allowed),True)
for field in ['input_identity_sha256','literal_commandlist_sha256','ordered_commands_canonical_sha256']:
 v=copy.deepcopy(b);v[field]='0'*64;check('reject_'+field,lambda v=v:i.validate_pair(a,v,allowed),True)
v=copy.deepcopy(b);v['ordered_commands']=list(reversed(v['ordered_commands']));v['ordered_commands_canonical_sha256']=i.canonical(v['ordered_commands']);check('reject_reordered_commandlist',lambda:i.validate_pair(a,v,allowed),True)
v=copy.deepcopy(b);v['ordered_kernel_identity'][0]['sha256']='0'*64;check('reject_kernel_content_drift',lambda:i.validate_pair(a,v,allowed),True)
v=copy.deepcopy(b);v['expected_effective_options']['-gpgpu_ep_l2_ms_observer']='0';v['fullconfig_sha256']=i.canonical(v['expected_effective_options']);check('reject_observer_flag_delta',lambda:i.validate_pair(a,v,allowed),True)
v=copy.deepcopy(b);v['clock_domains']='1132.0:1132.0:1132.0:1020.0';v['expected_effective_options']['-gpgpu_clock_domains']=v['clock_domains'];v['fullconfig_sha256']=i.canonical(v['expected_effective_options']);check('reject_clock_delta',lambda:i.validate_pair(a,v,allowed),True)
v=copy.deepcopy(b);v['expected_effective_options']['-new_undeclared_port']='2';v['effective_option_count']+=1;v['fullconfig_sha256']=i.canonical(v['expected_effective_options']);check('reject_option_population_and_hidden_port',lambda:i.validate_pair(a,v,allowed),True)
for owner in ['A','C']:
 family=json.loads((O/(owner+'_DIRECTORY_FAMILY_DRAFT_NOT_REQUESTABLE.json'if owner=='A'else'C_CLEAN_FAMILY_DRAFT_NOT_REQUESTABLE.json')).read_text())
 check(owner+'_current_gap_formal0_valid',lambda f=family:i.validate_family(f))
 wrong=copy.deepcopy(family);wrong['formal_proposed_start_count']=3;check(owner+'_gap_cannot_be_formal3',lambda f=wrong:i.validate_family(f),True)
 wrong=copy.deepcopy(family);wrong['status']='REQUESTABLE';wrong['formal_proposed_start_count']=3;check(owner+'_partial_not_requestable',lambda f=wrong:i.validate_family(f),True)
# Pure CPU fixtures below exercise only cost/tail predicates, never claim an
# actual producer/Source/loader or full-application qualification.
fixed=dict(frontend_cam_ports=1,completion_cam_ports=1,directory_bound_wb_uid_bits=32,extra_packet_identity_bits=0)
common=dict(slice=0,metadata_PPA='UNKNOWN',metadata_clock_closure='UNKNOWN',logical_control_read_views=3,**fixed)
add=dict(extra_optional_metadata_rows=128,extra_query_ports=0,base_query_latency_l2_cycles=1,extension_extra_query_latency_l2_cycles=1,extension_update_lanes=1,ticket_capacity=1)
ac=dict(legacy_update_contract='PRESERVED_PLUS_ADDITIVE',invariant_cost_fields=fixed,new_additive_cost_fields=add,extension_rows=128,extension_clean_only=True,paid_nonnegative_counter_fields=['paid_row_commits'],timed_cleanup_required=False)
row=dict(common,legacy_indexed_control_update_lanes=3,paid_row_commits=5,**add);ac['expected_cost_field_names']=list(row);arows=[dict(row,slice=s)for s in range(64)]
check('A_preserve_old3_plus_explicit_additive_cost_CPU_fixture',lambda:c.check_legacy_and_new_cost(arows,ac))
repl=dict(row_service_lanes=1,count_commit_lanes=1,registered_ingress_heads=6,ingress_depth_per_head=1,selector='indexed_paid_scan')
cc=dict(legacy_update_contract='REPLACED_BY_SHARED_TOKEN_EXECUTION',invariant_cost_fields=fixed,replacement_cost_fields=repl,extension_rows=0,extension_clean_only=False,paid_nonnegative_counter_fields=['paid_row_commits'],timed_cleanup_required=True,cleanup_producer_marker='EPL2CLEANV2')
row=dict(common,update_execution='SHARED_TOKEN_GATED',paid_row_commits=7,**repl);cc['expected_cost_field_names']=list(row);crows=[dict(row,slice=s)for s in range(64)]
check('C_reconstructed_update_token_readviews3_CPU_fixture',lambda:c.check_legacy_and_new_cost(crows,cc))
for name,mut in [('fake_old3_in_reconstructed',lambda r:r.__setitem__('legacy_indexed_control_update_lanes',3)),('readviews_replaced_by_K',lambda r:r.__setitem__('logical_control_read_views',1)),('hidden_extra_port_field',lambda r:r.__setitem__('hidden_CAM_ports',64)),('invented_PPA_PASS',lambda r:r.__setitem__('metadata_PPA','PASS')),('bool_count_lane',lambda r:r.__setitem__('count_commit_lanes',True))]:
 rr=copy.deepcopy(crows);mut(rr[0]);check('reject_'+name,lambda rr=rr:c.check_legacy_and_new_cost(rr,cc),True)
inv=dict(slice=0,observed_app_cycles=100,physical_slots=1168,bank_count=4,bank_ops_per_physical_cycle=1,wad_capacity=128,line_mshr_capacity=128,descriptor_capacity=512,descriptor_free=512,mandatory_live=0,wb_live=0,bank_pending=0,row_tokens_live=0,metadata_updates_pending=0,packet_credits_outstanding=0,role_free=832,role_resident=256,role_bypass=0,role_wb=0,role_tvd=80,base_tvd_live=64,extension_tvd_live=16,extension_dirty_live=0,cleanup_done_at=95)
inventories=[dict(inv,slice=s)for s in range(64)]
tail=dict(cycle_domain='GPU_CUMULATIVE',last_kernel_cycles=90,cleanup_requested_at=90,app_after_cleanup_cycles=100,native_final_cycles=100,kernel_count=1,cleanup_is_kernel=False,cleanup_cycles_included_in_app=True,cleanup_producer_marker='EPL2CLEANV2')
check('exact64_tail_CPU_fixture',lambda:c.check_tail(tail,inventories,cc,1))
check('fixed_payload_bank_WAD_and_segment_CPU_fixture',lambda:c.check_inventory(inventories,ac,100))
for name,mut in [('extraPayload',lambda r:r.__setitem__('physical_slots',1169)),('mandatory_WAD_gift',lambda r:r.__setitem__('wad_capacity',256)),('ext_overflow',lambda r:r.__setitem__('extension_tvd_live',129)),('dirty_in_clean_ext',lambda r:r.__setitem__('extension_dirty_live',1)),('pending_row_token',lambda r:r.__setitem__('row_tokens_live',1)),('pending_packet_credit',lambda r:r.__setitem__('packet_credits_outstanding',1)),('wrong_final_snapshot_cycle',lambda r:r.__setitem__('observed_app_cycles',99))]:
 rr=copy.deepcopy(inventories);mut(rr[0]);check('reject_'+name,lambda rr=rr:c.check_inventory(rr,ac,100),True)
rr=copy.deepcopy(inventories);rr[1]['slice']=0;check('reject_duplicate_or_missing_slice',lambda:c.check_inventory(rr,ac,100),True)
for name,mut in [('mixed_L2_clock',lambda t:t.__setitem__('cycle_domain','L2')),('tail_subtracted',lambda t:t.__setitem__('native_final_cycles',90)),('cleanup_not_included',lambda t:t.__setitem__('cleanup_cycles_included_in_app',False)),('cleanup_fake_kernel',lambda t:t.__setitem__('kernel_count',2))]:
 t=copy.deepcopy(tail);mut(t);check('reject_'+name,lambda t=t:c.check_tail(t,inventories,cc,1),True)
rr=copy.deepcopy(inventories);rr[0]['cleanup_done_at']=101;check('reject_cleanup_after_app_end',lambda:c.check_tail(tail,rr,cc,1),True)
unqualified=json.loads((O/'C_RESOURCE_TAIL_CONSUMER_UNQUALIFIED_TEMPLATE.json').read_text());check('unqualified_template_never_grants_Source_PASS',lambda:c.validate({},unqualified,{}),True)
bad_contract=copy.deepcopy(unqualified);bad_contract['status']='SOURCE_SPECIFIC_ENGINEERING_CONTRACT_FROZEN';bad_contract['source_identity']={}
check('malformed_frozen_Source5_rejected',lambda:c.validate(dict(source_identity={}),bad_contract,dict(source_identity={})),True)
out=dict(schema='NEXT_COST_AWARE_SMALL_METADATA_IDENTITY_AND_CONSUMER_COUNTEREXAMPLES_V1',status='PASS_FINITE_METADATA_AND_CPU_FIXTURE_ONLY',count=len(checks),checks=checks,actual_new_A_or_C_Source_qualified=0,production_correctness_proven_by_these_checks=False,old_loader_Host_NI_suite_reruns=0,dispatcher_registered_or_model_starts=0,Trace_or_raw_body_reads=0)
(O/'FINITE_IDENTITY_AND_CONSUMER_CHECKS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status=out['status'],count=len(checks))))
