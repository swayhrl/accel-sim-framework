"""Own CPU fixture only: real GDB->mmap->Py_AddPendingCall on main thread.
No science PID is attached, signalled, launched or selected. Real existing
five-scope accounting is read-only; pipe/UDS/seq and run frame stay continuous.
"""
import pathlib,json,hashlib,subprocess,time,os,tempfile,ast,importlib.util,copy,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=F/'ops/revision19';SRC=D/'runtime_resource_override_v1.py';RESOURCE=D/'resource_accounting_v1.py';POLICY=F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json';read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();work=P(tempfile.mkdtemp(prefix='R19_HOT_PENDING_CPU_',dir=F/'control'));cell='CPU_R19_ONLY';uid='CPU_R19_NO_SCIENTIFIC_MODEL';out=work/'out';out.mkdir();native=work/'fixture_native.py';sender=work/'cpu_sender.py'
sender.write_text('import socket,sys,time,json\ns=socket.socket(fileno=int(sys.argv[1]))\nfor n in range(1,4001):\n b=json.dumps({"seq":n}).encode();s.send(b);print(n,flush=True);time.sleep(.005)\n')
native.write_text('''import pathlib,json,os,time,socket,subprocess,sys,select,threading
P=pathlib.Path;root=P(sys.argv[1]);REQUEST='DTC_AE_V100_FULL_SWEEP_20261025_V1'
def read_current_authority():return json.loads((root/'authority.json').read_bytes()),{}
def resources(spec,fresh_source=False):return {'physical_RAM_pass':False,'physical_disk_pass':False,'required_free_bytes':123456789,'old_disk_counter':'unchanged','telemetry':'unchanged'}
def run_native(cohort):
 ident='CPU_R19_NO_SCIENTIFIC_MODEL';out=root/'out';a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_DGRAM);p=subprocess.Popen(['/usr/bin/python3','-B',str(root/'cpu_sender.py'),str(b.fileno())],pass_fds=(b.fileno(),),stdout=subprocess.PIPE,text=True);ticks=int(P('/proc',str(p.pid),'stat').read_text().rsplit(')',1)[1].split()[19]);observations=[{'pid':p.pid,'start_ticks':ticks}];raw=(out/'cpu_pipe.log').open('w');udp=[];pipe=[];_old_state={'preserve':'oldR12state'};globals()['_LIVE_RAM_OVERRIDE_STATE_R12']=_old_state;old_frame_ids={'p':id(p),'raw':id(raw),'observations':id(observations),'channel':id(a),'oldR12':id(_old_state)};(root/'READY.json').write_text(json.dumps({'pid':os.getpid(),'start_ticks':int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'model_pid':p.pid,'model_start_ticks':ticks}));deadline=time.monotonic()+25;post=0;effective=None
 try:
  while time.monotonic()<deadline:
   available=select.select([a,p.stdout],[],[],.01)[0]
   if a in available:udp.append(json.loads(a.recv(4096))['seq'])
   if p.stdout in available:
    line=p.stdout.readline()
    if line:pipe.append(int(line));raw.write(line);raw.flush()
   effective=resources({'cohort':cohort,'request':REQUEST},False)
   if '_LIVE_RESOURCE_ACCOUNTING_STATE_R19'in globals():
    post+=1
    if post>=12:break
  new_ids={'p':id(p),'raw':id(raw),'observations':id(observations),'channel':id(a),'oldR12':id(globals()['_LIVE_RAM_OVERRIDE_STATE_R12'])};(root/'FIXTURE_RESULT.json').write_text(json.dumps({'main_thread':threading.current_thread()is threading.main_thread(),'udp':udp,'pipe':pipe,'old_frame_ids':old_frame_ids,'new_frame_ids':new_ids,'effective':effective,'old_R12_state':globals()['_LIVE_RAM_OVERRIDE_STATE_R12'],'post_calls':post,'model_poll_before_cleanup':p.poll()}))
 finally:
  p.terminate();p.wait(timeout=3);raw.close();a.close();b.close()
run_native('CPU_R19_ONLY')
''')
proc=subprocess.Popen(['/usr/bin/python3','-B',str(native),str(work)],stdin=subprocess.DEVNULL,stdout=(work/'frontend.stdout').open('w'),stderr=(work/'frontend.stderr').open('w'));model_pid=None
try:
 until=time.monotonic()+4
 while not(work/'READY.json').exists()and time.monotonic()<until:time.sleep(.01)
 ready=read(work/'READY.json');assert ready['pid']==proc.pid;model_pid=ready['model_pid'];assert int(P('/proc',str(model_pid),'stat').read_text().rsplit(')',1)[1].split()[1])==proc.pid
 helper_spec=importlib.util.spec_from_file_location('r19_cpu_code_fingerprint',T/'tools/sweep_live_ram_override_v1.py');helper=importlib.util.module_from_spec(helper_spec);helper_spec.loader.exec_module(helper);tree=ast.parse(native.read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='resources');g={};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(native),'exec'),g);binding=dict(uuid=uid,frontend_pid=proc.pid,frontend_start_ticks=ready['start_ticks'],model_pid=model_pid,model_start_ticks=ready['model_start_ticks'],launcher_pid=model_pid,launcher_start_ticks=ready['model_start_ticks'],output=str(out),expected_resource_function_code_identity=helper.code_identity(g['resources']),resource_function_source_sha256=sha(native));plan=dict(profile_id='R19_EXACT_FIVE_SCOPE_RUNTIME_RESOURCE_ACCOUNTING_V1',patch_source_sha256=sha(SRC),request='DTC_AE_V100_FULL_SWEEP_20261025_V1',targets={cell:binding},unchanged_native_source_path=str(native),unchanged_native_source_sha256=sha(native),resource_module_path=str(RESOURCE),resource_module_sha256=sha(RESOURCE),policy_path=str(POLICY),policy_sha256=sha(POLICY));planpath=work/'plan.json';planpath.write_text(json.dumps(plan));profile=dict(profile_id=plan['profile_id'],plan_sha256=sha(planpath),patch_source_sha256=sha(SRC),policy_sha256=sha(POLICY),targets={cell:binding});(work/'authority.json').write_text(json.dumps({'registered_future_requests':{'DTC_AE_V100_FULL_SWEEP_20261025_V1':{'live_resource_accounting_correction_profile_R19':profile}}}));ackroot=work/'acks'
 code=("import importlib.util,pathlib;_s=importlib.util.spec_from_file_location('r19_cpu_pending_payload',"+repr(str(SRC))+");_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m);_m.ACKROOT=pathlib.Path("+repr(str(ackroot))+");_m.apply(pathlib.Path("+repr(str(planpath))+"))").encode()+b'\0';blob=work/'pending.bin';blob.write_bytes(code);commands=work/'attach.gdb';commands.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf = (void *)mmap((void*)0,4096,3,34,-1,0)\nprintf "BUFFER=%p\\n",$buf\nrestore '+str(blob)+' binary $buf\nset $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n');start=time.monotonic();r=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p',str(proc.pid),'-x',str(commands)],capture_output=True,text=True,timeout=8);duration=time.monotonic()-start;(work/'gdb.stdout').write_text(r.stdout);(work/'gdb.stderr').write_text(r.stderr);assert r.returncode==0 and'QUEUED=0'in r.stdout
 proc.wait(timeout=15);assert proc.returncode==0, (work/'frontend.stderr').read_text();result=read(work/'FIXTURE_RESULT.json');acks=list(ackroot.glob('*.ACK.json'));assert len(acks)==1;ack=read(acks[0]);assert result['main_thread']and result['post_calls']>=12 and result['model_poll_before_cleanup']is None and result['old_frame_ids']==result['new_frame_ids']and result['old_R12_state']=={'preserve':'oldR12state'}
 for stream in ['udp','pipe']:assert len(result[stream])>=12 and result[stream]==list(range(1,len(result[stream])+1)),stream
 sample=result['effective'];assert sample['old_disk_counter']=='unchanged'and sample['telemetry']=='unchanged'and sample['required_free_bytes']==123456789 and sample['live_resource_accounting_correction_R19']['status']=='EFFECTIVE_ACCOUNTING_APPLIED';assert(sample['physical_RAM_pass'],sample['physical_disk_pass'])==(sample['live_resource_accounting_correction_R19']['effective_resource_sample']['physical_RAM_pass'],sample['live_resource_accounting_correction_R19']['effective_resource_sample']['physical_disk_pass'])
 proof=dict(schema='R19_REAL_PENDING_CALL_CPU_ONLY_RUNTIME_TRANSITION_QUALIFICATION_V1',status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),payload_path=str(SRC),payload_sha256=sha(SRC),resource_module_path=str(RESOURCE),resource_module_sha256=sha(RESOURCE),policy_sha256=sha(POLICY),driver_sha256=sha(__file__),fixture_root=str(work),GDB_returncode=r.returncode,GDB_mmap_pending_delivery_seconds=duration,ACK=ack,pipe_contiguous_records=len(result['pipe']),UDS_contiguous_records=len(result['udp']),main_thread_delivery=True,same_native_frame_process_raw_pipe_UDS_and_oldR12state=True,old_sample_all_fields_preserved_except_effective_RAM_disk=True,post_replacement_resource_calls=result['post_calls'],CPU_frontend_PID_attached=proc.pid,CPU_sender_PID_never_attached=model_pid,scientific_processes_attached_or_signalled=0,scientific_models_started=0,production_authority_control_or_source_mutations=0,scope='Only own verified CPU child was attached. Real existing R19 five-scope resource reads used; all activation authority/plan/ACK fixtures private. No scientific simulation or wait receipt.')
 dest=D/'RUNTIME_PENDING_CALL_CPU_QUALIFICATION_V1.json'
 with dest.open('x')as f:json.dump(proof,f,indent=2);f.write('\n')
 print(json.dumps(dict(status='PASS',path=str(dest),sha256=sha(dest),payload_sha256=sha(SRC),GDB_seconds=duration,pipe_records=len(result['pipe']),UDS_records=len(result['udp']),scientific_attaches=0)))
finally:
 if proc.poll()is None:proc.terminate();proc.wait(timeout=3)
 if model_pid and P('/proc',str(model_pid)).exists():
  try:os.kill(model_pid,15)
  except ProcessLookupError:pass
