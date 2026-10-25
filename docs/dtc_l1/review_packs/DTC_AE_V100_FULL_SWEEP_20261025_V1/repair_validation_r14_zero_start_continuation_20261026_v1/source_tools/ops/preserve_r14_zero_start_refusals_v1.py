"""Preserve R13 pre-INTENT refusal JSONs without moving or editing originals."""
import pathlib,json,hashlib,fcntl,datetime
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');V=R/'validation';PRE=R/'ops/r14_handoff_preimages_v1';D=PRE/'R13_zero_start_results';D.mkdir(exist_ok=False);REQ='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();scope=json.loads((V/'control/REPAIR_SCOPE_CANDIDATE_V2.json').read_bytes());cells=[x['cohort']for x in scope['points']];assert len(cells)==23
with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as f:
 fcntl.flock(f,fcntl.LOCK_SH);body=(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes();q=json.loads(body)['registered_future_requests'][REQ];assert not q['consumed']and q['remaining']==q['budget']==23
ledger=N/'control/science_authority/requests'/REQ;assert not list(ledger.glob('*.INTENT.json'))
rows=[]
for c in cells:
 src=V/'analysis'/(c+'.RESULT.json');body=src.read_bytes();r=json.loads(body);assert not r.get('partial_cycles_accepted',False);assert '_SPEC.json'in str(r)and('No such file or directory'in str(r)or'FileNotFoundError'in str(r)),(c,r);dest=D/src.name
 with dest.open('xb')as f:f.write(body)
 assert h(dest)==h(src);rows.append({'cohort':c,'source':str(src),'preserved_path':str(dest),'bytes':len(body),'sha256':h(dest),'state':r.get('state'),'error':r.get('error')})
launches=list((V/'DTC/run/results').glob('*/NATIVE_LAUNCH.json'));pidfiles=list((V/'DTC/run/results').glob('*/NATIVE_SIMULATOR_PID_AND_MAPS.json'));assert not launches and not pidfiles
out={'schema':'R13_ZERO_START_REFUSALS_PRESERVED_FOR_R14_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':REQ,'repair_budget':23,'repair_remaining':23,'repair_consumed':0,'repair_INTENT_count':0,'repair_NATIVE_LAUNCH_count':len(launches),'repair_model_PID_receipt_count':len(pidfiles),'preserved_result_count':len(rows),'results':rows,'originals_moved_or_changed':False,'scientific_starts':0,'native_registry_or_entry_writes':False,'histories_refunded_or_cleared':False};p=PRE/'R13_ZERO_START_ERROR_FACTS_V1.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'23_ZERO_START_REFUSALS_PRESERVED','facts':str(p),'facts_sha256':h(p),'files':len(rows),'launches':len(launches),'PID_receipts':len(pidfiles)}))
