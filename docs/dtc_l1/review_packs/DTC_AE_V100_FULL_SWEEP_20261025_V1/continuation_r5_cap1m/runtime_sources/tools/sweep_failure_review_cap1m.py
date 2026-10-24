"""Closed-failure evidence only. Never accepts performance or retries a model."""
import pathlib,json,hashlib,gzip,importlib.util,subprocess,datetime,collections,re
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def classify(cell):
 engine=load('closed_failure_exact_versioned_spec','sweep_native_cap1m.py');spec=engine.spec_for(cell);reg,_=engine.read_current_authority();q=reg['registered_future_requests'][engine.REQUEST];row=q['consumed'][cell]
 ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(ip);dp=ip.with_name(cell+'.DONE.json');done=read(dp);out=P(intent['output'])
 assert sha(ip)==row['intent_sha256'] and done==row['execution_receipt']==read(out/'NATIVE_EXIT.json') and done['uuid']==row['uuid']==intent['uuid'] and out==T/'DTC/run/results'/done['uuid']
 abort=done['launcher_wait_returncode']==1 and done['stop_reason']=='DTC_NATURAL_TELEMETRY_CLOSURE_MISSING'
 cap=done['launcher_wait_returncode']==-15 and done['stop_reason']=='DTC_TELEMETRY:MISSING_OR_STALE_PRODUCER';assert abort or cap,'not a reviewed closed failure signature'
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'model generation still live'
 launch=read(out/'NATIVE_LAUNCH.json');assert launch['argv'][-len(spec['native_simulator_argv']):]==spec['native_simulator_argv'] and spec['native_simulator_argv'][0] in pid['maps']
 for r in spec['runtime_files']:
  p=T/r['target'];assert sha(p)==r['sha256'] and str(p.resolve())==r['actual_realpath']
 for kind,commit in [('core',spec['core_commit']),('framework',spec['framework_commit'])]:
  repo=P(spec.get('source_worktrees',{}).get(kind,str(T/kind)));assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==commit and not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
 raw=out/'raw.log.gz';assert sha(raw)==done['raw_sha256'];h=hashlib.sha256();size=0;deadlock=False;sigabrt=False;natural=False;fw=False;core=False;examples=[];last_kernel=None
 with gzip.open(raw,'rb') as stream:
  for n,line in enumerate(stream,1):
   h.update(line);size+=len(line);fw=fw or spec['framework_commit'].encode() in line;core=core or spec['core_commit'][:7].encode() in line
   if b'ERROR ** deadlock detected:' in line:deadlock=True;examples.append({'line':n,'text':line.decode().strip()})
   if b'=== CRASH: SIGABRT (signal 6) ===' in line:sigabrt=True;examples.append({'line':n,'text':line.decode().strip()})
   if b'GPGPU-Sim: *** exit detected ***' in line:natural=True
   if line.startswith(b'Processing kernel '):last_kernel=line.decode().strip()
 assert h.hexdigest()==done['raw_uncompressed_sha256'] and size==done['raw_uncompressed_bytes'] and not natural and fw and core
 if abort:assert deadlock and sigabrt
 count=0;last=None;previous_completed=-1;previous_ns=0
 with gzip.open(out/'progress.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);count+=1;assert r['seq']==count and r['pid']==pid['pid'] and r['start_ticks']==pid['start_ticks'] and r['generation']==done['uuid'] and r['input']==spec['original_environment']['DTC_AG7_INPUT_SHA'] and r['roi']==spec['original_environment']['DTC_AG7_ROI_SHA']
   assert r['mono_ns']>previous_ns and r['completed']>=previous_completed and r['end']=='NONE';previous_ns=r['mono_ns'];previous_completed=r['completed'];last=r
 assert last and last['completed']<spec['expected']['instructions']
 decisions=[]
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line)
   if 'DTC_exact_original_policy' in r:
    d=r['DTC_exact_original_policy']['decision'];assert d['decision'] in ['CONTINUE','WARN'] and not d['stop_reasons'];decisions.append({'decision':d['decision'],'warnings':d['warnings'],'wall_seconds':d['profile']['wall_deadline_s']})
 assert decisions
 runtime=spec.get('operational_runtime_profile','ORIGINAL_CAP8192_WALL21600');source_cap=1048576 if runtime=='OBSERVABILITY_CAP1M_WALL90_V1' else 8192
 if cap:
  assert count==source_cap and last['seq']==source_cap and not deadlock and not sigabrt
  trace=(out/'actual_file_process_network.log').read_text();assert re.search(str(pid['pid'])+r' \+\+\+ killed by SIGTERM \+\+\+',trace)
  header=P(spec.get('source_worktrees',{}).get('framework',str(T/'framework')))/'gpu-simulator/ag7_policyb_progress.h';assert ('kMaximumRecords = '+str(source_cap)+';') in header.read_text() and 'sequence_ >= kMaximumRecords' in header.read_text()
 qual=T/'qualification'/spec['input_digest']/'QUALIFICATION.json';assert read(qual)['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'
 classification='CLOSED_OBSERVATIONAL_TELEMETRY_RECORD_CAP_UNACCEPTED' if cap else 'CLOSED_NATIVE_MODEL_DEADLOCK_UNACCEPTED'
 result={'schema':'DTC_VERSIONED_RUNTIME_CLOSED_FAILURE_CLASSIFICATION_V1','status':classification,'cohort':cell,'uuid':done['uuid'],'input_digest':spec['input_digest'],'program':spec['program'],'runtime_profile':runtime,'framework_commit':spec['framework_commit'],'binary_sha256':spec['binary_sha256'],'intent_sha256':sha(ip),'done_sha256':sha(dp),'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'raw_uncompressed_bytes':size,'progress_records':count,'last_progress':last,'record_limit':source_cap,'last_processing_kernel_diagnostic_only':last_kernel,'original_policy_decisions':decisions,'source_and_runtime_pins_rechecked':True,'body_qualification_sha256':sha(qual),'observed_crash_signature':examples,'root_cause':'Observational producer/receiver finite record ceiling reached;unchanged freshness guard stopped an incomplete input' if cap else 'Simulator deadlock/SIGABRT;precise source/input synchronization cause remains unresolved','scientific_acceptance':False,'accepted_cycles':None,'partial_cycles_accepted':False,'model_retries':0,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dest=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json')
 if dest.exists():
  saved=read(dest);assert all(saved[k]==v for k,v in result.items() if k!='verified_utc');return saved
 with dest.open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
 return result
if __name__=='__main__':
 import sys
 r=classify(sys.argv[1]);print(json.dumps({k:v for k,v in r.items() if k!='original_policy_decisions'},indent=2))
