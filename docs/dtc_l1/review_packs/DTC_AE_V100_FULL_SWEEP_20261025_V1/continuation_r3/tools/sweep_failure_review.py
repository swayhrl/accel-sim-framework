"""Narrow closed-failure evidence classifier. No simulation/retry/acceptance API."""
import pathlib,json,hashlib,gzip,importlib.util,subprocess,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def module(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def classify(cell):
 spec=read(T/'control'/(cell+'_SPEC.json'));intentfile=T/'control/qualification_ledger'/(cell+'.INTENT.json');intent=read(intentfile);donefile=intentfile.with_name(cell+'.DONE.json');done=read(donefile);out=P(intent['output'])
 assert out==T/'DTC/run/results'/intent['uuid'] and done==read(out/'NATIVE_EXIT.json') and done['uuid']==intent['uuid']
 assert done['launcher_wait_returncode']==1 and done['stop_reason']=='DTC_NATURAL_TELEMETRY_CLOSURE_MISSING'
 pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():assert int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=pid['start_ticks'],'failure process still alive'
 for row in spec['runtime_files']:
  p=T/row['target'];assert str(p.resolve())==row['actual_realpath'] and sha(p)==row['sha256'],'frozen runtime drift'
 for kind,commit in [('core',spec['core_commit']),('framework',spec['framework_commit'])]:
  assert subprocess.check_output(['git','-C',str(T/kind),'rev-parse','HEAD'],text=True).strip()==commit
  assert not subprocess.check_output(['git','-C',str(T/kind),'status','--porcelain'],text=True).strip()
 p=out/'raw.log.gz';assert sha(p)==done['raw_sha256'];h=hashlib.sha256();size=0;deadlock=False;abort=False;natural=False;excerpts=[]
 with gzip.open(p,'rb') as stream:
  for n,line in enumerate(stream,1):
   h.update(line);size+=len(line)
   if b'ERROR ** deadlock detected:' in line or b'DEADLOCK  shader cores no longer committing' in line:
    deadlock=True;excerpts.append({'line':n,'text':line.decode(errors='replace').strip()})
   if b'=== CRASH: SIGABRT (signal 6) ===' in line:abort=True;excerpts.append({'line':n,'text':line.decode().strip()})
   if b'GPGPU-Sim: *** exit detected ***' in line:natural=True
 assert h.hexdigest()==done['raw_uncompressed_sha256'] and size==done['raw_uncompressed_bytes'] and deadlock and abort and not natural,'not the reviewed native deadlock class'
 decisions=[]
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
  for line in f:
   row=json.loads(line);decision=row.get('DTC_exact_original_policy',{}).get('decision',{})
   if decision:assert decision['decision']=='CONTINUE' and not decision['stop_reasons'];decisions.append(decision['decision'])
 assert decisions,'missing original resource decisions'
 progress=[]
 with gzip.open(out/'progress.jsonl.gz','rt') as f:
  for line in f:progress.append(json.loads(line))
 assert progress and not any(x['end']=='NATURAL' for x in progress)
 qual=T/'qualification'/spec['input_digest']/'QUALIFICATION.json';assert read(qual)['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'
 result={'schema':'DTC_FROZEN_NATIVE_DEADLOCK_CLASSIFICATION_V1','status':'CLOSED_NATIVE_MODEL_DEADLOCK_UNACCEPTED','cohort':cell,'uuid':intent['uuid'],'program':spec['program'],'input_digest':spec['input_digest'],'intent_sha256':sha(intentfile),'done_sha256':sha(donefile),'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'raw_uncompressed_bytes':size,'body_qualification_sha256':sha(qual),'observed_signature':excerpts,'root_cause':'UNRESOLVED_SOURCE_OR_INPUT_SYNCHRONIZATION_CAUSE;no performance inference','last_progress_completed_diagnostic_only':progress[-1]['completed'],'accepted_cycles':None,'scientific_acceptance':False,'model_retries':0,'runtime_config_source_pins_rechecked':True,'original_resource_decisions':decisions,'continuation_scope':'Only other original unused cells;never rerun/refund this UUID. Same exact deadlock/SIGABRT class may close as unaccepted evidence;other failures checkpoint for diagnosis.','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dest=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION.json')
 if dest.exists():
  saved=read(dest);assert all(saved[k]==v for k,v in result.items() if k!='verified_utc');return saved
 with dest.open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
 return result
if __name__=='__main__':
 import sys
 print(json.dumps(classify(sys.argv[1]),indent=2))
