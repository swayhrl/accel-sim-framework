import os,pathlib,json,subprocess,shlex,hashlib,sys
root=pathlib.Path(os.environ['TASK_DATA']);plan=json.loads((root/'archive_plan.json').read_text());dest=plan['destination'];quote=shlex.quote
verify=root/'verify_node164.py'
verify.write_text('''import pathlib,json,hashlib,tarfile,subprocess,sys
base=pathlib.Path(sys.argv[1]);archive=base/'AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1_STOP_RAW.tar.gz';expected=sys.argv[2];expected_manifest=sys.argv[3]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
assert digest(archive)==expected,'ARCHIVE_SHA256_MISMATCH'
with tarfile.open(archive) as t:
 for member in t.getmembers():
  assert member.isfile() or member.isdir(),'unexpected link/special file'
  assert (base/member.name).resolve().is_relative_to(base.resolve()),'unsafe archive member'
subprocess.run(['tar','--no-same-owner','--no-same-permissions','-xzf',str(archive),'-C',str(base)],check=True)
payload=base/'payload';manifest=payload/'SHA256SUMS';assert digest(manifest)==expected_manifest
rows=[]
for line in manifest.read_text(encoding='utf-8').splitlines():
 h,rel=line.split('  ',1);p=payload/rel;actual=digest(p);assert actual==h,rel
 rows.append({'asset':rel,'bytes':p.stat().st_size,'sha256':actual})
receipt={'status':'NODE164_RAW_READBACK_PASS','authority_mount':subprocess.check_output(['findmnt','-T',str(base),'-n','-o','SOURCE,FSTYPE'],text=True).strip(),'destination':str(base),'archive_bytes':archive.stat().st_size,'archive_sha256':digest(archive),'manifest_items_verified':len(rows),'manifest_sha256':digest(manifest),'verified_payload_bytes':sum(r['bytes'] for r in rows),'verified_files':rows}
(base/'NODE164_READBACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\\n',encoding='utf-8')
print(json.dumps(receipt))
''',encoding='utf-8')
# Only create the new task destination. Never overwrite or move historical assets.
if '--resume-verification' not in sys.argv:
 subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','hrl174new','test ! -e '+quote(dest)+' && mkdir -p '+quote(dest)],check=True)
 subprocess.run(['scp',plan['archive'],str(verify),'hrl174new:'+dest+'/'],check=True)
else:
 # Bounded wrapper repair at the same task destination; archive identity is checked first remotely.
 subprocess.run(['scp',str(verify),'hrl174new:'+dest+'/'],check=True)
cmd='python3 '+quote(dest+'/verify_node164.py')+' '+quote(dest)+' '+quote(plan['archive_sha256'])+' '+quote(plan['payload_manifest_sha256'])
r=subprocess.run(['ssh','-o','BatchMode=yes','hrl174new',cmd],check=True,capture_output=True,text=True)
receipt=json.loads(r.stdout);assert receipt['manifest_items_verified']==plan['payload_manifest_items'];assert '10.208.130.164' in receipt['authority_mount']
(root/'NODE164_READBACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
pack=pathlib.Path('docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1');(pack/'NODE164_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_files'},indent=2))
