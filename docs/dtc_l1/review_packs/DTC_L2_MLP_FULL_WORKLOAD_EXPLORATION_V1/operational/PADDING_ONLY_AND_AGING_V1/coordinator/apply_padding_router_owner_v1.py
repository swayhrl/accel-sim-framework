"""One-time Main activation, after separately staged qualified publication pins.

No controller/model restart. Existing entry body remains an exact suffix.
Do not rerun a queued callback when its ACK is merely delayed.
"""
import pathlib,json,hashlib,subprocess,os,stat,datetime,time
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=R/'control/operational_amendments/padding_only_v1';N=P('/root/data/ep_l2_dtc_l1_native_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def write(p,d):
 with P(p).open('x')as h:json.dump(d,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
def main():
 request=read(A/'coordinator/PADDING_INSTALL_REQUEST_V1.json');cfg=read(D/'ACTIVE_FRONTEND.json');registered=read(D/'REGISTERED.json');assert sha(D/'ACTIVE_FRONTEND.json')==registered['config_sha256'];assert cfg['request']==request['request'];assert not(D/'OWNER_QUEUED.json').exists()and not(D/'OWNER_ACK.json').exists()
 for role in ['source','frontend','extra_strict','owner','history_validator','policy','certificate','QA','readback']:assert sha(cfg[role+'_path'])==cfg[role+'_sha256']==request[role+'_sha256']
 manifest=read(request['router_manifest_path']);assert sha(request['router_manifest_path'])==request['router_manifest_sha256'];qa=read(request['router_qa_path']);assert sha(request['router_qa_path'])==request['router_qa_sha256']and qa['status']=='PASS';candidate=P(request['router_candidate_path']);assert sha(candidate)==manifest['candidate_sha256']==request['router_candidate_sha256'];native=N/'bin/native';assert native.is_file()and not native.is_symlink()and sha(native)==manifest['old_entry_sha256'];old=native.read_bytes();new=candidate.read_bytes();assert new.endswith(old)and len(old)==manifest['old_entry_bytes'];assert manifest['frontend_path']==cfg['frontend_path']
 owner=P('/proc/1498278');fields=(owner/'stat').read_text().rsplit(')',1)[1].split();assert int(fields[19])==977758783 and fields[0]!='Z';assert 'FLOCK'in(owner/'fdinfo/4').read_text();assert os.readlink(owner/'fd/4')==str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock')
 for pin in read(R/'control/EXECUTION_PLAN.json')['source_pins']:assert sha(pin['path'])==pin['sha256']
 check=subprocess.run(['/bin/sh','-n',str(candidate)],capture_output=True,text=True,timeout=10);assert check.returncode==0,check.stderr
 backup=D/'native.before.sh';assert not backup.exists();backup.write_bytes(old);temp=native.with_name('.native.padding_only_v1.tmp');assert not temp.exists();st=native.stat()
 with temp.open('xb')as h:h.write(new);h.flush();os.fsync(h.fileno())
 os.chmod(temp,stat.S_IMODE(st.st_mode));os.chown(temp,st.st_uid,st.st_gid);os.replace(temp,native);assert sha(native)==manifest['candidate_sha256'];fd=os.open(native.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
 write(D/'ROUTER_ACTIVATED.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_sha256=manifest['old_entry_sha256'],new_sha256=sha(native),old_body_exact_suffix=True,all_original_noflag_routes_unchanged=True,no_models_interrupted=True))
 code='''import pathlib,json,importlib.util,hashlib,traceback,datetime
_d=pathlib.Path(%r)
try:
 _p=_d/'padding_owner.py';assert hashlib.sha256(_p.read_bytes()).hexdigest()==%r
 _s=importlib.util.spec_from_file_location('dtc_padding_only_installed_owner_v1',_p);_m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _es=importlib.util.spec_from_file_location('dtc_padding_main_native_lease',_d.parents[2]/'tools/l2_native.py');_e=importlib.util.module_from_spec(_es);_es.loader.exec_module(_e);_e.assert_parent_lease()
 _proof=_m.apply_in_owner(str(_d/'ACTIVE_FRONTEND.json'));_proof['UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with(_d/'OWNER_ACK.json').open('x')as _h:json.dump(_proof,_h,indent=2);_h.write('\\n')
except BaseException:
 with(_d/'OWNER_ERROR.json').open('x')as _h:json.dump({'traceback':traceback.format_exc()},_h)
'''%(str(D),cfg['owner_sha256'])
 # D=R/control/operational_amendments/padding_only_v1; parents[2] is R.
 payload=code.encode()+b'\0';assert len(payload)<4096;(D/'OWNER_PENDING.bin').write_bytes(payload);gdb=D/'OWNER_APPLY.gdb';gdb.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf = (void *)mmap((void*)0,4096,3,34,-1,0)\nrestore '+str(D/'OWNER_PENDING.bin')+' binary $buf\nset $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n')
 result=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p','1498278','-x',str(gdb)],capture_output=True,text=True,timeout=8);(D/'OWNER_GDB.stdout').write_text(result.stdout);(D/'OWNER_GDB.stderr').write_text(result.stderr);assert result.returncode==0 and 'QUEUED=0'in result.stdout,(result.stdout,result.stderr);write(D/'OWNER_QUEUED.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=cfg['owner_sha256'],no_second_controller=True))
 until=time.monotonic()+25
 while not(D/'OWNER_ACK.json').exists()and not(D/'OWNER_ERROR.json').exists()and time.monotonic()<until:time.sleep(.2)
 assert not(D/'OWNER_ERROR.json').exists(),(D/'OWNER_ERROR.json').read_text()if(D/'OWNER_ERROR.json').exists()else''
 assert(D/'OWNER_ACK.json').exists(),'Callback queued but ACK missing; inspect same owner, never blindly queue again'
 ack=read(D/'OWNER_ACK.json');assert ack['owner_pid']==1498278 and ack['source_sha256']==cfg['source_sha256'];assert ack['pool_object_id']==read(R/'control/operational_amendments/consistent_admission_v1/ACK.json')['executor_id']
 for pin in read(R/'control/EXECUTION_PLAN.json')['source_pins']:assert sha(pin['path'])==pin['sha256']
 print(json.dumps(dict(status='PADDING_PILOT_SOURCE_AND_CLI_ACTIVATED',owner=ack,router_sha256=sha(native),all_frozen_source_pins_unchanged=True,models_started_by_installer=0,model_admission_still_rechecks_fresh_resources=True)))
if __name__=='__main__':main()
