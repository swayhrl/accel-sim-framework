"""Metadata-only exact target_config supplement. Never activates or reads/stat traces."""
from pathlib import Path
import json,hashlib,ast,os,subprocess,time
T=Path('/root/share/mnt164/huangrulin/traces/receipts/sm70_public_bootstrap_preparation_20261025_v1');CAS=T/'proofs/sha256';CID='e2b1a814a201f7f5dd95c55c61a94f04069690dd18ecfabd89c9f88dc7ae19c7';PKG=Path('/root/share/mnt164/huangrulin/traces/tools/versions')/CID
canon=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();H=lambda b:hashlib.sha256(b).hexdigest()
def putraw(b):
 p=CAS/H(b)
 if p.exists():assert p.read_bytes()==b
 else:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
  assert p.read_bytes()==b
 return {'path':str(p),'bytes':len(b),'sha256':H(b)}
def readpin(p,h):
 b=Path(p).read_bytes();assert H(b)==h;return b
oldraw=readpin(CAS/'d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0','d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0');old=json.loads(oldraw)
manifest_raw=readpin(PKG/'CODE_MANIFEST.json','312c2ea4e05ca0bb163d2f8a8abdcdb2676131befc32d5fce061158ac035e392');manifest=json.loads(manifest_raw);assert manifest['code_version_id']==CID
refs=[];uses=[]
for name,row in manifest['files'].items():
 q=PKG/name;b=q.read_bytes();assert len(b)==row['bytes']and H(b)==row['sha256'];refs.append({'name':name,'bytes':len(b),'sha256':H(b)})
 if q.suffix=='.py':
  tree=ast.parse(b,filename=str(q))
  for node in ast.walk(tree):
   if isinstance(node,ast.Subscript)and isinstance(node.value,ast.Name)and node.value.id=='spec'and isinstance(node.slice,ast.Constant)and isinstance(node.slice.value,str):uses.append({'key':node.slice.value,'file':name,'line':node.lineno})
required={x['key']for x in uses};assert required-set(old)=={'target_config','test_dimensions'}
profile_raw=(PKG/'PROFILE.json').read_bytes();profile=json.loads(profile_raw);actual=subprocess.check_output(['findmnt','-T',profile['nas_mount_root'],'-n','-o','SOURCE,FSTYPE,TARGET'],text=True).strip().split();assert actual==[profile['nas_endpoint'],'fuse.sshfs',profile['nas_mount_root']]
assert os.uname().nodename==profile['expected_host']and str(Path('/proc/self/ns/mnt').readlink())==profile['expected_mount_namespace']and Path('/root/data').stat().st_dev==profile['native_device']
endpoint=profile['nas_endpoint'];remote=endpoint.split(':',1)[1];assert remote=='/home/shared'and profile['nas_mount_root']=='/root/share/mnt164';cfg={'endpoint':endpoint,'mount_root':profile['nas_mount_root'],'remote_root':remote}
new=dict(old);new['target_config']=cfg;assert {k:v for k,v in new.items()if k!='target_config'}==old;assert required-set(new)=={'test_dimensions'}and 'test_dimensions'not in new
assert new['schema']=='SM70_BINDING_INTEGRATION_SPEC_V3_TEMPLATE_UNRESOLVED_NOT_EXECUTABLE'and new['body_reads_authorized']is False and new['scientific_starts_authorized']is False and new['protected_after_ref']is None and new['unresolved_inputs']==old['unresolved_inputs']
assert (new['expected_assets'],new['expected_objects'],new['expected_declared_members'],new['expected_unique_bytes'])==(125,22769,25149,972603859656)
newref=putraw(canon(new));profileref=putraw(profile_raw);mountref=putraw(canon({'source':actual[0],'fstype':actual[1],'target':actual[2],'host':os.uname().nodename,'mount_namespace':str(Path('/proc/self/ns/mnt').readlink()),'native_device':Path('/root/data').stat().st_dev,'unix':time.time()}));manifestref=putraw(manifest_raw)
report={'status':'METADATA_ONLY_TARGET_CONFIG_ADDED_UNEXECUTABLE_TEMPLATE_V5','schema':'SM70_BOOTSTRAP_TARGET_CONFIG_COMPLETENESS_V5','original_v4_template_ref':{'path':str(CAS/'d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0'),'sha256':'d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0'},'prepared_template_ref':newref,'target_config':cfg,'configuration_source':{'sealed_profile_ref':profileref,'sealed_code_manifest_ref':manifestref,'actual_findmnt_and_host_ref':mountref},'exact_delta':'Only target_config added;all existingV4 keys and values unchanged','all_direct_spec_key_uses':uses,'production_missing_direct_keys_after_addition':[],'qualification_only_test_dimensions_deliberately_absent':True,'code_members_revalidated':refs,'Source2_pending':True,'protected_after_ref':None,'body_reads_authorized':False,'activation':False,'catalog_CURRENT_or_commands_or_delegates_or_markers_modified':False,'original_source_or_template_bytes_modified':False,'trace_payload_reads':0,'target_trace_stat_calls':0,'scientific_starts':0,'source_KEEP':True,'release_bytes':0,'unresolved_inputs':new['unresolved_inputs'],'unix':time.time()};reportref=putraw(canon(report))
commit={'schema':'SM70_BOOTSTRAP_TARGET_CONFIG_ONLY_INCREMENT_V5','prepared_template_ref':newref,'report_ref':reportref,'prior_COMMIT_ref':{'path':str(T/'COMMIT_V4.json'),'sha256':H((T/'COMMIT_V4.json').read_bytes())},'metadata_only':True,'Source2_pending':True,'activation':False,'body_read_authorized':False,'protected_after_ref':None}
b=canon(commit);q=T/'COMMIT_V5.json'
with q.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
assert q.read_bytes()==b and H((CAS/'d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0').read_bytes())=='d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0'
print(json.dumps({'COMMIT':{'path':str(q),'sha256':H(b)},'template':newref,'report':reportref,'target_config':cfg,'activation':False,'Source2_pending':True}))
