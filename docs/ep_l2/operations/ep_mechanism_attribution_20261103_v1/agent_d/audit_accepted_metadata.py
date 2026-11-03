#!/usr/bin/env python3
"""Independent bounded accepted-metadata audit. No raw/Trace, actor imports or writes outside agent_d."""
from pathlib import Path
import json,hashlib,copy,csv,datetime
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');E=J/'execution_v2_20261103_v1';R=J/'receipts/lane_o_v1r2_20261029/review';P=R/'docs/ep_l2/operations/ep_main_implementation_performance_v2_20261029_v1/chatgpt_review_20261103_v1';Q=J/'research/mechanism_attribution_20261103_v1/agent_d'
reads={};checks=[]
def read(p,expected=None):
 p=Path(p);b=p.read_bytes();assert len(b)<8*1024*1024, str(p)
 h=hashlib.sha256(b).hexdigest();reads[str(p)]={'path':str(p),'bytes':len(b),'sha256':h}
 if expected:assert h==expected,(str(p),h,expected)
 return json.loads(b)
def exact(r):return read(r['path'],r['sha256'])
def ck(name,value):
 checks.append({'check':name,'pass':bool(value)});assert value,name
summary=read(P/'COMPLETED_EIGHT_RESULTS.json')
points=[]
for x in summary['points']:
 a=exact(x['accepted_point_ref']);ck(a['cohort']+' snapshot copy',a==read(P/'evidence/accepted_points'/f"{a['cohort']}.json"));points.append((a,x))
for p in sorted((P/'evidence/reused_reference_points').glob('*.json')):points.append((read(p),None))
records=[];bundles={};specs={}
for a,x in points:
 c=a['cohort'];s=exact(a['spec_ref']);v=exact(a['validation_ref']);exact(a['done_ref']);
 ck(c+' Source5 consistency',a['source_identity']==s['source_identity']==v['source_identity'])
 ck(c+' input consistency',a['input_identity_sha256']==s['input_identity_sha256']==v['input_identity_sha256'])
 opts=v['application']['actual_options'];ck(c+' actual options equal frozen expected',opts==s['expected_effective_options'])
 ck(c+' full counters',all(a[k]==v[k] for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']))
 ck(c+' complete hardware drain',a['hardware_drained'] and v['model']['hardware_drained'])
 ck(c+' input binding SHA',exact(s['input_binding_ref']) is not None)
 arch=exact(x['archive_receipt_ref']) if x else read(J/'cases'/c/'control/ARCHIVE_RECEIPT.json')
 ck(c+' true164 two restores',arch['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and len(arch['native_restores'])==2 and all(z['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' for z in arch['native_restores']) and arch['archive_ref']['path'].startswith('/root/share/mnt164/'))
 if x:ck(c+' terminal accepted',x['state']=='CLOSED_ACCEPTED' and x['controller_state']['status']=='CLOSED_ACCEPTED')
 ck(c+' accepted pending is preserved chronological stage',a['archive_status']=='PENDING_MANDATORY_ARCHIVE_CLOSURE')
 row={'cohort':c,'mode':a['mode'],'input_identity_sha256':a['input_identity_sha256'],'source_identity':a['source_identity'],'geometry':v.get('actual_tag_geometry',s.get('geometry')),'options_count':len(opts),'dram_latency':opts['-dram_latency'],'cycles':a['cycles'],'instructions':a['instructions'],'CTA':a['CTA'],'kernel_count':a['kernel_count'],'observer_env':s['observer_env'],'archive_status':arch['status'],'archive_ref':arch['archive_ref'],'spec_ref':a['spec_ref'],'validation_ref':a['validation_ref'],'accepted_early_archive_pending':True,'numeric_output':a['numeric_output']}
 records.append(row);bundles[c]=v;specs[c]=s
ck('population 8 new + 4 reused',len(records)==12 and sum(x is not None for a,x in points)==8)
trows=[r for r in records if 'T3_CONV16X8' in r['cohort']]
ck('all six T points same Source5',len({json.dumps(r['source_identity'],sort_keys=True) for r in trows})==1)
ck('T 283 actual options / 16x8 geometry',all(r['options_count']==283 and r['geometry']=={'line_bytes':128,'sets':16,'slices':64,'ways':8} and r['dram_latency']=='100' for r in trows))
ck('W all6 Source78 / 282 options /32x8',all(r['options_count']==282 and r['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04' and r['geometry']=={'line_bytes':128,'sets':32,'slices':64,'ways':8} and r['dram_latency']=='100' for r in records if r not in trows))
def projection(v):
 m=copy.deepcopy(v['model']);m.pop('raw_log_sha256');a=v['application'];return {**{k:v[k] for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']},'model':m,'application':{k:a[k] for k in ['actual_options','ordered_kernel_catalog','application_scopes']}}
nis=[]
for arm in 'ABC':
 off=next(c for c in bundles if 'T3_CONV16X8_'+arm in c and '_OFF_' in c);on=off.replace('_OFF_','_ON_');a=specs[off];b=specs[on]
 pair=read(P/'evidence/NI_RESULTS'/f'{off}.json');ck(off+' independent compact NI',projection(bundles[off])==projection(bundles[on]))
 ck(off+' NI source/input/mode exact',all(a[k]==b[k] for k in ['source_identity','input_identity_sha256','geometry','expected_effective_options','mode','T','M','ordinary_ro_tag_relief','input_binding_ref','ro_qualification_ref','binary_path','static_library_path']))
 delta={k:[a['observer_env'].get(k),b['observer_env'].get(k)] for k in set(a['observer_env'])|set(b['observer_env']) if a['observer_env'].get(k)!=b['observer_env'].get(k)}
 ck(off+' only declared diag delta',delta=={'EPL2_DETACH_DIAG':['0','1'],'EPL2_TAGPRESSURE_DIAG':['0','1']})
 ck(off+' published NI agrees',pair['status']=='PASS_ACCEPTED_SAME_ARM_COMPACT_SEMANTICS' and all(pair['equal'].values()))
 nis.append({'arm':arm,'OFF':off,'ON':on,'recomputed_equal':True,'changed_observer_env':delta,'scope':'same-arm compact semantics only; no ordered trace, strict demand-unique or numeric-output proof'})
# Actual options arm deltas; no expected-only identity shortcut.
base=next(c for c in bundles if 'T3_CONV16X8_A_'in c and '_OFF_'in c);deltas={}
for arm in 'BC':
 c=next(c for c in bundles if 'T3_CONV16X8_'+arm in c and '_OFF_'in c)
 aa=bundles[base]['application']['actual_options'];bb=bundles[c]['application']['actual_options'];deltas[arm]={k:[aa.get(k),bb.get(k)] for k in set(aa)|set(bb) if aa.get(k)!=bb.get(k)}
wdeltas={}
for program in ['GEMM','FASTWALSHTRANSFORM']:
 cs={r['mode']:r['cohort'] for r in records if program in r['cohort']}
 for mode in ['S','WV_ZERO_RO']:
  aa=bundles[cs['W_ONLY']]['application']['actual_options'];bb=bundles[cs[mode]]['application']['actual_options'];wdeltas[program+' W_ONLY->'+mode]={k:[aa.get(k),bb.get(k)] for k in set(aa)|set(bb) if aa.get(k)!=bb.get(k)}
# Exact accepted ON diagnostic projections only, all populations retained as named.
funnel=[]
for arm in 'ABC':
 c=next(c for c in bundles if 'T3_CONV16X8_'+arm in c and '_ON_'in c);m=read(E/'control/MECHANISM_METRICS'/f'{c}.json');d=m['DETACH_DIAG_final_GLOBAL']['counters']
 ck(c+' diagnostic closure',m['DETACH_DIAG_final_GLOBAL']['closure_ok'] and not m['DETACH_DIAG_final_GLOBAL']['output_invalid'] and d['closure_errors']==0)
 ck(c+' actual detached retirement',d['detach_success']==d['detached_responses']==d['detached_retired'])
 ck(c+' immediate commit accounting',d['detach_success']==d['trigger_accepted_after_detach']+d['trigger_denied_after_detach']+d['trigger_exception_after_detach'])
 p1=m['P1_final_records_by_slice'];keys=['raw_reservation_fail','pressure_T_disabled','pressure_T_enabled','pressure_eligible','eligible_frontend_admitted','eligible_frontend_denied','eligible_capacity_consulted','eligible_capacity_not_consulted','raw_tag_fail_commit','relieve_calls','detach_success','trigger_accepted_after_detach','trigger_denied_after_detach','detached_responses','detached_retired','closure_errors']
 funnel.append({'arm':arm,'cohort':c,**{k:d[k] for k in keys},'ordinary_queries':sum(int(z['issued']) for z in p1.values()),'paid_slice_gpu_cycle_exposure':sum(int(z['paid_wait_gpu_cycles']) for z in p1.values()),'port_wait_attempts':sum(int(z['port_wait_attempts']) for z in p1.values()),'later_UID_completion_chain':m['later_UID_completion_chain'],'strict_demand_unique_NEW':m['strict_demand_unique_NEW']})
old=read(J/'research/observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json');ret=[]
for program in ['stencil','scan']:
 r=next(r for r in old['rows'] if r['program']==program);a=next(a for a in r['reference_endpoints'] if a['mode']=='F');v=a['V']['metrics'];ck(program+' total retention partition',v['total_retention_slot_cycles']==v['clean_retention_slot_cycles']+v['retention_slot_cycles']);ret.append({'program':program,'input':r['input_identity_sha256'],'read_responses':v['read_responses'],'clean':v['clean_retention_slot_cycles'],'extra_inflight_and_complete':v['retention_slot_cycles'],'total':v['total_retention_slot_cycles'],'response_per_total':v['read_responses']/v['total_retention_slot_cycles']})
report={'schema':'EP_INDEPENDENT_ACCEPTED_EVIDENCE_AUDIT_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_BOUNDED_IDENTITY_ARITHMETIC_AND_COMPACT_NI_AUDIT','new_model_starts':0,'raw_and_Trace_reads':0,'manuscript':'MANUSCRIPT_NOT_SUPPLIED','records':records,'T_actual_option_deltas_from_A':deltas,'W_actual_option_deltas_from_W':wdeltas,'NI_recomputed':nis,'T_diagnostic_audit':funnel,'historical_total_retention_audit':ret,'historical_stencil_over_scan_service_density_ratio':ret[0]['response_per_total']/ret[1]['response_per_total'],'checks':checks,'read_receipts':list(reads.values()),'bounded_metadata_bytes_read':sum(r['bytes'] for r in reads.values()),'not_claimed':['new protocol CPU tests','ordered request trace NI','numerical functional correctness','PPA or RTL timing closure','full current ISCAS manuscript audit','fresh independent archive restoration or full archive rehash']}
(Q/'INDEPENDENT_RECOMPUTATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'points':len(records),'bytes':report['bounded_metadata_bytes_read'],'T_deltas':deltas,'W_deltas':wdeltas,'retention_ratio':report['historical_stencil_over_scan_service_density_ratio']}))
