from pathlib import Path
import subprocess,json,time,resource,os,hashlib
p=Path(__file__).parent
q=json.loads((p/'BUILD_LOCATION.json').read_text());build=Path(q['build']);bulk=Path(q['bulk']);cpu=bulk/'cpu_v1';cpu.mkdir(exist_ok=True)
assert json.loads((p/'BUILD_STATE.json').read_text())['state']=='BUILD_PASS'
exe=build/'gpgpu-sim/ep_l2_quota_handshake_v5';assert exe.is_file()
assert not (p/'PRODUCTION_CPU_DELTA_RECEIPT.json').exists()
base='/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/cpu_fixture_inputs/base.config'
def limits():
 os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(45,45))
def ref(f):
 b=Path(f).read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
rows=[]
for k in (1,2):
 for path in ('simple','real'):
  label='K'+str(k)+'_'+path;cmd=[str(exe),base,str(p/('cpu_K'+str(k)+'.config')),path]
  work=cpu/(label+'_work');work.mkdir(exist_ok=True)
  start=time.time()
  with (cpu/(label+'.stdout')).open('w') as out,(cpu/(label+'.stderr')).open('w') as err:
   r=subprocess.run(cmd,stdout=out,stderr=err,timeout=90,preexec_fn=limits,start_new_session=True,cwd=str(work))
  stdout=(cpu/(label+'.stdout')).read_text(errors='replace')
  row={'label':label,'argv':cmd,'returncode':r.returncode,'seconds':time.time()-start,'stdout':ref(cpu/(label+'.stdout')),'stderr':ref(cpu/(label+'.stderr')),'pass_lines':[x for x in stdout.splitlines() if x.startswith('PASS ')]}
  rows.append(row);print(json.dumps(row),flush=True)
  if r.returncode!=0 or not row['pass_lines']:
   (p/'PRODUCTION_CPU_DELTA_ATTENTION.json').write_text(json.dumps({'status':'NEW_DELTA_FAILURE_RETAINED','rows':rows},indent=2)+'\n');raise SystemExit(1)
(p/'PRODUCTION_CPU_DELTA_RECEIPT.json').write_text(json.dumps({'status':'PASS_BOUNDED_NEW_HANDSHAKE_PATHS_ONLY','rows':rows,'executable':ref(exe),'old12_and3185_rerun':False,'old_parser_rerun':False,'full_application_starts':0,'full_quota_pipeline_qualified':False,'physical_PPA_qualified':False},indent=2)+'\n')
