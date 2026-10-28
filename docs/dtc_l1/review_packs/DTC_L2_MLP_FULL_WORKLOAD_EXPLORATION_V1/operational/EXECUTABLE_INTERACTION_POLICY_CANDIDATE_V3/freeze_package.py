"""Finalize only this independent E candidate directory and its small review zip."""
import datetime,hashlib,json,pathlib,zipfile
P=pathlib.Path;H=P(__file__).resolve().parent
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
names=['interaction_policy.py','owner_adapter.py','resource_qualifier.py','qualify_policy.py','qualify_journal.py',
 'qualify_actual_readonly.py','freeze_package.py','README.md','CONTRACT_DIFF.md','MAIN_INTEGRATION.md',
 'CPU_QUALIFICATION.json','JOURNAL_CPU_QUALIFICATION.json','ACTUAL_RESOURCE_QUALIFICATION.json',
 'ACTUAL_READONLY_COUPLING.json','SCIENTIFIC_CONTRACT.json']
cpu=read(H/'CPU_QUALIFICATION.json');journal=read(H/'JOURNAL_CPU_QUALIFICATION.json');actual=read(H/'ACTUAL_READONLY_COUPLING.json')
assert cpu['status']=='PASS'and cpu['count']==43
assert journal['status']=='PASS'and journal['count']==20
for n,pin in cpu['candidate_sources'].items():assert sha(H/n)==pin
assert actual['status']=='PASS_READONLY_ACTUAL_PRIMARY_R2_TRANSPORT9A_F21_A7_V3_CHAIN'
contract=read(H/'SCIENTIFIC_CONTRACT.json')
for pin in contract['source_pins']:assert sha(pin['path'])==pin['sha256']
proofs=read(H/'ACTUAL_RESOURCE_QUALIFICATION.json')['proofs']
assert len(proofs)==2 and all(p['status']=='PASS_SEPARATE_COMBINATION_RESOURCE_QUALIFICATION'and len(p['cell_forecasts'])==35 for p in proofs)
for proof in proofs:
 for pin in proof['source_pins']:assert sha(pin['path'])==pin['sha256']
manifest=dict(schema='DTC_L2_MLP_EXECUTABLE_INTERACTION_V3_REVIEW_MANIFEST',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 status='FROZEN_CANDIDATE_NOT_PUBLISHED_NOT_INSTALLED',files=[dict(path=n,sha256=sha(H/n),bytes=(H/n).stat().st_size)for n in names],
 source_pins=contract['source_pins'],CPU_checks=43,journal_resource_CPU_checks=20,actual_readonly_coupling='PASS',
 new_production_grants=0,model_starts=0,production_changes=0,primary350_unchanged=True,original_M16_HOLD=True,R2_automatic_union=False,
 policy='six fixed structural seeds + four wide ablations +14 fixed conditional ladders + mandatory distinct moderate/high uniform CH35',
 live_canary_and_installation='MAIN_ONLY_AFTER_REVIEW_PUBLICATION',
 limitations=['Forecast-chain compatibility is not measured new-profile peak RSS','Original ratified forecast contains inherited128MiB margin, not a new sizeof bound',
 'Sparse contextual search is not exhaustive or a physical performance upper bound','Original engineering-negative manual review remains required'])
(H/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
z=H/'INTERACTION_POLICY_V3_REVIEW.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED)as out:
 for n in names+['MANIFEST.json']:out.write(H/n,n)
print(json.dumps(dict(status='FROZEN_CANDIDATE',manifest_sha256=sha(H/'MANIFEST.json'),zip_sha256=sha(z),zip_bytes=z.stat().st_size,
 policy_sha256=sha(H/'interaction_policy.py'),owner_sha256=sha(H/'owner_adapter.py'),resource_callback_sha256=sha(H/'resource_qualifier.py'))))
