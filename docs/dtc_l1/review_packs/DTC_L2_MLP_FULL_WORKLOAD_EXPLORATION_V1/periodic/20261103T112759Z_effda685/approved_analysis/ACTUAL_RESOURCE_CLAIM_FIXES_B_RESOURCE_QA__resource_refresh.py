"""Inert Main-only positive resource forecast refresh; no grants or model starts.

prepare() is read-only. apply() requires the existing owner/aging lock and uses
only q/file CAS inside update_authority. Partial file publication reconciles
forward from the immutable proposal and exact old/new byte pairs.
"""
import pathlib,json,hashlib,copy,os,threading,contextlib,fcntl
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='PENDING_SYRK_RESOURCE_FORECAST_REFRESH_V1'
SCOPE_SHA='cd08c013af3b5c2f61cc028b73727818dbf3ae1196ce554a4861fd0429b13b65'
G=1024**3
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(v).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def science(s):
 v=copy.deepcopy(s);v.pop('estimated_peak_model_RAM_bytes')
 for k in ['max_process_tree_rss_bytes','max_process_tree_vms_bytes']:v['limits'].pop(k)
 return v
def pair(p,old,new):return dict(path=str(p),old_utf8=old.decode(),old_sha256=digest(old),new_utf8=new.decode(),new_sha256=digest(new))
def pure_pair(v):
 assert digest(v['old_utf8'].encode())==v['old_sha256']and digest(v['new_utf8'].encode())==v['new_sha256']
def scope_rows(path):
 assert digest(P(path).read_bytes())==SCOPE_SHA
 rows=read(path)['rows'];return {r['cohort']:r for r in rows}
def receipt_for(proposal):return dict(status='RESOURCE_REFRESH_COMMITTED_RECONCILED',proposal_sha256=digest(js(proposal)),cohorts=[i['cohort']for i in proposal['items']],new_grants=0,models_started=0)
def idle(root,c,q,claims):
 assert c not in q['consumed']and c not in claims,'SPENT_OR_INFLIGHT'
 assert not(root/'control/qualification_ledger'/(c+'.INTENT.json')).exists(),'INTENT_EXISTS'
def prepare(root,engine,res,history,policy,scope_path,claims):
 """Read-only exact current SYRK scope; no lock acquisition or file writes."""
 root=P(root);rows=scope_rows(scope_path);q=engine.registered()[2];items=[]
 persisted=read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 for c,row in sorted(rows.items()):
  if c not in q['admitted_specs']:continue
  s=engine.canonical(c)
  if s['program']!='SYRK'or c in q['consumed']:continue
  idle(root,c,q,claims);idle(root,c,q,persisted)
  assert s['host_cpu']is None and row['cohort']==c
  canonical=root/'control/specs'/(c+'.json');alias=root/'control'/(c+'_SPEC.json')
  old=canonical.read_bytes();assert old==alias.read_bytes()and digest(old)==q['admitted_specs'][c]
  f=res.forecast(s,history,policy);new=copy.deepcopy(s)
  new['estimated_peak_model_RAM_bytes']=max(s['estimated_peak_model_RAM_bytes'],f['predicted_peak_RAM_bytes'])
  hard=max(s['limits']['max_process_tree_rss_bytes'],f['proposed_process_tree_rss_cap_bytes'])
  new['limits']['max_process_tree_rss_bytes']=hard
  new['limits']['max_process_tree_vms_bytes']=max(s['limits']['max_process_tree_vms_bytes'],2*hard,hard+8*G)
  assert science(new)==science(s)
  files=[pair(canonical,old,js(new)),pair(alias,old,js(new))]
  db=root/'control/dispatch_bindings'/(c+'.json')
  if db.exists():
   raw=db.read_bytes();b=json.loads(raw)
   assert b['cohort']==c and b['canonical_spec_sha256']==digest(old)and type(b['host_cpu'])is int
   assert b['resolved_spec_sha256']==digest(js(dict(s,host_cpu=b['host_cpu'])))
   nb=dict(b,canonical_spec_sha256=digest(js(new)),resolved_spec_sha256=digest(js(dict(new,host_cpu=b['host_cpu']))))
   files.append(pair(db,raw,js(nb)))
  items.append(dict(cohort=c,forecast=f,old_spec_sha256=digest(old),new_spec_sha256=digest(js(new)),science_sha256=digest(js(science(s))),files=files,DB_present=db.exists()))
 assert len(items)==10,'EXPECTED_EXACT_TEN_UNSPENT_SYRK'
 return dict(schema=ID,request=REQ,root=str(root),scope_path=str(scope_path),scope_sha256=SCOPE_SHA,source_sha256=digest(P(__file__).read_bytes()),history_sha256=digest(js(history)),policy=copy.deepcopy(policy),items=items,qualification_only=root!=R,new_grants=0,refunds=0,models_started=0)
def immutable(p,b):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 try:
  with p.open('xb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 except FileExistsError:assert p.read_bytes()==b,'IMMUTABLE_PREIMAGE_DRIFT'
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def atomic(p,b):
 p=P(p);tmp=p.with_name('.'+p.name+'.resource-refresh')
 with tmp.open('wb')as h:h.write(b);h.flush();os.fsync(h.fileno())
 os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def validate_proposal(proposal,root):
 assert proposal['schema']==ID and proposal['request']==REQ and proposal['root']==str(root)
 assert proposal['source_sha256']==digest(P(__file__).read_bytes())
 rows=scope_rows(proposal['scope_path']);assert len(proposal['items'])==10
 assert len({i['cohort']for i in proposal['items']})==10
 for i in proposal['items']:
  c=i['cohort'];assert c in rows
  assert len(i['files'])==2+int(i['DB_present'])
  expected=[root/'control/specs'/(c+'.json'),root/'control'/(c+'_SPEC.json')]
  if i['DB_present']:expected.append(root/'control/dispatch_bindings'/(c+'.json'))
  assert [P(v['path'])for v in i['files']]==expected
  for v in i['files']:pure_pair(v)
  old=json.loads(i['files'][0]['old_utf8']);new=json.loads(i['files'][0]['new_utf8'])
  assert old['cohort']==new['cohort']==c and old['program']==new['program']=='SYRK'and old['host_cpu']is new['host_cpu']is None
  assert science(old)==science(new)and digest(js(science(old)))==i['science_sha256']
  assert i['old_spec_sha256']==i['files'][0]['old_sha256']and i['new_spec_sha256']==i['files'][0]['new_sha256']
  f=i['forecast'];hard=max(old['limits']['max_process_tree_rss_bytes'],f['proposed_process_tree_rss_cap_bytes'])
  assert new['estimated_peak_model_RAM_bytes']==max(old['estimated_peak_model_RAM_bytes'],f['predicted_peak_RAM_bytes'])
  assert new['limits']['max_process_tree_rss_bytes']==hard
  assert new['limits']['max_process_tree_vms_bytes']==max(old['limits']['max_process_tree_vms_bytes'],2*hard,hard+8*G)
  assert i['files'][1]['old_utf8']==i['files'][0]['old_utf8']and i['files'][1]['new_utf8']==i['files'][0]['new_utf8']
  if i['DB_present']:
   b=json.loads(i['files'][2]['old_utf8']);nb=json.loads(i['files'][2]['new_utf8'])
   assert nb==dict(b,canonical_spec_sha256=i['new_spec_sha256'],resolved_spec_sha256=digest(js(dict(new,host_cpu=b['host_cpu']))))
   assert b['canonical_spec_sha256']==i['old_spec_sha256']and b['resolved_spec_sha256']==digest(js(dict(old,host_cpu=b['host_cpu'])))
 return rows
def apply(proposal,engine,res,history,claims,aging,owner_assert):
 """Main invokes under its existing owner; never call from a dispatcher worker."""
 assert threading.current_thread()is threading.main_thread();owner_assert();root=P(proposal['root'])
 if root==R:assert os.getpid()==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 else:assert proposal['qualification_only']is True
 with aging.lock,contextlib.ExitStack()as locks:
  validate_proposal(proposal,root);q=engine.registered()[2]
  all_new=all(q['admitted_specs'].get(i['cohort'])==i['new_spec_sha256']and all(P(v['path']).read_bytes()==v['new_utf8'].encode()for v in i['files'])for i in proposal['items'])
  folder=root/'control/operational_amendments/pending_resource_forecast_refresh_v1'/digest(js(proposal))
  if all_new:
   assert (folder/'PREPARED.json').exists(),'MISSING_PREPARED_PROVENANCE'
   receipt=receipt_for(proposal)
   immutable(folder/'COMMITTED.json',js(receipt));return receipt
  persisted=read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
  before=copy.deepcopy(q)
  for i in proposal['items']:
   c=i['cohort'];idle(root,c,q,claims);idle(root,c,q,persisted)
   lock=locks.enter_context((root/'control/qualification_ledger'/(c+'.ATTEMPT.lock')).open('a+b'));fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   assert q['admitted_specs'][c]in[i['old_spec_sha256'],i['new_spec_sha256']]
   old=json.loads(i['files'][0]['old_utf8']);f=res.forecast(old,history,proposal['policy'])
   assert f==i['forecast'],'FORECAST_CHANGED_REPREPARE_NO_MUTATION'
   assert (root/'control/dispatch_bindings'/(c+'.json')).exists()==i['DB_present'],'BINDING_BORN_SINCE_PREPARE'
   for v in i['files']:
    assert P(v['path']).read_bytes()in[v['old_utf8'].encode(),v['new_utf8'].encode()],'FILE_CAS_DRIFT'
    immutable(folder/'preimages'/(v['old_sha256']+'.json'),v['old_utf8'].encode())
  immutable(folder/'PREPARED.json',js(proposal))
  def mutate(reg):
   # PURE FILE/q CAS ONLY: no engine/authority/registry/forecast calls in EX.
   current=reg['registered_future_requests'][REQ];assert current==before,'AUTHORITY_CHANGED_REPREPARE'
   assert read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']==persisted
   for i in proposal['items']:
    c=i['cohort'];idle(root,c,current,persisted)
    for v in i['files']:assert P(v['path']).read_bytes()in[v['old_utf8'].encode(),v['new_utf8'].encode()]
   for i in proposal['items']:
    for v in i['files']:atomic(v['path'],v['new_utf8'].encode())
    current['admitted_specs'][i['cohort']]=i['new_spec_sha256']
   check=copy.deepcopy(current);check['admitted_specs']=before['admitted_specs'];assert check==before
  engine.update_authority(mutate)
  after=engine.registered()[2];check=copy.deepcopy(after);check['admitted_specs']=before['admitted_specs'];assert check==before
  for i in proposal['items']:
   assert after['admitted_specs'][i['cohort']]==i['new_spec_sha256']
   if i['DB_present']:assert engine.spec_for(i['cohort'])['host_cpu']==json.loads(i['files'][2]['old_utf8'])['host_cpu']
  receipt=receipt_for(proposal)
  immutable(folder/'COMMITTED.json',js(receipt));return receipt
