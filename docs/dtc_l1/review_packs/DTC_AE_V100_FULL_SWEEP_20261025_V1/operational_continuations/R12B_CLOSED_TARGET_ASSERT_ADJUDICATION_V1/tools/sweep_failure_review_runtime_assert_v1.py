"""Exact OO/PIB terminal-stats assertion evidence; no performance acceptance."""
import pathlib,json,hashlib,gzip,importlib.util,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');SCHEMA='DTC_OO_PIB_STATS_ASSERT_FAILURE_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def classify(cell):
 ip=T/'control/qualification_ledger'/(cell+'.INTENT.json');i=read(ip);out=P(i['output']);done=read(out/'NATIVE_EXIT.json');dest=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json')
 if done['stop_reason']!='DTC_NATURAL_TELEMETRY_CLOSURE_MISSING' or done['launcher_wait_returncode']!=1 or (dest.exists() and read(dest).get('schema')!=SCHEMA):return load('preserved_six_negative_classes','sweep_failure_review_telemetry_v1.py').classify(cell)
 n=load('OO_PIB_assert_native_identity','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];s=n.spec_for(cell);row=q['consumed'][cell];dp=ip.with_name(cell+'.DONE.json');assert done==read(dp)==row['execution_receipt'] and done['uuid']==i['uuid']==row['uuid'] and sha(ip)==row['intent_sha256'];pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');proc=P('/proc')/str(pid['pid'])
 if proc.exists():
  st=(proc/'stat').read_text().rsplit(')',1)[1].split();assert int(st[19])!=pid['start_ticks'] or st[0] in ['Z','X']
 launch=read(out/'NATIVE_LAUNCH.json');assert launch['argv'][-len(s['native_simulator_argv']):]==s['native_simulator_argv'] and s['native_simulator_argv'][0] in pid['maps']
 assert sha(out/'raw.log.gz')==done['raw_sha256'];h=hashlib.sha256();size=0;signature=False;crash=False;fw=False;core=False
 with gzip.open(out/'raw.log.gz','rb') as f:
  for line in f:
   h.update(line);size+=len(line);signature=signature or (b'shader_print_dtc_l1_stats' in line and b'Assertion `total.oo_pib_occupancy == 0\' failed.' in line);crash=crash or b'=== CRASH: SIGABRT (signal 6) ===' in line;fw=fw or s['framework_commit'].encode() in line;core=core or s['core_commit'][:7].encode() in line
 assert signature and crash and fw and core and h.hexdigest()==done['raw_uncompressed_sha256'] and size==done['raw_uncompressed_bytes'];trace=(out/'actual_file_process_network.log').read_text();assert 'SIGABRT' in trace and str(pid['pid']) in trace and not (out/'AEFAIR_STRICT.json').exists();progress=[]
 with gzip.open(out/'progress.jsonl.gz','rt') as f:
  for line in f:
   p=json.loads(line);assert p['seq']==len(progress)+1 and (p['pid'],p['start_ticks'],p['generation'])==(pid['pid'],pid['start_ticks'],done['uuid']) and p['input']==s['original_environment']['DTC_AG7_INPUT_SHA'] and p['roi']==s['original_environment']['DTC_AG7_ROI_SHA'] and p['end']=='NONE'
   if progress:assert p['mono_ns']>progress[-1]['mono_ns'] and p['completed']>=progress[-1]['completed']
   progress.append(p)
 assert progress;resources=[]
 with gzip.open(out/'RESOURCE_SAMPLES.jsonl.gz','rt') as f:
  for line in f:
   p=json.loads(line)
   if 'physical_RAM_pass' in p:resources.append(p)
 assert resources and all(r['physical_RAM_pass'] and r['physical_disk_pass'] for r in resources)
 for r in s['runtime_files']:assert sha(T/r['target'])==r['sha256']
 result={'schema':SCHEMA,'status':'CLOSED_OO_PIB_STATS_ASSERT_ABORT_UNACCEPTED','cohort':cell,'uuid':done['uuid'],'input_digest':s['input_digest'],'program':s['program'],'framework_commit':s['framework_commit'],'binary_sha256':s['binary_sha256'],'intent_sha256':sha(ip),'done_sha256':sha(dp),'raw_compressed_sha256':done['raw_sha256'],'raw_uncompressed_sha256':h.hexdigest(),'raw_uncompressed_bytes':size,'progress_records':len(progress),'last_progress':progress[-1],'resource_sample_count':len(resources),'signature':'shader_print_dtc_l1_stats: total.oo_pib_occupancy == 0 assertion;SIGABRT','root_cause':'Actual native terminal-statistics assertion is captured;why OO/PIB occupancy remained nonzero is unresolved. No accepted cycles,even if partial populations appear complete.','scientific_acceptance':False,'accepted_cycles':None,'classifier_source_sha256':sha(__file__),'model_retries':0,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 if dest.exists():
  saved=read(dest);assert all(saved[k]==v for k,v in result.items() if k!='verified_utc');return saved
 with dest.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 return result
