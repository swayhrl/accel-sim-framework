from pathlib import Path
import hashlib,importlib.util,json,tempfile
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
V=A/'agents/M_unified_publication_proposal_v2';O=A/'agents/M_unified_publication_timeout_supplement_v1';O.mkdir(exist_ok=True)
p=V/'unified_watch_publish_source_proposal.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('V2_only_cpu',p);w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w);m=w.source_module()
calls=[]
def deny(*a,**kw):calls.append(a);raise AssertionError('No actual Git allowed')
config=json.loads((A/'agents/M_unified_publication_caller_template_v1/UNARMED_PUBLICATION_ENABLE.template.json').read_bytes())
assert config['enabled']is False
try:m.GitPublication(A,config,runner=deny)
except ValueError as e:assert 'not Main enabled'in str(e)
else:raise AssertionError('defaultunarmed accepted')
assert not calls
assert m.__file__==str(p)
report=json.loads((A/'agents/M_clean_successor_unified_consumer_v2/qualified_actual_projection_v2/ORACLE_LIVE_RESULTS.json').read_bytes())
matrix=json.loads((A/'control/authority/FUTURE_DH_ORACLE_MATRIX.json').read_bytes())
with tempfile.TemporaryDirectory(dir=O,prefix='CPU_PAYLOAD_')as d:
 r=Path(d);dr=r/'derived';dr.mkdir();(dr/'CPU_ONLY.json').write_text('{}\n')
 m.build_payload(report,matrix,dr,r/'leaf','CPU_BRIDGE_TEST')
 scope=json.loads((r/'leaf/PUBLICATION_SCOPE.json').read_bytes())
 assert scope['watcher_implementation_sha256']==sha(p)
 assert scope['watcher_implementation_sha256']!='74d8b0ee8661d2d8557ac83c56519fa3d5cf1e310a47ba5b531ed99342824fc1'
out={'status':'PASS_V2_DEFAULT_UNARMED_AND_WATCHER_SHA_CPU','cases':3,'default_enable_false_rejected_before_Git':True,'subprocess_Git_calls':len(calls),'module_file_is_actual_V2':m.__file__,'payload_watcher_sha256':sha(p),'actual_Git':0,'publisher_started':False}
(O/'CPU_QUALIFICATION.fixed.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
files=sorted(x for x in O.iterdir()if x.is_file()and x.name!='MANIFEST.fixed.json')
mf={'schema':'DTC_PUBLISHER_V2_MINIMAL_SUPPLEMENT_V1','members':[{'path':x.name,'bytes':x.stat().st_size,'sha256':sha(x)}for x in files]}
mp=O/'MANIFEST.fixed.json';mp.write_text(json.dumps(mf,sort_keys=True,indent=2)+'\n')
print(json.dumps({'root':str(O),'manifest_sha256':sha(mp),'CPU_qualification_sha256':sha(O/'CPU_QUALIFICATION.fixed.json')}))
