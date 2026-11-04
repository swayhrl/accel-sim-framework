import pathlib,json,hashlib,datetime
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');D=V/'agents/D_independent_review_v1'
base=V/'control/V1_REQUEST_IMMUTABLE_BASELINE.json';reg=pathlib.Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
b=json.loads(base.read_text());r=json.loads(reg.read_text());qq=r['registered_future_requests'];checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
for name,old in b['requests'].items():
 new=qq[name]
 ck(name+' fixed budget',new.get('budget')==old['budget'])
 ck(name+' zero remaining unspent',new.get('remaining')==old['remaining']==0)
 ck(name+' identical consumed cohort set',set(new['consumed'])==set(old['consumed']))
 for cohort,prev in old['consumed'].items():
  now=new['consumed'][cohort]
  for k in ['uuid','intent','intent_sha256','charged']:
   ck(cohort+' '+k,now.get(k)==prev.get(k))
 for k in ['owner','registration_authority','source_authority','specs']:
  if old.get(k) is not None:ck(name+' '+k,new.get(k)==old[k])
bad=[name for name in qq if ('PERF' in name.upper() and 'V2' in name.upper()) or 'CPU_PREPARATION' in name.upper()]
ck('No V2 performance scientific request registered',not bad)
p=D/'INDEPENDENT_V1_IDENTITY_PRESERVATION_CHECK.json';assert not p.exists();p.write_text(json.dumps({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'registry_path':str(reg),'registry_read_sha256':hashlib.sha256(reg.read_bytes()).hexdigest(),'baseline_path':str(base),'baseline_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'forbidden_matching_request_names':bad,'meaning':'Compared consumed UUID/intent/charge/cohort/specs/budget only; natural scientific closure metadata may evolve. Read-only snapshot, no lifecycle/raw reads/writes and no dispatcher/model launch.'},indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
