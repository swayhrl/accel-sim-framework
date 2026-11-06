"""Read only two registrar deltas; no import/execution or suite rerun."""
import pathlib,json,hashlib,ast,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');D=P(__file__).parent;B=A/'agents/B/adaptive_batch_registry_v2';V1=B.parent/'adaptive_batch_registry_v1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
source=B/'adaptive_batch_registry.py';helper=B/'terminal_evidence.py';qa=B/'CPU_DELTA_QUALIFICATION.json';actual=B/'ACTUAL_TYPED_CERTIFICATE_READONLY.json'
assert sha(source)=='d58af291827b4b0a28af9753b1be19aa4e9b3d01fe72524d78b0d62659273542'
assert sha(helper)=='ebbc35c574ca1436a1aa33fada901a4da80c18cce96f1d25f279e6b11b4066c7'
assert sha(qa)=='69c1f90ff0b7a02165d361611b00cff34f13e5c749da8429d3ac6386bdb52352'
assert sha(B/'MANIFEST.json')=='82f51336684b3b9a131ffbdce300a75a3f138d8b2c36316094fe4904764075fd'
for row in read(B/'MANIFEST.json')['members']:assert sha(row['path'])==row['sha256']
q=read(qa);proof=read(actual);assert q['source_sha256']==sha(source)and q['terminal_adapter_sha256']==sha(helper)and q['count']==4 and all(x['status']=='PASS'for x in q['checks'])
assert proof['result']['terminal_status_verified']is True and proof['result']['performance_accepted']is False and proof['result']['accepted_cycles']is None
assert proof['result']['certificate_sha256']=='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7'
def funcs(p):return {n.name:n for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.FunctionDef)}
v1=funcs(V1/'adaptive_batch_registry.py');v2=funcs(source)
assert ast.dump(v1['grant'],include_attributes=False)==ast.dump(v2['grant'],include_attributes=False)
assert not any(ast.unparse(n.func).startswith('self.engine.')for n in ast.walk(v2['grant'])if isinstance(n,ast.Call))
assert 'terminal.validate_row' in ast.unparse(v2['fresh_sources']) and 'terminal.validate_row'not in ast.unparse(v2['grant'])
review=dict(schema='E_ADAPTIVE_BATCH_REGISTRAR_V2_DELTA_REVIEW',status='TWO_REPORTED_FINDINGS_CLOSED_SOURCE_DELTA_SUITABLE_FOR_SEPARATE_MAIN_QUALIFICATION',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_path=str(source),source_sha256=sha(source),terminal_helper_sha256=sha(helper),QA_path=str(qa),QA_sha256=sha(qa),actual_typed_verification_path=str(actual),actual_typed_verification_sha256=sha(actual),closed_findings=[dict(id='TYPED_NEGATIVE_TERMINAL_SCHEMA_INCOMPATIBLE',disposition='New helper recognizes only exact scan typed cert/source/UUID and preserves absence of DONE/EXIT/native/q execution receipt and cycles. Actual qualified9a verifier executes outside EX. Existing B actual readonly proof reused; E did not re-run it.'),dict(id='SAME_PROPOSAL_Q_BEFORE_RETRY_CONFLICTS_WITH_LEGAL_PEER_CLOSURE',disposition='First Q_BEFORE is retained once. Every attempt writes fresh immutable CAS q record. Only existing sameUUID consumed records may append naturalrc0 DONE-joined execution receipt; unrelated changes fail closed. Fresh grant callback is AST-identical to V1 and still exact q CAS/+N once.')],guard_assessment=dict(grant_AST_identical_to_v1=True,engine_authority_reentry_in_grant=False,typed_verifier_called_outside_EX=True,original_preimage_preserved=True,old_negative_NOT_accepted=True,no_IR_R2_union=True,no_runtime_activation=True),remaining=['Actual Main registration approval tied to finalV2 source/catalog/cohorts/readback remains absent; Root7ef alone has approved_for_registration=False.', 'Actual same-owner registrar handoff needs its own qualified source/config callback and exception containment.', 'Role-specific scope/resource/native/strict/consumer/dispatch generation and fresh resource admission remain separate. This review does not activate catalog70.', 'Partial retry deliberately permits natural receipt evolution only. New births, negative closure or unrelated q drift HOLD for explicit safe Main disposition; no identity is refunded/reset.'],qualification_limits=dict(source_and_existing_receipts_only=True,no_old8_rerun=True,no_new4_fixture_mirror=True,no_registrar_execution=True,no_fullarchive_replay=True),production_release_eligible=False,models_started=0,new_grants=0,production_changes=0)
put(D/'REVIEW.json',review)
files=[source,helper,qa,actual,B/'MANIFEST.json',B/'EXACT_DIFF_FROM_V1.patch',D/'review.py',D/'REVIEW.json']
put(D/'MANIFEST.json',dict(schema='E_REGISTRAR_V2_DELTA_REVIEW_MANIFEST',files=[dict(path=str(p),sha256=sha(p))for p in files],production_release_eligible=False))
print(json.dumps(dict(review_path=str(D/'REVIEW.json'),review_sha256=sha(D/'REVIEW.json'),manifest_sha256=sha(D/'MANIFEST.json'),status=review['status'])))
