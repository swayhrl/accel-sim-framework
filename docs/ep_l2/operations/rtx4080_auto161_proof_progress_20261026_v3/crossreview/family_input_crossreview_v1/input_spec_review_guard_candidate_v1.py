"""Private cross-review hardening candidate; no capture or routing authority."""
import pathlib,hashlib,json,importlib.util
P=pathlib.Path(__file__).resolve().parent/'replay/input_source_policy_v1.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='4114bf6a5ba246d042aedc2fffa59df108a85add915b7cc39e99d363b74d1400'
sp=importlib.util.spec_from_file_location('original_input_policy',P);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
PREP_GATE='ACTUAL_INPUT_CAPTURE_REQUEST_SPEC_CPU_PREPARED_V1'
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def validate_review_spec(spec,row,job):
 old.validate_spec(spec)
 assert spec['row_binding_sha256']==canon(row),'ROW_BINDING_NOT_AUTHORITY'
 assert spec['queue_id']==row['queue_id']and spec['binary_sha256']==row['binary_sha256']and spec['argv']==row['argv'],'EXACT_ROW_ARGV_BINARY'
 assert spec['input_binding']['declared_identity_sha256']==row['declared_identity_sha256'],'DECLARED_IDENTITY_BINDING'
 t=job['task'];sources=list(t.get('sources',t.get('source_files',[])))
 if not sources and t.get('source'):sources=[{'path':t['source'],'sha256':t['source_sha256']}]
 expected={(s['path'],s['sha256'])for s in sources}
 actual={(s['original_path'],s['sha256'])for s in spec['facts']['all_source_refs']}
 assert actual==expected,'EXACT_DECLARED_SOURCE_SET'
 main=spec['facts']['main_source_ref'];assert(main['original_path'],main['sha256'])in expected,'MAIN_SOURCE_NOT_DECLARED'
 for r in spec['facts']['regions']:
  assert type(r['bytes_per_region_static'])is int and r['bytes_per_region_static']>=0 and type(r['logical_copy_or_region_count_static'])is int and r['logical_copy_or_region_count_static']>=0,'STATIC_BYTE_EXPRESSION_TYPE'
 w=spec['worker_binding']
 if w['implementation_state']=='EXISTING_ROOT_CONTROLLER_OWNED':
  assert w['entrypoint_for_existing_owner_only']is True and w['new_invocation_allowed_by_this_preparer']is False,'SDK_OWNER_ONLY_NOT_REENTRANT'
 if w['implementation_state']=='EXISTING_COMMITTED_ROUTE_REVIEW':
  assert w['entrypoint_argv']is None and w['archived_worker_not_to_be_reentered']is True,'ARCHIVED_WORKER_MUST_NOT_REENTER'
 return True
def consume_preparation_gate_only(artifact,row,pending_dynamic,current_accepted_stage):
 assert artifact['provided_gates']==[PREP_GATE],'INPUT_PREPARATION_CANNOT_SUPPLY_DYNAMIC_GATE'
 assert artifact['qualification_granted']is False and artifact['gpu_executed']is False and artifact['historical_queue_mutated']is False
 assert artifact.get('actual_input_snapshot_complete')is False
 assert row['queue_id']in artifact['target_queue_ids']and artifact['row_bindings'][row['queue_id']]==canon(row)
 return {'CPU_gate':PREP_GATE,'remaining_dynamic_proofs':list(pending_dynamic),'routing_authority':False,'artifact_next_hint_ignored':True,'current_accepted_stage_preserved':current_accepted_stage,'input_or_trace_qualification':False}
