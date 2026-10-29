#!/usr/bin/env python3
"""Bounded round-2 analysis: only cached compact evidence and fetched small historical metadata."""
from pathlib import Path
import json,csv,io,hashlib,datetime
from collections import defaultdict
R=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/observation_guided_20261029_v1')
D=R/'round2/agent_a'; D.mkdir(parents=True,exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()
def dump(name,x): (D/name).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def ref(p): p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':H(b)}
def table(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
a=json.loads((R/'agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json').read_text())
b=json.loads((R/'agent_b/WV_CANDIDATES.json').read_text())
selected=['bd0309df','f9f80028','140f6ed3','fc3a9062','cf8d1c4d','438eefd6']
rows=[]; provenance=[];endpoint_rows=[]
for prefix in selected:
 ar=next(x for x in a['rows'] if (x.get('input_identity_sha256') or '').startswith(prefix))
 br=next(x for x in b['measured_evidence'] if x['input_identity_sha256']==ar['input_identity_sha256'])
 S=br['modes']['S']; mode=br['reference_treatment'];F=br['modes'][mode]
 for e in ar['reference_endpoints']:
  assert e['source_identity']['core_source_commit']=='78f4b59e865b136eede74df74c44c210f5b4ca04'
  assert e['source_identity']['framework_source_commit']=='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
  assert e['source_identity']['binary_sha256']=='78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a'
  assert e['geometry']=={'line_bytes':128,'sets':32,'slices':64,'ways':8}
  assert e['observer']['B0']==e['observer']['M0a']==e['observer']['MS']=='1'
  provenance.append({k:e[k] for k in ['cohort','mode','source_identity','spec_ref','validation_ref','point_ref','archive_ref','geometry','observer']})
  endpoint_rows.append({'program':ar['program'],'input_sha':ar['input_identity_sha256'],'cohort':e['cohort'],'mode':e['mode'],'cycles':e['cycles'],'ordinary_MSHR':e['ordinary_MSHR'],'RO_M':e['RO_M'],'T':e['T']})
 sw,fw=S['W_counters'],F['W_counters']; fv=F['V_counters']; se=next(x for x in ar['reference_endpoints'] if x['mode']=='S');fe=next(x for x in ar['reference_endpoints'] if x['mode']==mode)
 if fw is None:
  fw=dict(fe['W']);fw['MS_bottleneck']=fw.get('head_reasons',{})
 fw=defaultdict(lambda:None,fw)
 def pct(x,y):return 100*(x/y-1) if x is not None and y else None
 def ms(w,key,k='distinct_requests_first_block'):return (w['MS_bottleneck'].get(key) or {}).get(k)
 def mean(w,key):
  q=w['MS_bottleneck'].get(key) or {};n=q.get('distinct_requests_first_block');return q['request_wait_cycle_sum']/n if n and q.get('unknown_while_unresolved')==0 else None
 row={'program':ar['program'],'input_sha':ar['input_identity_sha256'],'S_mode':'S','treatment_mode':mode,'S_cycles':S['cycles'],'treatment_cycles':F['cycles'],'cycle_delta':F['cycles']-S['cycles'],'cycle_change_pct':100*(F['cycles']/S['cycles']-1),'S_over_treatment':S['cycles']/F['cycles'],'S_logical_copy_ops':sw['logical_copy_reads']+sw['logical_copy_writes'],'treatment_logical_copy_ops':fw['logical_copy_reads']+fw['logical_copy_writes'],'S_bank_logical_ops':sw['bank_logical_ops'],'treatment_bank_logical_ops':fw['bank_logical_ops'],'bank_logical_ops_change_pct':pct(fw['bank_logical_ops'],sw['bank_logical_ops']),'S_bank_wait_accum':sw['bank_wait_cycles'],'treatment_bank_wait_accum':fw['bank_wait_cycles'],'bank_wait_accum_change_pct':pct(fw['bank_wait_cycles'],sw['bank_wait_cycles']),'S_WB_DATA_SPACE_firstUID':ms(sw,'WB_DATA_SPACE'),'treatment_WB_DATA_SPACE_firstUID':ms(fw,'WB_DATA_SPACE'),'S_sameaddrWB_firstUID':ms(sw,'SAME_ADDRESS_WB'),'treatment_sameaddrWB_firstUID':ms(fw,'SAME_ADDRESS_WB'),'S_sameaddrWB_firstreason_clear_mean':mean(sw,'SAME_ADDRESS_WB'),'treatment_sameaddrWB_firstreason_clear_mean':mean(fw,'SAME_ADDRESS_WB'),'S_WAD_FULL_firstUID':ms(sw,'WAD_FULL'),'treatment_WAD_FULL_firstUID':ms(fw,'WAD_FULL'),'S_WB_mean_over_sampled_slice_ticks':sw['wb_mean_over_slice_ticks'],'treatment_WB_mean_over_sampled_slice_ticks':fw['wb_mean_over_slice_ticks'],'S_WAD_peak_over_slices':sw['wad_max'],'treatment_WAD_peak_over_slices':fw['wad_max'],'S_WB_created':sw['wb_created'],'treatment_WB_created':fw['wb_created'],'actual_V_read_responses':fv['read_responses'],'actual_V_dirty_forward_responses':fv['dirty_forward_responses'],'V_retention_slot_ticks':fv['total_retention_slot_cycles'],'S_lineMSHR_peak_over_slices':se['ordinary_MSHR'].get('line_max_over_slices'),'treatment_lineMSHR_peak_over_slices':fe['ordinary_MSHR'].get('line_max_over_slices'),'S_lineMSHR_full_head_observations':se['ordinary_MSHR'].get('line_full_head_observations_sum'),'treatment_lineMSHR_full_head_observations':fe['ordinary_MSHR'].get('line_full_head_observations_sum'),'S_descriptor_peak_over_slices':se['ordinary_MSHR'].get('descriptor_max_over_slices'),'treatment_descriptor_peak_over_slices':fe['ordinary_MSHR'].get('descriptor_max_over_slices'),'attribution':'CONTROLLED_PACKAGE_DIFFERENCE; INDIVIDUAL_MECHANISMS_UNKNOWN'}
 rows.append(row)
table('POSITIVE_NEGATIVE_RESOURCE_COMPARISON.csv',rows)
dump('ACCEPTED_ENDPOINT_PROVENANCE.json',{'references':provenance,'original_caches':[ref(R/'agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json'),ref(R/'agent_b/WV_CANDIDATES.json')],'new_bundle_reads':0})
dump('SELECTED_M_T_COMPACT_REUSE.json',endpoint_rows)
# Materialise recovered connector content exactly; verify Git blob identity.
github=json.loads((D/'HISTORICAL_GITHUB_RECOVERY.json').read_text())
mapfiles={'0':('motivation','README.md'),'1':('motivation','motivation_summary.csv'),'2':('motivation','aggregation_manifest.json'),'3':('streaming','LANE_STREAMING_REUSE_LATEST.md'),'5':('motivation','SOURCE_MAP.md'),'7':('streaming','sector_reuse_summary.csv')}
for key,(family,fn) in mapfiles.items():
 q=github[key];payload=((D/'historical/streaming/LANE_STREAMING_REUSE_LATEST.md').read_bytes() if key=='3' else q['content'].encode());blob=hashlib.sha1(('blob '+str(len(payload))+'\0').encode()+payload).hexdigest();assert blob==q['sha'],(fn,blob,q['sha'])
 d=D/'historical'/family;d.mkdir(parents=True,exist_ok=True);(d/fn).write_bytes(payload)
mot=list(csv.DictReader(io.StringIO(github['1']['content'])))
sr=list(csv.DictReader(io.StringIO(github['7']['content'])))
stream_manifest=json.loads((D/'historical/streaming/aggregation_manifest.json').read_text())
historical=[]
for x in mot:
 y=next((z for z in sr if z['workload']==x['workload']),None)
 dist=sum(int(x[k]) for k in x if k.startswith('reuse_') and k!='reuse_instances')
 assert dist==int(x['reuse_instances'])
 assert int(x['wb_packets_created'])==int(x['wb_packets_lower_accepted']) and int(x['wb_active_at_snapshot'])==0
 hist={'historical_name':x['workload'],'Motivation_core':'2a6a31591bc42023e5997cca969e4b672efe0405','demand_references':int(x['eligible_demand_references']),'line_reuse_instances':int(x['reuse_instances']),'line_reuse_fraction':int(x['reuse_instances'])/int(x['eligible_demand_references']),'line_reuse_le32_share':sum(int(x[k]) for k in ['reuse_le8','reuse_9_16','reuse_17_32'])/int(x['reuse_instances']),'post_evictions':int(x['post_evictions']),'post_eviction_rerefs':int(x['post_eviction_rerefs']),'post_eviction_reref_per_recorded_eviction':int(x['post_eviction_rerefs'])/int(x['post_evictions']) if int(x['post_evictions']) else None,'post_eviction_distinct_stack_histogram':'NOT_IN_THIS_TABLE','sector_temporal_reuse_fraction':float(y['sector_temporal_reuse_fraction']) if y else None,'far_sector_gt1024_share_of_temporal_reuses':None if y is None or y['far_sector_reuse_share_gt1024']=='NA' else float(y['far_sector_reuse_share_gt1024']),'sector_reference_events':int(y['total_sector_reference_events']) if y else None,'sector_events_equals_Motivation_demand_total':int(y['total_sector_reference_events'])==int(x['eligible_demand_references']) if y else None,'same_run_identity':'DIFFERENT_RUNTIME_NOT_JOINED','current_Source78_input_match':'UNPROVEN_CONTENT_AND_ORDERED_COMMANDLIST'}
 historical.append(hist)
table('RECOVERED_HISTORICAL_REUSE_COMPARISON.csv',historical)
# Exact data closure and single-sector-total diagnostic. This is not a new acceptance gate.
for y in sr:
 assert sum(int(y[k]) for k in y if k.startswith('sector_reuse_'))==int(y['temporal_sector_reuse_instances'])
 assert int(y['new_sector_on_new_line_events'])+int(y['new_sector_on_seen_line_events'])+int(y['temporal_sector_reuse_instances'])==int(y['total_sector_reference_events'])
identity={'recovered_increment':['Motivation exact10-row CSV, post_eviction table and RAW_LOG_INDEX10','Streaming exact12-row sector summary and12-trace-path aggregation manifest','Exact historical branch publication heads and Git blob/SHA256 receipts'],'Motivation_publication_head':'11cbd5a79127ad2fedf9801969a656be73fead96','Streaming_publication_head':'cdab5765b65f6e1575d9c185de127a1c1c49dd70','current_input_join':'NOT_PROVEN','trace_path_identity_recovered':len(stream_manifest['inputs']),'Motivation_raw_log_checksums_recovered':len(mot),'missing':['Content-root/input SHA manifest of historical capture','Exact ordered commandlist and kernel identity binding for historical manifests','Independent final review/recency-tie closure for Streaming; latest remote is still PREFINAL'], 'current_Source78_policy':'Historical numbers not inserted into current feature rows or used to predict current capacity hit rates','effort_boundary':'Named tracked documents and two exact remote directories;bounded small GitHub contents files and connector fetches, no recursive Trace/raw body scan; no remote old result paths opened','raw_trace_or_models':0}
dump('HISTORICAL_IDENTITY_RECOVERY_STATUS.json',identity)
gaps=[
 {'priority':1,'question':'Does W-only help independently and does optional V help given W?','existing_answer':'S/F package or S/WV package only; no accepted W_ONLY','minimal_next_step':'B closes exact W_ONLY CPU/Host/mode qualification; reuse accepted baselines then proposed W_ONLY/WV controlled points','new_counter_required':'NO','new_full_start_authorised':0,'decision_changed':'Separate copy/allocation benefit from V retention and M/T interaction'},
 {'priority':2,'question':'Why Scan package slows while bank and WB-space aggregate counts improve?','existing_answer':'Same-address WB and MSHR blocking populations rise; downstream/critical-path correlation unresolved','minimal_next_step':'First project already-accepted small B0/C7E/lower/DRAM per-stage fields into same source and clock scopes; do not rescan raw','new_counter_required':'ONLY_IF_EXISTING_ACCEPTED_SMALL_FIELDS_INSUFFICIENT','new_full_start_authorised':0,'decision_changed':'Choose service bottleneck vs admission-order/retention policy before resource enlargement'},
 {'priority':3,'question':'Would service-aware optional reclaim preserve useful V entries?','existing_answer':'Actual service and retention area measured; no first-service/reclaim age distribution bykind','minimal_next_step':'After V package is independently useful, defaultOFF bounded served-at-reclaim and age counters by clean/WB_COMPLETE with exact eligible reclaim population; S/WV/F separate NI','new_counter_required':'CONDITIONAL_NOT_NOW','new_full_start_authorised':0,'decision_changed':'Choose reclaim policy rather than cap/queue scan'},
 {'priority':4,'question':'Can historical locality classify current exact inputs?','existing_answer':'10old line rows and12old sector rows recovered; historical raw SHA/path available','minimal_next_step':'Recover existing small input content/ordered-command manifest from original custodian/index only; do not rerun models or traces','new_counter_required':'NO','new_full_start_authorised':0,'decision_changed':'Enable defensible cross-era input binding; until then historical-only paper observation'},
 {'priority':5,'question':'Does T provide independent cycles gain at witnessed detach geometry?','existing_answer':'Actual detach witnesses and engineering P1 report exist; REF joint opportunity and causal gain unknown','minimal_next_step':'Main reviews D P1 influence first; C exact Conv16x8 F_MINUS_T/F causal design, only separately authorised later','new_counter_required':'NO_FOR_INITIAL_CYCLES_CONTROL; T_JOINT_IF_NEEDED','new_full_start_authorised':0,'decision_changed':'Avoid attributing S/F or Scan loss to T or D P1 without workload witness'}]
dump('MINIMAL_DECISION_CHANGING_GAPS.json',gaps)
table('MINIMAL_DECISION_CHANGING_GAPS.csv',gaps)
qa={'schema':'EP_OBSERVATION_A_ROUND2_QA_V1','checks':{'six_exact_inputs':len(rows)==6,'Source78_same_geometry_observer_checked':True,'no_new_bundle_reads':True,'Motivation10rows':len(mot)==10,'Streaming12rows':len(sr)==12,'Motivation_histogram_closure':True,'Motivation_WB_lifecycle_closure':True,'Streaming_sector_hist_and_class_closure':True,'connector_content_Git_blob_checked':True,'no_current_historical_name_only_join':True,'new_model_starts_zero':True},'test_kind':'Offline metadata and arithmetic checks; not GPU correctness, NI, protocol or performance test','new_CPU_protocol_tests':0,'new_scientific_starts':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
dump('ROUND2_OFFLINE_QA.json',qa)
print(json.dumps({'rows':rows,'historical':historical,'QA':qa},indent=2))
