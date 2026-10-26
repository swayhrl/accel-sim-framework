"""Rehydrate one verified cold restore to native2128 before fresh native checking."""
import pathlib,json,hashlib,os,stat,shutil,uuid,argparse,importlib.util,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/restore_cold_tier_20261026_v1';T=P('/root/data/dtc_main_v100_sweep_20261025_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def verify(root,entries):
 observed=[]
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=P(base)/name;r=dict(path=str(p.relative_to(root)));s=p.lstat()
   if stat.S_ISLNK(s.st_mode):r.update(type='symlink',target=os.readlink(p))
   elif stat.S_ISDIR(s.st_mode):r.update(type='directory')
   elif stat.S_ISREG(s.st_mode):r.update(type='file',bytes=s.st_size,sha256=sha(p))
   else:raise RuntimeError('unexpected entry type')
   observed.append(r)
 assert sorted(observed,key=lambda x:x['path'])==entries,'restore bytes/types differ'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cohort',required=True);ap.add_argument('--dry-run',action='store_true');args=ap.parse_args();summary=read(D/'SUMMARY.json');assert sha(D/'TRANSACTIONS.jsonl')==summary['TRANSACTIONS_sha256'];rows=[json.loads(x)for x in(D/'TRANSACTIONS.jsonl').read_text().splitlines()];matched=[r for r in rows if r['cohort']==args.cohort];assert len(matched)==1;r=matched[0];assert sha(r['manifest_path'])==r['manifest_sha256'];m=read(r['manifest_path']);src=P(r['cold_164_path']);dest=P(r['historic_native_restore_path']);assert m['target']==str(src)and m['source']==str(dest);allowed=[T/'DTC/run/recovery',F/'validation/DTC/run/recovery'];assert dest.parent in allowed and dest.parent.stat().st_dev==2128;verify(src,m['entries'])
 if not dest.is_symlink():assert dest.is_dir()and dest.stat().st_dev==2128;verify(dest,m['entries']);print(json.dumps(dict(status='ALREADY_NATIVE_VERIFIED_BYTES',cohort=args.cohort)));return
 assert dest.resolve()==src.resolve();spec=importlib.util.spec_from_file_location('rehydrate_current_resources',F/'ops/revision19/resource_accounting_v1.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);one=next((T/'control').glob('E2-AEV100-*_SPEC.json'));resource=a.resources(read(one),False);needed=resource['required_free_bytes']+r['bytes']+16*1024**2;v=os.statvfs(dest.parent);assert v.f_bavail*v.f_frsize>needed,'storage HOLD; do not rehydrate into reserved native space'
 if args.dry_run:print(json.dumps(dict(status='READ_ONLY_REHYDRATION_READY',cohort=args.cohort,bytes=r['bytes'],required_native_free_bytes=needed)));return
 writing=dest.with_name('.NATIVE_REHYDRATE_'+dest.name+'_'+uuid.uuid4().hex);writing.mkdir()
 for e in m['entries']:
  if e['type']=='directory':(writing/e['path']).mkdir(parents=True,exist_ok=True)
 for e in m['entries']:
  if e['type']=='file':p=writing/e['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/e['path'],p)
 for e in m['entries']:
  if e['type']=='symlink':(writing/e['path']).symlink_to(e['target'])
 verify(writing,m['entries']);assert writing.stat().st_dev==2128 and dest.is_symlink()and dest.resolve()==src.resolve();linkpre=dest.with_name('.COLD_LINK_PREIMAGE_'+dest.name+'_'+uuid.uuid4().hex);dest.rename(linkpre)
 try:writing.rename(dest);verify(dest,m['entries']);assert dest.stat().st_dev==2128
 except BaseException:
  if not dest.exists():linkpre.rename(dest)
  raise
 linkpre.unlink();proof=dict(status='NATIVE2128_REHYDRATED_EXACT_MANIFEST_BYTES',cohort=args.cohort,native_path=str(dest),cold_copy_retained=str(src),manifest_sha256=r['manifest_sha256'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scientific_ledger_or_original_archive_receipt_mutations=0)
 with(D/'REHYDRATIONS.jsonl').open('a')as f:f.write(json.dumps(proof)+'\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(proof))
if __name__=='__main__':main()
