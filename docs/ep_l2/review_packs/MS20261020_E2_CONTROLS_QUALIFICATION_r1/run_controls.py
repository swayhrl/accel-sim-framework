"""Finite original-matrix queue feed through existing controller.step, with immediate publication."""
from pathlib import Path
import sys,json,time,copy,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner,controller
spec=__import__('importlib.util',fromlist=['']).spec_from_file_location('pub',P.parent/'MS20261020_E2_TAKEOVER_r1/publish.py')
pub=__import__('importlib.util',fromlist=['']).module_from_spec(spec);spec.loader.exec_module(pub)
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def checkpoint(event,pair=None,extra=()):
 coord=c.Coordinator();s=coord.snapshot();data=read(c.SHARED/'RUN_REGISTRY.json');usage=c.output_usage();base=read(P/'BASELINE.json')
 buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']}
 assert buckets['contingency']==8 and s['t0_unix']==base['T0'] and usage['old_bytes']==base['output_usage']['old_bytes']
 paths=[];metrics={}
 for a in s['attempts'][20:]:
  if not a.get('receipt_path'):continue
  rp=Path(a['receipt_path']);assert c.digest(rp)==a['receipt_sha256'];r=read(rp);f=P/(a['attempt_id']+'_RUN_STATUS.json');f.write_bytes(rp.read_bytes());paths.append(f)
  for name in ['NATIVE_EXECUTION_READY.json','NATIVE_EXIT.json']:
   original=Path(a['result_directory'])/name
   if original.exists():
    if name=='NATIVE_EXIT.json':assert c.digest(original)==r['native_exit_receipt_sha256']
    f=P/(a['attempt_id']+'_'+name);f.write_bytes(original.read_bytes());paths.append(f)
 if pair:
  assert pair['status']=='CURRENT_ACCEPTED'
  for side,e in pair['endpoints'].items():
   assert c.digest(e['path'])==e['sha256'];r=read(e['path']);assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS'
   assert r['summary']['instructions']==714547200 and r['summary']['slices']==64 and runner.validate_summary(r['summary'],r['identity'])['status']=='PASS'
   coord.require_no_hold(s,r['qualification_id'])
   if e['attempt_id'] in [a['attempt_id'] for a in s['attempts'][20:]]:
    n=r['native_exit_evidence'];assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and n['native_process']==r['process']
   metrics[side]=dict(profile=r['profile'],labels=r['labels'],cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],result_directory=next(a['result_directory'] for a in s['attempts'] if a['attempt_id']==e['attempt_id']),receipt=e,mechanism_metrics=r['mechanism_metrics'])
  f=P/(pair['pair_id']+'_ACCEPTED_CONTROL.json');c.write_json(f,dict(accepted_control=pair,endpoints=metrics,interpretation='Fixed predeclared control, not a new MAIN S/F pair. S_COPY_FREE is a diagnostic copy-service counterfactual, not hardware P1 throughput or full-scheme speedup. Other ablations retain physical P1.'));paths.append(f)
 report=dict(schema='E2_ORIGINAL_CONV_CONTROL_CHECKPOINT_V1',event=event,at_unix=time.time(),source_identity=s['final_source_identity'],T0=s['t0_unix'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],maximum=40,budget_buckets=buckets,contingency_remaining=0,output_usage=usage,result_growth_since_control_baseline_bytes=usage['new_bytes']-base['output_usage']['new_bytes'],resources=c.local_resources(),controller=s['controller'],active_runs={k:v for k,v in data['runs'].items() if v['status'] in c.ACTIVE},active_leases={k:v for k,v in data['resource_leases'].items() if v['status'] in c.ACTIVE},accepted_main_pairs={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_MAIN_')},accepted_controls={k:v for k,v in s['accepted_pairs'].items() if v['status']=='CURRENT_ACCEPTED' and k.startswith('V2_CONTROL_')},scientific_holds=s['scientific_holds'],next_original_controls=[r['profile'] for r in read(P/'ADMISSION_PLAN.json')['profiles'] if r['control_pair_id'] not in s['accepted_pairs']],DWT_CFD_reallocation='PROPOSAL_ONLY_NO_MUTATION_NO_LAUNCH_WITHOUT_USER_APPROVAL',FWT_Vector_Btree_retries=False,start_deadline=c.START_DEADLINE,intake_deadline=c.INTAKE_DEADLINE)
 f=P/(event+'.json');c.write_json(f,report);paths.append(f)
 hand=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/e';c.write_json(hand/'RECEIPT.json',report)
 text='# Lane E2 — '+event+'\n\n'+f"Original174; originalT0={s['t0_unix']}; actual{s['actual_starts']}/40,remaining{s['remaining_start_capacity']},contingency8/8 consumed. main61/Core d010/Framework9dd unchanged. Controller {s['controller']['state']}; original unique registry/lock and maximum2.\n\n"
 text+='| Main S/F | S cycles | F cycles | S/F |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_main_pairs'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+='\n| Independently accepted control | Anchor cycles | Control cycles | Anchor/control |\n|---|---:|---:|---:|\n'
 for k,v in report['accepted_controls'].items():text+=f"| {k} | {v['cycles_left']} | {v['cycles_right']} | {v['ratio_left_over_right']:.9f} |\n"
 text+=f"\nNew results{usage['new_bytes']}B, old+new{usage['total_bytes']}B; growth since20-start control baseline{report['result_growth_since_control_baseline_bytes']}B.6/20GiB and5GiB+2GiB monitoring reserves unchanged.\n\nRemaining original qualified controls: "+','.join(report['next_original_controls'])+'. DWT/CFD four-cell revision stays proposal-only until explicit user approval, distinct E qualification and live capacity checks. FWT INCOMPLETE,Vector F RESOURCE_LIMIT/exit-15,Btree HOLD and all old receipts remain; no refunds,replay,newGoal,second controller or new migration. COPY_FREE remains diagnostic.\n'
 (hand/'STATUS.md').write_text(text);paths += [hand/'STATUS.md',hand/'RECEIPT.json',*extra]
 notice=None
 if pair:
  notice=dict(schema='E2_TO_D_INCREMENTAL_INDEPENDENT_CONTROL_V1',at_unix=time.time(),accepted_control=pair,endpoints=metrics,source_identity=s['final_source_identity'],actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],output_usage=usage,analysis_request='Analyze this exact predeclared independent control now. Preserve four MAIN S/F pairs,all labels and denominator; do not pool diagnostics into hardware results or sum overlapping request waits as GPU stall cycles.')
  nf=P/(pair['pair_id']+'_D_INCREMENTAL_NOTICE.json');c.write_json(nf,notice);paths.append(nf)
 rb=pub.publish('docs(ep-l2-e2): '+event,paths);c.write_json(P/(event+'_REMOTE_READBACK.json'),rb)
 if notice:
  notice['remote_publication']=rb['remote_commit']
  for channel in ['events','inbox']:c.write_json(c.HANDOFF/channel/('E2_TO_D_'+pair['pair_id']+'.json'),notice)
 print(json.dumps(dict(event=event,actual_starts=s['actual_starts'],remaining=s['remaining_start_capacity'],accepted_controls=list(report['accepted_controls']),output_usage=usage,remote_commit=rb['remote_commit'])),flush=True)
 return report

def main():
 coord=c.Coordinator();plan=read(P/'ADMISSION_PLAN.json');published=read(P/'PRELAUNCH_REMOTE_READBACK.json')['remote_commit']
 assert subprocess.check_output(['git','-C',str(ROOT),'show',published+':'+str(Path(__file__).relative_to(ROOT))])==Path(__file__).read_bytes()
 assert coord.snapshot()['controller']['state']=='STOPPED' and coord.snapshot()['actual_starts']==20
 clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(clientpath)
 for row in plan['profiles']:
  assert c.digest(row['qualification']['path'])==row['qualification']['sha256'] and c.digest(row['spec']['path'])==row['spec']['sha256']
  if not any(x['qualification_id']==row['qualification_id'] for x in client['current_qualifications']):client['current_qualifications'].append(dict(path=row['qualification']['path'],qualification_id=row['qualification_id'],qualification_sha256=row['qualification_id'],workload='convolutionSeparable',profile=row['profile']))
 client['terminal_adapter_qualified_scope']+=';CONV_EXACT_W_ONLY_F_MINUS_V_F_MINUS_R_S_COPY_FREE_WV_M_WV_T';c.write_json(clientpath,client);c.write_json(P/'CLIENT_CONV_CONTROLS_READY.json',client)
 original_roll=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original_roll(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 for batchno in range(3):
  rows=plan['profiles'][batchno*2:batchno*2+2];specs=[];pairs=[];audits=[]
  for row in rows:
   assert c.digest(row['queue']['path'])==row['queue']['sha256'];q=read(row['queue']['path']);spec=read(row['spec']['path']);audit=runner.inspect(spec,coord);assert not any(a['run_key']==audit['run_key'] for a in coord.snapshot()['attempts']);specs+=q['specs'];pairs+=q['pairs'];audits.append(dict(profile=row['profile'],input_and_identity=audit))
  data=read(c.SHARED/'RUN_REGISTRY.json');s=coord.snapshot();resources=c.local_resources();usage=c.output_usage();data[c.FIELD]['target_simulators']=2
  first=read(rows[0]['spec']['path']);c.resource_gate(data,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
  shadow=copy.deepcopy(data);shadow['runs']['E2_CONTROL_FORECAST_NOT_LEASE']=dict(status='RESERVED',host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=first['memory_bytes'],disk_growth_bytes=first['maximum_result_bytes'],monitor_reserve_bytes=2*c.GIB,result_directory=str(c.OUTPUT/'NONEXISTENT_CONTROL_FORECAST'),scan=False)
  slots=2;reason='Both original conservative reservations admitted'
  try:c.resource_gate(shadow,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
  except ValueError as error:slots=1;reason=str(error)
  with coord.locked() as (all_data,item):assert item['controller']['state']=='STOPPED';item['target_simulators']=slots
  qp=P/('BATCH_'+str(batchno+1)+'_QUEUE.json');c.write_json(qp,dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=plan['at_unix'],specs=specs,pairs=pairs))
  ap=P/('BATCH_'+str(batchno+1)+'_PRELAUNCH_AUDIT.json');c.write_json(ap,dict(status='PASS',at_unix=time.time(),slots=slots,two_slot_reason=reason,resources=resources,output_usage=usage,audits=audits,queue=ref(qp)))
  checkpoint('CONV_CONTROLS_BATCH_'+str(batchno+1)+'_QUALIFIED_ADMISSION',extra=[qp,ap,P/'CLIENT_CONV_CONTROLS_READY.json'])
  result=controller.step(coord,qp);rp=P/('BATCH_'+str(batchno+1)+'_CONTROLLER_RESULT.json');c.write_json(rp,result)
  accepted=all(coord.snapshot()['accepted_pairs'].get(r['control_pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for r in rows)
  checkpoint('CONV_CONTROLS_BATCH_'+str(batchno+1)+'_TERMINAL',extra=[rp])
  if not accepted:print('AFFECTED_BATCH_NEEDS_EXACT_REVIEW_NO_REPLAY',flush=True);return
 print('SIX_ORIGINAL_CONV_CONTROLS_ACCEPTED_NO_EXTRA_STARTS',flush=True)
if __name__=='__main__':main()
