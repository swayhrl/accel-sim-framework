#!/usr/bin/env python3
"""Bounded engineering inventory by default; only --commit-copy publishes.
Reuses the source-copy mount/receiver framework; adds regular-file extraction.
Never invokes models, compilers, controllers, entries, registries or budgets.
"""
import argparse,datetime,fcntl,gzip,hashlib,importlib.util,json,os,resource,stat,subprocess,tarfile,uuid
from pathlib import Path,PurePosixPath
J=Path('/root/data/ep_tag_reservation_lifetime_20261026_v1');A=J/'agent_a';M=1<<20;G=1<<30;CAP=192*M
SOURCEQ=J/'control/SOURCE_QUALIFICATION_V2.json';QS='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
BASE_RESOURCE=A/'resource_snapshot_qualified_r20.py';BASE_SHA='ab986c9ceb2310fcaaedfaefae313eb6de3bfbfe63a85c725afa80e8dfa40003'
NAS=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments')
RECEIVER=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02/.TARGET_RECEIVER.lock')
def need(x,s):
 if not x:raise ValueError(s)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def canon(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('xb') as f:f.write(canon(v));f.flush();os.fsync(f.fileno())
def safe_name(name):
 p=PurePosixPath(name);need(name and not p.is_absolute() and all(x not in {'..','.'} for x in p.parts) and '\\' not in name and '\0' not in name,'unsafe archive path');return p

def inventory(extra_roots=(),extra_files=()):
 need(sha(SOURCEQ)==QS,'SourceQ8ed drift');q=read(SOURCEQ);selected={};omitted=[]
 fixtures=set(q['actual_compiled_fixture_binaries']);matrixref=q['evidence_refs']['cpu_matrix_v2'];need(sha(matrixref['path'])==matrixref['sha256'],'CPUv2 matrix drift');matrix=read(matrixref['path'])
 rawmap={r['raw_path']:r['raw_sha256'] for r in matrix['tests']};need(len(rawmap)==22,'exact CPUv2 raw22 required')
 def add(p,expected=None,explicit=False):
  p=Path(p);local=p.is_relative_to(J)
  need(local or expected is not None,'external extra files must be already pinned dependencies')
  if not local and p.suffix not in {'.py','.json','.sh'}:
   omitted.append({'path':str(p),'sha256':expected,'reason':'external binary/library reference only; not an engineering tar member'});return
  s=p.lstat();need(stat.S_ISREG(s.st_mode) and not p.is_symlink(),'inventory only regular files: '+str(p));need(s.st_size<=CAP,'single member cap')
  if local:
   rel=p.relative_to(J);parts=rel.parts
   if any(x in {'.git','__pycache__','source_restore','source_restore_v2'} for x in parts):return
   if parts[0] in {'core','framework','build','build_v2'} and str(p) not in fixtures and p.name!='accelsim_version.h':
    omitted.append({'path':str(p),'sha256':expected,'reason':'source/model artifact already separately archived'});return
   if 'results' in parts or p.suffix in {'.traceg','.gz'}:return
   if any(x in p.name.upper() for x in ['FINAL_STATUS','FINAL_REPORT','ENGINEERING_ARCHIVE_RECEIPT','ENGINEERING_INVENTORY']):return
   name=rel.as_posix()
  else:
   if p.suffix not in {'.py','.json','.sh'} or s.st_size>2*M:
    omitted.append({'path':str(p),'sha256':expected,'reason':'external artifact reference only'});return
   name='external_references/'+sha(p)+'/'+p.name
  if p.suffix.lower() in {'.md','.docx','.pdf'} and not explicit:return
  h=sha(p);need(expected is None or h==expected,'pinned engineering member drift '+str(p));safe_name(name)
  selected[name]={'name':name,'source_path':str(p),'size':s.st_size,'sha256':h,'mode':stat.S_IMODE(s.st_mode)&0o777}
 add(SOURCEQ,QS)
 for ref in q['evidence_refs'].values():add(ref['path'],ref['sha256'],True)
 for field in ['qualifier_implementation','binding_manifest']:
  if field in q:add(q[field]['path'],q[field]['sha256'],True)
 br=read(q['evidence_refs']['independent_B_review_v2']['path'])
 if 'auditor_path' in br:add(br['auditor_path'],br['auditor_sha256'],True)
 for path,h in rawmap.items():add(path,h,True)
 for path,h in q['actual_compiled_fixture_binaries'].items():add(path,h,True)
 for directory in [J/'control',J/'tools_v2',J/'tools_v3',J/'cpu_fixture_inputs']:
  if not directory.exists():continue
  for p in directory.iterdir():
   if p.is_file() and not p.is_symlink() and p.suffix in {'.py','.sh','.json','.jsonl','.log','.txt','.patch'}:add(p)
 for case in ['EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2','EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2']:
  b=J/'cases'/case/'control'
  if not b.exists():continue
  for p in b.iterdir():
   if p.is_file() and not p.is_symlink() and p.suffix=='.json':add(p)
  frozen=read(b/'FROZEN_SPEC.json')
  for path,h in frozen['pinned_files'].items():add(path,h)
  for path,h in frozen['env_hashes'].items():add(path,h)
 # Frozen SourceQ CPU review refs above are prerequisites, not later finaldocs.
 # Do not sweep agent review/finaldoc trees or any case results/app raw.
 for root in extra_roots:
  root=Path(root);root=root if root.is_absolute() else J/root
  need(root.resolve().is_relative_to(J.resolve()) and root.is_dir() and not root.is_symlink(),'extra-root must be an explicit local analysis directory')
  need(root.relative_to(J).parts[0] not in {'core','framework','build','build_v2','cases','source_restore','source_restore_v2'},'large/source/app roots excluded')
  for p in root.rglob('*'):
   need(not p.is_symlink(),'extra-root alias forbidden')
   if p.is_file():add(p)
 for p in extra_files:add(Path(p) if Path(p).is_absolute() else J/p)
 rows=sorted(selected.values(),key=lambda r:r['name']);total=sum(x['size'] for x in rows)
 need(len(rows)<=4096 and total+len(canon(rows))+Path(__file__).stat().st_size<=CAP,'192MiB bounded engineering inventory exceeded')
 return {'schema':'EP_LIFETIME_FINAL_ENGINEERING_MEMBER_INVENTORY_V1','archive_implementation_sha256':sha(Path(__file__)),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_identity':q['source_identity'],'source_qualification_sha256':QS,'members':rows,'payload_bytes':total,'payload_cap_bytes':CAP,'files':len(rows),'CPUv2_raw_count':22,'fixture_ELF_count':2,'separately_archived_references':omitted,'scope':'CPUv2 raw+exact fixture ELF+frozen engineering refs/tools/receipts and explicitly added analysis; excludes finalreview docs, app raw, source/build trees and trace payload','review_documents_swept':False,'new_model_or_help_or_budget_operations':0,'source_keep':True}

def restore(bundle,destination):
 b=Path(bundle);d=Path(destination);commit=read(b/'COMMIT.json');manifest=read(b/'MEMBER_MANIFEST.json')
 need(sha(b/'MEMBER_MANIFEST.json')==commit['manifest_sha256'] and sha(Path(__file__))==commit['restore_tool_sha256'],'bundle manifest/tool SHA')
 archive=b/'ENGINEERING_EVIDENCE.tar.gz';need(archive.stat().st_size==commit['archive_bytes']<=CAP and sha(archive)==commit['archive_sha256'],'closed archive SHA')
 rows=manifest['members'];need(len(rows)<=4096 and sum(r['size'] for r in rows)<=CAP,'restore payload envelope');expected={r['name']:r for r in rows};need(len(expected)==len(rows),'duplicate manifest names')
 need(not os.path.lexists(d) and d.parent.exists(),'fresh absent native restore target with existing parent required')
 need(d.parent.stat().st_dev==Path('/root/data').stat().st_dev,'native data target required')
 need(subprocess.check_output(['findmnt','-n','-T',str(d.parent),'-o','FSTYPE'],text=True).strip()=='ext4','native ext4 restore target required')
 need(os.statvfs(d.parent).f_bavail*os.statvfs(d.parent).f_frsize>=8*G+CAP,'native restore disk floor')
 d.mkdir(mode=0o700);data=d/'data';data.mkdir(mode=0o700);seen=set()
 with tarfile.open(archive,mode='r|gz') as tar:
  for member in tar:
   name=member.name;parts=safe_name(name);need(name in expected and name not in seen and member.type in {tarfile.REGTYPE,tarfile.AREGTYPE},'unexpected/duplicate/nonregular tar member');row=expected[name];need(member.size==row['size'],'tar member size');target=data.joinpath(*parts.parts)
   target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);need(target.parent.resolve().is_relative_to(data.resolve()),'restore path escaped')
   h=hashlib.sha256();count=0
   with tar.extractfile(member) as src,target.open('xb') as dst:
    for chunk in iter(lambda:src.read(M),b''):dst.write(chunk);h.update(chunk);count+=len(chunk)
    dst.flush();os.fsync(dst.fileno())
   need(count==row['size'] and h.hexdigest()==row['sha256'],'restored member independent SHA');os.chmod(target,row['mode']);seen.add(name)
 need(seen==set(expected),'missing tar members')
 for row in rows:need(sha(data/row['name'])==row['sha256'],'closed/reopened native member SHA')
 receipt={'schema':'EP_LIFETIME_ENGINEERING_EXTRACTION_RECEIPT_V1','status':'REGULAR_MEMBERS_INDEPENDENT_NATIVE_EXTRACTION_SHA_PASS','destination':str(d),'manifest_sha256':commit['manifest_sha256'],'archive_sha256':commit['archive_sha256'],'verified_files':len(rows),'verified_bytes':sum(r['size'] for r in rows),'only_regular_files':True,'model_or_controller_invocations':0}
 put(d/'RESTORE_RECEIPT.json',receipt);return receipt

def commit_copy(path,expected_sha):
 need(sha(path)==expected_sha,'inventory SHA mismatch');manifest=read(path);need(manifest['source_qualification_sha256']==QS and manifest['payload_bytes']<=CAP and manifest['archive_implementation_sha256']==sha(Path(__file__)),'inventory identity/cap/tool SHA');rows=manifest['members']
 for row in rows:
  p=Path(row['source_path']);need(stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink() and p.stat().st_size==row['size'] and sha(p)==row['sha256'],'inventory changed before commit')
 need(sha(BASE_RESOURCE)==BASE_SHA,'qualified copy resource reference changed');sp=importlib.util.spec_from_file_location('engineering_copy_readonly_resources',BASE_RESOURCE);r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
 def gate(copies):
  sample=r.snapshot(str(J),'EP_TAG_LIFETIME_ENGINEERING_COPY_ONLY_REFERENCE',phase='admission',own_write_bytes=max(16*M,copies*manifest['payload_bytes']+16*M),own_memory_cap_bytes=G)
  need(sample['consistent_snapshot'] and sample['resource_pass'],'COPY_ONLY_RESOURCE_HOLD')
  mount=json.loads(subprocess.check_output(['findmnt','-J','-T',str(NAS)],text=True))['filesystems'][0]
  need(mount['fstype']=='fuse.sshfs' and mount['source']=='admin-wcx@10.208.130.164:/home/shared','not genuine164');need(os.statvfs(NAS).f_bavail*os.statvfs(NAS).f_frsize>=G,'164 bounded write headroom');return sample
 resource.setrlimit(resource.RLIMIT_AS,(384*M,384*M));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.nice(10)
 own=(A/'ENGINEERING_ARCHIVE_COPY.lock').open('a+b');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB);gate(2)
 receiver=RECEIVER.open('rb');fcntl.flock(receiver,fcntl.LOCK_EX|fcntl.LOCK_NB)
 ident=str(uuid.uuid4());b=NAS/('20261026_ep_tag_lifetime_engineering_final_'+ident);b.mkdir(mode=0o700);put(b/'MEMBER_MANIFEST.json',manifest)
 archive=b/'ENGINEERING_EVIDENCE.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
   with tarfile.open(fileobj=gz,mode='w|') as tar:
    for row in rows:
     p=Path(row['source_path']);need(sha(p)==row['sha256'],'source member drift');info=tarfile.TarInfo(row['name']);info.size=row['size'];info.mode=row['mode'];info.mtime=0;info.type=tarfile.REGTYPE
     with p.open('rb') as src:tar.addfile(info,src)
     need(sha(p)==row['sha256'],'source changed during archive')
  raw.flush();os.fsync(raw.fileno())
 need(archive.stat().st_size<=CAP,'compressed archive cap');tool=b/'RESTORE_ENGINEERING_EVIDENCE.py'
 with Path(__file__).open('rb') as src,tool.open('xb') as dst:
  for block in iter(lambda:src.read(M),b''):dst.write(block)
  dst.flush();os.fsync(dst.fileno())
 need(sha(tool)==sha(Path(__file__)),'restore tool copy SHA')
 put(b/'COMMIT.json',{'uuid':ident,'manifest_sha256':sha(b/'MEMBER_MANIFEST.json'),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'restore_tool_sha256':sha(tool),'source_inventory_sha256':expected_sha})
 receiver.close();parent=A/'engineering_evidence_restores';parent.mkdir(exist_ok=True);restores=[]
 for i in (1,2):
  gate(3-i);target=parent/(ident+'_'+str(i));cp=subprocess.run(['/usr/bin/python3','-B',str(tool),'--restore-bundle',str(b),'--destination',str(target)],capture_output=True,text=True,timeout=300);need(cp.returncode==0,'independent restore failed: '+cp.stderr[-2000:]);restores.append(json.loads(cp.stdout))
 receipt={'schema':'EP_LIFETIME_FINAL_ENGINEERING_ARCHIVE_RECEIPT_V1','status':'ENGINEERING_GENUINE164_STREAM_GZIP_TWO_NATIVE_EXTRACTIONS_PASS','bundle':str(b),'manifest_sha256':sha(b/'MEMBER_MANIFEST.json'),'archive_sha256':sha(archive),'compressed_bytes':archive.stat().st_size,'uncompressed_bytes':manifest['payload_bytes'],'source_inventory_sha256':expected_sha,'source_qualification_sha256':QS,'restores':restores,'new_model_or_help_or_budget_operations':0,'source_keep':True,'final_review_documents_included':False}
 output=A/('ENGINEERING_ARCHIVE_RECEIPT.'+ident+'.json');put(output,receipt);return {'receipt_path':str(output),'receipt':receipt}

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--extra-root',action='append',default=[]);a.add_argument('--extra-file',action='append',default=[]);a.add_argument('--inventory-output');a.add_argument('--inventory');a.add_argument('--inventory-sha256');a.add_argument('--commit-copy',action='store_true');a.add_argument('--restore-bundle');a.add_argument('--destination');args=a.parse_args()
 if args.restore_bundle:need(args.destination,'restore destination required');print(json.dumps(restore(args.restore_bundle,args.destination)));return
 if args.commit_copy:need(args.inventory and args.inventory_sha256,'main-reviewed exact inventory required');print(json.dumps(commit_copy(args.inventory,args.inventory_sha256)));return
 result=inventory(args.extra_root,args.extra_file)
 if args.inventory_output:
  out=Path(args.inventory_output);need(out.resolve().is_relative_to(A.resolve()),'inventory output confined to agent_a');put(out,result);print(json.dumps({'mode':'INVENTORY_ONLY_NO_NAS_WRITES','path':str(out),'sha256':sha(out),'files':result['files'],'payload_bytes':result['payload_bytes']}))
 else:print(json.dumps(result,indent=2))
if __name__=='__main__':main()
