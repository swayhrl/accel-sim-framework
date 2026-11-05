from pathlib import Path
import hashlib,json
O=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
put('INTERFACE_SEQUENCE.json',{'status':'INTERFACE_GUIDANCE_ONLY_INSTALLER_DRAFT_NOT_REVIEWED',
 'E_frozen_manifest_sha256':'1f77920ab9086771dd036212e90ef3bba6bee0f0a459c559795d5ce335aaf14f',
 'E_extra_sha256':'702a0a3e27645ece6cf15a68c598bce4067b69132a74c1fb1e3cfde03a621c3b',
 'E_consumer_sha256':'de70cede8876fca5bf909f5b8d685b74da43a6ca08880e18e09d59e924c0225b',
 'critical_exposure':'Registered primary points are already visible: before B worker assignment, not merely before IR reader assignment.',
 'installation_0_new_V3_consumption_requires_prearm_fence':True,
 'actual4_prerequisite_mandatory':True,'authority_mutators':'Supplied locked q plus pure/file validation only; no authority read/replay reentry.',
 'consumer_before_worker':True,'IR_view_last':True,'preserve_primary350':True,'recovery_union_authorized':False,
 'failure':'Keep mandatory selected B/E and precise HOLD fences after any possible exposure; cached pending cannot fall back to old entry.',
 'new_grants':0,'models_started':0,'production_changes':0,'tests_rerun':0,'Git_actions':0})
h=put('MANIFEST.json',{'schema':'DTC_E_V3_INSTALL_INTERFACE_GUIDANCE_MANIFEST','files':[{'path':p.name,'sha256':sha(p)}for p in sorted(O.iterdir())if p.is_file()and p.name!='MANIFEST.json']})
print(json.dumps({'manifest_sha256':h,'sequence_sha256':sha(O/'SEQUENCE.md')}))
