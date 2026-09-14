import hashlib,json,re,secrets,datetime,shutil
from pathlib import Path
STATUSES={"FORMAL","MECHANISM_ONLY","DIAGNOSTIC","PRE_FIX","OBSOLETE","INVALID"}
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def run_id(model,scenario,phase,instrument,target):
 s=lambda x:re.sub(r"[^a-z0-9]+","-",x.lower()).strip("-")
 return f"C16R_{s(model)}_{s(scenario)}_{s(phase)}_{s(instrument)}_{s(target)}_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{secrets.token_hex(6)}"
def inventory(d):
 out=[]
 for p in sorted(Path(d).rglob('*')):
  if p.is_symlink():raise ValueError('symlink')
  if p.is_file() and p.name not in {'RUN_MANIFEST.json','READY'}:out.append({'relative_path':str(p.relative_to(d)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
 return out
def finalize(staging,ready,manifest):
 s=Path(staging); r=Path(ready); rid=manifest['run_id']
 if (s/'CAPTURING').exists() or not inventory(s):raise ValueError('incomplete')
 if manifest.get('scientific_status') not in STATUSES:raise ValueError('status')
 dest=r/rid
 if dest.exists():raise FileExistsError('collision')
 manifest['artifacts']=inventory(s); (s/'RUN_MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n'); (s/'READY').write_text('READY\n'); shutil.move(str(s),str(dest)); return dest
def ack(ack,manifest_sha,dest):
 a=json.loads(Path(ack).read_text())
 if a.get('verification_status')!='PASS' or a.get('source_manifest_sha256')!=manifest_sha or a.get('destination_raw_path')!=dest:raise ValueError('ack')
 return True
