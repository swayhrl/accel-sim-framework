#!/usr/bin/env python3
"""Exact3 private C8 availability review. Metadata only; never publishes a production overlay."""
import pathlib,json,hashlib,os,sys,time,types,copy,argparse,resource,stat,fcntl
sys.dont_write_bytecode=True
N=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1')
D=pathlib.Path(__file__).resolve().parent
CONFIG_SHA='c5a6099fe4a3ca29183405d4e3e163c22da0ca7368dac9a5a03482eba203ce6d'
SCOPE_SHA='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'
PRODUCER='AUTO161_C8_AVAILABILITY_REVIEW_ADAPTER_V1'
PROFILE='AUTO161_EXISTING_C8_AVAILABILITY_REVIEW_V1'
GATE='EXISTING_C8_AVAILABILITY_METADATA_REVIEW_CLOSED_V1'
MEMBERS={'TASK.json':'task','ASSET.json':'asset','EXECUTION.json':'execution','INPUT_CAPSULE_QUALIFICATION_V4R2.json':'capsule','INPUT_SNAPSHOT_PAIR_IDENTITY.json':'pair','COMMIT.json':'commit','MANIFEST.json':'manifest'}
def need(v,msg):
 if not v:raise ValueError(msg)
def canon(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
def secure(p):
 p=pathlib.Path(p);need(p.is_absolute()and '..'not in p.parts,'unsafe metadata path')
 for q in [p,*p.parents]:
  if q==N.parent:break
  need(not q.is_symlink(),'symlink metadata path')
 s=p.stat();need(stat.S_ISREG(s.st_mode)and s.st_size<=2*1024**2,'small regular metadata only')
 return p
def read_ref(ref):
 p=secure(ref['path']);b=p.read_bytes();need(len(b)==ref['bytes']and sha(b)==ref['sha256'],'closed metadata SHA/length mismatch');return b
def file_ref(p):
 p=secure(p);b=p.read_bytes();return {'path':str(p),'sha256':sha(b),'bytes':len(b)}
def write_json(p,o):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def load_config():
 p=D/'FROZEN_INPUTS.json';b=p.read_bytes();need(sha(b)==CONFIG_SHA,'frozen exact3 inputs changed');o=json.loads(b)
 need(o['scope_ref']['sha256']==SCOPE_SHA and len(o['rows'])==3,'exact3 authority')
 need(len({r['scope_row']['queue_id']for r in o['rows']})==3,'duplicate exact row')
 return o
def comparator(config):
 raw=read_ref(config['comparator_source_ref']);accept=json.loads(read_ref(config['comparator_Root_acceptance_ref']))
 need(accept['status']=='PASS_FOR_READONLY_GOAL_AUDIT_ONLY','Root pure comparator acceptance')
 mod=types.ModuleType('frozen_private_availability_comparator');exec(compile(raw,config['comparator_source_ref']['path'],'exec'),mod.__dict__);return mod
def validate_first_round(item):
 ack=json.loads(read_ref(item['first_round_ACK_ref']));execution=json.loads(read_ref(item['first_round_execution_ref']));result=json.loads(read_ref(item['first_round_result_ref']));row=item['scope_row']
 need(ack['queue_id']==result['queue_id']==row['queue_id']and ack['admission_sha256']==item['admission_sha256'],'first round exact identity')
 need(ack['stage']=='METADATA_IDENTITY_STATIC'and result['stage_execution_complete']is True,'real first round stage')
 need(ack['exact_trace_qualified']is False and ack['qualification_granted']is False,'first round overclaim')
 need(result['status']in ['HOLD','PASS']and result['checks']and all(x['passed']is True for x in result['checks']),'first round binding checks incomplete')
 need(result['frozen_row_sha256']==item['row_sha256']==digest(row)and result['scope_sha256']==SCOPE_SHA,'first round row/scope hash')
 need(execution['returncode']==0 and execution['ended_monotonic_ns']>execution['started_monotonic_ns'],'real closed CPU execution')
 need(ack['execution_ref']==item['first_round_execution_ref']and ack['result_ref']==item['first_round_result_ref'],'ACK closed receipt references')
 for k in ['process_start_ref','intent_ref','context_ref','stdout_ref','stderr_ref']:read_ref(ack[k])
 return ack,execution,result
def build_side(item,output):
 root=pathlib.Path(item['object_path']);need(root.name==item['existing_route']['asset_id'],'selected object identity')
 need(root.is_relative_to(pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/objects')),'unexpected object scope')
 side={'metadata_raw_utf8':{}};refs=[];readback=[]
 for name,key in MEMBERS.items():
  expected=item['existing_route']['member_refs'][name];raw=(secure(root/name)).read_bytes()
  need(sha(raw)==expected['sha256']and len(raw)==expected['bytes'],'current selected object metadata drift: '+name)
  target=output/'current_metadata'/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  refs.append(file_ref(target));side['metadata_raw_utf8'][name]=raw.decode();side[key]=json.loads(raw);readback.append({'current_object_path':str(root/name),'raw_sha256':sha(raw),'bytes':len(raw),'closed_copy_ref':refs[-1]})
 side['manifest_raw_utf8']=side['metadata_raw_utf8']['MANIFEST.json']
 return side,refs,readback
def validate_route(mod,left,right,expected_asset,row):
 need(right['asset']['asset_id']==right['commit']['asset_id']==expected_asset,'C8 asset/COMMIT mismatch')
 need(right['task']['binary_sha256']==row['binary_sha256']and right['task']['argv']==row['argv'],'selected C8 workload identity')
 result=mod.compare(left,right)
 need(result['availability_route']=='WORKLOAD_AVAILABILITY_ROUTE_ONLY_NO_HISTORICAL_EQUIVALENCE','metadata comparator did not establish availability route')
 need(result['declared_workload_identity']['equal']is True,'declared workload differs')
 need(result['actual_capture_profile']['right']['valid']is True and result['actual_capture_profile']['right']['full_capture_evidence']is True,'C8 profile not closed')
 need(result['observed_input_bytes']['right']['valid']is True,'C8 supported input proof not closed')
 need(result['historical_equivalence']is False and result['observed_input_bytes']['equal_observed_supported_scope_only']is False and result['actual_capture_profile']['equal']is False,'historical input/profile equivalence forbidden')
 need(result['consumer_acceptance']is False and result['science_acceptance']is False,'qualification promotion forbidden')
 return result
def routing_row(item,right,result,refs,comparison_ref):
 row=item['scope_row'];profile=result['actual_capture_profile']['right']['profile'];observed=result['observed_input_bytes']['right'];objects=item['object_path']
 return {'queue_id':row['queue_id'],'frozen_row_sha256':item['row_sha256'],'selection_relation':'PRIVATE_EXISTING_WORKLOAD_AVAILABILITY_ONLY_NO_HISTORICAL_ALIAS','selected_asset_id':right['asset']['asset_id'],'selected_object_path':objects,'selected_manifest_sha256':right['commit']['manifest_sha256'],'selected_actual_producer_sha256':profile['actual_producer_sha256'],'selected_capture_profile':profile,'selected_supported_source_input_scope':observed,'selected_trace_entry_path':objects+'/'+right['asset']['full_application']['commandlist'],'trace_entry_from_manifest_only_not_body_rehashed':True,'metadata_closed_readback_refs':refs,'comparison_ref':comparison_ref,'historical_queue_status':row['historical_queue_status'],'historical_queue_mutated':False,'old_actual_input_equal':False,'old_actual_capture_profile_equal':False,'historical_equivalence':False,'consumer_qualified':False,'native_qualified':False,'timing_qualified':False,'science_qualified':False,'qualification_granted':False,'source_keep':True,'release_bytes':0,'numerical_limitations_preserved':right['asset'].get('numerical_qualification_limitations'),'next_stage':'WAIT_SOURCE_RUNTIME_ADAPTER','requires_Root_registration':True}
def install_boundary(run,config):
 current={str(pathlib.Path(r['object_path'])/name)for r in config['rows']for name in MEMBERS}
 def hook(event,args):
  if event in ['subprocess.Popen','os.system','os.exec','socket.__new__','socket.connect','ctypes.dlopen']:raise ValueError('metadata-only prohibited '+event)
  if event=='open':
   path,mode,flags=args
   if isinstance(path,int):return
   p=pathlib.Path(os.fsdecode(path));need('..'not in p.parts,'path traversal')
   resolved=p.absolute().resolve(strict=False);writing=(isinstance(mode,str)and any(x in mode for x in 'wax+'))or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
   if writing:need(resolved==run or run in resolved.parents,'write outside private run')
   else:need((resolved==N or N in resolved.parents)and resolved.suffix.lower()in ['.json','.py','.log']or str(p)in ['/proc/self/stat','/proc/sys/kernel/random/boot_id']or str(resolved)in current,'nonmetadata read prohibited')
  elif event in ['os.mkdir','os.remove','os.rmdir','os.chmod','os.chown','os.utime']:
   p=pathlib.Path(args[0]).absolute().resolve(strict=False);need(p==run or run in p.parents,'mutation outside private run')
  elif event in ['os.rename','os.link','os.symlink']:raise ValueError('metadata review uses no rename/link operations')
 sys.addaudithook(hook)
def run():
 config=load_config();scope=json.loads(read_ref(config['scope_ref']));audit=json.loads(read_ref(config['first_round_Root_audit_ref']))
 need(audit['status']=='ACCEPTED_REAL_CPU_EXECUTION_COVERAGE_NOT_TRACE_QUALIFICATION'and audit['scope_sha256']==SCOPE_SHA and audit['real_CPU_execution_covered_ids']==161 and audit['trace_qualified']==0 and not audit['errors'],'independent first-round acceptance missing')
 held=(D/'PRIVATE_FAMILY_REVIEW.lock').open('a');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
 run=D/'runs'/('run_'+str(time.time_ns()));run.mkdir(parents=True,exist_ok=False)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(60,61));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));os.nice(19)
 cpus=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpus[0]})
 install_boundary(run,config);mod=comparator(config);started=time.time();cpu=time.process_time();catalog=[];artifact_refs=[]
 source_ref=file_ref(__file__);config_ref=file_ref(D/'FROZEN_INPUTS.json')
 for item in config['rows']:
  row=item['scope_row'];need(scope['rows'][item['row_index']]==row and row['next_step']=='READONLY_EXISTING_WORKLOAD_AVAILABILITY_ROUTE_REVIEW_NO_HISTORICAL_ALIAS','exact3 scope drift')
  validate_first_round(item);projection=json.loads(read_ref(item['projection_ref']));need(projection['scope_row']==row,'projection binding')
  job=json.loads(read_ref(item['job_snapshot_ref']));need(job['task']['binary_sha256']==row['binary_sha256']and job['task']['argv']==row['argv'],'legacy job binding')
  output=run/row['queue_id'];output.mkdir()
  right,metadata_refs,readback=build_side(item,output)
  result=validate_route(mod,{'task':job['task'],'old_hold_status':row['historical_queue_status']},right,item['existing_route']['asset_id'],row)
  comparison=output/'COMPARATOR_REEXECUTED.json';write_json(comparison,result);comparison_ref=file_ref(comparison)
  route=routing_row(item,right,result,metadata_refs,comparison_ref);write_json(output/'CURRENT_ROUTING_ROW_CANDIDATE.json',route)
  receipt={'schema':'EXACT3_C8_AVAILABILITY_REVIEW_RECEIPT_V1','queue_id':row['queue_id'],'row_sha256':item['row_sha256'],'status':'PASS_CLOSED_METADATA_AVAILABILITY_ONLY','source_ref':source_ref,'config_ref':config_ref,'first_round_ACK_ref':item['first_round_ACK_ref'],'first_round_execution_ref':item['first_round_execution_ref'],'first_round_result_ref':item['first_round_result_ref'],'Root_comparator_acceptance_ref':config['comparator_Root_acceptance_ref'],'comparator_source_ref':config['comparator_source_ref'],'comparator_result_ref':comparison_ref,'current_metadata_readback':readback,'historical_queue_mutated':False,'GPU_executions':0,'simulations':0,'trace_body_rehashed':False,'qualification_granted':False}
  write_json(output/'REVIEW_RECEIPT.json',receipt);rr=file_ref(output/'REVIEW_RECEIPT.json')
  artifact={'schema':'AUTO161_ARTIFACT_V1','producer_id':PRODUCER,'profile':PROFILE,'producer_source_sha256':source_ref['sha256'],'status':'PASS','target_queue_ids':[row['queue_id']],'family_keys':['EXISTING_C8_AVAILABILITY:'+row['binary_sha256']+':'+digest(row['argv'])],'row_bindings':{row['queue_id']:item['row_sha256']},'provided_gates':[GATE],'requires':[],'next_stage':'WAIT_SOURCE_RUNTIME_ADAPTER','evidence':[rr,comparison_ref,file_ref(output/'CURRENT_ROUTING_ROW_CANDIDATE.json'),*metadata_refs,item['first_round_ACK_ref'],item['first_round_execution_ref'],item['first_round_result_ref'],config['comparator_Root_acceptance_ref'],source_ref,config_ref],'qualification_granted':False,'gpu_executed':False,'simulation_executed':False,'historical_queue_mutated':False,'consumer_qualified':False,'native_qualified':False,'timing_qualified':False,'science_qualified':False,'trace_qualified':False,'historical_input_equivalence':False,'historical_profile_equivalence':False,'consumer_or_runtime_qualification_required_next':True}
  path=output/'AUTO161_ARTIFACT.json';write_json(path,artifact);artifact_refs.append(file_ref(path));catalog.append(route)
 final={'schema':'PRIVATE_EXACT3_CURRENT_ROUTING_CANDIDATE_V1','status':'CANDIDATE_ROOT_REVIEW_REQUIRED_NOT_PUBLIC_OVERLAY','rows':catalog,'artifact_refs':artifact_refs,'producer_source_ref':source_ref,'Root_registration_applied':False,'consumer_native_timing_science_qualified':False,'historical_queue_mutated':False}
 write_json(run/'CURRENT_ROUTING_CANDIDATE.json',final)
 process={'pid':os.getpid(),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'start_ticks':pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]}
 execution={'schema':'EXACT3_AVAILABILITY_CPU_EXECUTION_V1','status':'PASS','rows_reviewed':3,'process':process,'started_unix':started,'ended_unix':time.time(),'cpu_seconds':time.process_time()-cpu,'max_CPU_workers':1,'actual_comparator_calls':3,'actual_object_metadata_reopens':21,'trace_or_input_payload_body_reads':0,'source_ref':source_ref,'config_ref':config_ref,'catalog_ref':file_ref(run/'CURRENT_ROUTING_CANDIDATE.json'),'artifact_refs':artifact_refs,'qualification_granted':False,'registration_applied':False}
 write_json(run/'EXECUTION.json',execution);print(json.dumps({'status':'PASS','run':str(run),'catalog_ref':execution['catalog_ref'],'artifact_refs':artifact_refs}))
if __name__=='__main__':
 need(sys.argv[1:]==['--run'],'only finite --run');run()
