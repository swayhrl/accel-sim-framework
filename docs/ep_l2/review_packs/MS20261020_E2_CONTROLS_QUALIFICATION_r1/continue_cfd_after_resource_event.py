"""One bounded original-controller intake after a new real resource-recovery event.

No polling, DWT replay, matrix adoption, source change or budget amendment.
"""
from pathlib import Path
import json,sys,time,copy,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'));sys.path.insert(0,str(P))
import coordinator as c,runner,controller
from report_approved_controls import checkpoint
def read(p):return json.loads(Path(p).read_text())
def main():
 coord=c.Coordinator();s=coord.snapshot();plan=read(P/'APPROVED_CONTROLS/PREPARATION_PLAN.json');rows=plan['profiles'][2:]
 assert s['actual_starts']==28 and s['remaining_start_capacity']==12 and s['controller']['state']=='STOPPED' and s['uncertain_start_intents']==0
 assert s['full_system_matrix']['sha256']==plan['approved_matrix']['sha256'] and read(P/'APPROVED_CONTROLS/MATRIX_ADOPTION_RECEIPT.json')['status']=='ADOPTED'
 publication=read(P/'APPROVED_CONTROLS/CFD_CONTINUATION_READY_REMOTE_READBACK.json')['remote_commit']
 qp=P/'APPROVED_CONTROLS/CFD_ONLY_CONTINUATION_QUEUE.json'
 for path in [Path(__file__),P/'report_approved_controls.py',qp]:assert subprocess.check_output(['git','-C',str(ROOT),'show',publication+':'+str(path.relative_to(ROOT))])==path.read_bytes()
 assert all(not any(a['run_key']==c.run_key(read(row['spec']['path'])['identity']) for a in s['attempts']) for row in rows)
 data=read(c.SHARED/'RUN_REGISTRY.json');resources=c.local_resources();usage=c.output_usage();first=read(rows[0]['spec']['path']);data[c.FIELD]['target_simulators']=2
 # The first real gate precedes target/lease changes or heavy input inspection.
 try:c.resource_gate(data,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 except ValueError as error:
  checkpoint('CFD_CONTINUATION_RESOURCE_BLOCKED_NO_START')
  print(json.dumps(dict(status='RESOURCE_BLOCKED_NO_START',reason=str(error),actual_starts=28,resources=resources)),flush=True);return
 shadow=copy.deepcopy(data);shadow['runs']['E2_CFD_FORECAST_NOT_LEASE']=dict(status='RESERVED',host=s['host'],experiment_id=c.CAMPAIGN,cpu_units=1,memory_bytes=first['memory_bytes'],disk_growth_bytes=first['maximum_result_bytes'],monitor_reserve_bytes=2*c.GIB,result_directory=str(c.OUTPUT/'NONEXISTENT_CFD_FORECAST'),scan=False)
 slots=2;reason='Two original reservations pass'
 try:c.resource_gate(shadow,'simulation',1,first['memory_bytes'],first['maximum_result_bytes'],resources,usage)
 except ValueError as error:slots=1;reason=str(error)
 if slots==2:
  slots=1;reason='Two forecast reservations pass, but two observed shared-RAM floor stops justify conservative sequential CFD intake after recovery. Original floors/quotas unchanged; one failed run would leave the next unstarted.'
 audits=[]
 for row in rows:
  for key in ['spec','qualification','queue']:
   ref=row[key];assert c.digest(ref['path'])==ref['sha256']
  spec=read(row['spec']['path']);audit=runner.inspect(spec,coord);assert audit['expected_full_instructions']==row['expected_full_instructions'];audits.append(audit)
 with coord.locked() as (all_data,item):assert item['controller']['state']=='STOPPED' and item['actual_starts']==28;item['target_simulators']=slots
 ap=P/'APPROVED_CONTROLS/CFD_CONTINUATION_RESOURCE_ADMISSION.json';c.write_json(ap,dict(status='PASS',at_unix=time.time(),resources=resources,usage=usage,slots=slots,two_slot_reason=reason,audits=audits,no_DWT_retry=True))
 original=controller.roll_pairs
 def immediate(coord,requests):
  pairs=original(coord,requests)
  for pair in pairs:checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',pair)
  return pairs
 controller.roll_pairs=immediate
 checkpoint('CFD_CONTINUATION_QUALIFIED_ADMISSION',extra=[ap,qp])
 result=controller.step(coord,qp);rp=P/'APPROVED_CONTROLS/CFD_CONTINUATION_CONTROLLER_RESULT.json';c.write_json(rp,result)
 checkpoint('CFD_CONTINUATION_TERMINAL',extra=[rp])
 print(json.dumps(dict(status='CURRENT_ACCEPTED' if all(coord.snapshot()['accepted_pairs'].get(row['control_pair_id'],{}).get('status')=='CURRENT_ACCEPTED' for row in rows) else 'PRECISE_TERMINAL_REVIEW_REQUIRED_NO_REPLAY',result=result)),flush=True)
if __name__=='__main__':main()
