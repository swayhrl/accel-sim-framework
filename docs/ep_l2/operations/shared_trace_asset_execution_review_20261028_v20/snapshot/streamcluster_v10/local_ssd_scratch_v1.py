# Exact local SSD scratch; final payload and all consumer-visible receipts remain on NAS.
import pathlib,os,stat,json,hashlib,shutil
G=2**30
BASE=pathlib.Path('/data/c16/sc_post_local_ssd_20261028_v9')
def need(x,m):
 if not x:raise RuntimeError(m)
def no_links(p):
 for q in [pathlib.Path(p),*pathlib.Path(p).parents]:need(not q.is_symlink(),'LOCAL_OR_EVIDENCE_SYMLINK')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def rawsave(p,raw):
 with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 need(p.stat().st_size==len(raw)and digest(p)==hashlib.sha256(raw).hexdigest(),'CLOSED_REOPENED_EVIDENCE_SHA')
def root_for(a):return BASE/a['run_id']
def setup(a,scope_sha):
 need(a['local_ssd_parent']==str(BASE),'FIXED_LOCAL_SSD_BASE');no_links(BASE)
 BASE.mkdir(mode=0o700,parents=True,exist_ok=True)
 root=root_for(a);no_links(root);root.mkdir(mode=0o700,exist_ok=False)
 need(root.stat().st_dev==pathlib.Path('/data/c16').stat().st_dev,'ACTUAL_LOCAL_SSD_NOT_NAS')
 marker=dict(run_id=a['run_id'],scope_sha256=scope_sha,owner_pid=os.getpid(),owner_start_ticks=pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),only_regenerable_derived_scratch=True)
 rawsave(root/'LOCAL_OWNER.json',(json.dumps(marker,sort_keys=True,separators=(',',':'))+'\n').encode())
 return root
def space(a,root,usage_fn):
 need(root==root_for(a),'EXACT_LOCAL_RUN');no_links(root)
 need(root.is_dir()and root.stat().st_dev==pathlib.Path('/data/c16').stat().st_dev,'LOCAL_SSD_ROOT')
 used=usage_fn(root);budget=a['local_scratch_budget_bytes'];need(used<=budget,'LOCAL_32GiB_ACCOUNTING_CAP')
 free=shutil.disk_usage(root).free;required=a['local_ssd_free_floor_bytes']+max(0,budget-used)
 need(free>=required,'LOCAL_10GiB_FLOOR_PLUS_REMAINING_32GiB_BUDGET')
 return dict(used_bytes=used,budget_bytes=budget,actual_free_bytes=free,required_free_bytes=required,filesystem_quota_claim=False)
def work(a,root,index):
 need(root==root_for(a),'EXACT_LOCAL_RUN');no_links(root)
 k=root/('kernel_%04d'%index);k.mkdir(mode=0o700,exist_ok=False)
 return k/'work'
def export_evidence(work,nas_evidence):
 no_links(work);no_links(nas_evidence);need(work.is_dir(),'LOCAL_WORK_MISSING')
 nas_evidence.mkdir(mode=0o700,exist_ok=False);members=[]
 for p in sorted(work.rglob('*')):
  no_links(p)
  if p.is_file():members.append(dict(name=str(p.relative_to(work)),bytes=p.stat().st_size,sha256=digest(p)))
 for name in ['GROUP_RECEIPT.json','CHECKPOINT.json']:
  p=work/name;raw=p.read_bytes();need(len(raw)<=8*2**20,'SMALL_EVIDENCE_BOUND');rawsave(nas_evidence/name,raw)
 q=dict(schema='SC_LOCAL_SCRATCH_FINAL_MEMBER_ATTESTATION_V1',local_work=str(work),local_members=members,local_members_regenerable_not_consumer_refs=True,all_final_payload_on_NAS=True,source_KEEP=True)
 rawsave(nas_evidence/'LOCAL_SCRATCH_MEMBERS.json',(json.dumps(q,sort_keys=True,separators=(',',':'))+'\n').encode())
 return nas_evidence/'GROUP_RECEIPT.json'
def cleanup(a,root,index,work,scope_sha,nas_evidence,normalized):
 expected=root_for(a)/('kernel_%04d'%index)/'work'
 need(root==root_for(a)and work==expected,'ONLY_EXACT_CURRENT_OWN_WORK_CLEANUP');no_links(work)
 marker=json.loads((root/'LOCAL_OWNER.json').read_bytes());need(marker['run_id']==a['run_id']and marker['scope_sha256']==scope_sha and marker['owner_pid']==os.getpid()and marker['owner_start_ticks']==pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]and marker['boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'CURRENT_SCOPE_EXACT_LOCAL_OWNER')
 expected_NAS=pathlib.Path(a['remote_runtime_root'])/'runs'/a['run_id']/('kernel_%04d'%index)
 need(nas_evidence==expected_NAS/'EVIDENCE'and normalized==expected_NAS/'NORMALIZED_CLOSED.json','EXACT_NAS_CLOSED_EVIDENCE_PATHS');no_links(normalized);no_links(nas_evidence)
 v=json.loads(normalized.read_bytes())
 for key,name in [('raw_receipt_ref','GROUP_RECEIPT.json'),('checkpoint_ref','CHECKPOINT.json'),('local_scratch_manifest_ref','LOCAL_SCRATCH_MEMBERS.json')]:
  p=nas_evidence/name;r=v[key];need(r['path']==str(p)and r['bytes']==p.stat().st_size and r['sha256']==digest(p),'NAS_CLOSED_EVIDENCE_REF_SHA')
 need((nas_evidence/'GROUP_RECEIPT.json').read_bytes()==(work/'GROUP_RECEIPT.json').read_bytes()and json.loads((nas_evidence/'GROUP_RECEIPT.json').read_bytes())==v['result'],'NAS_ORIGINAL_RECEIPT_MATCH_BEFORE_LOCAL_CLEANUP')
 need(work.resolve()==expected and root.resolve()in work.resolve().parents,'LOCAL_CLEANUP_CONTAINMENT')
 shutil.rmtree(work)
