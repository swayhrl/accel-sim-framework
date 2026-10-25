"""Preserve original failure review; separately classify exact outer RAM STOP."""
import pathlib,json,hashlib,gzip,importlib.util,datetime,re
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def classify(cell):
 ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');i=read(ip);out=P(i['output']);done=read(out/'NATIVE_EXIT.json')
 if done['stop_reason']!='MEMORY_HEADROOM':return load('unchanged_failure_classifier','sweep_failure_review_cap1m.py').classify(cell)
 n=load('memory_STOP_identity_engine','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];s=n.spec_for(cell);row=q['consumed'][cell];dp=ip.with_name(cell+'.DONE.json')
 assert done==read(dp)==row['execution_receipt'] and done['uuid']==i['uuid']==row['uuid'] and sha(ip)==row['intent_sha256'] and done['launcher_wait_returncode']==-15
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks']
 launch=read(out/'NATIVE_LAUNCH.json');assert launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'] and s['native_simulator_argv'][0] in pid['maps']
 assert sha(out/'raw.log.gz')==done['raw_sha256'];h=hashlib.sha256();size=0;natural=False;fw=False;core=False
 with gzip.open(out/'raw.log.gz','rb') as f:
  for line in f:
   h.update(line);size+=len(line);natural=natural or b'GPGPU-Sim: *** exit detected ***' in line;fw=fw or s['framework_commit'].encode() in line;core=core or s['core_commit'][:7].encode() in line
 assert not natural and fw and core and h.hexdigest()==done['raw_uncompressed_sha256'] and size==done['raw_uncompressed_bytes']
 progress=[]
 with gzip.open(out/'progress.jsonl.gz','rt') as f:
  for line in f:
   p=json.loads(line);assert p['seq']==len(progress)+1 and p['pid']==pid['pid'] and p['start_ticks']==pid['start_ticks'] and p['generation']==done['uuid'] and p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA'] and p['end']=='NONE'
   if progress:assert p['mono_ns']>progress[-1]['mono_ns'] and p['completed']>=progress[-1]['completed']
   progress.append(p)
 assert progress and progress[-1]['completed']<s['expected']['instructions']
 bad=[];samples=0
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
  for line in f:
   p=json.loads(line)
   if 'physical_RAM_pass' in p:
    samples+=1
    if not p['physical_RAM_pass']:bad.append(p)
 assert samples and bad and all(r['physical_disk_pass'] for r in bad)
 assert re.search(str(pid['pid'])+r' \+\+\+ killed by SIGTERM \+\+\+',(out/'actual_file_process_network.log').read_text())
 for r in s['runtime_files']:assert sha(T/r['target'])==r['sha256']
 result={'schema':'DTC_OUTER_MEMORY_HEADROOM_STOP_CLASSIFICATION_V1','status':'CLOSED_OUTER_MEMORY_HEADROOM_GUARD_STOP_UNACCEPTED','cohort':cell,'uuid':done['uuid'],'input_digest':s['input_digest'],'program':s['program'],'runtime_profile':s.get('operational_runtime_profile'),'framework_commit':s['framework_commit'],'binary_sha256':s['binary_sha256'],'intent_sha256':sha(ip),'done_sha256':sha(dp),'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'raw_uncompressed_bytes':size,'progress_records':len(progress),'last_progress':progress[-1],'negative_outer_RAM_samples':bad,'resource_sample_count':samples,'classifier_source_sha256':sha(__file__),'root_cause':'Captured outer physical_RAM_pass false caused MEMORY_HEADROOM SIGTERM;partial simulated cycles are unaccepted. Shared cached pages and outstanding reservations are retained in the original sample,not attributed exclusively to this model.','scientific_acceptance':False,'accepted_cycles':None,'model_retries':0,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dest=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json')
 if dest.exists():
  saved=read(dest);assert all(saved[k]==v for k,v in result.items() if k!='verified_utc');return saved
 with dest.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 return result
