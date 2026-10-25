"""Read only prior failed identities and prepare a distinct two-point scope."""
import pathlib,json,hashlib,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_lava_memory_v2';R1=F/'validation';REQ='DTC_AE_LAVAMEM_REPAIR_20261026_V2'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def main():
 points=[]
 for arm in ['CM','CH']:
  old='E2-AEREPAIR-ddb6806316876a85-'+arm+'-V1';sp=R1/'control/specs'/(old+'.json');s=read(sp);ip=R1/'control/qualification_ledger'/(old+'.INTENT.json');dp=ip.with_name(old+'.DONE.json');intent=read(ip);done=read(dp);assert done==read(P(intent['output'])/'NATIVE_EXIT.json') and done['uuid']==intent['uuid'] and (done['stop_reason'] or done['launcher_wait_returncode'])
  assert s['program']=='lavamd' and s['cell']==arm and s['limits']['max_process_tree_rss_bytes']==16*1024**3
  archive=R1/'control'/(old+'_ARCHIVE_RECEIPT.json');assert archive.exists(),'preserve and close prior16GiB failure before capacity-only new attempt'
  assert s['expected_options']['-trace']==[s['native_simulator_argv'][s['native_simulator_argv'].index('-trace')+1]]
  points.append({'cohort':'E2-AEREPAIR-LAVAMEM2-'+s['input_digest'][:16]+'-'+arm+'-V1','program':'lavamd','arm':arm,'input_digest':s['input_digest'],'prior_repair_cohort':old,'prior_repair_uuid':done['uuid'],'prior_frozen_spec_path':str(sp),'prior_frozen_spec_sha256':sha(sp),'prior_INTENT_path':str(ip),'prior_INTENT_sha256':sha(ip),'prior_DONE_path':str(dp),'prior_DONE_sha256':sha(dp),'prior_archive_receipt_path':str(archive),'prior_archive_receipt_sha256':sha(archive),'prior_hard_AS_RSS_cap_bytes':16*1024**3,'expected':s['expected'],'source_disposition':'SOURCE_KEEP','original_failure_refunded':False})
 o={'schema':'DTC_LAVAMEM_SEPARATE_FINITE_SCOPE_CANDIDATE_V2','request':REQ,'points':points,'finite_budget':2,'maximum_model_slots':2,'correctness_validation_only':True,'prior_request_modified':False,'original288_membership':False,'status':'CANDIDATE_NOT_REGISTERED_NOT_ACTIVATED','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'models_started':0}
 path=R/'control/LAVAMEM_SCOPE_CANDIDATE_V2.json'
 with path.open('x') as f:json.dump(o,f,sort_keys=True,indent=2);f.write('\n')
 print(json.dumps({'scope_path':str(path),'sha256':sha(path),'points':2,'models_started':0}))
if __name__=='__main__':main()
