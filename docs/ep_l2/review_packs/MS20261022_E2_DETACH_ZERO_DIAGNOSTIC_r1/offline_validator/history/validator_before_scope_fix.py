"""Offline declaration checker. Not a simulator parser or scientific qualification.

No production metric names are built in. An owner-reviewed adapter must declare
metrics/domains/units, exact scope coverage, and conservation equations.
"""
import json
import sys


def _audit(document):
    errors, incomplete, checks = [], [], []
    def err(code, where, detail):
        errors.append({'code': code, 'where': where, 'detail': detail})
    def uint(v):
        return type(v) is int and 0 <= v <= (1 << 64) - 1
    def interval(s):
        i = s.get('interval', {})
        return i.get('start'), i.get('end')
    if not isinstance(document, dict):
        return {'status':'INVALID','errors':[{'code':'DOCUMENT_TYPE'}], 'incomplete':[], 'checks':[]}
    declarations = document.get('declarations', {})
    definitions = declarations.get('metrics', {})
    domains = declarations.get('domains', [])
    if not isinstance(domains, list) or not domains or not all(isinstance(d,str) and d for d in domains) or len(set(domains)) != len(domains):
        err('DOMAINS', 'declarations', 'Explicit unique domains required')
    if not isinstance(definitions, dict) or not definitions:
        err('METRIC_DECLARATIONS', 'declarations', 'Owner metric declarations required')
        definitions = {}
    for name, m in definitions.items():
        if not isinstance(m, dict) or m.get('domain') not in domains or not isinstance(m.get('unit'),str) or not m.get('unit') or m.get('measurement_kind') not in ('EXPOSURE_COUNT','TRANSITION_COUNT','REQUESTER_COUNT','POPULATION_COUNT'):
            err('METRIC_DOMAIN_UNIT', name, 'Explicit declared domain and unit required')
    records = {}
    scope_keys = set()
    for record in document.get('records', []):
        if not isinstance(record, dict):
            err('RECORD_TYPE', 'records', 'Object required'); continue
        rid = record.get('id')
        if not isinstance(rid, str) or not rid or rid in records:
            err('DUPLICATE_OR_INVALID_RECORD', str(rid), 'Unique record ID required'); continue
        records[rid] = record
        scope = record.get('scope', {})
        start, end = interval(scope)
        if scope.get('domain') not in domains or scope.get('level') not in ('GLOBAL','SLICE','KERNEL_INTERVAL','UNATTRIBUTED'):
            err('SCOPE', rid, 'Explicit domain and supported level required')
        if not uint(start) or not uint(end) or end < start:
            err('INTERVAL', rid, 'Half-open nonnegative physical-clock interval required')
        dims = scope.get('dimensions')
        if not isinstance(dims, dict) or not dims:
            err('DIMENSIONS', rid, 'Explicit dimensions including run ID required')
        if scope.get('level') == 'KERNEL_INTERVAL' and (type(scope.get('overlap')) is not bool or scope.get('attribution') not in ('INTERVAL_SCOPE','EXACT_REQUESTER')):
            err('KERNEL_SCOPE', rid, 'Attribution and overlap flags required')
        key = json.dumps(scope,sort_keys=True)
        if key in scope_keys:
            err('DUPLICATE_SCOPE', rid, 'Scope repeated under another ID')
        scope_keys.add(key)
        if type(record.get('overflow')) is not bool:
            err('OVERFLOW_FLAG_MISSING', rid, 'Explicit boolean overflow required')
        elif record['overflow']:
            err('COUNTER_OVERFLOW', rid, 'Overflow invalidates diagnostic counts')
        metrics = record.get('metrics', {})
        if not isinstance(metrics,dict):
            err('METRICS', rid, 'Object required'); continue
        for name, value in metrics.items():
            path = rid + '.' + name
            definition = definitions.get(name)
            if definition is None:
                err('UNDECLARED_METRIC', path, 'Adapter must declare name'); continue
            if definition.get('domain') != scope.get('domain'):
                err('RECORD_DOMAIN_MISMATCH', path, 'Counter emitted in wrong domain')
            if not isinstance(value, dict) or value.get('status') not in ('OK','NA'):
                err('METRIC_VALUE', path, 'Use explicit OK/value or NA/reason'); continue
            if value['status'] == 'OK' and (not uint(value.get('value')) or 'reason' in value):
                err('COUNT_TYPE', path, 'Unsigned64 integer required, bool forbidden')
            if value['status'] == 'NA' and ('value' in value or not isinstance(value.get('reason'),str) or not value.get('reason')):
                err('NA_VALUE', path, 'NA has reason and no numeric value')
    for required_scope in declarations.get('required_scopes',[]):
        if json.dumps(required_scope,sort_keys=True) not in scope_keys:
            err('MISSING_REQUIRED_SCOPE',str(required_scope),'Owner adapter requires this exact scope; missing is not zero')
    def reference(ref):
        if not isinstance(ref, dict) or set(ref) != {'record','metric'}:
            err('REFERENCE',str(ref),'Exact record/metric reference required'); return None
        r = records.get(ref['record'])
        d = definitions.get(ref['metric'])
        value = r.get('metrics',{}).get(ref['metric']) if r else None
        if r is None or d is None or value is None:
            err('MISSING_COUNTER',str(ref),'Missing is not zero'); return None
        if value.get('status') == 'NA':
            incomplete.append({'code':'NA_RELATION','reference':ref,'reason':value.get('reason')}); return None
        if value.get('status') != 'OK' or not uint(value.get('value')):
            return None
        return r,d,value['value']
    for ref in declarations.get('required',[]):
        reference(ref)
    for ref in declarations.get('expected_na',[]):
        r = records.get(ref.get('record'),{})
        v = r.get('metrics',{}).get(ref.get('metric'))
        if not isinstance(v,dict) or v.get('status') != 'NA':
            err('NA_FILLED_AS_ZERO',str(ref),'Declared unavailable counter must remain NA')
    relations = declarations.get('relations',[])
    if not relations:
        err('NO_RELATIONS','declarations','No conservation claims declared')
    relation_ids=set()
    for relation in relations:
        name=relation.get('id')
        if not isinstance(name,str) or not name or name in relation_ids:
            err('RELATION_ID',str(name),'Unique relation ID required')
        relation_ids.add(name)
        kind=relation.get('kind')
        terms=relation.get('parts',[])
        if kind not in ('partition','equivalence','rollup') or not terms:
            err('RELATION_KIND',str(name),'Explicit nonempty partition/equivalence/rollup required'); continue
        if kind=='partition' and relation.get('exclusive') is not True:
            err('NONEXCLUSIVE_SUM',name,'Only explicitly exclusive partitions may be conserved')
        if len({json.dumps(x,sort_keys=True) for x in terms}) != len(terms):
            err('REPEATED_TERM',name,'Duplicate counter would double count')
        target=reference(relation.get('total'))
        values=[reference(x) for x in terms]
        if not target or any(x is None for x in values):
            continue
        allvalues=[target]+values
        if len({x[1].get('unit') for x in allvalues}) != 1:
            err('UNIT_MISMATCH',name,'Head cycles, transitions and requester responses are distinct'); continue
        if len({x[1].get('domain') for x in allvalues}) != 1:
            # Explicit transition reconciliation only. A string label cannot
            # assert head cycles and access attempts are the same event.
            event={x[1].get('event_identity') for x in allvalues}
            if kind!='equivalence' or relation.get('bridge')!='SAME_REAL_TRANSITION' or len(event)!=1 or None in event or not relation.get('evidence') or any(x[1].get('measurement_kind')!='TRANSITION_COUNT' for x in allvalues):
                err('DOMAIN_MISMATCH',name,'Cross-domain equality requires same-event transition provenance'); continue
        starts={interval(x[0]['scope']) for x in allvalues}
        if kind in ('partition','equivalence'):
            if len(starts)!=1 or len({json.dumps({k:v for k,v in x[0]['scope'].items() if k!='domain'},sort_keys=True) for x in allvalues})!=1:
                err('SCOPE_MISMATCH',name,'Equation must use same population and interval'); continue
            if kind=='equivalence' and len(values)!=1:
                err('EQUIVALENCE_ARITY',name,'Equivalence has exactly one paired measure'); continue
        if kind=='rollup':
            mode=relation.get('axis')
            parent=target[0]['scope']
            parent_dims={k:v for k,v in parent.get('dimensions',{}).items() if k not in ('slice','kernel')}
            for child,_,_ in values:
                child_scope=child['scope']
                child_dims={k:v for k,v in child_scope.get('dimensions',{}).items() if k not in ('slice','kernel')}
                if parent_dims!=child_dims:
                    err('ROLLUP_POPULATION',name,'Child run/config population differs')
                lo,hi=interval(child_scope)
                p_lo,p_hi=interval(parent)
                if not all(uint(v) for v in (lo,hi,p_lo,p_hi)) or lo<p_lo or hi>p_hi:
                    err('ROLLUP_INTERVAL',name,'Child outside parent physical interval')
            labels=relation.get('members')
            expected=relation.get('expected_members')
            if mode not in ('slice','kernel') or not isinstance(labels,list) or not isinstance(expected,list) or len(labels)!=len(values) or len(labels)!=len(set(labels)) or set(labels)!=set(expected):
                err('ROLLUP_MEMBERS',name,'Exact declared children required including unattributed'); continue
            if relation.get('unattributed_policy') not in ('EXPLICIT_BUCKET','NOT_APPLICABLE_PARTITION_BY_SLICE'):
                err('UNATTRIBUTED_POLICY',name,'Explicit handling of unattributed/residual required')
            if mode=='kernel' and ('UNATTRIBUTED' not in labels or relation.get('unattributed_policy')!='EXPLICIT_BUCKET'):
                err('UNATTRIBUTED_MISSING',name,'Kernel rollup requires residual bucket')
            if mode=='slice' and (parent.get('level')!='GLOBAL' or any(x[0]['scope'].get('level')!='SLICE' for x in values)):
                err('ROLLUP_LEVEL',name,'Slice rollup needs global parent and slice children')
            if mode=='kernel' and (parent.get('level') not in ('GLOBAL','SLICE') or any(x[0]['scope'].get('level')!='KERNEL_INTERVAL' for label,x in zip(labels,values) if label!='UNATTRIBUTED') or any(x[0]['scope'].get('level')!='UNATTRIBUTED' for label,x in zip(labels,values) if label=='UNATTRIBUTED')):
                err('ROLLUP_LEVEL',name,'Kernel rollup needs interval children plus explicit unattributed scope')
            if mode=='slice' and len(starts)!=1:
                err('ROLLUP_INTERVAL',name,'Slice rollup must share whole interval')
            if mode=='kernel':
                kernels=[x[0]['scope'] for label,x in zip(labels,values) if label!='UNATTRIBUTED']
                if any(s.get('overlap') is not False for s in kernels):
                    err('OVERLAPPING_KERNEL_SUM',name,'Overlapping/unknown intervals cannot be summed')
                ordered=sorted(interval(s) for s in kernels)
                if any(a[1]>b[0] for a,b in zip(ordered,ordered[1:])):
                    err('OVERLAPPING_KERNEL_SUM',name,'Physical intervals overlap')
        total=target[2]; actual=sum(x[2] for x in values)
        if total!=actual:
            err('CONSERVATION',name,{'total':total,'sum':actual})
        else:
            checks.append({'id':name,'kind':kind,'value':total})
    samples=document.get('samples')
    if not isinstance(samples,dict):
        err('SAMPLES_FLAGS','samples','Explicit cap/emitted/dropped/truncated required')
    else:
        cap=samples.get('cap'); emitted=samples.get('emitted'); dropped=samples.get('dropped')
        rows=samples.get('rows')
        if not all(uint(x) for x in (cap,emitted,dropped)) or cap>64 or not isinstance(rows,list) or emitted!=len(rows) or emitted>cap:
            err('SAMPLE_BOUNDS','samples','Bound64 and exact emitted rows required')
        if type(samples.get('truncated')) is not bool or (uint(dropped) and samples.get('truncated') != (dropped>0)):
            err('SAMPLE_TRUNCATION','samples','Dropped/truncated must agree')
        seen=set()
        for row in rows or []:
            if not isinstance(row,dict) or not all(uint(row.get(k)) for k in ('slice','physical_cycle','request_uid')) or not row.get('reason'):
                err('SAMPLE_SCHEMA','samples','Bounded sample requires head key and reason'); continue
            key=tuple(row[k] for k in ('slice','physical_cycle','request_uid'))+(row['reason'],)
            if key in seen:
                err('DUPLICATE_SAMPLE','samples','Same reason/sample key emitted twice')
            seen.add(key)
    return {'schema':'E2_DECLARATIVE_COUNTER_AUDIT_RESULT_V1','status':'INVALID' if errors else ('INCOMPLETE' if incomplete else 'VALID_DECLARATIONS_ONLY'),'errors':errors,'incomplete':incomplete,'checks':checks,'scope':'OFFLINE_DECLARED_COUNTS_ONLY_NOT_NATIVE_OR_APPLICATION_QUALIFICATION'}


def audit(document):
    try:
        return _audit(document)
    except (TypeError, ValueError, KeyError, AttributeError, IndexError) as exc:
        return {'schema':'E2_DECLARATIVE_COUNTER_AUDIT_RESULT_V1','status':'INVALID','errors':[{'code':'MALFORMED_DOCUMENT','detail':type(exc).__name__}], 'incomplete':[], 'checks':[], 'scope':'OFFLINE_DECLARED_COUNTS_ONLY_NOT_NATIVE_OR_APPLICATION_QUALIFICATION'}


if __name__=='__main__':
    with open(sys.argv[1],encoding='utf8') as f:
        result=audit(json.load(f))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    sys.exit(0 if result['status']=='VALID_DECLARATIONS_ONLY' else 1)
