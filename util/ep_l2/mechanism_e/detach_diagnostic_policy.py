"""Candidate original-central adapter. No final authority exists until E seals it.

Root must replace/configure exact source-pinned final manifest/approval references
after real producer qualification. No environment override or unknown binary pin.
"""
import copy
import json
from pathlib import Path
from detach_scope_core import Authority, FIELD, CAMPAIGN, SCI_SCOPE, require, sha, spec_sha
import detach_validation
import detach_successor as successor

# Deliberately unconfigured. Tests inject explicit synthetic Authority in memory;
# production integration must bind actual E-derived final metadata, then publish.
_AUTHORITY = None
_FINAL_SEALED_AUTHORITY_REFS = {'manifest_path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/final_adoption/FINAL_MANIFEST.json', 'manifest_sha256': 'ef9a351495721112651511dea68173963cc585e9d6ae238473cae0c25e268be2', 'approval_path': '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/final_adoption/DERIVED_GOAL_APPROVAL.json', 'approval_sha256': 'd22b87fc2606cab4e394672fb5637c0643331c12a291ec9f56c50a84df07830d'}

def authority():
    global _AUTHORITY
    if _AUTHORITY is None and _FINAL_SEALED_AUTHORITY_REFS is not None:
        refs=_FINAL_SEALED_AUTHORITY_REFS
        require(type(refs) is dict and set(refs)=={'manifest_path','manifest_sha256','approval_path','approval_sha256'},
                'root-sealed authority refs must be exact source constants')
        _AUTHORITY=Authority(**refs)  # Same source-bound metadata in controller and parser process.
    require(_AUTHORITY is not None, 'ROOT_SEALED_OBSERVER_FINAL_AUTHORITY_UNAVAILABLE')
    return _AUTHORITY

def is_spec(spec):
    return spec.get('scientific_scope') == SCI_SCOPE

def active(item):
    if successor.has(item):return successor.scope().active(item,authority().active)
    if FIELD not in item:
        require(len(item['attempts']) <= 50, 'unauthorized post50 tail')
        return False
    return authority().active(item)

def adopt(item, source_leases):
    return authority().adopt(item, source_leases)

def bind_condition(item, spec, digest):
    if successor.is_spec(spec):return successor.scope().bind(item,spec,authority().active)
    return authority().bind(item, spec)

def scope_allowed(item, spec):
    if successor.is_spec(spec):
        if not successor.has(item):return False
        try:return successor.scope().scope_allowed(item,spec,authority().active)
        except (ValueError,KeyError,TypeError):return False
    if not is_spec(spec) or not active(item):return False
    a=authority()
    try:
        a.check_spec(a.authority(), spec)
        row=item[FIELD].get('binding')
        return row is not None and row['spec_sha256']==spec_sha(spec)
    except (ValueError, KeyError, TypeError):return False

def condition_check(item, spec, digest):
    if successor.is_spec(spec):
        require(scope_allowed(item,spec),'unbound exact successor condition')
        require(successor.scope().fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,'new exact decoder qualification incomplete')
        return dict(condition_id=spec['condition_id'],group='INDEPENDENT_DIAGNOSTIC_POINT')
    require(scope_allowed(item,spec),'unbound exact observer condition')
    require(authority().fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,
            'real observer schema qualification incomplete')
    return dict(condition_id=spec['condition_id'],group='INDEPENDENT_DIAGNOSTIC_POINT')

def batch_guard(item,spec):
    if successor.is_spec(spec):
        condition_check(item,spec,None);return successor.scope().guard(item,spec,authority().active)
    condition_check(item,spec,None)
    return authority().guard(item,spec)

def effective_timeout(item,spec):
    require(scope_allowed(item,spec),'unbound observer operational limit')
    return spec['timeout_seconds']

def qualification(q,digest):
    if successor.is_q(q):return successor.qualification(q,digest)
    a=authority();m=a.authority();b=m['scientific_binding']
    require(q['source_identity']==b['source_identity'],'wrong observer producer source')
    require(q.get('detach_observer_diagnostic') is not None,'new observer Q required')
    require(a.fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,
            'new observer schema has no independent terminal qualification')
    require(digest(b['qualification']['path'])==b['qualification']['sha256'],'observer Q changed')
    return True

def record_reservation(item,spec,attempt):
    if successor.is_spec(spec):return successor.scope().record_reservation(item,spec,attempt,authority().active)
    batch_guard(item,spec)
    attempt.update(condition_id=spec['condition_id'],diagnostic_spec_sha256=spec_sha(spec),
                   scientific_scope=SCI_SCOPE)
    item[FIELD]['attempt_ids'].append(attempt['attempt_id'])

def record_started(item,attempt):
    if attempt.get('condition_id') in successor.CONDITIONS:return successor.scope().record_started(item,attempt)
    require(item[FIELD]['start_witness'] is None,'observer already charged')
    witness=dict(attempt_id=attempt['attempt_id'],run_key=attempt['run_key'],
                 process=copy.deepcopy(attempt['process']),started_unix=attempt['started_unix'])
    attempt.update(started_identity=copy.deepcopy(attempt['process']),immutable_started_marker=sha(witness))
    item[FIELD]['start_witness']=copy.deepcopy(witness)

def queue_guard(item,queue,digest):
    if successor.has(item):return successor.queue_guard(item,queue,digest,authority().active)
    specs=[]
    for ref in queue.get('specs',[]):
        path=Path(ref['path'])
        require(digest(path)==ref['sha256'],'queued spec changed')
        specs.append(json.loads(path.read_text()))
    if not any(is_spec(s) for s in specs):return
    require(len(specs)==1 and queue.get('pairs',[])==[],'observer queue only one point, no union or pair')
    require(scope_allowed(item,specs[0]),'unbound observer queue')

def _legacy_crosscheck_data(data,item):
    """Cross-check existing canonical runs; no extra journal or authority.

    Detect missing/refunded tail while its original canonical run survives.
    Coherent malicious rewriting of every state/evidence store is outside the
    original single-writer/process-lifetime assumptions, not prevented here.
    """
    batch=item.get(FIELD)
    expected_key=None
    if batch and batch.get('binding'):
        expected_key=sha(batch['binding']['identity'])
    attempt_ids=set(batch.get('attempt_ids',[])) if batch else set()
    rows={key:row for key,row in data['runs'].items()
          if row.get('experiment_id')==CAMPAIGN and
          (row.get('scientific_scope')==SCI_SCOPE or row.get('diagnostic_spec_sha256')
           or key==expected_key or row.get('lease_id') in attempt_ids)}
    if not batch:
        require(not rows,'canonical observer run exists without adopted batch/tail')
        return False
    active(item)
    tail=item['attempts'][50:]
    require(len(rows)==len(tail),'canonical run/tail count mismatch')
    for attempt in tail:
        key=attempt['run_key'];require(key in rows,'canonical observer run missing')
        run=rows[key]
        require(run.get('run_key')==key and run.get('lease_id')==attempt['attempt_id']
                and run.get('identity')==attempt['identity']
                and run.get('scientific_scope')==SCI_SCOPE
                and run.get('diagnostic_spec_sha256')==attempt['diagnostic_spec_sha256']
                and run.get('condition_id')==attempt['condition_id']
                and run.get('qualification_id')==attempt['qualification_id']
                and run.get('budget_bucket')==attempt['budget_bucket'],
                'canonical observer identity/lease/binding mismatch')
        if attempt['state'] in ('RESERVED','START_INTENT_UNRECONCILED'):
            require(run['status']=='RESERVED' and not run.get('process')
                    and not run.get('started_unix'),'canonical started run forbids reservation/refund')
        elif attempt['state'] in ('FAILED_SPAWN','CANCELLED_BEFORE_START'):
            require(run['status']=='FAILED' and not run.get('process')
                    and not run.get('started_unix'),'canonical started run forbids prestart refund')
        else:
            require(run['status']==attempt['state'] and run.get('process')==attempt['process']
                    and run.get('started_unix')==attempt['started_unix'],
                    'canonical run/start state disagrees with charged attempt')
    return True


def prepare_validator(qrow,spec,digest):
    if successor.is_spec(spec):return successor.prepare_validator(qrow,spec,digest)
    """Initialize one adapter only from the exact root-sealed registered Q/spec.

    No environment override, free Q, callback or second initializer authority.
    Parent inspect and original parser CLI use this same source-bound function.
    """
    a=authority();m=a.authority();binding=m['scientific_binding']
    require(is_spec(spec),'only exact observer scope can prepare its validator')
    expected=binding['qualification']
    require(qrow.get('sha256')==expected['sha256']==spec.get('qualification_id')
            and Path(qrow['path']).resolve()==Path(expected['path']).resolve(),
            'registered Q/path differs from final root seal')
    path=Path(qrow['path'])
    require(path.is_file() and path.stat().st_size<=4*1024**2 and digest(path)==expected['sha256'],
            'registered Q bytes changed or oversized')
    q=qrow['qualification']
    require(json.loads(path.read_text())==q,'registered Q metadata differs from exact body')
    require(q.get('scientific_scope')==SCI_SCOPE and q.get('qualified_by')=='E'
            and q.get('source_identity')==binding['source_identity'],
            'new Q/source/scope not root-sealed')
    a.check_spec(m,spec)  # Exact spec and newQ/producer/parser/assets, not old fallback Q.
    scope=q.get('detach_observer_diagnostic',{}).get('validation_scope')
    require(type(scope) is dict,'new Q has no exact independent validation scope')
    if detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY:
        require(detach_validation._ADAPTER is not None and detach_validation._BINDING==scope,
                'already bound adapter cannot change validation scope')
        detach_validation._ADAPTER.check(spec,qrow)
        return {'status':'SYNTHETIC_BINDING_CHECK_ONLY' if a.fixture_mode else 'ADAPTER_BINDING_READY',
                'newly_configured':False}
    require(detach_validation._ADAPTER is None and detach_validation._BINDING is None,
            'partial validator state cannot be silently overwritten')
    detach_validation.configure_binding(scope)  # Production constructor refuses synthetic/callback bindings.
    detach_validation._ADAPTER.check(spec,qrow)
    return {'status':'ADAPTER_BINDING_READY','newly_configured':True}


def crosscheck_data(data,item):
    if successor.has(item):
        return successor.scope().crosscheck(data,item,authority().active,_legacy_crosscheck_data)
    return _legacy_crosscheck_data(data,item)

def adopt_successor(item,data,source_leases):
    return successor.scope().adopt(item,data,source_leases,authority().active)

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
