from pathlib import Path
import subprocess, json, hashlib, base64, shlex

local = Path(__file__).resolve().parent
remote = '/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/F'
manifest = json.loads((local/'MANIFEST.json').read_text(encoding='utf-8'))
files = list(manifest['files']) + ['MANIFEST.json']
payload = {'root':remote,'files':{name:base64.b64encode((local/name).read_bytes()).decode() for name in files},
           'expected':{name:hashlib.sha256((local/name).read_bytes()).hexdigest() for name in files}}
receiver = r'''
from pathlib import Path
import json,sys,base64,hashlib,datetime
p=json.load(sys.stdin)
root=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/F')
assert p['root']==str(root)
root.mkdir(parents=True,exist_ok=True)
checks=[]
for name,encoded in p['files'].items():
    assert Path(name).name==name and name not in ['.','..']
    dest=root/name
    assert dest.resolve(strict=False).parent==root.resolve()
    data=base64.b64decode(encoded)
    assert hashlib.sha256(data).hexdigest()==p['expected'][name]
    dest.write_bytes(data)
    actual=hashlib.sha256(dest.read_bytes()).hexdigest()
    assert actual==p['expected'][name]
    checks.append({'file':name,'sha256':actual,'bytes':len(data),'readback_pass':True})
freeze=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1/analysis/REPRESENTATIVE_FREEZE.json')
freeze_sha=hashlib.sha256(freeze.read_bytes()).hexdigest()
assert freeze_sha=='a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d'
receipt={'schema':'DTC_AGENT_F_164_ARCHIVE_RECEIPT_V1','root':str(root),'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':checks,'all_readback_pass':True,'v1_freeze_sha256_unchanged':freeze_sha,'model_starts':0,'writes_confined_to_agent_F':True}
(root/'ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
'''
r = subprocess.run(['ssh','hrl-174-new','python3 -c '+shlex.quote(receiver)],input=json.dumps(payload).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=100)
if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace'))
receipt=json.loads(r.stdout)
(local/'ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive_root':remote,'files':len(receipt['files']),'all_readback_pass':receipt['all_readback_pass'],'model_starts':0}))
