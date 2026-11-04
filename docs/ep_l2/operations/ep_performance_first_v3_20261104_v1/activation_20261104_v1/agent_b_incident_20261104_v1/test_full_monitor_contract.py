"""Synthetic actual-info/run-monitor contract CPU harness: no model/Trace/authority actor."""
from pathlib import Path
import json,copy,hashlib,importlib.util,sys,os
I=Path(__file__).resolve().parent;C=I/'candidate';V=I.parent.parent;A=V/'activation_20261104_v1/agent_b_formal';H=A/'runtime'
J=V.parent.parent;F=J/'execution_vector1700_decomposition_v3_20261104_v1/vector1700'
def read(p):return json.loads(Path(p).read_bytes())
def mod(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sys.path.insert(0,str(H));sys.path.insert(0,str(C))
eng=mod('original_sealed_verify_actual',H/'ep_perf_native_wv_modes_draft.py')
schema=mod('candidate_schema',C/'runtime_monitor_schema.py')
closure=read(C/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json')
contract=read(C/'RUNTIME_STATIC_KEY_CONTRACT.json')
rows=[]
def check(label,fn,reject=False,contains=None):
 try:r=fn();ok=not reject;err=None
 except Exception as e:r=None;err=type(e).__name__+': '+str(e);ok=reject and(contains is None or contains in err)
 rows.append(dict(label=label,PASS=ok,error=err,expected='REJECT' if reject else 'PASS'))
 return r
candidate_specs=[]
for mode in ['W_ONLY','WV_ZERO_RO']:
 old=read(F/'cases'/('EP_PERF_PFV3_VECTOR4M_'+mode+'_1700_V1')/'control/FROZEN_SPEC.json')
 s=copy.deepcopy(old);s['host_cpu']=min(os.sched_getaffinity(0))
 s['native_boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 s['native_mount_namespace']=os.readlink('/proc/self/ns/mnt')
 s['pinned_files']={**closure['pinned_files'],**s['pinned_files']}
 helper=mod('real_helper_'+mode,Path(s['helpers_ref']['path']))
 out=I/'SYNTHETIC_NOT_MODEL_OUT';args=helper.command(s,out)
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH='/root/data/ep_l2_dtc_l1_native_v2/common-lib',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'),XDG_CACHE_HOME=str(out/'cache'),**s['observer_env'])
 maps=[s['binary_path']]+[p for p in closure['pinned_files']if '/EP/env/lib/'in p or'/common-lib/'in p]
 info=dict(pid=424242,parent_pid=424241,start_ticks=123456,process_state='R',boot_id=s['native_boot_id'],mnt_namespace=s['native_mount_namespace'],exe=s['binary_path'],cmdline=[a.encode()for a in args],environment={k.encode():v.encode()for k,v in env.items()},maps='\n'.join('00400000-00401000 r-xp 00000000 00:00 1 '+p for p in maps),limits='Max address space         '+str(s['limits']['AS_bytes'])+' '+str(s['limits']['AS_bytes'])+' bytes\n',affinity=[s['host_cpu']],nice=10)
 # Hashes stand in for already sealed hashes; do not read/model mapped files or execute any process.
 eng.sha=lambda p,s=s:s['source_identity']['binary_sha256']if p==s['binary_path']else s['pinned_files'][p]
 check(mode+'_actual_sealed_failing_spec_reproduces_KeyError',lambda:eng.verify_actual(helper,info,dict(old,host_cpu=s['host_cpu']),args,env),True,'native_boot_id')
 oldboot=copy.deepcopy(old);oldboot['native_boot_id']=s['native_boot_id'];oldboot['host_cpu']=s['host_cpu']
 check(mode+'_boot_only_still_rejects_unpinned_libraries',lambda:eng.verify_actual(helper,info,oldboot,args,env),True,'unqualified mapped library')
 check(mode+'_preconsume_rejects_failed_original',lambda:schema.validate_spec_contract(old),True,'native_boot_id')
 check(mode+'_preconsume_rejects_boot_only',lambda:schema.validate_spec_contract(oldboot),True,'runtime dependency pins')
 proof=check(mode+'_candidate_full_actual_verify',lambda:eng.verify_actual(helper,info,s,args,env))
 serialized=helper.serializable_info(info);assert serialized['cmdline']==args
 check(mode+'_candidate_preconsume_current_domain_bound_CPU',lambda:schema.validate_spec_contract(s,require_bound_cpu=True,check_current_domain=True))
 for key in contract['required_keys']:
  z=copy.deepcopy(s);z.pop(key);check(mode+'_required_key_'+key,lambda z=z:schema.validate_spec_contract(z),True,'missing required runtime fields')
 for key in ['AS_bytes','RSS_bytes','wall_seconds','result_bytes']:
  z=copy.deepcopy(s);z['limits'].pop(key);check(mode+'_missing_hardlimit_'+key,lambda z=z:schema.validate_spec_contract(z),True,'runtime hard limit')
 for label,mut,why in [
  ('CPU',lambda x:x.__setitem__('affinity',[s['host_cpu']+1]),'CPU/nice'),
  ('nice',lambda x:x.__setitem__('nice',0),'CPU/nice'),
  ('argv',lambda x:x.__setitem__('cmdline',[b'BAD']),'argv/environment'),
  ('env',lambda x:x['environment'].__setitem__(b'BAD',b'1'),'argv/environment'),
  ('boot',lambda x:x.__setitem__('boot_id','0'*36),'native domain'),
  ('mount',lambda x:x.__setitem__('mnt_namespace','mnt:[1]'),'native domain'),
  ('maps',lambda x:x.__setitem__('maps',x['maps']+'\n00400000-00401000 r-xp 0 00:00 1 /tmp/UNQUALIFIED.so'),'unqualified mapped library'),
  ('AS',lambda x:x.__setitem__('limits','Max address space 1 1 bytes\n'),'AS limit')]:
  x=copy.deepcopy(info);mut(x);check(mode+'_monitor_negative_'+label,lambda x=x:eng.verify_actual(helper,x,s,args,env),True,why)
 # The exact production syscall parser consumes only synthetic strings, never Trace bodies.
 p=I/(mode+'_SYNTHETIC_SYSCALL.log')
 files=[s['trace_entry']]+[x['path']for x in s['all_unique_kernel_members']]
 p.write_text(''.join(str(info['pid'])+' openat(AT_FDCWD, '+json.dumps(f)+', O_RDONLY) = 3\n'for f in files))
 check(mode+'_actual_syscall_parser_synthetic_scope',lambda:helper.syscall_proof(p,s,info['pid']))
 candidate_specs.append(dict(mode=mode,Source5_unchanged=s['source_identity']==old['source_identity'],effective282_unchanged=s['expected_effective_options']==old['expected_effective_options'],native_pins_restored=len(closure['pinned_files']),mapped_fixture_paths=len(maps),spec_frozen_not_modified=True))
result=dict(schema='EP_VECTOR_HOST_FULL_ACTUAL_MONITOR_CONTRACT_CPU_FIXTURE_V1',status='PASS'if all(x['PASS']for x in rows)else'PARTIAL',rows=rows,candidate_specs=candidate_specs,monitor_verifier='actual sealed verify_actual function',syscall_verifier='actual Source-bound helper syscall_proof, synthetic text only',actual_process_or_model_started=0,real_registry_writes=0,Trace_body_reads=0,new_science_budget_consumed=0,application_NI='NOT_MEASURED',not_application_correctness_or_performance=True)
(I/'FULL_MONITOR_CONTRACT_CPU_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],passed=sum(r['PASS']for r in rows),total=len(rows),failed=[r for r in rows if not r['PASS']])));assert result['status']=='PASS'
