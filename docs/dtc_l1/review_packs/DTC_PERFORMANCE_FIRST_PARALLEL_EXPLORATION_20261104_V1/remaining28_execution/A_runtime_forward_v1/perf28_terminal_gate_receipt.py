"""Read-only consumption of C's one-shot full first4 closure receipt.
Does not run --audit, rehash raw model logs/chunks, register or grant a model.
"""
from pathlib import Path
import json,hashlib,types
P=Path
FIRST4=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1')
FIRST4_REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'
VALIDATOR_SOURCE=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/C_first4_terminal_gate_preparation_v1/first4_terminal_gate.py')
VALIDATOR_SHA='06996cc8f27ddbe67eb73e8979c98bcceb63e8993d98edfb3d7485076070d516'
PREPARATION_MANIFEST=VALIDATOR_SOURCE.parent/'MANIFEST.json'
PREPARATION_SHA='d006d8772698fb5d5ca025694c36871e1cf7037890770e4a21fbd0688238518b'
OUTPUT=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/C_first4_terminal_gate_v1/C_FIRST4_TERMINAL_GATE.json')
SCHEMA='C_PERFFIRST_FIRST4_TERMINAL_GATE_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def _load_validator():
 assert sha(VALIDATOR_SOURCE)==VALIDATOR_SHA and sha(PREPARATION_MANIFEST)==PREPARATION_SHA,'C_FULL_CLOSURE_VALIDATOR_SOURCE_DRIFT'
 m=types.ModuleType('perf28_private_C_first4_closure_metadata');m.__file__=str(VALIDATOR_SOURCE)
 exec(compile(VALIDATOR_SOURCE.read_bytes(),str(VALIDATOR_SOURCE),'exec'),m.__dict__);return m
def validate_document(gate,q,validator):
 assert gate['schema']==SCHEMA and gate['status']=='PASS'and gate['gate_passed']is True,'ACTUAL_C_FULL_CLOSURE_NOT_PASS'
 assert P(gate['validator_source_path']).resolve()==VALIDATOR_SOURCE.resolve() and gate['validator_source_sha256']==VALIDATOR_SHA
 assert gate['request']==FIRST4_REQ and gate['budget']==gate['consumed']==4 and gate['remaining']==0
 assert gate['model_starts']==gate['registry_writes']==gate['owner_actions']==0 and gate['not_a_REQ28_registration_or_extra_grant']is True
 assert gate['execution_plan_sha256']==q['execution_plan_sha256']==validator.PLAN_SHA
 assert gate['registry_candidate_sha256']==validator.CANDIDATE_SHA==sha(FIRST4/'control/REGISTRY_REQUEST_CANDIDATE.json')
 assert gate['Tag16_review_manifest_sha256']==validator.TAG_SHA and P(gate['Tag16_review_manifest_path']).resolve()==validator.TAG_MANIFEST.resolve()and sha(validator.TAG_MANIFEST)==validator.TAG_SHA
 assert set(gate['points'])==set(q['consumed']) and len(gate['points'])==4 and len({p['uuid']for p in gate['points'].values()})==4
 for c,row in q['consumed'].items():
  point=gate['points'][c];assert point['uuid']==row['uuid']and point['strict_reexecuted']is True and point['natural_nonlive']is True and point['archive_native_full_rehash']is True
  rr=read(FIRST4/'analysis'/(c+'.RESULT.json'));spec=read(FIRST4/'control/specs'/(c+'.json'));assert point['cycles']==rr['cycles']and point['program']==spec['program']and point['input_digest']==spec['input_digest'],'C_POINT_IDENTITY_DRIFT'
  out=FIRST4/'DTC/run/results'/row['uuid'];expected={str(FIRST4/'analysis'/(c+'.RESULT.json')),str(FIRST4/'control/qualification_ledger'/(c+'.INTENT.json')),str(FIRST4/'control/qualification_ledger'/(c+'.DONE.json')),str(FIRST4/'control'/(c+'_ARCHIVE_RECEIPT.json')),str(out/'NATIVE_EXIT.json'),str(out/'L2_STRICT.json'),str(FIRST4/'control/specs'/(c+'.json'))}
  assert set(point['closure_file_sha256'])==expected,'C_CLOSURE_FILE_SET_MISMATCH'
  for path,pin in point['closure_file_sha256'].items():assert sha(path)==pin,'C_CLOSURE_METADATA_DRIFT '+path
  proof=point['archive_native_proof'];assert P(proof['path']).resolve()==(OUTPUT.parent/(c+'.FULL_ARCHIVE_NATIVE_REHASH.json')).resolve()and sha(proof['path'])==proof['sha256']
  archive=read(proof['path']);assert archive['status']=='PASS_FULL_CHUNK_SOURCE_NATIVE_TYPED_REHASH'and archive['typed_entry_count']==point['typed_entry_count']==len(archive['typed_entries'])
  assert archive['metadata_references']==point['metadata_references'] and len(point['metadata_references'])==6,'C_ARCHIVE_METADATA_SET_MISMATCH'
  for path,pin in point['metadata_references'].items():assert sha(path)==pin,'C_ARCHIVE_METADATA_DRIFT '+path
  assert not validator.live_generation(read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')),'FIRST4_GENERATION_BECAME_LIVE'
 return True
def verify(plan,reg,release_evidence=None):
 cfg=plan['first4_terminal_gate'];assert P(cfg['source_path']).resolve()==VALIDATOR_SOURCE.resolve()and cfg['source_sha256']==VALIDATOR_SHA
 assert P(cfg['output_path']).resolve()==OUTPUT.resolve()and cfg['required_schema']==SCHEMA and cfg['required_status']=='PASS'and cfg['required_gate_passed']is True
 validator=_load_validator();gate=read(OUTPUT)
 q=validator.closure_readiness(reg)  # Metadata-only rejoin; never calls the full audit.
 validate_document(gate,q,validator)
 evidence=dict(first4_terminal_gate_report_path=str(OUTPUT),first4_terminal_gate_report_sha256=sha(OUTPUT),validator_source_sha256=VALIDATOR_SHA)
 if release_evidence is not None:assert release_evidence==evidence,'REGISTERED_FIRST4_RELEASE_PROOF_DRIFT'
 return evidence
