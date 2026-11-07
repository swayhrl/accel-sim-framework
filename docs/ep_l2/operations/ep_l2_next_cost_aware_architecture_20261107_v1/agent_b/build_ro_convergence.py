#!/usr/bin/env python3
"""Bounded metadata-only RO convergence. No actors, raw/Trace or source writes."""
from pathlib import Path
from fractions import Fraction
import copy,hashlib,json,sys
ROOT=Path(__file__).parent.resolve()
R=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research')
U=R/'unified_memory_taxonomy_20261106_v1/execution_authorized4_20261106_v1/control'
V=R/'performance_first_v5_20261105_v1/activation_20261105_v1/control'
COST=R/'performance_first_v5_20261105_v1/track_b_fullf/COST_AND_CYCLE_CONTRACT.json'
AUTHORITY='eae40596cb9a550785a50a3d64617686a6daa160'
INPUTS={}
def need(x,m):
 if not x:raise AssertionError(m)
def read_meta(path):
 p=Path(path);need(p.suffix in ['.json','.md'],'metadata formats only')
 need('traces'not in p.parts and not p.name.startswith('raw.')and p.stat().st_size<=2<<20,'no Trace/raw/large reads')
 b=p.read_bytes();INPUTS[str(p)]=dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 if p.suffix=='.md':return b.decode()
 def pairs(xs):
  d={}
  for k,v in xs:need(k not in d,'duplicate JSON metadata key');d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs)
def exact(r):
 x=read_meta(r['path']);need(INPUTS[r['path']]['sha256']==r['sha256'],'evidence SHA drift')
 if 'bytes'in r:need(INPUTS[r['path']]['bytes']==r['bytes'],'evidence size drift')
 return x
def put(name,x):
 p=ROOT/name;p.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n');return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def group_summary(c):
 out={}
 for name,g in c['groups'].items():
  rows=g['last_per_slice'];need(set(rows)=={str(i)for i in range(64)},'one final record each64 slices')
  for k,total in g.get('totals',{}).items():need(sum(int(row[k])for row in rows.values())==total,'final64 total:'+k)
  for k,peak in g.get('max_over_slices',{}).items():need(max(int(row[k])for row in rows.values())==peak,'max not sum:'+k)
  out[name]=dict(totals=g.get('totals',{}),max_over_slices=g.get('max_over_slices',{}),population='LAST_CUMULATIVE_RECORD_ONCE_PER_SLICE_64',original_emitted_records=g.get('emitted_records',g.get('emitted_lines')))
 return out
def point(p):
 s=exact(p['spec_ref']);a=exact(p['accepted_point_ref']);archive=exact(p['archive_receipt_ref']);c=exact(p['closed_counter_summary_ref'])
 need(p['state']=='CLOSED_ACCEPTED'and a['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED'and p['hardware_drained']is True,'accepted complete cell')
 need(a['cohort']==s['cohort']==p['cohort']and a['uuid']==p['uuid']==archive['uuid'],'single UUID/cohort')
 need(a['cycles']==p['cycles']and a['hardware_drained']is True,'exact full cycles')
 need(p['CTA']==a['CTA']==s['expected_CTA']and p['instructions']==a['instructions']==s['expected_instructions'],'exact complete input CTA/instructions')
 need(p['kernel_count']==a['kernel_count']==len(s['expected_kernel_launches']),'entire declared kernel population')
 need(a['source_identity']==s['source_identity']==c['source_identity'],'same Source5 across metadata')
 need(a['input_identity_sha256']==s['input_identity_sha256']==c['input_identity_sha256'],'same exact input')
 need(a['spec_ref']==p['spec_ref'],'accepted frozen Spec')
 need(c['accepted_point_ref']['sha256']==p['accepted_point_ref']['sha256'],'counter joins same accepted cell')
 need(archive['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and archive['source_keep']is True,'archive closure metadata')
 rr=archive['native_restores'];need(len(rr)==2 and {z['restore_label']for z in rr}=={'FIRST','INDEPENDENT'}and len({z['target']for z in rr})==2,'two distinct reported complete Native restores')
 need(all(z['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'and z['archive_sha256']==archive['archive_ref']['sha256']for z in rr),'restore metadata identity')
 need(archive['archive_ref']['path'].startswith('/root/share/mnt164/'),'true164 archive metadata')
 need(len(s['expected_effective_options'])==283,'exact283 frozen options')
 gs=group_summary(c);ro=gs['EPL2ROV1|SUMMARY|']['totals'];ad=gs['EPL2ROP5|ADMISSION|']['totals']
 need(ro['accepted_ro']==ro['transactions']+ro['merges']==ro['responses'],'RO requester/response closure')
 need(all(int(row['live'])==0 for row in c['groups']['EPL2ROV1|SUMMARY|']['last_per_slice'].values()),'RO live0 final')
 ar=c['groups']['EPL2ROP5|ADMISSION|']['last_per_slice'];policy=int(s['expected_effective_options']['-gpgpu_ep_l2_ro_pressure_epoch'])
 need(all(int(x['policy_pressure_epoch'])==policy for x in ar.values()),'actual policy per slice')
 ids=[int(k)for k,row in ar.items()if int(row['active'])];ids.sort()
 need(sum(int(x['activations'])for x in ar.values())==ad['activations']==len(ids),'sticky activation count closes')
 need(all(int(x['activations'])in [0,1]for x in ar.values()),'one sticky activation maximum per slice')
 status='POLICY_DISABLED'if policy==0 else('NO_ACTIVATION'if not ids else'ACTIVATED_ON_EXACT_PRESSURE_GATE')
 out=dict(cohort=p['cohort'],mode=p['mode'],state=p['state'],cycles=p['cycles'],Source5=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],clock_domains=s['expected_effective_options']['-gpgpu_clock_domains'],geometry=s['geometry'],command_count=s['command_count'],kernel_count=p['kernel_count'],CTA=p['CTA'],instructions=p['instructions'],pressure=dict(policy=policy,status=status,active_slices=len(ids),applicable_slices=64,active_slice_ids=ids,activations=ad['activations'],native_before_activation=ad['native_before_activation'],joint_opportunity_denominator='NOT_EXPORTED'),groups=gs,evidence_refs=dict(spec=p['spec_ref'],accepted=p['accepted_point_ref'],closed_counters=p['closed_counter_summary_ref'],archive_receipt=p['archive_receipt_ref']),restore_count_reused_metadata=2,numeric_output=a.get('numeric_output','UNKNOWN'),_options=s['expected_effective_options'])
 return out
def matched_pair(a,b):
 need(a['mode']=='F_BASELINE'and b['mode']=='F_PRESSURE_EPOCH','exact two policy modes')
 for k in ['Source5','input_identity_sha256','clock_domains','geometry','command_count','kernel_count','CTA','instructions']:need(a[k]==b[k],'matched identity/background:'+k)
 oa,ob=a['_options'],b['_options'];need(set(oa)==set(ob)and len(oa)==283,'full same283 key set')
 diff={k:[oa[k],ob[k]]for k in oa if oa[k]!=ob[k]}
 need(diff=={'-gpgpu_ep_l2_ro_pressure_epoch':['0','1']},'only intended policy difference')
 need(a['state']==b['state']=='CLOSED_ACCEPTED','only qualified complete pairs')
 saved=a['cycles']-b['cycles'];f=Fraction(saved,a['cycles'])
 return dict(saved_cycles=saved,reduction_percent=float(f*100),exact_reduction_fraction=dict(numerator=f.numerator,denominator=f.denominator),performance_sign='positive'if saved>0 else'zero'if saved==0 else'negative',only_option_difference=diff,reference_scope='SAME_SOURCE_SAME_INPUT_SAME_CLOCK_SAME_OTHER282_OPTIONS')
def main():
 up=read_meta(U/'PERFORMANCE_CURRENT.json');vp=read_meta(V/'PERFORMANCE_CURRENT.json')
 ua=read_meta(U/'FINAL_REQUIREMENT_COMPLETION_AUDIT.json');uc=read_meta(U/'FINAL_SCOPE_CLOSURE.json')
 va=read_meta(V/'FINAL_REQUIREMENT_COMPLETION_AUDIT.json');vc=read_meta(V/'FINAL_SCOPE_CLOSURE.json')
 ur=read_meta(U/'REMOTE_FINAL_CLOSEOUT_PUBLICATION_RECEIPT.json');vr=read_meta(V/'REMOTE_FINAL_CLOSEOUT_PUBLICATION_RECEIPT_V2.json')
 duplicate=read_meta(U/'DUPLICATE_COUNTER_SEMANTICS_REVIEW.json');cost=read_meta(COST)
 read_meta(U/'UMT1_FINAL_SCIENTIFIC_RESULTS_AND_CLOSEOUT.md')
 need(ur['head']==AUTHORITY and ur['status']=='REMOTE_EXACT_HEAD_AND_ALL_EXPORTED_GIT_BLOBS_VERIFIED','latest UMT1 published authority')
 need(ua['accepted']==ua['consumed']==4 and ua['Native_full_restores']==8 and ua['model_technical_failures']==0,'UMT final complete')
 need(all(row[1]=='CLOSED_COMPLETED'for row in uc['groups']),'UMT closed scopes')
 need(va['goal_complete_proven']is True and va['remaining_scope_count']==0,'V5 final scope complete')
 need(all(row[1]=='CLOSED_COMPLETED'for row in vc['groups']),'V5 closed scopes')
 sel={}
 for p in vp['points']:
  if p['group']=='B':sel.setdefault('Vector1700',{})[p['mode']]=point(p)
 for p in up['points']:sel.setdefault('Conv850'if p['group']=='CONV'else'Scan850',{})[p['mode']]=point(p)
 pairs={};checks=[];negative=[]
 expected={'Vector1700':(55925,45425,0),'Conv850':(335088,333789,61),'Scan850':(2224142,2212128,4)}
 for name,points in sel.items():
  a,b=points['F_BASELINE'],points['F_PRESSURE_EPOCH'];comparison=matched_pair(a,b)
  need((a['cycles'],b['cycles'],b['pressure']['active_slices'])==expected[name],'frozen expected performance/activation')
  need(a['Source5']==cost['source_identity'],'same implemented B1 Source5')
  # Deliberate finite comparison guards; these mutate in-memory fixtures only.
  for key in ['Source5','input_identity_sha256','clock_domains']:
   bad=copy.deepcopy(b);bad[key]='WRONG'
   try:matched_pair(a,bad)
   except AssertionError:negative.append(dict(pair=name,case='reject_'+key))
   else:raise AssertionError('comparison guard failed')
  bad=copy.deepcopy(b);bad['_options']['-gpgpu_ep_l2_tvd_clean']='0'
  try:matched_pair(a,bad)
  except AssertionError:negative.append(dict(pair=name,case='reject_extra_mechanism_change'))
  else:raise AssertionError('option guard failed')
  ra=a['groups']['EPL2ROV1|SUMMARY|']['totals'];rb=b['groups']['EPL2ROV1|SUMMARY|']['totals']
  change={k:dict(baseline=ra[k],policy=rb[k],delta=rb[k]-ra[k])for k in ['accepted_ro','transactions','merges','responses','lower_sectors','ro_bank_fill_ops','ro_bank_response_ops','detached','concurrent_duplicate_sectors']}
  resource_key='EPL2ROC1|RESOURCE|'
  if resource_key in a['groups']and resource_key in b['groups']:
   qa=a['groups'][resource_key]['totals']['query_count'];qb=b['groups'][resource_key]['totals']['query_count']
   query=dict(status='PUBLISHED_FINAL64_SUM',baseline=qa,policy=qb,reduction_percent=float(Fraction(qa-qb,qa)*100))
  else:query=dict(status='RO_QUERY_TOTAL_NOT_EXPORTED_IN_THIS_SMALL_V5_COLLECTOR',not_substituted_from_requester_count=True)
  interpretation='OVERHEAD_AVOIDANCE_WITH_NO_PRESSURE_ACTIVATION_NOT_ACTIVE_RO_BENEFIT'if name=='Vector1700'else'ACTUAL_TRIGGER_REACHED_SMALL_END_TO_END_POLICY_GAIN_NO_ISOLATED_POST_TRIGGER_CAUSAL_ATTRIBUTION'
  for p in points.values():p.pop('_options')
  pairs[name]=dict(points=points,comparison=comparison,interpretation=interpretation,RO_counter_changes=change,RO_query_count=query)
  checks.append(dict(pair=name,exact283_only_policy_diff=True,RO_population_closure=True,final64_totals_recomputed=True,matching_archive_restore_metadata=True))
 need(duplicate['observed_values']['CONV_F_BASELINE']==duplicate['observed_values']['CONV_F_PRESSURE_EPOCH']==1,'duplicate1 retained')
 for mode in ['F_BASELINE','F_PRESSURE_EPOCH']:need(pairs['Conv850']['points'][mode]['groups']['EPL2ROV1|SUMMARY|']['totals']['concurrent_duplicate_sectors']==1,'actual Conv counter unchanged')
 # Clock context never enters a combined matched reference or aggregate speedup.
 need(pairs['Vector1700']['points']['F_BASELINE']['clock_domains']!=pairs['Conv850']['points']['F_BASELINE']['clock_domains'],'distinct1700/850 backgrounds retained')
 result=dict(schema='EP_L2_RO_POLICY_THREE_INPUT_CONVERGENCE_V1',status='SMALL_PUBLISHED_METADATA_CONVERGENCE_COMPLETE',latest_authority=AUTHORITY,V5_authority_context=vr['head'],pairs=pairs,
  conclusions=dict(measured_policy_pairs=3,performance_sign_counts=dict(positive=3,negative=0,zero=0),negative_or_zero_performance_results_not_invented=True,
   no_activation_is_not_policy_disabled=True,activation_does_not_establish_active_RO_speedup=True,large_RO_query_reduction_is_not_critical_path_cycle_reduction=True,
   separate_clock_backgrounds_context_only=True,cross_background_geomean_or_pooled_speedup='NOT_COMPUTED',
   representative_population='Three selected existing inputs, not blind/general workload coverage',
   converge_current_direction=True,request_new_scientific_models_now=0),
  duplicate_counter_semantics=dict(observed_Conv_pair=[1,1],observed_Scan_pair=[0,0],observed_Vector_pair=[0,0],definition=duplicate['exact_definition'],pending_definition=duplicate['pending_mask_definition'],event_level_cause='UNKNOWN',simultaneous_outstanding_DRAM_duplicate='NOT_PROVEN',only_ready_draining_overlap='NOT_PROVEN',harmlessness_or_universal_ownership='NOT_PROVEN',do_not_relabel_one_as_zero=True,evidence_ref=INPUTS[str(U/'DUPLICATE_COUNTER_SEMANTICS_REVIEW.json')]),
  costs=dict(runtime_control_bits_per_slice=1,policy_configuration_select_bit=1,added_CAM_entries=0,added_directory_entries=0,added_Payload=0,added_Banks=0,added_query_ports=0,RO_original_query_cycles=1,original_finite_query_and_completion_constraints_retained=True,extra_OR_mux_and_state_update_cost='EXPLICIT; physical timing/PPA NOT_PROVEN',one_epoch_sticky_state_no_mid_epoch_clear=True,existing_whole_epoch_oracle_input_not_free_hardware=True,cost_contract_ref=INPUTS[str(COST)]),
  boundaries=['All RO/native/Tag/descriptor/Payload/sector/completion identities keep existing qualified scope; acceptance not universal proof','RO transactions are not unique addresses; native-before-activation plus RO accepted are not an exclusive all-candidate partition','Wait categories overlap; slice maxima are not simultaneous GPU maxima; lower issued bytes are not achieved DRAM bandwidth','Activation slice fraction is not the joint trigger opportunity rate','Vector1700 service-sensitive diagnostic is not real GPU calibration; do not substitute Source862 S/W/WV or850 results as matching references','Application NI NOT_MEASURED, B0/M0a not proven here, numeric output UNKNOWN, physical PPA NOT_PROVEN'],
  decisions=dict(retain='Existing one-bit conditional-RO candidate and complete positive/small/zero-activation evidence without changing defaults or historical results',stop_now=['Threshold/hysteresis sweeps','Frequency scans','More inputs only to accumulate activation/merge counts','Second full B2 query-overlap implementation without a concrete finite-port/cycle opportunity','Long Scan reruns merely because query count fell'],
   conditional_future_gate=['New realizable structure with explicit metadata/port/ticket/queue/clock cost','Bounded production CPU correctness/reachability for that actual change','Specific end-to-end performance opportunity, not a ratio target','New exact Source5 and same-Source/input/clock original-versus-new matched baseline','Independent precise user-approved scientific scope before complete models'],
   future_order_only_if_gate_met='Use Vector as short no-pressure overhead control and Conv as activated-pressure check; defer long Scan unless the new service structure predicts a relevant benefit. This is not an experiment request.'),
  execution=dict(new_models=0,Source_changes=0,Native_changes=0,budget_changes=0,dispatcher_changes=0,Git_changes=0,Trace_body_reads=0,raw_log_reads=0,old_CPU124_loader_parser_repeated=False))
 put('RO_STRATEGY_CONVERGENCE.json',result)
 put('FINITE_CALCULATION_CHECKS.json',dict(status='PASS',positive_pair_checks=checks,finite_negative_comparison_guards=negative,original_UMT_4of4_and_8_restores_reused=True,archive_receipts_checked=6,native_restore_records_checked=12,new_restores=0,published_counter_totals_recomputed_without_raw=True,raw_or_Trace_opened=False,old_qualification_tests_repeated=False))
 put('SMALL_EVIDENCE_INPUT_MANIFEST.json',dict(status='EXACT_SMALL_EVIDENCE_SHA_FROZEN',files=list(INPUTS.values()),total_bytes_read=sum(x['bytes']for x in INPUTS.values()),no_raw_or_Trace_refs_followed=True,archive_payload_not_read_or_rehashed=True))
 return result
if __name__=='__main__':
 x=main()
 print(json.dumps(dict(status=x['status'],pairs={k:v['comparison']for k,v in x['pairs'].items()},evidence_files=len(INPUTS),new_models=0)))
