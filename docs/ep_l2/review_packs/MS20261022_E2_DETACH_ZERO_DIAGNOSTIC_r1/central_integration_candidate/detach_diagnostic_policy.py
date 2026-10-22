"""Candidate original-central adapter. No final authority exists until E seals it.

Root must replace/configure exact source-pinned final manifest/approval references
after real producer qualification. No environment override or unknown binary pin.
"""
import copy
import json
from pathlib import Path
from detach_scope_core import Authority, FIELD, CAMPAIGN, SCI_SCOPE, require, sha, spec_sha
import detach_validation

# Deliberately unconfigured. Tests inject explicit synthetic Authority in memory;
# production integration must bind actual E-derived final metadata, then publish.
_AUTHORITY = None

def authority():
    require(_AUTHORITY is not None, 'ROOT_SEALED_OBSERVER_FINAL_AUTHORITY_UNAVAILABLE')
    return _AUTHORITY

def is_spec(spec):
    return spec.get('scientific_scope') == SCI_SCOPE

def active(item):
    if FIELD not in item:
        require(len(item['attempts']) <= 50, 'unauthorized post50 tail')
        return False
    return authority().active(item)

def adopt(item, source_leases):
    return authority().adopt(item, source_leases)

def bind_condition(item, spec, digest):
    return authority().bind(item, spec)

def scope_allowed(item, spec):
    if not is_spec(spec) or not active(item):return False
    a=authority()
    try:
        a.check_spec(a.authority(), spec)
        row=item[FIELD].get('binding')
        return row is not None and row['spec_sha256']==spec_sha(spec)
    except (ValueError, KeyError, TypeError):return False

def condition_check(item, spec, digest):
    require(scope_allowed(item,spec),'unbound exact observer condition')
    require(authority().fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,
            'real observer schema qualification incomplete')
    return dict(condition_id=spec['condition_id'],group='INDEPENDENT_DIAGNOSTIC_POINT')

def batch_guard(item,spec):
    condition_check(item,spec,None)
    return authority().guard(item,spec)

def effective_timeout(item,spec):
    require(scope_allowed(item,spec),'unbound observer operational limit')
    return spec['timeout_seconds']

def qualification(q,digest):
    a=authority();m=a.authority();b=m['scientific_binding']
    require(q['source_identity']==b['source_identity'],'wrong observer producer source')
    require(q.get('detach_observer_diagnostic') is not None,'new observer Q required')
    require(a.fixture_mode or detach_validation.INDEPENDENT_SCHEMA_VALIDATION_READY,
            'new observer schema has no independent terminal qualification')
    require(digest(b['qualification']['path'])==b['qualification']['sha256'],'observer Q changed')
    return True

def record_reservation(item,spec,attempt):
    batch_guard(item,spec)
    attempt.update(condition_id=spec['condition_id'],diagnostic_spec_sha256=spec_sha(spec),
                   scientific_scope=SCI_SCOPE)
    item[FIELD]['attempt_ids'].append(attempt['attempt_id'])

def record_started(item,attempt):
    require(item[FIELD]['start_witness'] is None,'observer already charged')
    witness=dict(attempt_id=attempt['attempt_id'],run_key=attempt['run_key'],
                 process=copy.deepcopy(attempt['process']),started_unix=attempt['started_unix'])
    attempt.update(started_identity=copy.deepcopy(attempt['process']),immutable_started_marker=sha(witness))
    item[FIELD]['start_witness']=copy.deepcopy(witness)

def queue_guard(item,queue,digest):
    specs=[]
    for ref in queue.get('specs',[]):
        path=Path(ref['path'])
        require(digest(path)==ref['sha256'],'queued spec changed')
        specs.append(json.loads(path.read_text()))
    if not any(is_spec(s) for s in specs):return
    require(len(specs)==1 and queue.get('pairs',[])==[],'observer queue only one point, no union or pair')
    require(scope_allowed(item,specs[0]),'unbound observer queue')

def crosscheck_data(data,item):
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
