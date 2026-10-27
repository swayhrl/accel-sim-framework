import pathlib,json,subprocess,hashlib
L=pathlib.Path(__file__).parent
remote='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/agents/E'
m=json.loads((L/'LATEST_MANIFEST_SUPPLEMENT.json').read_bytes());names=[x['name'] for x in m['files']]+['LATEST_MANIFEST_SUPPLEMENT.json']
names += [p.name for p in L.glob('*_PRE_RECONCILIATION.*')]
assert 'DELIVERY_MANIFEST.json' not in names
subprocess.run(['scp',*[str(L/n) for n in names],'hrl-174-new:'+remote+'/'],check=True)
code="""import pathlib,json,hashlib
A=pathlib.Path(%r)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
man=json.loads((A/'LATEST_MANIFEST_SUPPLEMENT.json').read_bytes())
rec=json.loads((A/'MANIFEST_IDENTITY_RECONCILIATION.json').read_bytes())
for f in man['files']:assert h(A/f['name'])==f['sha256'],f['name']
for n,s in rec['prior_files_sha256_164_original'].items():assert h(A/n)==s,n
assert h(A/'DELIVERY_MANIFEST_WINDOWS_ORIGINAL_BYTES.json')==rec['windows_original']['sha256']
assert h(A/'DELIVERY_MANIFEST_164_ORIGINAL_BYTES.json')==rec['164_original']['sha256']
result={'all_new_files_exact_SHA256_verified_on164':True,'all_original164_files_preserved_at_own_original_SHA256':True,'both_manifest_original_byte_copies_preserved':True,'original164_manifest_sha256':h(A/'DELIVERY_MANIFEST.json'),'supplement_sha256':h(A/'LATEST_MANIFEST_SUPPLEMENT.json'),'addendum_sha256':h(A/'LATEST_ACCEPTED_ADDENDUM.json')}
print(json.dumps(result))
"""%remote
r=subprocess.run(['ssh','hrl-174-new','python3','-'],input=code,text=True,capture_output=True,check=True)
for n,s in json.loads((L/'MANIFEST_IDENTITY_RECONCILIATION.json').read_bytes())['prior_files_sha256_windows_original'].items():assert hashlib.sha256((L/n).read_bytes()).hexdigest()==s,n
print(r.stdout)
