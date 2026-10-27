import pathlib,json,hashlib,subprocess,datetime,time,os
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');B=A/'agents/B/lease_object_retention_v1';D=R/'control/operational_amendments/lease_object_retention_v1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
q=read(B/'CPU_QUALIFICATION.json');assert q['status']=='PASS'and q['total_checks']==9 and q['model_starts']==q['model_signals']==q['production_mutations']==0;assert sha(B/'retain_original_lease_io.py')==q['source_sha256']=='b9fbf5c341986b15091178fe48003467b8aadc3285e2031d7e991abc627b4b2e';assert not D.exists();D.mkdir(parents=True)
for name in ['retain_original_lease_io.py','CPU_QUALIFICATION.json','qualify_cpu.py']:
 src=B/name
 if src.exists():(D/name).write_bytes(src.read_bytes())
for fd in[3,4]:assert 'FLOCK'in P('/proc/1498278/fdinfo',str(fd)).read_text()
assert int(P('/proc/1498278/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
code='''import pathlib,json,importlib.util,hashlib,traceback,datetime
_d=pathlib.Path(%r)
try:
 _p=_d/'retain_original_lease_io.py';assert hashlib.sha256(_p.read_bytes()).hexdigest()==%r
 _s=importlib.util.spec_from_file_location('dtc_original_lease_io_retention_v1',_p);_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _proof=_m.apply_in_owner();_proof['UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with(_d/'ACK.json').open('x')as _h:json.dump(_proof,_h,indent=2);_h.write('\\n')
except BaseException:
 with(_d/'ERROR.json').open('x')as _h:json.dump({'traceback':traceback.format_exc()},_h)
'''%(str(D),q['source_sha256'])
payload=code.encode()+b'\0';assert len(payload)<4096;(D/'PENDING.bin').write_bytes(payload);gdb=D/'APPLY.gdb';gdb.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf = (void *)mmap((void*)0,4096,3,34,-1,0)\nrestore '+str(D/'PENDING.bin')+' binary $buf\nset $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n')
r=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p','1498278','-x',str(gdb)],capture_output=True,text=True,timeout=8);(D/'GDB.stdout').write_text(r.stdout);(D/'GDB.stderr').write_text(r.stderr);assert r.returncode==0 and 'QUEUED=0'in r.stdout,(r.stdout,r.stderr);(D/'QUEUED.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=q['source_sha256']))+'\n')
until=time.monotonic()+25
while not(D/'ACK.json').exists()and not(D/'ERROR.json').exists()and time.monotonic()<until:time.sleep(.2)
assert not(D/'ERROR.json').exists(),(D/'ERROR.json').read_text()if(D/'ERROR.json').exists()else''
assert(D/'ACK.json').exists(),'Callback queued, inspect same handle; never blindly requeue'
ack=read(D/'ACK.json');assert ack['owner_pid']==1498278 and ack['owner_start_ticks']==977758783 and len(ack['objects'])==2
for pin in read(R/'control/EXECUTION_PLAN.json')['source_pins']:assert sha(pin['path'])==pin['sha256']
print(json.dumps(dict(status='ORIGINAL_IO_LIFETIME_RETAINED',ack=ack,models_started=0,model_signals=0,no_new_lock_acquired=True,all_frozen_source_pins_unchanged=True)))
