import pathlib,os,json,subprocess,shlex,hashlib
root=pathlib.Path(os.environ['TASK_DATA']);plan=json.loads((root/'ARCHIVE_PLAN.json').read_text());dest=plan['destination'];q=shlex.quote
verify=root/'verify_node164.py';verify.write_text('''import pathlib,sys,json,tarfile,subprocess,hashlib
base=pathlib.Path(sys.argv[1]);archive=base/pathlib.Path(sys.argv[2]).name
expected=sys.argv[3];manifest_expected=sys.argv[4]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
assert sha(archive)==expected
with tarfile.open(archive) as t:
 for m in t.getmembers():
  assert m.isfile() or m.isdir()
  assert (base/m.name).resolve().is_relative_to(base.resolve())
subprocess.run(['tar','--no-same-owner','--no-same-permissions','-xzf',str(archive),'-C',str(base)],check=True)
payload=base/'payload';manifest=payload/'SHA256SUMS';assert sha(manifest)==manifest_expected
records=[]
for line in manifest.read_text().splitlines():
 expected,rel=line.split('  ',1);p=payload/rel;actual=sha(p);assert actual==expected,rel
 records.append({'asset':rel,'bytes':p.stat().st_size,'sha256':actual})
receipt={'status':'NODE164_RAW_READBACK_PASS','authority_mount':subprocess.check_output(['findmnt','-T',str(base),'-n','-o','SOURCE,FSTYPE'],text=True).strip(),'destination':str(base),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'manifest_sha256':sha(manifest),'manifest_items':len(records),'payload_bytes':sum(r['bytes'] for r in records),'verified_files':records}
(base/'NODE164_READBACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\\n',encoding='utf-8')
print(json.dumps(receipt))
''',encoding='utf-8')
subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','hrl174new','test ! -e '+q(dest)+' && mkdir -p '+q(dest)],check=True)
subprocess.run(['scp',plan['archive'],str(verify),'hrl174new:'+dest+'/'],check=True)
cmd='python3 '+q(dest+'/verify_node164.py')+' '+q(dest)+' '+q(pathlib.Path(plan['archive']).name)+' '+plan['archive_sha256']+' '+plan['manifest_sha256'];r=subprocess.run(['ssh','-o','BatchMode=yes','hrl174new',cmd],text=True,capture_output=True)
(root/'NODE164_PUBLICATION.log').write_text(r.stderr,encoding='utf-8');r.check_returncode();receipt=json.loads(r.stdout);assert receipt['manifest_items']==plan['manifest_items'] and receipt['payload_bytes']==plan['payload_bytes'];assert '10.208.130.164' in receipt['authority_mount']
(root/'NODE164_READBACK_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');pack=pathlib.Path('docs/ai_workload_research/review_packs/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CANARY_V1');(pack/'NODE164_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in receipt.items() if k!='verified_files'},indent=2))
