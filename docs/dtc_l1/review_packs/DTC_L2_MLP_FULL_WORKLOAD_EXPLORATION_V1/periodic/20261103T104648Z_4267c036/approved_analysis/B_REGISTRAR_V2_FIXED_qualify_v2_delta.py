"""Only new V2 deltas: real typed scan evidence and partial-forward evolution.
Original V1 eight-case suite is not rerun. No production apply or models.
"""
import pathlib,json,hashlib,copy,sys,threading,types,tempfile,fcntl,importlib.util,ast
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/B/adaptive_batch_registry_v2';C=A/'agents/A/adaptive_ch_ad1_candidates_v1';S=types.SimpleNamespace
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_adaptive_registry_v2',D/'adaptive_batch_registry.py');t=load('B_typed_evidence_v2',D/'terminal_evidence.py');adapter=load('B_same_A_adapter_v2',D/'a_candidate_adapter.py');catalog,source=adapter.normalize(C,R)
(D/'A70_NORMALIZED_CATALOG_REFERENCE.json').write_bytes(m.raw(catalog));(D/'A70_SOURCE_MANIFEST_REFERENCE.json').write_bytes(m.raw(source))
# Import definitions only from the sealed CPU driver; no old test body executes.
old_driver=A/'agents/B/adaptive_batch_registry_v1/qualify_adaptive_registry.py';tree=ast.parse(old_driver.read_text());defs=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef))and node.name in['Engine','fixture']]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(old_driver),'exec'),globals())
def f(profiles=('F256',),early=True):
 root,e,reg,dep=fixture(profiles,early);reg.cfg['terminal_adapter_path']=str(D/'terminal_evidence.py');reg.cfg['terminal_adapter_sha256']=m.sha(D/'terminal_evidence.py');reg.cfg['dependency_pins'][str(D/'terminal_evidence.py')]=m.sha(D/'terminal_evidence.py')
 return root,e,reg,dep
checks=[]
def test(name,fn):fn();checks.append(dict(case=name,status='PASS'))
def reject(fn):
 try:fn()
 except(AssertionError,RuntimeError,KeyError):return
 raise AssertionError('EXPECTED_HOLD')
# Actual read-only qualified historical verifier, exactly once. Its archive and
# native restore reads are real; no execute/repair/restore-producing path runs.
native=load('readonly_v2_authority',R/'tools/l2_native.py');actualq=native.registered()[2]
cfg=read_cfg=json.loads((R/'control/operational_amendments/typed_negative_transport_v3/INSTALL_CONFIG.json').read_bytes());binding=cfg['bindings'][0];cert=P(binding['bundle_path'])/'ENGINEERING_TERMINAL_NEGATIVE.json';verifier=cfg['verifier']
actualrow=dict(cohort=t.C,state=t.TYPED,uuid=t.U,IR_R2_engineering_substitution=False,terminal_evidence_path=str(cert),terminal_evidence_sha256=t.CERT_SHA,typed_negative_verifier=verifier)
actual_receipt=t.validate_row(actualrow,actualq,R)
(D/'ACTUAL_TYPED_CERTIFICATE_READONLY.json').write_bytes(m.raw(dict(status='PASS_ACTUAL_TYPED_CERTIFICATE_AND_QUALIFIED_HISTORICAL_VERIFIER_READONLY',adapter_sha256=m.sha(D/'terminal_evidence.py'),row=actualrow,result=actual_receipt,source_q_UUID=actualq['consumed'][t.C]['uuid'],original_DONE_absent=not(R/'control/qualification_ledger'/(t.C+'.DONE.json')).exists(),no_cycles_or_fake_receipts_added=True,production_actions=0,models_started=0)))
captured=m.read(R/'control/operational_amendments/typed_negative_transport_v3/FRESH_READONLY_TRANSPORT_PROOF.json');assert captured['certificate_sha256']==t.CERT_SHA and captured['verifier_source_sha256']==t.VERIFIER_SHA
def typed():
 root,e,reg,dep=f(early=False);iv=R/'control/qualification_ledger'/(t.C+'.INTENT.json');(root/'control/qualification_ledger'/iv.name).write_bytes(iv.read_bytes())
 e.q['admitted_specs'][t.C]=actualq['admitted_specs'][t.C];e.q['consumed'][t.C]=copy.deepcopy(actualq['consumed'][t.C]);e.q['budget']+=1
 app=m.read(reg.cfg['approval_path']);cp=P(app['initial_single_factor_completion']['path']);completion=m.read(cp);row=next(x for x in completion['cell_evidence']if x['cohort']==t.C);row.clear();row.update(actualrow);cp.write_bytes(m.raw(completion));app['initial_single_factor_completion']['sha256']=m.sha(cp);P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path'])
 # Private verifier leaf reuses Root's pinned prior actual read-only verdict
 # after this driver independently reverified the same cert/source above; production
 # helper explicitly refuses this override when q/root are not qualification.
 private=S(validate_row=lambda row,q,root:t.validate_row(row,q,root,qualified_verifier=lambda p,h:copy.deepcopy(captured))if row['state']==t.TYPED else t.validate_row(row,q,root))
 old=m.terminal_adapter;m.terminal_adapter=lambda cfg:private
 try:p=reg.prepare();assert len(p['rows'])==35
 finally:m.terminal_adapter=old
 for kind in['cycles','uuid','standard_FAIL']:
  r=copy.deepcopy(actualrow)
  if kind=='cycles':r['cycles']=1
  elif kind=='uuid':q=copy.deepcopy(e.q);q['consumed'][t.C]['uuid']='BAD';reject(lambda:t.validate_row(r,q,root,qualified_verifier=lambda p,h:captured));continue
  else:r['state']='ORIGINAL_TERMINAL_NEGATIVE';r['cycles']=None
  reject(lambda:t.validate_row(r,e.q,root,qualified_verifier=lambda p,h:captured))
 assert not(root/'control/qualification_ledger'/(t.C+'.DONE.json')).exists()and e.calls==0
test('real_scan_typed_certificate_is_terminal_only_no_cycles_DONE_EXIT_and_exact_verifier_provenance',typed)
def natural_after_partial():
 root,e,reg,dep=f();oldlive='CPU_OLD_HEALTHY_GENERATION';e.q['admitted_specs'][oldlive]='KEEP';e.q['consumed'][oldlive]={'uuid':'CPU_KEEP_OLD_UUID'};e.q['budget']+=1;e.q['state']='RUNNING';p=reg.prepare();hit=[False]
 def fault(stage):
  if stage=='AFTER_FIRST_SPEC'and not hit[0]:hit[0]=True;raise RuntimeError('CPU_PARTIAL_CANONICAL_ONLY')
 reg.fault_hook=fault;reject(lambda:reg.commit(p));qbefore=reg.folder(p)/'preimages/Q_BEFORE.json';initial=qbefore.read_bytes();assert e.calls==0
 receipt=dict(cohort=oldlive,uuid='CPU_KEEP_OLD_UUID',stop_reason=None,launcher_wait_returncode=0,CPU_ONLY_STANDIN=True);e.q['consumed'][oldlive]['execution_receipt']=receipt;(root/'control/qualification_ledger'/(oldlive+'.DONE.json')).write_bytes(m.raw(receipt));reg.fault_hook=None
 reg.commit(p);assert qbefore.read_bytes()==initial and e.calls==1 and e.q['budget']==37 and e.q['remaining']==35 and e.q['consumed'][oldlive]['execution_receipt']==receipt
 assert len(list((reg.folder(p)/'attempts').glob('*.Q_CAS.json')))==2
 reg.commit(p);assert e.calls==1
test('partial_first_spec_then_old_natural_DONE_sameproposal_preserves_initialQ_fresh_attemptCAS_grant35_once',natural_after_partial)
def forbid_changed_old():
 for kind in['UUID','negative_receipt','unrelated_budget']:
  root,e,reg,dep=f();oldlive='CPU_OLD_HEALTHY';e.q['admitted_specs'][oldlive]='KEEP';e.q['consumed'][oldlive]={'uuid':'KEEP'};e.q['budget']+=1;p=reg.prepare();initial=copy.deepcopy(e.q)
  if kind=='UUID':e.q['consumed'][oldlive]['uuid']='WRONG'
  elif kind=='negative_receipt':e.q['consumed'][oldlive]['execution_receipt']={'cohort':oldlive,'uuid':'KEEP','stop_reason':'NONNATURAL','launcher_wait_returncode':-15}
  else:e.q['remaining']+=1
  reject(lambda:m.natural_receipt_evolution(initial,e.q,root));assert e.calls==0
test('oldUUID_negativeclosure_budget_or_unjoined_receipt_change_not_allowed_as_natural_recovery',forbid_changed_old)
def actual_phase1_review_no_grant():
 root,e,reg,dep=f();review=A/'coordinator/AD1_CH_F256_PHASE1_MATCHED_EXECUTION_ORDER_REVIEW_V1/REVIEW.json';assert m.sha(review)=='7ef10d7159dc0b86a361852dacb8e78c0e077988d5a76fe3395a113323335ff4'
 app=m.read(reg.cfg['approval_path']);app['superseding_execution_order_review']={'path':str(review),'sha256':m.sha(review)};P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path']);p=reg.prepare();assert len(p['rows'])==35 and e.calls==0
 assert m.read(review)['approved_for_registration']is False and m.read(review)['new_grants']==0
 app['approved_for_registration']=False;P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path']);reject(reg.prepare);assert e.calls==0
test('actual_Root7ef_execution_order_review_joins_F25635_but_cannot_replace_separate_registration_approval',actual_phase1_review_no_grant)
qa=dict(schema='B_ADAPTIVE_BATCH_REGISTRY_V2_DELTA_CPU_QUALIFICATION',status='PASS_ADAPTIVE_BATCH_ISOLATED_TRANSACTION_CPU',source_sha256=m.sha(D/'adaptive_batch_registry.py'),terminal_adapter_sha256=m.sha(D/'terminal_evidence.py'),candidate_adapter_sha256=m.sha(D/'a_candidate_adapter.py'),driver_sha256=m.sha(__file__),prior_v1_source_sha256='7993bc88e3e6c89784d73cf57134f56e2231ef3b2aee1f31004359bcc7ada7e6',count=len(checks),checks=checks,pure_EX_callback_qualified=True,actual_candidate_schema_qualified=True,prior_8_case_qualification_path=str(A/'agents/B/adaptive_batch_registry_v1/CPU_QUALIFICATION.json'),prior_8_case_not_rerun=True,production_release_eligible=False,qualification_only=True,production_actions=0,models_started=0,limits=['Real current typed certificate/historical verifier was executed read-only. Qualification scopes use captured typed verdict as explicit verifier leaf, never production override.','Stage350 completion, registration approval, owner and authority in fixtures are CPU standins. Actual Root7ef review is execution-order-only and has no grant permission.'])
(D/'CPU_DELTA_QUALIFICATION.json').write_bytes(m.raw(qa));print(json.dumps(dict(status=qa['status'],count=len(checks),source_sha256=qa['source_sha256'],terminal_sha256=qa['terminal_adapter_sha256'],QA_sha256=m.sha(D/'CPU_DELTA_QUALIFICATION.json')),indent=2))
