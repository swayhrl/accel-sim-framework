"""Independent CPU-only qualification. Never selects or attaches production PIDs."""
import pathlib, tempfile, subprocess, os, time, json, hashlib, importlib.util, copy
P=pathlib.Path; T=P('/root/data/dtc_main_v100_sweep_20261025_v1'); G=1024**3
D=P(tempfile.mkdtemp(prefix='CPU_RAM_PATCH_',dir=T/'control')); tests=[]
PATCH=T/'tools/sweep_live_ram_override_v1.py'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def record(name,details=None):tests.append({'name':name,'pass':True,'details':details})
def load():
 s=importlib.util.spec_from_file_location('qualified_ram_patch',PATCH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load();patchsha=sha(PATCH)
binding={'cohort':'CPU_FIXTURE','uuid':'cpu-uuid','frontend_pid':os.getpid(),'frontend_start_ticks':m.generation(os.getpid())['start_ticks'],'model_pid':123,'model_start_ticks':456}
profile={'profile_id':m.PROFILE,'plan_sha256':'plan','patch_source_sha256':patchsha,'targets':{'CPU_FIXTURE':binding.copy()}}
def authority():return ({'registered_future_requests':{'DTC_AE_V100_FULL_SWEEP_20261025_V1':{'live_RAM_guard_override_profile':profile}}},None)
sample={'host_MemAvailable_bytes':64*G,'cgroup_effective_headroom_bytes':48*G,'frontend_pid':binding['frontend_pid'],'frontend_start_ticks':binding['frontend_start_ticks']}
base={'physical_RAM_pass':False,'disk_pass':False,'telemetry_pass':False,'model_peak_RSS_bytes':15*G,'hard_RSS_cap_bytes':16*G,'opaque':['keep']}
w=m.make_wrapper(lambda *a:copy.deepcopy(base),authority,binding,'plan',patchsha,lambda:dict(sample));out=w({},False)
assert out['physical_RAM_pass'] is True and all(out[k]==v for k,v in base.items() if k!='physical_RAM_pass') and set(out)==set(base)|{'live_RAM_guard_override'}
record('only_RAM_field_replaced_disk_telemetry_and_16GiB_hardcap_preserved')
assert out['physical_RAM_pass'] and out['model_peak_RSS_bytes']>4*G
record('RSS_above_4GiB_is_not_a_hardkill')
for host,eff,expected in [(64*G,48*G,True),(64*G-1,48*G,False),(64*G,48*G-1,False),(64*G,None,True)]:assert m.decision({'host_MemAvailable_bytes':host,'cgroup_effective_headroom_bytes':eff}) is expected
record('fresh_RAM_64GiB_host_48GiB_cgroup_exact_boundaries_and_unlimited')
for label,mutate in [('bad_profile',lambda p:p.update(profile_id='BAD')),('bad_certificate_plan',lambda p:p.update(plan_sha256='wrong')),('bad_patch_source_SHA',lambda p:p.update(patch_source_sha256='wrong')),('bad_UUID',lambda p:p['targets']['CPU_FIXTURE'].update(uuid='wrong')),('bad_frontend_generation',lambda p:p['targets']['CPU_FIXTURE'].update(frontend_start_ticks=-1))]:
 old=copy.deepcopy(profile);mutate(profile)
 try:w({},False);raise RuntimeError('accepted invalid '+label)
 except AssertionError:pass
 profile.clear();profile.update(old);record(label+'_refused')
class FakeFile:
 def __init__(self,s):self.s=s
 def __truediv__(self,x):return FakeFile(self.s+'/'+x)
 def read_text(self):
  if self.s=='/proc/meminfo':return 'MemAvailable: '+str(64*G//1024)+' kB\n'
  if self.s.endswith('/memory.max'):return str(256*G)
  if self.s.endswith('/memory.current'):return str(230*G)
  if self.s.endswith('/memory.stat'):return '\n'.join(k+' '+str(v*G) for k,v in {'file':60,'inactive_file':50,'shmem':3,'file_mapped':4,'file_dirty':5,'file_writeback':6}.items())
  raise RuntimeError(self.s)
oldP,oldgen=m.P,m.generation;m.P=lambda s:FakeFile(str(s));m.generation=lambda pid:{'start_ticks':1}
try:
 s=m.snapshot();assert s['cgroup_reclaimable_clean_inactive_file_credit_bytes']==34*G and s['cgroup_effective_headroom_bytes']==60*G
finally:m.P,m.generation=oldP,oldgen
record('clean_inactive_file_credit_formula_independently_mocked',{'credit_GiB':34,'effective_headroom_GiB':60})
CHILD=r"""import pathlib,json,sys,os,time,threading,subprocess,socket,hashlib,marshal,importlib.util
P=pathlib.Path;R=P(sys.argv[1]);ver=sys.argv[2];patch=sys.argv[3];invalid=sys.argv[4]=='invalid'
spec=importlib.util.spec_from_file_location('_fixture_identity_only',patch);payload=importlib.util.module_from_spec(spec);spec.loader.exec_module(payload)
def gen(pid):return int((P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19])
sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);sock.bind(str(R/'model.sock'));sock.settimeout(.2)
modelsource="import socket,sys,time; s=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM); p=sys.argv[1]; i=0\nwhile True:\n print(i,flush=True);s.sendto(str(i).encode(),p);i+=1;time.sleep(.01)\n"
model=subprocess.Popen([sys.executable,'-u','-c',modelsource,str(R/'model.sock')],stdout=subprocess.PIPE,text=True,stderr=(R/'model.stderr').open('w'))
pipe=[];uds=[];stop=False
def readpipe():
 for line in model.stdout:pipe.append(int(line))
def readuds():
 while not stop:
  try:uds.append(int(sock.recv(100)))
  except socket.timeout:pass
threading.Thread(target=readpipe,daemon=True).start();threading.Thread(target=readuds,daemon=True).start()
tools=R/'tools';tools.mkdir();host=tools/('fixture_host_'+ver+'.py');host.write_text('def resources(spec,fresh_source=False):\n return '+repr({'physical_RAM_pass':False,'disk_pass':True,'telemetry_pass':True,'hard_RSS_cap_bytes':16*1024**3,'fixture_version':ver})+'\n')
native=tools/'sweep_native_cap1m.py';native.write_text('''def run_native(cohort):
 ident='cpu-uuid';out=R/'DTC/run/results'/ident;observations=[{'pid':model.pid,'start_ticks':gen(model.pid)}];frame_identity=id(sys._getframe());before=None;deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  value=resources({},False)
  if (R/'FINISH').exists():
   result={'frame_identity_before':frame_identity,'frame_identity_after':id(sys._getframe()),'model_pid':model.pid,'model_start_ticks':gen(model.pid),'model_alive':model.poll() is None,'pipe':pipe[:],'uds':uds[:],'value':value,'before_sequence':before,'after_sequence':len(pipe),'main_thread':threading.current_thread() is threading.main_thread()};(R/'CHILD_RESULT.json').write_text(json.dumps(result));return
  if before is None and (R/'INJECT_NOW').exists():
   before=len(pipe);(R/'DEBUG_IDENTITY.json').write_text(json.dumps(payload.code_identity(resources)))
  time.sleep(.005)
''')
ns={'__file__':str(native),'R':R,'model':model,'gen':gen,'sys':sys,'time':time,'pipe':pipe,'uds':uds,'json':json,'threading':threading,'hashlib':hashlib,'marshal':marshal,'payload':payload}
exec(compile(host.read_text(),str(host),'exec'),ns)
ns['read_current_authority']=lambda: (json.loads((R/'PROFILE.json').read_text()),None)
exec(compile(native.read_text(),str(native),'exec'),ns)
f=ns['resources'];identity=payload.code_identity(f)
ready={'pid':os.getpid(),'start_ticks':gen(os.getpid()),'model_pid':model.pid,'model_start_ticks':gen(model.pid),'native_source':str(native),'native_sha':hashlib.sha256(native.read_bytes()).hexdigest(),'host_source':str(host),'host_sha':hashlib.sha256(host.read_bytes()).hexdigest(),'resource_code_identity':identity};(R/'READY.json').write_text(json.dumps(ready))
globals().update(ns)
try:ns['run_native']('CPU_FIXTURE')
finally:
 stop=True
 if model.poll() is None:model.terminate();model.wait(timeout=3)
"""
def waitfile(p,timeout=5):
 end=time.monotonic()+timeout
 while not p.exists() and time.monotonic()<end:time.sleep(.01)
 assert p.exists(),str(p)
fixtures=[]
for ver,invalid in [('V1',False),('V2',False),('V3',False),('V3_BAD_SOURCE',True)]:
 r=D/ver;r.mkdir();(r/'control/live_ram_override').mkdir(parents=True);child=r/'fixture_frontend.py';child.write_text(CHILD)
 p=subprocess.Popen(['/usr/bin/python3','-B',str(child),str(r),ver,str(PATCH),'invalid' if invalid else 'valid'],stdin=subprocess.DEVNULL,stdout=(r/'frontend.stdout').open('wb'),stderr=(r/'frontend.stderr').open('wb'))
 try:
  waitfile(r/'READY.json');ready=json.loads((r/'READY.json').read_bytes());assert ready['pid']==p.pid
  b={'uuid':'cpu-uuid','frontend_pid':p.pid,'frontend_start_ticks':ready['start_ticks'],'model_pid':ready['model_pid'],'model_start_ticks':ready['model_start_ticks'],'resource_function_source_path':ready['host_source'],'resource_function_source_sha256':'wrong' if invalid else ready['host_sha'],'expected_resource_function_code_identity':ready['resource_code_identity']}
  plan={'profile_id':m.PROFILE,'patch_source_sha256':patchsha,'request':'DTC_AE_V100_FULL_SWEEP_20261025_V1','targets':{'CPU_FIXTURE':b},'unchanged_native_source_sha256':ready['native_sha']};pp=r/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json';pp.write_text(json.dumps(plan));pr={'profile_id':m.PROFILE,'plan_sha256':sha(pp),'patch_source_sha256':patchsha,'targets':{'CPU_FIXTURE':b}};(r/'PROFILE.json').write_text(json.dumps({'registered_future_requests':{plan['request']:{'live_RAM_guard_override_profile':pr}}}))
  time.sleep(.2);(r/'INJECT_NOW').write_text('fixture only')
  stub="import importlib.util,pathlib,json,threading,traceback;_s=importlib.util.spec_from_file_location('_cpu_fixture_payload',"+repr(str(PATCH))+");_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m);_m.T=pathlib.Path("+repr(str(r))+")\ntry:\n _a=_m.apply();_result={'installed':True,'main_thread':threading.current_thread() is threading.main_thread(),'ack':_a}\nexcept BaseException as _e:\n _result={'installed':False,'error_type':type(_e).__name__,'error':str(_e),'traceback':traceback.format_exc(),'main_thread':threading.current_thread() is threading.main_thread()}\npathlib.Path("+repr(str(r/'APPLY_RESULT.json'))+").write_text(json.dumps(_result))\n"
  blob=r/'pending.bin';blob.write_bytes(stub.encode()+b'\0');assert blob.stat().st_size<16384
  gf=r/'attach.gdb';gf.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf = (void *)mmap((void*)0,16384,3,34,-1,0)\nrestore '+str(blob)+' binary $buf\nset $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n')
  waitfile(r/'DEBUG_IDENTITY.json');assert json.loads((r/'DEBUG_IDENTITY.json').read_bytes())==ready['resource_code_identity'],'Function identity changed during ordinary execution'
  start=time.monotonic();g=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p',str(p.pid),'-x',str(gf)],capture_output=True,text=True,timeout=5);elapsed=time.monotonic()-start;(r/'gdb.stdout').write_text(g.stdout);(r/'gdb.stderr').write_text(g.stderr);assert g.returncode==0 and 'QUEUED=0' in g.stdout
  waitfile(r/'APPLY_RESULT.json');a=json.loads((r/'APPLY_RESULT.json').read_bytes());assert a['main_thread'] and a['installed'] is (not invalid),a
  time.sleep(.25);(r/'FINISH').write_text('fixture only');waitfile(r/'CHILD_RESULT.json');p.wait(timeout=3);result=json.loads((r/'CHILD_RESULT.json').read_bytes());assert result['frame_identity_before']==result['frame_identity_after'] and result['model_alive'] and result['model_pid']==ready['model_pid'] and result['model_start_ticks']==ready['model_start_ticks']
  for key in ['pipe','uds']:
   seq=result[key];assert len(seq)>20 and seq==list(range(len(seq))) and len(seq)>result['before_sequence']+10,(key,result)
  assert ('live_RAM_guard_override' in result['value']) is (not invalid)
  assert result['value']['fixture_version']==ver and result['value']['disk_pass'] and result['value']['telemetry_pass'] and result['value']['hard_RSS_cap_bytes']==16*G
  proof={'fixture_directory':str(r),'frontend_pid':p.pid,'CPU_only_model_pid':ready['model_pid'],'gdb_seconds':elapsed,'pipe_samples':len(result['pipe']),'UDS_samples':len(result['uds']),'frame_preserved':True,'model_generation_preserved':True,'main_thread_callback':a['main_thread'],'installed':a['installed']};fixtures.append(proof);record('real_pending_callback_'+ver,proof)
 finally:
  if p.poll() is None:p.terminate();p.wait(timeout=3)
  if 'ready' in locals() and ready.get('pid')==p.pid:
   try:
    if m.generation(ready['model_pid'])['start_ticks']==ready['model_start_ticks']:os.kill(ready['model_pid'],15)
   except ProcessLookupError:pass
   except FileNotFoundError:pass
proof={'schema':'LIVE_RAM_GUARD_CPU_QUALIFICATION_R12_V1','status':'PASS','CPU_only':True,'patch_source_path':str(PATCH),'patch_source_sha256':patchsha,'driver_source_path':str(P(__file__).resolve()),'driver_source_sha256':sha(__file__),'fixture_directory':str(D),'tests':tests,'real_GDB_pending_fixtures':fixtures,'scientific_frontends_attached':0,'scientific_models_attached':0,'scientific_models_started':0,'production_registry_modified':False,'production_pinned_sources_modified':False,'limitations':['CPU fixtures validate delivery and transition mechanics; no scientific model was attached or run.']}
(D/'RESULT.json').write_text(json.dumps(proof,indent=2)+'\n');out=T/'control/LIVE_RAM_GUARD_CPU_QUALIFICATION_R12.json'
with out.open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','tests':len(tests),'fixture_directory':str(D),'proof':str(out),'patch_sha256':patchsha,'driver_sha256':proof['driver_source_sha256'],'GDB_seconds':[f['gdb_seconds'] for f in fixtures]}))
