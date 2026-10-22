from pathlib import Path
O=Path('/tmp/e2_r5_central_candidate');A=O/'app';D=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
s=(O/'tagpressure_successor.py').read_text().replace('Historical51','Historical55').replace('old51','old55').replace("scope['old212_compatibility_decoder']","scope['fixed_r4_decoder']")
(A/'tagpressure_successor.py').write_text(s)
p=(D/'detach_diagnostic_policy.py').read_text()
p+='''
# New exact r5 scope, independently qualified; old r4 functions remain byte-preserved.
import tagpressure_successor as tagpressure
import tagpressure_validation
SCIENTIFIC_SCOPES=(SCI_SCOPE,tagpressure.SCI_SCOPE)
def is_scope(value):return value in SCIENTIFIC_SCOPES
def validation_module(spec):return tagpressure_validation if tagpressure.is_spec(spec) else detach_validation
def active_successor(item):return tagpressure if tagpressure.has(item) else successor
_old_active=active
_old_bind_condition=bind_condition
_old_scope_allowed=scope_allowed
_old_condition_check=condition_check
_old_batch_guard=batch_guard
_old_qualification=qualification
_old_record_reservation=record_reservation
_old_record_started=record_started
_old_queue_guard=queue_guard
_old_prepare_validator=prepare_validator
_old_crosscheck_data=crosscheck_data

def is_spec(spec):return spec.get('scientific_scope') in SCIENTIFIC_SCOPES

def active(item):
 if tagpressure.has(item):return tagpressure.scope().active(item,_old_active)
 return _old_active(item)
def bind_condition(item,spec,digest):
 if tagpressure.is_spec(spec):return tagpressure.scope().bind(item,spec,_old_active)
 return _old_bind_condition(item,spec,digest)
def scope_allowed(item,spec):
 if tagpressure.is_spec(spec):
  if not tagpressure.has(item):return False
  try:return tagpressure.scope().scope_allowed(item,spec,_old_active)
  except (ValueError,KeyError,TypeError):return False
 return _old_scope_allowed(item,spec)
def condition_check(item,spec,digest):
 if not tagpressure.is_spec(spec):return _old_condition_check(item,spec,digest)
 require(scope_allowed(item,spec),'unbound exact r5 condition')
 require(tagpressure.scope().fixture_mode or tagpressure_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,'r5 source/schema qualification incomplete')
 return dict(condition_id=spec['condition_id'],group='INDEPENDENT_DIAGNOSTIC_POINT')
def batch_guard(item,spec):
 if tagpressure.is_spec(spec):condition_check(item,spec,None);return tagpressure.scope().guard(item,spec,_old_active)
 return _old_batch_guard(item,spec)
def qualification(q,digest):
 if tagpressure.is_q(q):return tagpressure.qualification(q,digest)
 return _old_qualification(q,digest)
def record_reservation(item,spec,attempt):
 if tagpressure.is_spec(spec):return tagpressure.scope().record_reservation(item,spec,attempt,_old_active)
 return _old_record_reservation(item,spec,attempt)
def record_started(item,attempt):
 if attempt.get('condition_id') in tagpressure.CONDITIONS:return tagpressure.scope().record_started(item,attempt)
 return _old_record_started(item,attempt)
def queue_guard(item,queue,digest):
 if tagpressure.has(item):return tagpressure.queue_guard(item,queue,digest,_old_active)
 return _old_queue_guard(item,queue,digest)
def prepare_validator(qrow,spec,digest):
 if tagpressure.is_spec(spec):return tagpressure.prepare_validator(qrow,spec,digest)
 return _old_prepare_validator(qrow,spec,digest)
def crosscheck_data(data,item):
 if tagpressure.has(item):return tagpressure.scope().crosscheck(data,item,_old_active,_old_crosscheck_data)
 return _old_crosscheck_data(data,item)
def adopt_tagpressure_successor(item,data,source_leases):
 return tagpressure.scope().adopt(item,data,source_leases,_old_active)
'''
(A/'detach_diagnostic_policy.py').write_text(p)
s=(O/'coordinator.py').read_text()
s=s.replace("require(detach_policy.successor.has(actual[FIELD]),'exact successor forecast only')\n    m=detach_policy.successor.scope().manifest()", "module=detach_policy.active_successor(actual[FIELD])\n    require(module.has(actual[FIELD]),'exact successor forecast only')\n    m=module.scope().manifest()")
s=s.replace('scientific_scope=detach_policy.SCI_SCOPE,','scientific_scope=spec[\'scientific_scope\'],')
s=s.replace("attempt.get('scientific_scope')==detach_policy.SCI_SCOPE", "detach_policy.is_scope(attempt.get('scientific_scope'))")
s=s.replace("item['accepted_results'][attempt_id]['scientific_scope']=detach_policy.SCI_SCOPE", "item['accepted_results'][attempt_id]['scientific_scope']=attempt['scientific_scope']")
needle='    def bind_detach_observer_condition(self, spec):'
new='''    def adopt_tagpressure_successor(self):
        """Exact r5 four, old55 verified, original lock/controller only."""
        with self.locked() as (data,item):
            rows=[r for g in ('runs','resource_leases') for r in data[g].values()
                  if r.get('experiment_id')==CAMPAIGN and r.get('status') in ACTIVE
                  and (g=='runs' or r.get('role')=='E' or r.get('owner')=='mechanism_E')]
            require(not rows,'own scientific/source lease must retire before r5 adoption')
            changed=detach_policy.adopt_tagpressure_successor(item,data,[])
            return dict(changed=changed,actual_starts=item['actual_starts'],t0_unix=item['t0_unix'])

'''
s=s.replace(needle,new+needle)
(A/'coordinator.py').write_text(s)
s=(D/'controller.py').read_text().replace('detach_policy.successor.has(data[FIELD])','detach_policy.active_successor(data[FIELD]).has(data[FIELD])');(A/'controller.py').write_text(s)
s=(D/'runner.py').read_text().replace('return detach_validation.validate_summary(summary,spec,qrow,audit)','return detach_policy.validation_module(spec).validate_summary(summary,spec,qrow,audit)').replace("summary.get('diagnostic_scope')!=detach_policy.SCI_SCOPE","not detach_policy.is_scope(summary.get('diagnostic_scope'))").replace("result['scientific_scope']=detach_policy.SCI_SCOPE","result['scientific_scope']=spec['scientific_scope']").replace("record.get('scientific_scope')!=detach_policy.SCI_SCOPE","not detach_policy.is_scope(record.get('scientific_scope'))")
(A/'runner.py').write_text(s)
