#!/usr/bin/env python3
"""Approved dependency artifact joins; status labels alone cannot unlock stages."""
from audit_common_v1 import need,no_qualification,canonical
from audit_attempt_v1 import WAITS,ROUTES
import hashlib
def permitted_next(reader,ctx,row,registry):
 refs=ctx.get('dependency_artifacts',[]);missing=ctx.get('missing_dependency_sha256',[])
 need(isinstance(refs,list) and len(refs)<=1024 and isinstance(missing,list),'INVALID_DEPENDENCY_CONTEXT')
 allowed={ROUTES[row['next_step']]};bysha={}
 for ref in refs:
  obj=reader.refobj(ref);need(obj.get('schema')=='AUTO161_ARTIFACT_V1','WRONG_ARTIFACT_SCHEMA')
  need(ref['sha256'] not in bysha,'DUPLICATE_DEPENDENCY_ARTIFACT');bysha[ref['sha256']]=obj
  producer=registry.get('artifact_producers',{}).get(obj.get('producer_id'))
  need(producer is not None,'UNKNOWN_ARTIFACT_PRODUCER')
  need(obj.get('profile')==producer['profile'] and obj.get('producer_source_sha256')==producer['source_sha256'],'WRONG_ARTIFACT_PROFILE_OR_TOOL')
  need(hashlib.sha256(reader.bytes(producer['source_path'])).hexdigest()==producer['source_sha256'],'ARTIFACT_PRODUCER_SOURCE_CHANGED')
  no_qualification(obj)
  for key in ['qualification_granted','gpu_executed','historical_queue_mutated']:need(obj.get(key) is False,'ARTIFACT_FORBIDDEN_PERMISSION',key)
  need(obj.get('status') in ('PASS','HOLD') and obj.get('next_stage') in WAITS and obj['next_stage'] in producer['allowed_next_stages'],'ARTIFACT_STAGE_NOT_ALLOWED')
  need(set(obj.get('provided_gates',[]))<=set(producer['allowed_gates']) and obj.get('evidence'),'ARTIFACT_GATES_WITHOUT_EVIDENCE')
  for evidence in obj['evidence']:reader.ref(evidence)
  relevant=row['queue_id'] in obj.get('target_queue_ids',[]) or bool(set(row.get('profile_families_nonexclusive',[]))&set(obj.get('family_keys',[])))
  need(relevant,'ARTIFACT_WRONG_TARGET_OR_FAMILY')
 def visit(key,stack):
  need(key not in stack,'CYCLIC_DEPENDENCY_ARTIFACT')
  for dep in bysha[key].get('requires',[]):
   need(dep in bysha and bysha[dep]['status']=='PASS','DEPENDENCY_NOT_CLOSED')
   visit(dep,stack|{key})
 for key,obj in bysha.items():
  visit(key,set())
  if not missing and obj['status']=='PASS' and obj.get('row_bindings',{}).get(row['queue_id'])==canonical(row):allowed.add(obj['next_stage'])
 return allowed
