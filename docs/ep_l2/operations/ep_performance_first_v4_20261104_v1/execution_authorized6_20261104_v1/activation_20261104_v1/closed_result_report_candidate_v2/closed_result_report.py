#!/usr/bin/env python3
"""Foreground one-shot metadata reporter. Import/default never starts actors.
No raw/log/Trace/archive-body access, registry writes, native imports or Git.
Default --once is read-only: JSON/Markdown candidates go to stdout only.
"""
import argparse,datetime,hashlib,json,os,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
UNKNOWN='UNKNOWN'
MAX_JSON_BYTES=32*1024*1024

def need(value,message):
    if not value:raise ValueError(message)
def same_ref(a,b):
    return isinstance(a,dict) and isinstance(b,dict) and all(a.get(k)==b.get(k) for k in ['path','sha256'])
def metadata_bytes(path):
    p=Path(path);need(p.suffix=='.json' and p.resolve().suffix=='.json','only JSON metadata may be read')
    need(p.stat().st_size<=MAX_JSON_BYTES,'metadata size bound exceeded')
    return p.read_bytes()
def read_json(path):return json.loads(metadata_bytes(path))
def exact(item):
    data=metadata_bytes(item['path']);need(hashlib.sha256(data).hexdigest()==item['sha256'],'metadata SHA drift: '+item['path'])
    return json.loads(data)
def file_ref(path):
    data=metadata_bytes(path);return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def authority_snapshot(cfg):
    # At most3 bounded coherence attempts, no sleep/background polling/lock/write.
    for attempt in range(3):
        e1=metadata_bytes(cfg['epoch_path']);r1=metadata_bytes(cfg['registry_path'])
        e2=metadata_bytes(cfg['epoch_path']);r2=metadata_bytes(cfg['registry_path'])
        e=json.loads(e1);digest=hashlib.sha256(r1).hexdigest()
        if e1==e2 and r1==r2 and digest==e.get('native_registry_sha256'):
            need(e.get('epoch')==2 and e.get('state')=='NATIVE_SCIENCE_ACTIVE','inactive authority epoch')
            need(e.get('holder')==os.uname().nodename,'native authority holder mismatch')
            return json.loads(r1),dict(registry_sha256=digest,epoch_sha256=hashlib.sha256(e1).hexdigest(),epoch=e['epoch'],holder=e['holder'],state=e['state'],coherence_attempt=attempt+1)
    raise ValueError('authority changed during bounded epoch/SHA snapshot')
def authority_still_matches(cfg,token):
    e=metadata_bytes(cfg['epoch_path']);r=metadata_bytes(cfg['registry_path'])
    return hashlib.sha256(e).hexdigest()==token['epoch_sha256'] and hashlib.sha256(r).hexdigest()==token['registry_sha256']
def lookup(reg,cohort,request=None):
    matches=[]
    for rid,q in reg['registered_future_requests'].items():
        if request is not None and rid!=request:continue
        rows=q.get('consumed',{})
        if isinstance(rows,dict) and cohort in rows:matches.append((rid,q,rows[cohort]))
    need(len(matches)==1,'missing or ambiguous exact registry cohort '+cohort)
    return matches[0]
def archive_gate(ar,cohort,uuid):
    need(ar.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS','archive closure status')
    need(ar.get('source_keep') is True and ar.get('cohort')==cohort and ar.get('uuid')==uuid,'archive cohort/UUID/KEEP')
    h=ar['archive_ref']['sha256'];need(re.fullmatch('[0-9a-f]{64}',h) is not None,'full archive SHA256 required')
    need(ar['archive_ref']['path'].startswith('/root/share/mnt164/'),'archive not on genuine164 path')
    rr=ar['native_restores'];need(len(rr)==2,'exactly two restore receipts required')
    need(len({x.get('target') for x in rr})==2 and all(x.get('target') for x in rr),'distinct restore targets required')
    for x in rr:
        need(x.get('status')=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' and x.get('archive_sha256')==h,'restore status/full SHA mismatch')
        need(x.get('source_keep') is True and x.get('permanent_scientific_source_deleted') is False,'restore source preservation')
        need(type(x.get('file_count')) is int and x['file_count']>0 and type(x.get('logical_bytes')) is int and x['logical_bytes']>0,'restore complete population')
    return dict(archive_sha256=h,archive_path=ar['archive_ref']['path'],two_distinct_restore_targets=[x['target'] for x in rr],archive_body_reopened=False)
def qualify_point(reg,spec_ref,cohort,request=None,expected_point_ref=None,expected_archive_ref=None):
    rid,q,row=lookup(reg,cohort,request)
    need(row.get('state')=='CLOSED_ACCEPTED','registry state is '+str(row.get('state',UNKNOWN)))
    s=exact(spec_ref);need(s['cohort']==cohort,'Spec cohort')
    admitted=q.get('admitted_specs',{})
    if cohort in admitted:need(admitted[cohort]==spec_ref['sha256'],'admitted Spec SHA mismatch')
    pr=row['accepted_point_ref'];ar_ref=row['archive_receipt_ref']
    if expected_point_ref is not None:need(same_ref(pr,expected_point_ref),'reference point differs from current registry')
    if expected_archive_ref is not None:need(same_ref(ar_ref,expected_archive_ref),'reference archive differs from current registry')
    pt=exact(pr);ar=exact(ar_ref)
    need(pt.get('status')=='EP_FULL_PERF_APPLICATION_ACCEPTED' and pt.get('hardware_drained') is True,'accepted status/full drain')
    need(pt.get('source_keep') is True and s.get('source_keep') is True,'accepted/Spec KEEP')
    need(pt['cohort']==cohort and pt['source_identity']==s['source_identity'],'accepted Source/cohort')
    need(pt['input_identity_sha256']==s['input_identity_sha256'] and pt['mode']==s['mode'],'accepted input/mode')
    need(same_ref(pt['spec_ref'],spec_ref),'accepted Spec pin')
    need(pt['uuid']==row['uuid']==ar['uuid'],'registry/point/archive UUID')
    need(same_ref(pt['validation_ref'],row['validation_ref']) and same_ref(pt['done_ref'],row['done_ref']),'validation/DONE identity')
    need(type(pt['cycles']) is int and pt['cycles']>0,'positive integer cycles')
    need(pt['CTA']==s['expected_CTA'] and pt['instructions']==s['expected_instructions'],'complete CTA/instruction population')
    need(pt['kernel_count']==len(s['expected_kernel_launches']),'complete kernel launch population')
    proof=archive_gate(ar,cohort,pt['uuid'])
    return dict(status='QUALIFIED_CLOSED_METADATA',cohort=cohort,mode=pt['mode'],program=s.get('program',s.get('workload',UNKNOWN)),cycles=pt['cycles'],state='CLOSED_ACCEPTED',request_id=rid,source_identity=pt['source_identity'],input_identity_sha256=pt['input_identity_sha256'],spec_ref=spec_ref,accepted_point_ref=pr,archive_receipt_ref=ar_ref,hardware_drained=True,CTA=pt['CTA'],instructions=pt['instructions'],kernel_count=pt['kernel_count'],geometry=s['geometry'],archive_proof=proof,_spec=s)
def safe_point(reg,spec_ref,cohort,request=None,expected_point_ref=None,expected_archive_ref=None):
    try:return qualify_point(reg,spec_ref,cohort,request,expected_point_ref,expected_archive_ref)
    except (KeyError,ValueError,OSError,TypeError) as exc:
        return dict(status=UNKNOWN,cohort=cohort,cycles=UNKNOWN,reason=str(exc))
def signed_metrics(candidate,baseline):
    need(type(candidate) is int and type(baseline) is int and baseline>0,'numeric closed cycles required')
    return dict(signed_cycle_delta=candidate-baseline,signed_cycle_reduction=baseline-candidate,cycle_reduction_percent=100.0*(baseline-candidate)/baseline,baseline_cycles=baseline,candidate_cycles=candidate)
def comparison(label,candidate,baseline,allow_geometry_difference=False,caveat=None):
    out=dict(label=label,candidate_cohort=candidate.get('cohort'),baseline_cohort=baseline.get('cohort'),signed_cycle_delta=UNKNOWN,signed_cycle_reduction=UNKNOWN,cycle_reduction_percent=UNKNOWN,status=UNKNOWN)
    if caveat:out['interpretation']=caveat
    try:
        need(candidate.get('status')==baseline.get('status')=='QUALIFIED_CLOSED_METADATA','one or both results not qualified closed metadata')
        for k in ['source_identity','input_identity_sha256','instructions','CTA','kernel_count']:need(candidate[k]==baseline[k],'comparison mismatch: '+k)
        if not allow_geometry_difference:need(candidate['geometry']==baseline['geometry'],'comparison geometry mismatch')
        a,b=candidate['_spec'],baseline['_spec']
        need(a['observer_env']==b['observer_env'],'observer environment differs')
        for k in ['-gpgpu_clock_domains','-dram_latency','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats','-gpgpu_ep_l2_ms_observer']:
            need(a['expected_effective_options'][k]==b['expected_effective_options'][k],'comparison fixed background differs: '+k)
        out.update(signed_metrics(candidate['cycles'],baseline['cycles']),status='QUALIFIED_CLOSED_METADATA_COMPARISON')
    except (KeyError,ValueError,TypeError) as exc:out['reason']=str(exc)
    return out
def public(value):
    if isinstance(value,dict):return {k:public(v) for k,v in value.items() if not k.startswith('_')}
    if isinstance(value,list):return [public(v) for v in value]
    return value

def report_from_snapshot(cfg,reg,token):
    m=exact(cfg['manifest_ref']);need(m['schema']=='EP_MAIN_PFV4_AUTHORIZED6_EXECUTION_MANIFEST_V1' and len(m['points'])==6,'exact6 manifest')
    rows=[];refs=[];pairs=[];by_group={};errors=[]
    for p in m['points']:
        s=exact(p['spec_ref']);g=p['group'];need(s['cohort']==p['cohort'] and s['mode']==p['mode'],'manifest/Spec identity')
        row=safe_point(reg,p['spec_ref'],p['cohort'],m['groups'][g]['request_id']);row.update(group=g,mode=p['mode']);rows.append(row);by_group[(g,p['mode'])]=row
        if g in ['A1','A3']:
            try:
                f=Path(m['groups'][g]['runtime_root'])/'FAMILY_SCOPE.json';pin=dict(path=str(f),sha256=s['pinned_files'][str(f)])
                scope=exact(pin);r=next(x for x in scope['points'] if x['id']==p['cohort'])['accepted_same_mode_ref']
                refrow=safe_point(reg,r['spec_ref'],r['cohort'],expected_point_ref=r['accepted_point_ref'],expected_archive_ref=r['archive_receipt_ref'])
                need(r['mode']==s['mode'],'FAMILY_SCOPE same-mode reference')
                if refrow.get('status')=='QUALIFIED_CLOSED_METADATA':need(refrow['mode']==s['mode'] and refrow['cycles']==r['cycles'] and refrow['source_identity']==s['source_identity'] and refrow['input_identity_sha256']==s['input_identity_sha256'],'FAMILY_SCOPE reference Source/input/cycles')
                refrow.update(group=g,role='FINAL_FAMILY_SCOPE_ACCEPTED_SAME_MODE_REF',family_scope_ref=pin);refs.append(refrow)
                pairs.append(comparison(g+' '+p['mode']+' G64W8 minus exact same-mode REF',row,refrow,True,'Geometry changes tag/data resources; no equal-area or PPA claim.'))
            except (KeyError,ValueError,OSError,StopIteration) as exc:
                errors.append(dict(cohort=p['cohort'],reference_error=str(exc)));pairs.append(dict(label=g+' '+p['mode']+' matched REF',status=UNKNOWN,signed_cycle_delta=UNKNOWN,cycle_reduction_percent=UNKNOWN,reason=str(exc)))
    # B uses the installed approved S/F reuse review. W is never its own same-mode REF.
    try:
        bs=[exact(p['spec_ref']) for p in m['points'] if p['group']=='B'];need(len(bs)==2 and same_ref(bs[0]['matched_controls_review_ref'],bs[1]['matched_controls_review_ref']),'B same approved controls review')
        review_ref=bs[0]['matched_controls_review_ref'];review=exact(review_ref)
        need(review['status']=='MAIN_REVIEWED_EXACT_SOURCE862_S_F1700_REUSE_PASS' and review['approved_by']=='EP-MAIN','B S/F review status')
        brefs={}
        for mode,expected_cycles in [('S',45974),('F',55925)]:
            r=review['controls'][mode];bref=safe_point(reg,r['spec_ref'],exact(r['accepted_point_ref'])['cohort'],expected_point_ref=r['accepted_point_ref'],expected_archive_ref=r['archive_receipt_ref'])
            if bref.get('status')=='QUALIFIED_CLOSED_METADATA':need(bref['mode']==mode and bref['cycles']==r['cycles']==expected_cycles and bref['source_identity']==review['source_identity'],'B exact S/F control')
            bref.update(group='B',role='MATCHED_S_F_REUSE_CONTROL',review_ref=review_ref);refs.append(bref);brefs[mode]=bref
        w=by_group[('B','W_ONLY')];wv=by_group[('B','WV_ZERO_RO')]
        pairs.extend([comparison('B W minus S',w,brefs['S'],caveat='Joint W implementation comparison at fixed background; W is not a same-mode REF.'),comparison('B WV minus W',wv,w,caveat='Incremental V-conditioned comparison on W background.'),comparison('B F minus WV',brefs['F'],wv,caveat='Not an independent causal T effect: F versus WV is a combined-mode contrast and may include interactions.')])
    except (KeyError,ValueError,OSError) as exc:
        errors.append(dict(group='B',reference_error=str(exc)))
        for label in ['B W minus S','B WV minus W','B F minus WV']:
            if not any(x['label']==label for x in pairs):pairs.append(dict(label=label,status=UNKNOWN,signed_cycle_delta=UNKNOWN,signed_cycle_reduction=UNKNOWN,cycle_reduction_percent=UNKNOWN,reason=str(exc)))
    # The original V3 eight accepted mode/geometry points, not V2 controls.
    old=exact(cfg['historical_v3_results_ref']);hist=[]
    for p in old['points']:
        if p.get('group')=='midtag' and p.get('state')=='CLOSED_ACCEPTED':
            r=safe_point(reg,p['spec_ref'],p['cohort'],expected_point_ref=p['accepted_point_ref'],expected_archive_ref=p['archive_receipt_ref']);r.update(group='V3_MIDTAG');hist.append(r)
    need(len(hist)==8,'exact original V3 eight geometry/mode cells')
    tag_pairs=[]
    for work in ['FWT','GEMM']:
        for mode in ['S','WV_ZERO_RO']:
            cells=[r for r in hist if ('_'+work+'_') in r['cohort'] and ('_'+mode+'_') in r['cohort']]
            baseline=next(r for r in cells if '_G32W16_' in r['cohort']);candidate=next(r for r in cells if '_G64W8_' in r['cohort'])
            tag_pairs.append(comparison('V3 '+work+' '+mode+' G64W8 minus G32W16',candidate,baseline,True,'Within-workload/mode geometry comparison only; no cross-workload aggregate or equal-area claim.'))
    out=dict(schema='EP_PFV4_READONLY_CLOSED_RESULT_REPORT_CANDIDATE_V1',status='ALL_SIX_CLOSED_QUALIFIED' if all(r['status']=='QUALIFIED_CLOSED_METADATA' for r in rows) else 'PARTIAL_UNKNOWN_RESULTS_PRESERVED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_ref=cfg['manifest_ref'],authority_snapshot=token,points=rows,matched_references=refs,comparisons=pairs,original_v3_eight_accepted_mode_points=hist,original_v3_geometry_comparisons=tag_pairs,errors=errors,scope=dict(metadata_only=True,raw_or_Trace_or_archive_body_reads=False,registry_writes=False,actors_started=False,Git_publication=False,cross_workload_aggregation=False,physical_PPA_or_timing_claim=False,unknown_results_not_imputed=True,signed_changes_preserved=True))
    return public(out)
def markdown(report):
    lines=['# Closed metadata performance report candidate','', 'Status: '+report['status'], '', 'Only CLOSED_ACCEPTED results with exact Source/input/Spec/full drain, full-SHA archive and two distinct same-SHA native restores receive cycles. Missing results remain UNKNOWN.','', '| Group | Cohort | Mode | Cycles | Qualification |','|---|---|---|---:|---|']
    for r in report.get('points',[]):lines.append('| '+str(r.get('group',UNKNOWN))+' | '+r['cohort']+' | '+str(r.get('mode',UNKNOWN))+' | '+str(r.get('cycles',UNKNOWN))+' | '+r['status']+' |')
    lines.extend(['','Delta is candidate minus baseline; reduction percent is 100*(baseline-candidate)/baseline. Both signs are retained.','','| Comparison | Signed cycle delta | Reduction percent | Status |','|---|---:|---:|---|'])
    for r in report.get('comparisons',[])+report.get('original_v3_geometry_comparisons',[]):
        pct=r.get('cycle_reduction_percent',UNKNOWN);pct=format(pct,'+.6f')+'%' if isinstance(pct,(int,float)) else UNKNOWN
        delta=r.get('signed_cycle_delta',UNKNOWN);delta=format(delta,'+d') if type(delta) is int else UNKNOWN
        lines.append('| '+r['label']+' | '+str(delta)+' | '+pct+' | '+r['status']+' |')
    lines.extend(['','Original V3 eight accepted cells (each independently requalified from closed metadata):','','| Cohort | Mode | Cycles | Qualification |','|---|---|---:|---|'])
    for r in report.get('original_v3_eight_accepted_mode_points',[]):lines.append('| '+r['cohort']+' | '+str(r.get('mode',UNKNOWN))+' | '+str(r.get('cycles',UNKNOWN))+' | '+r['status']+' |')
    lines.extend(['','A1/A3 references come from each final FAMILY_SCOPE accepted_same_mode_ref. B reuses S45974/F55925; W is not a same-mode REF. F minus WV does not identify an independent causal T effect. Geometry changes resources; no equal-area, cross-workload aggregate, geometric mean or PPA claim.','','This foreground tool reads only JSON metadata and emits stdout. It never starts a model/background actor, writes authority/controller state, imports native/dispatcher code, reads raw logs/Trace/archive bodies, copies Trace or publishes Git.'])
    return '\n'.join(lines)+'\n'
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--once',action='store_true',default=True,help='one foreground read-only snapshot (also the default)');ap.add_argument('--format',choices=['json','md'],default='json');args=ap.parse_args(argv)
    cfg=read_json(HERE/'REPORT_READSET.json')
    try:
        reg,token=authority_snapshot(cfg);report=report_from_snapshot(cfg,reg,token)
        need(authority_still_matches(cfg,token),'authority changed while gathering immutable metadata; rerun manually')
    except (ValueError,KeyError,OSError,TypeError,StopIteration) as exc:
        try:
            descriptor=exact(cfg['manifest_ref']);unknown_rows=[dict(cohort=p['cohort'],group=p['group'],mode=p['mode'],status=UNKNOWN,cycles=UNKNOWN,reason=str(exc)) for p in descriptor['points']]
        except (ValueError,KeyError,OSError,TypeError):unknown_rows=[]
        report=dict(schema='EP_PFV4_READONLY_CLOSED_RESULT_REPORT_CANDIDATE_V1',status='HOLD_UNKNOWN',reason=str(exc),points=unknown_rows,comparisons=[],original_v3_eight_accepted_mode_points=[],original_v3_geometry_comparisons=[],registry_writes=False,actors_started=False)
    md=markdown(report)
    if args.format=='md':print(md,end='')
    else:report['markdown_candidate']=md;print(json.dumps(report,indent=2,sort_keys=True))
    return 0 if report['status']!='HOLD_UNKNOWN' else 2
if __name__=='__main__':sys.exit(main())
