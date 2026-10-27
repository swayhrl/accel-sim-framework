"""Four isolated adapter/schema checks; fake verifier is explicitly CPU-only.
Archive/restore truth belongs to scan Agent's separately qualified real verifier.
"""
import copy,hashlib,json,pathlib,sys,tempfile
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from typed_analysis_view import project,TYPED
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
checks=[]
with tempfile.TemporaryDirectory()as tmp:
 p=P(tmp)/'CPU_ONLY_FAKE_VERIFIER.py'
 cert=dict(schema='L2_MLP_ENGINEERING_TERMINAL_NEGATIVE_V1',cohort='c',uuid='u',performance_accepted=False,accepted_cycles=None,state=TYPED,original_done_present=False,original_exit_present=False,original_registry_execution_receipt_present=False,
  original_spent_starts=1,refunded_starts=0,automatic_retry=False,scientific_identity=dict(input_digest='d',cell='DH',target_profile='M16'))
 bundle=P(tmp)/'CPU_ONLY_SCOPE/CPU_ONLY_TX';bundle.mkdir(parents=True)
 cp=bundle/'ENGINEERING_TERMINAL_NEGATIVE.json';cp.write_text(json.dumps(cert))
 value=dict(status='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED',cohort='c',uuid='u',certificate=str(cp),
  certificate_sha256=sha(cp),accepted_cycles=None,performance_accepted=False,original_native_execution_receipt_present=False)
 p.write_text('import pathlib\nPROD=pathlib.Path('+repr(str(bundle.parent))+')\ndef verify_bundle(path, expected_self_sha):\n return '+repr(value)+'\n')
 raw=dict(table={'d':{'M16':{'DH':dict(cohort='c',state='PENDING',accepted=False,cycles=None,uuid=None)}}},
  aggregates={'M16':{'n':34}},state_counts={'PENDING':1})
 before=copy.deepcopy(raw);binding=dict(cohort='c',uuid='u',input_digest='d',cell='DH',profile='M16',bundle_path=str(bundle),certificate_sha256=sha(cp))
 view,proofs=project(raw,[binding],p,sha(p))
 assert raw==before and raw['table']['d']['M16']['DH']['state']=='PENDING'
 assert view['table']['d']['M16']['DH']['state']==TYPED and not view['table']['d']['M16']['DH']['accepted']
 assert view['table']['d']['M16']['DH']['typed_engineering_original_row']==raw['table']['d']['M16']['DH']
 assert view['aggregates']==raw['aggregates']and proofs['c']['cycles']is None
 checks.append('typed_sidecar_view_preserves_raw_state_and_performance_aggregates')
 for args in ((dict(binding,certificate_sha256='WRONG'),p,sha(p)),(binding,p,'WRONG')):
  try:project(raw,[args[0]],args[1],args[2])
  except AssertionError:pass
  else:raise AssertionError('bad source/certificate pin accepted')
 checks.append('wrong_verifier_or_certificate_pin_rejected')
 accepted=copy.deepcopy(raw);accepted['table']['d']['M16']['DH'].update(accepted=True,cycles=1)
 try:project(accepted,[binding],p,sha(p))
 except AssertionError:pass
 else:raise AssertionError('accepted performance overwritten')
 checks.append('accepted_performance_never_demoted_or_replaced')
 changed=copy.deepcopy(binding);changed['profile']='M8'
 try:project(raw,[changed],p,sha(p))
 except AssertionError:pass
 else:raise AssertionError('different scientific profile accepted')
 checks.append('certificate_profile_identity_mismatch_rejected')
output=dict(status='PASS',count=len(checks),checks=checks,
 source_sha256=sha(HERE/'typed_analysis_view.py'),driver_sha256=sha(__file__),
 qualification_scope='adapter and schema only; fake CPU verifier does not certify actual archive',
 real_verifier_integration_pending=True,models_started=0,registry_grants=0,production_mutations=0)
(HERE/'TYPED_VIEW_CPU_QUALIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
