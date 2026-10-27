"""Private V9 runtime/control evidence join. No public catalog or qualification writes."""
import pathlib,json,hashlib,sys,argparse
D=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/gaussian16_inner_manifest_closure_repair_20261027_v6/runtime');sys.path.insert(0,str(D/'control'))
from gpu_leaf_bridge_v9 import mode,PERMISSIONS,plan
from inherited_leases_v5 import digest
from activity_proof_v3 import same_identity
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(root,scope_sha,code_sha):
 root=pathlib.Path(root)
 from cross_host_v9 import NB,RB
 need(root.resolve().is_relative_to((D/'cpu_runs').resolve())or root.resolve().is_relative_to((D/'runtime').resolve())or root.resolve().is_relative_to((NB/'runtime').resolve()),'private fixed run roots only')
 def read(n):return json.loads((root/n).read_bytes())
 need(sha(root/'CPU_STATIC_SCOPE.json')==scope_sha,'original Root raw scope')
 scope=read('CPU_STATIC_SCOPE.json');which=mode(scope)
 cross_host='native_run_id'in scope
 script_root=RB if cross_host else D
 remote_root=RB/'runtime'/root.name if cross_host else root
 if cross_host:
  from cross_host_v9 import approval
  native=read('NATIVE_KEEPER.json');a,actual=approval(root,native['Root_sha256'])
  need(actual==which and scope['root_authorization_sha256']==native['Root_sha256']and scope['family']==a['family']=='gaussian'and scope['root_scope_id']==a['root_scope_id']and scope['native_run_id']==a['run_id']==root.name,'original Native Root raw scope join')
  need(scope['native_run_root']==str(NB/'runtime'/root.name)and scope['remote_run_root']==str(remote_root),'fixed Native/remote run path projection')
  need(scope['job_sha256']==a['job_sha256']and scope['absolute_deadline_unix']==a['Root_absolute_deadline_unix'],'Root exact job/original absolute wall deadline')
  need(sha(root/'ROOT_AUTHORITY_RAW.json')==native['Root_sha256'],'original Root raw bytes')
  from root_go_v3 import verify_receipts
  verify_receipts(root,a,which)

 need(sha(D/'control/CODE_MANIFEST.json')==code_sha==scope['code_sha256'],'external immutable code pin')
 for r in json.loads((D/'control/CODE_MANIFEST.json').read_text())['files']:need(sha(D/'control'/r['relative'])==r['sha256'],'runtime source ref bytes')
 guard=read('GUARD_START.json');worker=read('WORKER_START.json');issuer=scope['issuer'];leases=read('GUARD_LEASES.json')
 def identity(x,expected_exe=None):
  need(set(['pid','start_ticks','boot_id','namespaces','exe','cmdline_sha256','parent_pid'])<=set(x),'complete identity fields')
  need(type(x['pid'])is int and x['pid']>0 and str(x['start_ticks']).isdigit(),'PID/ticks fields')
  need(x['boot_id']==scope['execution_boot_id']and x['namespaces']==scope['execution_namespaces']and x['exe']==(expected_exe or scope['interpreter']['exe']),'local109 boot/ns/exe join')
 for x in [guard,worker,issuer]:identity(x)
 for role,proof in [('guard',guard),('worker',worker),('issuer',issuer)]:
  args=[scope['interpreter']['argv0'],'-B',str(script_root/'control'/(role+'_v9.py')),'--run',str(remote_root),'--code-sha',code_sha]
  need(hashlib.sha256(b'\0'.join(x.encode()for x in args)+b'\0').hexdigest()==proof['cmdline_sha256'],'exact script argv bytes, not path membership')
 need(worker['parent_pid']==guard['pid'],'exact worker parent')
 need(same_identity(leases['guard'],guard) and len(leases['files'])==2,'lease guard')
 table={r['relative']:r['sha256']for r in json.loads((D/'control/CODE_MANIFEST.json').read_text())['files']}
 need(leases['bindings']==dict(approval_sha256=scope_sha,worker_sha256=table['worker_v9.py'],guard_sha256=table['guard_v9.py'],job_sha256=scope['job_sha256']),'exact lease source/job/Root pins')
 hello=read('LIVE_HANDSHAKE.json');h=hello['hello'];a=hello['ack'];ready=hello['ready']
 need(h['schema']=='CPU_GUARD_HELLO_V6'and a['schema']=='CPU_WORKER_ACK_V6'and ready['schema']=='CPU_GUARD_READY_V6','complete HELLO/ACK/READY schema')
 need(h['scope_sha256']==a['scope_sha256']==ready['scope_sha256']==scope_sha and h['nonce']==a['nonce']==ready['nonce']and len(h['nonce'])==64,'one handshake challenge')
 need(same_identity(h['worker'],worker)and same_identity(a['worker'],worker) and same_identity(h['guard'],guard)and same_identity(a['guard'],guard) and h['leases_sha256']==a['leases_sha256']==digest(leases),'full identity/lease join')
 need(hello['actual_sender']['pid']==guard['pid'],'SCM guard sender')
 prep=read('READY.json');need(same_identity(prep['worker'],worker) and same_identity(prep['guard'],guard) and prep['leases']==leases,'slow preparation same roles/leases')
 need(prep['static_pass']is True and prep['capture_permission']is False and prep['idle_count']==15 and len(prep['idle'])==15 and prep['idle_elapsed_seconds']>=15,'actual15 slow idle')
 need([x['seq']for x in prep['idle']]==list(range(1,16))and all(x['CPU_SYNTHETIC_IDLE']==(which=='test')for x in prep['idle']),'actual/virtual mode evidence')
 raw=(root/'FIRST_ADMISSION.json').read_bytes();ad=json.loads(raw)
 need((root/'RUNTIME_ADMISSION_RAW_FROZEN.json').read_bytes()==raw,'independent exact runtime raw frozen bytes')
 need(read('RUNTIME_ADMISSION_VIEW.json')==ad,'semantic view matches raw, not reencoding claim')
 need(ad['schema']=='FIRST_GAUSSIAN16_ADMISSION_V3_GO'and ad['permission']==PERMISSIONS[which]and ad['scope_sha256']==scope_sha,'GPU/CPU schema separation')
 need(same_identity(ad['worker'],worker) and same_identity(ad['guard'],guard) and same_identity(ad['issuer'],issuer) and ad['leases_sha256']==digest(leases)and ad['ready_sha256']==sha(root/'READY.json'),'runtime exact original roles/ready')
 need(ad['job_sha256']==scope['job_sha256']and ad['nonce']==prep['request_nonce'],'runtime job/challenge')
 need(ad['execution_boot_id']==scope['execution_boot_id']and ad['execution_namespaces']==scope['execution_namespaces'],'runtime local boot/ns')
 claim=read('ISSUANCE_CLAIM.json');need(claim['first_and_only']is True and claim['scope_sha256']==scope_sha and claim['ready_sha256']==ad['ready_sha256']and claim['nonce']==ad['nonce']and same_identity(claim['issuer'],issuer),'first issuance claim join')
 consumed=read('ADMISSION_CONSUMED.json');acked=read('ISSUER_ACKED.json');need(acked['ack']==consumed and consumed['admission_sha256']==sha(root/'FIRST_ADMISSION.json')and consumed['scope_sha256']==scope_sha and consumed['nonce']==ad['nonce']and same_identity(consumed['worker'],worker) and acked['actual_sender']['pid']==worker['pid'],'one ACK full raw hash/challenge/SCM identity')
 response=read('ISSUER_RESPONSE_RECEIVED.json');need(response['actual_sender']['pid']==issuer['pid']and same_identity(response['issuer'],issuer) and response['message']['admission_sha256']==sha(root/'FIRST_ADMISSION.json'),'actual issuer sender')
 need(ad['root_absolute_deadline_unix']==scope['absolute_deadline_unix']and ad['root_absolute_deadline_monotonic_ns']==scope['absolute_deadline_monotonic_ns'],'original deadlines unchanged')
 need(prep['ready_unix']<=ad['issued_unix']<ad['expires_unix']<=ad['issued_unix']+30 and 0<ad['expires_monotonic_ns']-ad['issued_monotonic_ns']<=30000000000,'first short window')
 start=read('LEAF_PROCESS_START.json');fixed_capture=plan(scope['family']);identity(start['proof'],fixed_capture['argv'][0]if which=='production'else None);need(start['proof']['cmdline_sha256']==hashlib.sha256(b'\0'.join(v.encode()for v in start['intended_argv'])+b'\0').hexdigest(),'exact actual capture argv bytes');need(start['proof']['parent_pid']==worker['pid']and ad['issued_unix']<=start['started_unix']<min(ad['expires_unix'],scope['absolute_deadline_unix']-60),'exact capture parent and fresh launch evidence')
 fixed=plan(scope['family']);need(start['intended_argv']==fixed['argv']and start['binary_sha256']==fixed['binary_sha256']and start['SO_sha256']==fixed['SO_sha256']and start['test_executor']==(which=='test'),'fixed actual scientific identity')

 need(which=='production','actual capture CPU derivation only')
 need(read('GUARD_CLOSED.json')['status']=='ALL_OWNED_CLOSED_LEASES_RELEASED','complete original guard cleanup')
 execution=read('EXECUTION.json');failed=read('WORKER_FAILED_RETAINED.json');ended=read('LEAF_CAPTURE_ENDED.json')
 need(execution['exit_code']==0 and execution['task']['argv']==fixed['argv']and execution['binary_sha256']==fixed['binary_sha256']and execution['tool_sha256']==fixed['SO_sha256'],'actual captured binary/SO exit0')
 need(same_identity(execution['capture_process'],start['proof'])and same_identity(execution['worker'],worker)and execution['scope_sha256']==scope_sha,'actual execution/capture/worker scope join')
 need(ended['capture_pid']==start['proof']['pid']and ended['start_ticks']==start['proof']['start_ticks']and ended['returncode']==0,'capture really exited0 before post failure')
 need(failed['error']=="ValueError('actual fixed post/reader failed')"and failed['scope_sha256']==scope_sha and same_identity(failed['worker'],worker),'original post failure retained, no manufactured WORKER_COMPLETE')
 return dict(status='PRIVATE_CAPTURE_CONTROL_JOIN_PASS_ORIGINAL_POST_FAILURE_RETAINED',mode=which,family=scope['family'],original_worker_post_succeeded=False,actual_capture_exited0=True,scientific_validation_required=True,public_or_GPU_qualification=False,source_refs={n:sha(root/n)for n in ['CPU_STATIC_SCOPE.json','FIRST_ADMISSION.json','RUNTIME_ADMISSION_RAW_FROZEN.json','LIVE_HANDSHAKE.json','GUARD_LEASES.json','LEAF_PROCESS_START.json','EXECUTION.json','WORKER_FAILED_RETAINED.json','LEAF_CAPTURE_ENDED.json']})

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--scope-sha',required=True);p.add_argument('--code-sha',required=True);x=p.parse_args();print(json.dumps(verify(x.run,x.scope_sha,x.code_sha)))
if __name__=='__main__':main()
