"""Event-driven post-native-intake r19 analysis, not a second acceptance system.

No experiments/lease/config writes/polling. A future entry references a complete
Lane6 native packet and hash. Existing native qualification must run first; the
H0-only native adapter must not be bypassed to manufacture headroom qualification.
This tool rechecks current V2, exact regime/config identity and matched anchors.
"""
import argparse,csv,hashlib,importlib.util,json,sys,math
from pathlib import Path
sys.dont_write_bytecode=True
from regime_rules import verify_appended_contract,verify_effective_dump,interaction,require
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--received-index',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
R=args.repo.resolve();P=args.output_dir.resolve();require(not P.exists(),'Do not overwrite an observation');P.mkdir(parents=True)
OLD=R/'docs/ep_l2/review_packs/FT20261017_LANE6_R17_SAD_INTAKE_r1';spec=importlib.util.spec_from_file_location('r19_frozen_engine',OLD/'intake_engine.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine);engine.R=R
helper=engine.module('r19_bridge',OLD.with_name('FT20261016_LANE6_PAPER_PPA_r4')/'current_pair_intake.py');helper.live_head=engine.live_reader();api=helper.vendor_api();head=helper.live_head(R);engine.git('fetch','--no-tags','--no-recurse-submodules','origin',head)
read=lambda p:engine.git('show',head+':'+p);raw=read(api.MANIFEST);meta=json.loads(raw);state=api.bind_manifest(raw,{'kind':'FETCHED_GITHUB_BRANCH','publication_commit':head,'manifest_sha256':engine.sha(raw),'generation':meta['generation'],'revision':meta['revision']},read);context=helper.bridge(R,state)
H0=OLD.with_name('FT20261017_LANE6_R18_FIVE_PAIR_EN_V6_r1');anchors={};records=[];resources=[]
def resource_row(run,packetpath,regime):
 evidence=json.loads(packetpath.with_name('SAD_64_SLICE_EVIDENCE.json').read_text())[run['mode']]
 ft=evidence['summary'];app=evidence['application_cumulative'];require(set(ft)==set(app)=={str(i) for i in range(64)},'Resource slice closure missing')
 total=lambda rows,key:sum(int(v[key]) for v in rows.values())
 out={'workload':run['workload'],'mode':run['mode'],'regime':regime,'run_key':run['run_key'],'cycles':run['summary']['cycles']}
 for key in ['copy_lines','wb_created','wb_completed','wb_lower_accept','wbuf_full','pool_full','staging_lifetime','observed_cycles','wb_occupancy_sum']:out[key]=total(ft,key)
 for key in ['bank_logical_ops','bank_grants','bank_wait_cycles','c7d_wad_full_events','c7d_wad_hazard_events','c7d_wad_hazard_wait_cycles','c7d_l2_to_dram_full_block','c7d_dram_scheduler_full_block','c7e_dram_scheduler_causal_block','c7e_dram_issue_attempt','c7d_dram_credit_block','c7d_dram_returnq_block','c7d_dram_to_l2_full_block','c7e_dram_successful_read_bytes','c7e_dram_successful_write_bytes']:out[key]=total(app,key)
 out['WB_stage_mean_GPU_cycles']=out['staging_lifetime']/out['wb_lower_accept'] if out['wb_lower_accept'] else None
 out['mean_staged_slots_per_observed_slice_L2_cycle']=out['wb_occupancy_sum']/out['observed_cycles'] if out['observed_cycles'] else None
 out['WAD_lifetime_max_GPU_cycles']=max(int(x['c7d_wad_lifetime_max']) for x in app.values())
 out['lowerq_max_across_slices']=max(int(x['lowerq_max']) for x in app.values())
 n=out['c7e_dram_issue_attempt'];out['scheduler_full_attempt_fraction']=out['c7d_dram_scheduler_full_block']/n if n else None
 out['scheduler_causal_attempt_fraction']=out['c7e_dram_scheduler_causal_block']/n if n else None
 out['L2_to_DRAM_full_opportunity_fraction']=None # Matching frontend need counter is not emitted.
 out['WBUF_full_opportunity_fraction']=None
 out['WB_completed_per_native_GPU_cycle']=out['wb_completed']/out['cycles']
 out['DRAM_issued_bytes_per_native_GPU_cycle']=(out['c7e_dram_successful_read_bytes']+out['c7e_dram_successful_write_bytes'])/out['cycles']
 channels={};monotonic=['dram_cycles','scheduler_full_cycles','returnq_full_cycles','successful_read_bytes','successful_write_bytes','bandwidth_util_numerator_bytes','bandwidth_util_denominator_bytes']
 root=Path(run['original_result']['allocation']['result_directory'])
 for line in (root/'raw.log').open():
  if not line.startswith('EPL2DRAMV1|scope=application|'):continue
  values=dict(x.split('=',1) for x in line.strip().split('|')[1:]);cid=int(values['channel'])
  if cid in channels:require(all(int(values[k])>=int(channels[cid][k]) for k in monotonic),'DRAM application counters are not monotonic')
  channels[cid]=values
 require(set(channels)==set(range(32)),'Detailed DRAM channel coverage incomplete')
 sums=lambda k:sum(int(c[k]) for c in channels.values())
 require(sums('successful_read_bytes')==out['c7e_dram_successful_read_bytes'] and sums('successful_write_bytes')==out['c7e_dram_successful_write_bytes'],'32-channel/64-slice byte mismatch')
 out['DRAM_model_atom_utilization']=sums('bandwidth_util_numerator_bytes')/sums('bandwidth_util_denominator_bytes')
 out['DRAM_scheduler_full_channel_cycle_fraction']=sums('scheduler_full_cycles')/sums('dram_cycles')
 return out
for item in json.loads((H0/'PAPER_CURRENT_FIVE_PAIR_INTAKE.json').read_text())['intakes']:
 packet=json.loads((R/item['intake_directory']/'SAD_NATIVE_INTAKE.json').read_text())
 for run in packet['packet']['runs']:
  context.check_run(run);anchors[(run['workload'],run['mode'])]=run
  if run['workload'] in ('sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21'):
   directory=Path(run['original_result']['allocation']['result_directory']);require(engine.sha((directory/'raw.log').read_bytes())==run['raw_log_sha256'],'H0 raw hash changed');verify_effective_dump((directory/'raw.log').read_text(),'H0')
   records.append({'workload':run['workload'],'mode':run['mode'],'regime':'H0','run_key':run['run_key'],'runtime_config_sha256':run['identity']['runtime_config_sha256'],'cycles':run['summary']['cycles']})
   resources.append(resource_row(run,R/item['intake_directory']/'SAD_NATIVE_INTAKE.json','H0'))
input_index=json.loads(args.received_index.read_text());seen=set();interactions=[]
for entry in input_index['pairs']:
 require(entry['experiment_id']=='EPL2_DOWNSTREAM_HEADROOM_R19','Wrong diagnostic family')
 packetpath=R/entry['native_packet_path'];require(engine.sha(packetpath.read_bytes())==entry['native_packet_sha256'],'Native intake packet changed');packet=json.loads(packetpath.read_text());require('packet' in packet and len(packet['packet']['runs'])==2,'Full native intake required')
 nr=json.loads(packetpath.with_name('R19_NATIVE_RECEIPT.json').read_text())
 require(nr['status']=='PASS_COMPLETE_R19_NATIVE_CONDITION_INTAKE' and nr['native_packet_sha256']==entry['native_packet_sha256'],'Missing complete r19 native/envelope/semantic closure')
 require(nr['experiment_id']==entry['experiment_id'] and nr['regime']==entry['regime'],'Native receipt condition differs')
 if 'input_scope_binding_sha256' in nr:require(engine.sha(packetpath.with_name('INPUT_SCOPE_BINDING.json').read_bytes())==nr['input_scope_binding_sha256'],'Scope binding changed')
 for name,expected in nr['native_sidecar_sha256'].items():require(engine.sha(packetpath.with_name(name).read_bytes())==expected,'Native counter/identity sidecar changed')
 require(entry['regime'] in ('Q4','D4','D2','L25'),'Unsupported/unselected additional r19 condition')
 runs={r['mode']:r for r in packet['packet']['runs']};require(set(runs)=={'B16_BANKED','U_WB16'},'Incomplete matched modes')
 require(set(nr['run_keys'])=={r['run_key'] for r in runs.values()},'Native receipt run-key mismatch')
 workload=runs['B16_BANKED']['workload'];key=(workload,entry['regime']);require(key not in seen,'Duplicate condition pair');seen.add(key)
 require(workload in ('sad','vectorAdd_4M','convolutionSeparable','FWT_7_21'),'Not in initial diagnostic workload set')
 for mode,run in runs.items():
  require(run['workload']==workload,'Mixed workload pair');context.check_run(run);root=Path(run['original_result']['allocation']['result_directory']);require(engine.sha((root/'raw.log').read_bytes())==run['raw_log_sha256'],'Diagnostic raw changed')
  require(engine.sha((root/'accel-sim.out').read_bytes())==run['identity']['binary_sha256'],'Binary changed')
  for i,config in enumerate(run['original_result']['audit']['configs']):require(engine.sha((root/f'config-{i}.config').read_bytes())==config['sha256'],'Ordered config changed')
  verify_appended_contract(anchors[(workload,mode)],run,entry['regime'],root)
  records.append({'workload':workload,'mode':mode,'regime':entry['regime'],'run_key':run['run_key'],'runtime_config_sha256':run['identity']['runtime_config_sha256'],'cycles':run['summary']['cycles']})
  resources.append(resource_row(run,packetpath,entry['regime']))
 b0=anchors[(workload,'B16_BANKED')]['summary']['cycles'];u0=anchors[(workload,'U_WB16')]['summary']['cycles'];bh=runs['B16_BANKED']['summary']['cycles'];uh=runs['U_WB16']['summary']['cycles'];interactions.append({'workload':workload,'regime':entry['regime'],**interaction(b0,u0,bh,uh)})
known={r['run_key'] for r in anchors.values()};unconsumed=[{'run_key':r['run_key'],'identity':r['identity'],'workload':r['workload'],'mode':r['mode'],'status':'CURRENT_ACCEPTED_NOT_NATIVE_INGESTED'} for r in state['manifest']['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED' and r['run_key'] not in known and r['run_key'] not in {x['run_key'] for x in records}]
context.assert_fresh()
group={}
for regime in ('D4','Q4','D2','L25'):
 selected=[p for p in interactions if p['regime']==regime and p['workload'] in ('convolutionSeparable','FWT_7_21')];complete={p['workload'] for p in selected}=={'convolutionSeparable','FWT_7_21'} and len(selected)==2
 group[regime]={'predeclared_workloads':['convolutionSeparable','FWT_7_21'],'received_pairs':len(selected),'geomean_S':math.exp(math.fsum(math.log(p['S_h']) for p in selected)/2) if complete else None,'geomean_J':math.exp(math.fsum(math.log(p['J_h_over_H0']) for p in selected)/2) if complete else None}
with (P/'CONDITION_CYCLES.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
with (P/'CONDITION_RESOURCES.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(resources[0]),lineterminator='\n');w.writeheader();w.writerows(resources)
(P/'INTERACTIONS.json').write_text(json.dumps({'authority':state['binding'],'status':'NO_NEW_NATIVE_PAIRS' if not interactions else 'MATCHED_RECEIVED_PAIRS_ONLY','H0_main_geomean_preserved':json.loads((H0/'PAPER_CURRENT_FIVE_PAIR_INTAKE.json').read_text())['independent_geomean_B_over_U'],'diagnostic_pairs':interactions,'not_yet_native_ingested_current_rows':unconsumed,'diagnostic_group_summaries':group,'missing_values_zero_filled':False,'new_simulators':0},indent=2,sort_keys=True)+'\n')
(P/'APPLICATION_ACCEPTANCE.json').write_bytes(raw)
print(json.dumps({'authority':head,'generation':meta['generation'],'H0_rows_current':len(anchors),'received_diagnostic_pairs':len(interactions),'new_current_rows_requiring_native_intake':len(unconsumed)}))
