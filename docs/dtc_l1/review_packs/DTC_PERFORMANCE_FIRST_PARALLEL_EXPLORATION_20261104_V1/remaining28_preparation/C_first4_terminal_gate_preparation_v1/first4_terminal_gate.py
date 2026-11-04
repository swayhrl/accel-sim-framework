"""Read-only all-first4 terminal gate. Import inert; never model, registry, owner or route actions."""
from pathlib import Path
import json,hashlib,os,stat,fcntl,sys,types,datetime,subprocess,argparse
sys.dont_write_bytecode=True
P=Path
R=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'
PLAN_SHA='f656a7a122ec270df1174ed12d6c669c85a329c0d1bd7fb2ebfe308c9d4220d4'
CANDIDATE_SHA='3e513d48000bae1aa3a3561c0bcd8e79cf6efa0f1e4854e332de1b8fb4c54738'
TAG_MANIFEST=A/'C_contract_and_native_capability_v1/MANIFEST.json'
TAG_SHA='6446219f207d3744c68be3d05d45dd0f29a27c904db7ef36636739ea24e0af54'
STRICT_SHA='f56ce460a88edbf66de0651bc3cd5fd92b632a13008a3c263fd52db0b19d1191'
OUTPUT=A/'C_first4_terminal_gate_v1'
SCHEMA='C_PERFFIRST_FIRST4_TERMINAL_GATE_V1'
PROGRAMS={'2DCONV','GEMM','MVT','BICG'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def canonical_sha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def put(p,v):
 b=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
 with P(p).open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def load(p):
 m=types.ModuleType('C_first4_terminal_readonly_private');m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def authority():
 with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as f:
  fcntl.flock(f,fcntl.LOCK_SH);rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';reg=read(rp);epoch=read(N/'control/CURRENT_SCIENCE_EPOCH.json');assert sha(rp)==epoch['native_registry_sha256'];assert epoch['epoch']==2
 return reg,epoch
def live_generation(v):
 try:
  fields=P('/proc',str(v['pid']),'stat').read_text().rsplit(')',1)[1].split();return int(fields[19])==v['start_ticks']and fields[0]not in['Z','X']
 except FileNotFoundError:return False
 # Permission, invalid PID metadata, unreadable /proc are not proof of nonlive.
def valid_member(name):
 p=P(name);assert not p.is_absolute()and '..'not in p.parts and str(p)==name and name not in['','/'],'ARCHIVE_MEMBER_ESCAPE'
 return p
def type_facts(path,entry,device=2128):
 p=P(path);before=p.lstat();assert before.st_dev==device,'WRONG_NATIVE_DEVICE'
 typ=entry['type'];assert typ in['file','directory','symlink']
 if typ=='file':assert stat.S_ISREG(before.st_mode)and before.st_size==entry['size'];actual=sha(p);assert actual==entry['sha256'];target=None
 elif typ=='directory':assert stat.S_ISDIR(before.st_mode);actual=None;target=None
 else:assert stat.S_ISLNK(before.st_mode);target=os.readlink(p);assert target==entry['target'];actual=None
 after=p.lstat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'FILE_CHANGED_WHILE_REHASHING'
 return dict(path=str(p),type=typ,size=after.st_size,sha256=actual,target=target,device=after.st_dev)
def tree_members(root):
 root=P(root);out={'.'}
 for parent,dirs,files in os.walk(root,followlinks=False):
  for n in dirs+files:out.add(str((P(parent)/n).relative_to(root)))
 return out
def closure_readiness(reg):
 q=reg['registered_future_requests'][REQ];plan=read(R/'control/EXECUTION_PLAN.json');matrix=read(R/'control/MATRIX.json')['points'];assert sha(R/'control/EXECUTION_PLAN.json')==PLAN_SHA and sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')==CANDIDATE_SHA
 assert q['request']==REQ and q['budget']==len(q['admitted_specs'])==len(q['consumed'])==4 and q['remaining']==0
 assert set(q['admitted_specs'])==set(q['consumed'])=={p['cohort']for p in matrix}and {p['program']for p in matrix}==PROGRAMS
 assert len({v['uuid']for v in q['consumed'].values()})==4
 assert q['execution_plan_sha256']==PLAN_SHA and q['strict_sha256']==STRICT_SHA==sha(R/'tools/perf4_strict.py')
 assert sha(TAG_MANIFEST)==TAG_SHA
 for x in plan['source_pins']:assert sha(x['path'])==x['sha256'],'SOURCE_PIN_DRIFT '+x['path']
 for c,row in q['consumed'].items():
  assert row['charged']==1 and row['execution_receipt']['stop_reason']is None and row['execution_receipt']['launcher_wait_returncode']==0 and row['execution_receipt']['native_simulator_observed']is True
  ip=R/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json');out=R/'DTC/run/results'/row['uuid'];rr=read(R/'analysis'/(c+'.RESULT.json'));i=read(ip)
  assert sha(ip)==row['intent_sha256']and i['cohort']==c and i['uuid']==row['uuid']and i['automatic_retry']is False and i['consumed_before_launcher_fork']==1
  assert read(dp)==read(out/'NATIVE_EXIT.json')==row['execution_receipt']and row['execution_receipt']['cohort']==c and row['execution_receipt']['uuid']==row['uuid']
  assert not live_generation(read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')),'FIRST4_MODEL_STILL_LIVE'
  assert rr['state']=='PASS_PERFFIRST4_DH_STRICT_ARCHIVE_NATIVE_RESTORE'and rr['cohort']==c and rr['uuid']==row['uuid']and type(rr['cycles'])is int and rr['cycles']>0
  assert rr['proof']['performance_accepted']is True and rr['proof']['cycles']==rr['cycles']
  ap=R/'control'/(c+'_ARCHIVE_RECEIPT.json');ar=read(ap);assert ar['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and ar['source_disposition']=='SOURCE_KEEP'and ar['cohort']==c
 return q

def verify_archive(c,row,rr):
 out=R/'DTC/run/results'/row['uuid'];ap=R/'control'/(c+'_ARCHIVE_RECEIPT.json');a=read(ap);target=P(a['target_mount_path']);restore=P(a['native_restore']);txid=a['txid']
 assert target==A/'results'/c/txid and restore==R/'DTC/run/recovery'/txid
 mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(target)],text=True))['filesystems'][0];assert mount['fstype']=='fuse.sshfs'and mount['source']=='admin-wcx@10.208.130.164:/home/shared','NOT_TRUE164'
 assert rr['archive']['receipt']==a==read(target/'RECEIPT.json')
 manp=target/'SOURCE_MANIFEST.json';idxp=target/'ARCHIVE_INDEX.json';commitp=target/'COMMIT.json';restorep=target/'RESTORE_VERIFIED_NATIVE_TARGET.json';man=read(manp);idx=read(idxp);commit=read(commitp);restoremeta=read(restorep)
 assert sha(manp)==a['manifest_sha256']==commit['manifest_sha256']and sha(idxp)==commit['archive_index_sha256'];assert commit['txid']==man['txid']==a['txid']==restoremeta['txid']
 assert man['source_root']==str(out)and man['cohort']==c and man['source_disposition']=='SOURCE_KEEP'and man['native_execution_receipt_sha256']==sha(out/'NATIVE_EXIT.json')
 assert idx['archive_sha256']==a['archive_sha256']and idx['archive_bytes']==a['archive_bytes']
 total=0;stream=hashlib.sha256();chunks=[]
 for x in idx['chunks']:
  name=valid_member(x['name']);assert len(name.parts)==1 and x['offset']==total and x['txid']==txid
  p=target/'chunks'/name;st=p.lstat();assert stat.S_ISREG(st.st_mode)and st.st_size==x['size'];h=hashlib.sha256()
  with p.open('rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b);stream.update(b)
  assert h.hexdigest()==x['sha256'];total+=x['size'];chunks.append(dict(path=str(p),sha256=h.hexdigest(),size=x['size']))
 assert total==idx['archive_bytes']and stream.hexdigest()==idx['archive_sha256'];assert {p.name for p in (target/'chunks').iterdir()}=={x['name']for x in idx['chunks']}
 entries=man['entries'];names=[x['path']for x in entries];assert len(names)==len(set(names))and '.'in names;assert tree_members(out)==tree_members(restore)==set(names),'SOURCE_RESTORE_TYPED_MEMBERSHIP_MISMATCH'
 restore_rows={x['path']:x for x in restoremeta['rows']};assert set(restore_rows)==set(names)
 facts=[]
 for entry in entries:
  member=valid_member(entry['path']);s=out/member;r=restore/member
  assert s.parent.resolve().is_relative_to(out.resolve())or member==P('.');assert r.parent.resolve().is_relative_to(restore.resolve())or member==P('.')
  sf=type_facts(s,entry);rf=type_facts(r,entry);pr=restore_rows[entry['path']];assert pr['type']==entry['type']and pr.get('sha256')==entry.get('sha256')and pr.get('target')==entry.get('target')
  facts.append(dict(member=entry['path'],source=sf,restore=rf))
 assert len(entries)==rr['archive']['independently_verified_entries'];return dict(status='PASS_FULL_CHUNK_SOURCE_NATIVE_TYPED_REHASH',receipt_sha256=sha(ap),manifest_sha256=sha(manp),archive_index_sha256=sha(idxp),archive_stream_sha256=stream.hexdigest(),chunks=chunks,typed_entries=facts,typed_entry_count=len(entries),metadata_references={str(p):sha(p)for p in [manp,idxp,commitp,restorep,target/'RECEIPT.json',target/'RESULT_ENGINE_PIN.json']})

def run(output=OUTPUT):
 assert P(output)==OUTPUT,'FIXED_GATE_OUTPUT_ONLY';reg,ep=authority();q=closure_readiness(reg)
 # No output or raw read occurs until ALL4 metadata readiness is satisfied.
 output.mkdir(exist_ok=True);put(output/'ATTEMPT_ONCE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),validator_source_sha256=sha(__file__),no_models=True))
 try:
  strict=load(R/'tools/perf4_strict.py');rows={}
  for c,row in q['consumed'].items():
   rr=read(R/'analysis'/(c+'.RESULT.json'));spec=read(R/'control/specs'/(c+'.json'));proof=strict.terminal(c);assert proof==rr['proof'],'INDEPENDENT_STRICT_PROOF_MISMATCH';assert proof['cycles']==rr['cycles']and proof['physical_capacity_parser_binding']['capacity_bound']==768*64
   archive=verify_archive(c,row,rr);ap=output/(c+'.FULL_ARCHIVE_NATIVE_REHASH.json');put(ap,archive);refs=[R/'analysis'/(c+'.RESULT.json'),R/'control/qualification_ledger'/(c+'.INTENT.json'),R/'control/qualification_ledger'/(c+'.DONE.json'),R/'control'/(c+'_ARCHIVE_RECEIPT.json'),R/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json',R/'DTC/run/results'/row['uuid']/'L2_STRICT.json',R/'control/specs'/(c+'.json')]
   rows[c]=dict(uuid=row['uuid'],program=spec['program'],input_digest=spec['input_digest'],cycles=rr['cycles'],strict_reexecuted=True,natural_nonlive=True,archive_native_full_rehash=True,closure_file_sha256={str(p):sha(p)for p in refs},archive_native_proof=dict(path=str(ap),sha256=sha(ap)),typed_entry_count=archive['typed_entry_count'],metadata_references=archive['metadata_references'])
  fresh,_=authority();assert fresh['registered_future_requests'][REQ]==q,'REQUEST_CHANGED_DURING_REVIEW';closure_readiness(fresh)
  result=dict(schema=SCHEMA,status='PASS',gate_passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),validator_source_path=str(P(__file__).resolve()),validator_source_sha256=sha(__file__),request=REQ,budget=4,consumed=4,remaining=0,execution_plan_sha256=PLAN_SHA,registry_candidate_sha256=CANDIDATE_SHA,Tag16_review_manifest_path=str(TAG_MANIFEST),Tag16_review_manifest_sha256=TAG_SHA,points=rows,model_starts=0,registry_writes=0,owner_actions=0,performance_scope='EXPLORATORY_FIXED4_PHYS768_ONLY_NOT_CORE32',numerical_coherence='UNPROVEN',not_a_REQ28_registration_or_extra_grant=True)
  put(output/'C_FIRST4_TERMINAL_GATE.json',result);entries=[dict(relative_path=p.name,size_bytes=p.stat().st_size,sha256=sha(p))for p in sorted(output.iterdir())if p.is_file()and p.name!='MANIFEST.json'];put(output/'MANIFEST.json',dict(schema='C_PERFFIRST_FIRST4_TERMINAL_GATE_MANIFEST_V1',files=entries));return result
 except BaseException as e:
  put(output/'HOLD_NO_AUTOMATIC_RETRY.json',dict(status='HOLD',error=repr(e),no_new_models=True));raise

def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--check-readiness',action='store_true');g.add_argument('--audit',action='store_true');args=ap.parse_args()
 if args.check_readiness:
  try:reg,_=authority();closure_readiness(reg);print(json.dumps(dict(ready=True,scope='METADATA_ONLY_NOT_FULL_GATE')))
  except (OSError,KeyError,AssertionError,ValueError,TypeError)as e:print(json.dumps(dict(ready=False,reason=repr(e),scope='METADATA_ONLY_NO_RAW_READ_NO_OUTPUT')));return 2
 else:result=run();print(json.dumps(dict(status=result['status'],gate_path=str(OUTPUT/'C_FIRST4_TERMINAL_GATE.json'),gate_sha256=sha(OUTPUT/'C_FIRST4_TERMINAL_GATE.json'))))
 return 0
if __name__=='__main__':raise SystemExit(main())
