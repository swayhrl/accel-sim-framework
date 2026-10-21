"""Export exact accepted summary counters; no acceptance, raw scan or execution."""
from pathlib import Path
import argparse,hashlib,json,time
P=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def export(pair_id):
 assert pair_id in ('V4_FWT_MAIN61_RESTORE_S_F','V4_SGEMM_MAIN61_EXPLORATORY_S_F')
 artifact=P/'execution'/(pair_id+'_ACCEPTED_PAIR.json');a=json.loads(artifact.read_text());pair=a['accepted_pair'];assert pair['status']=='CURRENT_ACCEPTED'
 endpoints={}
 for side,entry in pair['endpoints'].items():
  path=Path(entry['path']);assert digest(path)==entry['sha256'];r=json.loads(path.read_text());s=r['summary'];n=r['native_exit_evidence']
  assert r['status']=='COMPLETE_VALID' and r['independent_acceptance']=='PASS' and r['complete_input_verified']
  assert n['exit_code']==n['wait_status']==0 and n['stop_reason'] is None and s['slices']==64 and s['hardware_drained']
  endpoints[side]={'attempt_id':r['attempt_id'],'profile':r['profile'],'receipt':entry,'identity':r['identity'],'qualification_id':r['qualification_id'],'source_identity':r['source_identity'],
   'cycles':s['cycles'],'instructions':s['instructions'],'slices':s['slices'],'mechanism_metrics':s['mechanism_metrics'],'source_map':s['source_map'],'structural_observations':s['structural_observations'],
   'closure':{k:s[k] for k in ('hardware_drained','live_descriptors','live_line_mshrs','live_wad','pending_lower_reads','pending_responses','pending_returns','payload_free','payload_capacity','transient_payloads','unique_requesters','responses','wb_created','wb_lower_accepted','wb_completed')},
   'requester_exact_once_audit':s['requester_exact_once_audit'],'workload_termination':s['workload_termination'],'native_exit_receipt':{'path':str(path.parent/'NATIVE_EXIT.json'),'sha256':r['native_exit_receipt_sha256']},'result_directory':str(path.parent)}
 out={'schema':'E2_ACCEPTED_PAIR_EXACT_MECHANISM_COUNTER_EXPORT_V1','pair_id':pair_id,'accepted_pair_artifact':{'path':str(artifact),'sha256':digest(artifact)},'exported_unix':time.time(),'scientific_acceptance_unchanged':True,'counter_provenance':'Exact summary.mechanism_metrics and closure fields in the SHA-bound accepted endpoint receipts; no new counter derivation or raw parsing.','endpoints':endpoints,
  'cohort':'ORIGINAL_MAIN61_FWT_RESTORATION' if 'FWT' in pair_id else 'INDEPENDENT_MAIN61_SGEMM_FROZEN_TRACE_EXPLORATION','claim_limits':['Retain interpretation_limits in each source metric group; zeros cannot supply missing coverage.','Empty certified RO admission does not measure actual workload RO opportunity.','No exclusive-stall/capacity-only/hardware/infinite/numerical-recapture claim; retain negative outcomes.','Do not merge SGEMM into original MAIN or either pair into new93a9 capacity cohort.']}
 path=P/'analysis_delivery'/(pair_id+'_EXACT_METRICS.json');path.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n');return path
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--pair-id',required=True);args=ap.parse_args();print(export(args.pair_id))
