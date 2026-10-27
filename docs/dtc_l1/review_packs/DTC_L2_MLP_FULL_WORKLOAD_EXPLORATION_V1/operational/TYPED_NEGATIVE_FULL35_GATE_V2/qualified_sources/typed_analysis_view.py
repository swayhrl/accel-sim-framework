"""Explicit sidecar view; never writes original summary/RESULT/receipt namespace.
Every call invokes the pinned real bundle verifier anew before trusting closure.
"""
import collections,copy,hashlib,json,pathlib,stat
from terminal_gate import TYPED,private_module,recommend

STATUS='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED'

def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def load_verified_certificate(value,binding,verifier):
 # Real scan verifier returns an exact certificate PATH, never a parsed object.
 assert type(value['certificate'])is str,'Verifier certificate must be an exact path'
 bundle=pathlib.Path(binding['bundle_path']);p=pathlib.Path(value['certificate'])
 assert bundle.is_absolute()and p.is_absolute()
 assert p.name=='ENGINEERING_TERMINAL_NEGATIVE.json'and p==bundle/p.name
 assert p.parent==bundle and bundle.parent==pathlib.Path(verifier.PROD)
 for component in (p,*p.parents):
  assert not stat.S_ISLNK(component.lstat().st_mode),'Symlink in certificate path'
 before=p.lstat();assert stat.S_ISREG(before.st_mode)
 raw=p.read_bytes();after=p.lstat()
 stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 assert stamp(before)==stamp(after),'Certificate changed during read'
 assert hashlib.sha256(raw).hexdigest()==value['certificate_sha256']==binding['certificate_sha256']
 cert=json.loads(raw)
 assert cert['schema']=='L2_MLP_ENGINEERING_TERMINAL_NEGATIVE_V1'
 assert cert['cohort']==binding['cohort']and cert['uuid']==binding['uuid']
 assert cert['performance_accepted']is False and cert['accepted_cycles']is None
 return cert

def project(raw_summary,bindings,verifier_path,verifier_sha256):
 view=copy.deepcopy(raw_summary);proofs={}
 verifier=private_module(verifier_path,verifier_sha256)
 for binding in bindings:
  value=verifier.verify_bundle(binding['bundle_path'],verifier_sha256)
  c=binding['cohort'];uuid=binding['uuid'];digest=binding['input_digest']
  assert c not in proofs,'Duplicate engineering-negative binding'
  assert value['status']==STATUS and value['cohort']==c and value['uuid']==uuid
  assert value['performance_accepted']is False and value['accepted_cycles']is None
  assert value['original_native_execution_receipt_present']is False
  assert value['certificate_sha256']==binding['certificate_sha256']
  cert=load_verified_certificate(value,binding,verifier);assert cert['state']==TYPED
  for key in ('original_done_present','original_exit_present','original_registry_execution_receipt_present'):
   assert cert[key]is False,key
  assert cert['original_spent_starts']==1 and cert['refunded_starts']==0 and cert['automatic_retry']is False
  identity=cert['scientific_identity']
  assert identity['input_digest']==digest and identity['cell']==binding['cell'] and identity['target_profile']==binding['profile']
  row=view['table'][digest][binding['profile']][binding['cell']]
  assert row['cohort']==c and row.get('uuid')in(None,uuid)
  assert row.get('accepted')is False and row.get('cycles')is None,'Cannot replace any accepted performance'
  old=copy.deepcopy(row)
  row.update(state=TYPED,uuid=uuid,accepted=False,cycles=None,
   typed_engineering_original_row=old,
   typed_engineering_negative_source=dict(bundle_path=binding['bundle_path'],certificate_sha256=value['certificate_sha256'],
    verifier_path=str(verifier_path),verifier_sha256=verifier_sha256,
    status=value['status'],missing_native_receipts_disclosed=True))
  proofs[c]=dict(verified=True,cohort=c,uuid=uuid,performance_accepted=False,cycles=None,
   source_identity_verified=True,archive_verified=True,no_model_retry_verified=True,missing_done_exit_disclosed=True,
   certificate_sha256=value['certificate_sha256'],bundle_path=binding['bundle_path'],
   verifier_sha256=verifier_sha256)
 view['typed_engineering_analysis_view']=dict(schema='EXPLICIT_TYPED_ENGINEERING_NEGATIVE_ANALYSIS_VIEW_V1',
  original_summary_sha256=canonical_sha(raw_summary),raw_summary_unmodified=True,
  original_aggregate_values_unmodified=True,original_state_counts_retained=raw_summary.get('state_counts'),
  state_counts=dict(collections.Counter(row['state']for pp in view['table'].values()for cc in pp.values()for row in cc.values())),
  projected_cohorts=sorted(proofs),native_receipts_created=False)
 return view,proofs

def recommend_from_bundles(raw_summary,scope,history,source_paths,source_pins,
                          bindings,verifier_path,verifier_sha256,final_guard=None):
 view,proofs=project(raw_summary,bindings,verifier_path,verifier_sha256)
 def verified_in_this_call(row,proof):
  assert proof is proofs[row['cohort']]and proof['uuid']==row['uuid']
  return proof
 result=recommend(view,scope,history,source_paths,source_pins,proofs,verified_in_this_call,final_guard)
 result['typed_engineering_analysis_view']=view['typed_engineering_analysis_view']
 return result
