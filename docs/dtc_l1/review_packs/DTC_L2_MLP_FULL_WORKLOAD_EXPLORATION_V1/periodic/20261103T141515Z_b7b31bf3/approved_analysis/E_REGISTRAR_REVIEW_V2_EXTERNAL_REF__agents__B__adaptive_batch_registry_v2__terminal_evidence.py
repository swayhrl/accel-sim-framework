"""Read-only terminal membership: native results and exact typed scan negative.
Typed closure never supplies performance cycles or fabricates native receipts.
"""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
TYPED='ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY'
C='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1'
U='19105d9d-7522-498e-bf1d-73fbf7aba766'
CERT_SHA='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7'
VERIFIER_SHA='9a023005a1847108dfb7e05ef0bacddbadcb7558766c5847bb08d2e2f678e673'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(p):s=importlib.util.spec_from_file_location('readonly_typed_scan_original_verifier',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_row(row,q,root,qualified_verifier=None):
 root=P(root);assert row['IR_R2_engineering_substitution']is False
 path=P(row['terminal_evidence_path']);assert sha(path)==row['terminal_evidence_sha256'];doc=read(path)
 assert doc['cohort']==row['cohort']
 if row['state']==TYPED:
  assert row['cohort']==doc['cohort']==C and doc['uuid']==U==q['consumed'][C]['uuid']
  assert doc['schema']=='L2_MLP_ENGINEERING_TERMINAL_NEGATIVE_V1'and doc['state']==TYPED and sha(path)==CERT_SHA and path.name=='ENGINEERING_TERMINAL_NEGATIVE.json'
  assert doc['performance_accepted']is doc['scientific_acceptance']is False and doc['accepted_cycles']is None
  assert doc['original_done_present']is doc['original_exit_present']is doc['original_native_execution_receipt_created']is doc['original_registry_execution_receipt_present']is False
  assert doc['source_disposition']=='SOURCE_KEEP'and doc['original_spent_starts']==1 and doc['refunded_starts']==0 and doc['automatic_retry']is False
  assert row.get('cycles')is None and row.get('performance_accepted',False)is False,'TYPED_NEGATIVE_CANNOT_SUPPLY_PERFORMANCE'
  assert 'execution_receipt'not in q['consumed'][C]and not(root/'control/qualification_ledger'/(C+'.DONE.json')).exists()
  assert q['consumed'][C]['intent_sha256']==doc['intent_sha256']
  iv=read(root/'control/qualification_ledger'/(C+'.INTENT.json'));assert iv['uuid']==U and sha(root/'control/qualification_ledger'/(C+'.INTENT.json'))==doc['intent_sha256']
  assert not(P(iv['output'])/'NATIVE_EXIT.json').exists(),'MISSING_NATIVE_EXIT_MUST_NOT_BE_FABRICATED'
  source=row['typed_negative_verifier'];assert sha(source['path'])==source['sha256']==VERIFIER_SHA
  if qualified_verifier is not None:assert q.get('qualification_only')is True and root!=R,'NO_FAKE_VERIFIER_FOR_PRODUCTION'
  else:qualified_verifier=load(source['path']).verify_certificate
  proof=qualified_verifier(path,VERIFIER_SHA)
  assert proof['status']=='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED'and proof['cohort']==C and proof['uuid']==U
  assert proof['certificate_sha256']==CERT_SHA and P(proof['certificate'])==path and proof['verifier_source_sha256']==VERIFIER_SHA
  assert proof['performance_accepted']is False and proof['accepted_cycles']is None and proof['original_native_execution_receipt_present']is False
  assert proof['DONE_or_EXIT_or_registry_writes']==proof['production_writes']==proof['models_started']==proof['signals']==proof['refunds']==0
  return dict(kind='QUALIFIED_TYPED_ENGINEERING_NEGATIVE',cohort=C,uuid=U,terminal_status_verified=True,performance_accepted=False,accepted_cycles=None,native_receipts_missing_preserved=True,certificate_sha256=CERT_SHA,verifier_source_sha256=VERIFIER_SHA)
 assert row['state']in['ACCEPTED','ORIGINAL_TERMINAL_NEGATIVE']
 assert doc['cycles']==row['cycles']and doc['proof']['performance_accepted']is(row['state']=='ACCEPTED')
 if row['state']=='ORIGINAL_TERMINAL_NEGATIVE':assert doc['state']=='FAIL_L2MLP_ARCHIVED_NO_RETRY'and row['cycles']is None
 else:assert type(row['cycles'])is int and row['cycles']>0
 if row['cohort']in q['consumed']:assert doc['uuid']==q['consumed'][row['cohort']]['uuid']
 return dict(kind='STANDARD_ACCEPTED'if row['state']=='ACCEPTED'else'STANDARD_NEGATIVE',cohort=row['cohort'],terminal_status_verified=True,performance_accepted=row['state']=='ACCEPTED',accepted_cycles=row['cycles'])
