import copy
import json
import time
from pathlib import Path
from validator import audit


def ok(v): return {'status':'OK','value':v}
def ref(record, metric): return {'record':record,'metric':metric}
def base():
    # Synthetic aliases intentionally do not claim A2's official schema.
    units={'H':('HEAD','HEAD_CYCLE'),'skipped':('HEAD','HEAD_CYCLE'),'hit':('HEAD','HEAD_CYCLE'),'miss':('HEAD','HEAD_CYCLE'),'rawF':('HEAD','HEAD_CYCLE'),'rewrite':('HEAD','HEAD_CYCLE'),'remainF':('HEAD','HEAD_CYCLE'),'notconsulted':('HEAD','HEAD_CYCLE'),'C':('ACCESS','ACCESS_ATTEMPT'),'accessOK':('ACCESS','ACCESS_ATTEMPT'),'accessDenied':('ACCESS','ACCESS_ATTEMPT'),'realD':('LIFETIME','DETACH_TRANSITION'),'newD':('ACCESS','DETACH_TRANSITION'),'triggerOK':('ACCESS','DETACH_TRANSITION'),'triggerDenied':('ACCESS','DETACH_TRANSITION'),'txn':('LIFETIME','TRANSACTION'),'retired':('LIFETIME','TRANSACTION'),'live':('LIFETIME','TRANSACTION'),'responses':('LIFETIME','REQUESTER_RESPONSE')}
    defs={n:{'domain':d,'unit':u,'measurement_kind':'TRANSITION_COUNT' if u=='DETACH_TRANSITION' else ('REQUESTER_COUNT' if u=='REQUESTER_RESPONSE' else 'EXPOSURE_COUNT')} for n,(d,u) in units.items()}
    for n in ('realD','newD'): defs[n]['event_identity']='REAL_DETACH_HANDSHAKE'
    def record(rid,domain,values):
        return {'id':rid,'scope':{'domain':domain,'level':'GLOBAL','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic'}},'overflow':False,'metrics':{k:ok(v) for k,v in values.items()}}
    rows=[record('h','HEAD',{'H':10,'skipped':1,'hit':2,'miss':3,'rawF':4,'rewrite':2,'remainF':1,'notconsulted':1}),record('a','ACCESS',{'C':3,'accessOK':2,'accessDenied':1,'newD':1,'triggerOK':0,'triggerDenied':1}),record('l','LIFETIME',{'realD':1,'txn':1,'retired':1,'live':0,'responses':3})]
    def partition(name,r,total,parts): return {'id':name,'kind':'partition','exclusive':True,'total':ref(r,total),'parts':[ref(r,p) for p in parts]}
    relations=[partition('head_partition','h','H',['skipped','hit','miss','rawF']),partition('raw_pressure_rewrite','h','rawF',['rewrite','remainF','notconsulted']),partition('actual_access','a','C',['accessOK','accessDenied']),partition('detach_trigger_outcome','a','newD',['triggerOK','triggerDenied']),partition('lifecycle','l','txn',['retired','live']),{'id':'real_transition_reconcile','kind':'equivalence','total':ref('l','realD'),'parts':[ref('a','newD')],'bridge':'SAME_REAL_TRANSITION','evidence':'synthetic one handshake observed in both domains'}]
    return {'declarations':{'domains':['HEAD','ACCESS','LIFETIME'],'metrics':defs,'relations':relations,'required':[ref(r['id'],m) for r in rows for m in r['metrics']]},'records':rows,'samples':{'cap':64,'emitted':1,'dropped':0,'truncated':False,'rows':[{'slice':0,'physical_cycle':10,'request_uid':1,'reason':'SYNTHETIC_DETACH_THEN_REQUEST_DENIED'}]}}


def rollup(kind='slice'):
    d=base(); d['declarations']['metrics']['R']={'domain':'HEAD','unit':'HEAD_CYCLE','measurement_kind':'EXPOSURE_COUNT'}
    global_r={'id':'g','scope':{'domain':'HEAD','level':'GLOBAL','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-rollup'}},'overflow':False,'metrics':{'R':ok(7)}}
    children=[]
    if kind=='slice':
        for i,value in enumerate((3,4)):
            children.append({'id':'s'+str(i),'scope':{'domain':'HEAD','level':'SLICE','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-rollup','slice':i}},'overflow':False,'metrics':{'R':ok(value)}})
        labels=['0','1']; policy='NOT_APPLICABLE_PARTITION_BY_SLICE'
    else:
        global_r['scope']['level']='SLICE'
        global_r['scope']['dimensions']['slice']=0
        for i,(lo,hi,value) in enumerate(((0,50,2),(50,100,3))):
            children.append({'id':'k'+str(i),'scope':{'domain':'HEAD','level':'KERNEL_INTERVAL','interval':{'start':lo,'end':hi},'dimensions':{'run':'synthetic-rollup','slice':0,'kernel':i},'overlap':False,'attribution':'INTERVAL_SCOPE'},'overflow':False,'metrics':{'R':ok(value)}})
        children.append({'id':'u','scope':{'domain':'HEAD','level':'UNATTRIBUTED','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-rollup','slice':0,'kernel':'UNATTRIBUTED'}},'overflow':False,'metrics':{'R':ok(2)}})
        labels=['0','1','UNATTRIBUTED']; policy='EXPLICIT_BUCKET'
    d['records'] += [global_r]+children
    d['declarations']['relations'].append({'id':'rollup','kind':'rollup','total':ref('g','R'),'parts':[ref(c['id'],'R') for c in children],'axis':kind,'members':labels,'expected_members':labels[:],'unattributed_policy':policy})
    return d


def phase_rollup():
    d=base()
    d['declarations']['metrics']['R']={'domain':'HEAD','unit':'HEAD_CYCLE','measurement_kind':'EXPOSURE_COUNT'}
    source={'commit':'a'*40,'path':'synthetic-fixture/phase_assignment_contract.json','sha256':'b'*64}
    parent={'id':'p0','scope':{'domain':'HEAD','level':'SLICE','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-phase','slice':0}},'overflow':False,'metrics':{'R':ok(7)}}
    labels=['SINGLE_ACTIVE_INTERVAL:100','SINGLE_ACTIVE_INTERVAL:101','UNASSIGNED','OVERLAP_UNKNOWN']
    children=[]
    for i,(label,value) in enumerate(zip(labels,(2,3,1,1))):
        children.append({'id':'phase'+str(i),'scope':{'domain':'HEAD','level':'PHASE_BUCKET','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-phase','slice':0,'phase_bucket':label},'partition_id':'synthetic-disjoint-assignment','attribution':'PHYSICAL_PHASE_ONLY'},'overflow':False,'metrics':{'R':ok(value)}})
    d['records'] += [parent]+children
    d['declarations']['relations'].append({'id':'physical_phase_rollup','kind':'rollup','axis':'phase','total':ref('p0','R'),'parts':[ref(c['id'],'R') for c in children],'members':labels,'expected_members':labels[:],'unattributed_policy':'EXPLICIT_PHASE_BUCKETS','assignment_partition':True,'partition_provenance':{'partition_id':'synthetic-disjoint-assignment','mutually_exclusive':True,'coverage':'COMPLETE','source_ref':source}})
    return d


def run():
    cases=[]
    def check(name,d,status,code=None):
        r=audit(d)
        assert r['status']==status,(name,r)
        if code: assert any(e.get('code')==code for e in r['errors']),(name,r)
        cases.append({'name':name,'expected':status,'actual':r['status'],'error_codes':[e.get('code') for e in r['errors']]})
    check('positive_declarations_only',base(),'VALID_DECLARATIONS_ONLY')
    check('detach_then_request_denied_legal',base(),'VALID_DECLARATIONS_ONLY')
    check('multiple_waiter_responses_not_transaction_count',base(),'VALID_DECLARATIONS_ONLY')
    check('raw_fail_masked_by_preview_miss_is_counted',base(),'VALID_DECLARATIONS_ONLY')
    check('native_preview_not_consulted_is_separate',base(),'VALID_DECLARATIONS_ONLY')
    d=base();d['records'][0]['metrics']['rawF']=ok(3);check('under_count',d,'INVALID','CONSERVATION')
    d=base();d['records'][0]['metrics']['rewrite']=ok(3);check('over_count',d,'INVALID','CONSERVATION')
    d=base();d['records'][0]['metrics']['H']=ok(True);check('bool_is_not_integer',d,'INVALID','COUNT_TYPE')
    d=base();d['records'][0]['metrics']['H']=ok(-1);check('negative_is_invalid',d,'INVALID','COUNT_TYPE')
    d=base();d['records'][0]['metrics']['H']=ok(1<<64);check('uint64_wrap_is_invalid',d,'INVALID','COUNT_TYPE')
    d=base();del d['records'][0]['metrics']['rawF'];check('missing_counter_not_zero',d,'INVALID','MISSING_COUNTER')
    d=base();d['records'][0]['metrics']['rawF']={'status':'NA','reason':'prior gate prevented probe'};check('NA_prevents_closed_claim',d,'INCOMPLETE')
    d=base();d['records'][0]['metrics']['rawF']={'status':'NA','reason':'not reached','value':0};check('NA_plus_zero_rejected',d,'INVALID','NA_VALUE')
    d=base();d['declarations']['expected_na']=[ref('h','rawF')];d['records'][0]['metrics']['rawF']=ok(0);check('declared_NA_cannot_be_filled',d,'INVALID','NA_FILLED_AS_ZERO')
    d=base();d['declarations']['relations'].append({'id':'fake_domain','kind':'equivalence','total':ref('h','H'),'parts':[ref('a','C')]});check('head_cycles_not_access_attempts',d,'INVALID','UNIT_MISMATCH')
    d=base();d['declarations']['metrics']['C']['unit']='HEAD_CYCLE';d['declarations']['metrics']['accessOK']['unit']='HEAD_CYCLE';d['declarations']['metrics']['accessDenied']['unit']='HEAD_CYCLE';d['declarations']['relations'].append({'id':'fake_domain','kind':'equivalence','total':ref('h','H'),'parts':[ref('a','C')]});check('renamed_unit_cannot_bridge_domains',d,'INVALID','DOMAIN_MISMATCH')
    d=base();d['records'][2]['metrics']['realD']=ok(0);check('existing_detached_must_match_real_success',d,'INVALID','CONSERVATION')
    d=base();d['declarations']['relations'][0]['exclusive']=False;check('nonexclusive_masks_not_partition',d,'INVALID','NONEXCLUSIVE_SUM')
    d=base();d['declarations']['relations'][0]['parts'].append(ref('h','hit'));check('duplicate_partition_term',d,'INVALID','REPEATED_TERM')
    d=base();d['records'][0]['overflow']=True;check('overflow_invalidates',d,'INVALID','COUNTER_OVERFLOW')
    d=base();del d['records'][0]['overflow'];check('missing_overflow_marker',d,'INVALID','OVERFLOW_FLAG_MISSING')
    d=base();d['samples']['cap']=65;check('sample_cap_exceeds64',d,'INVALID','SAMPLE_BOUNDS')
    d=base();d['samples']['dropped']=3;check('dropped_requires_truncated',d,'INVALID','SAMPLE_TRUNCATION')
    d=base();d['samples']['rows']*=2;d['samples']['emitted']=2;check('duplicate_samples',d,'INVALID','DUPLICATE_SAMPLE')
    check('slice_rollup',rollup(),'VALID_DECLARATIONS_ONLY')
    d=rollup();d['declarations']['required_scopes']=[copy.deepcopy(d['records'][-1]['scope'])];d['records'].pop();check('missing_required_slice_scope',d,'INVALID','MISSING_REQUIRED_SCOPE')
    d=rollup();d['records'][-1]['metrics']['R']=ok(3);check('slice_rollup_missing_residual',d,'INVALID','CONSERVATION')
    d=rollup();d['declarations']['relations'][-1]['expected_members'].append('2');check('omitted_expected_slice',d,'INVALID','ROLLUP_MEMBERS')
    check('kernel_with_explicit_unattributed',rollup('kernel'),'VALID_DECLARATIONS_ONLY')
    d=rollup('kernel');d['declarations']['relations'][-1]['members'][-1]='other';d['declarations']['relations'][-1]['expected_members'][-1]='other';check('unattributed_not_discarded',d,'INVALID','UNATTRIBUTED_MISSING')
    d=rollup('kernel');d['records'][-2]['scope']['interval']['start']=40;check('overlap_cannot_be_summed',d,'INVALID','OVERLAPPING_KERNEL_SUM')
    d=rollup('kernel');d['records'][-2]['scope']['overlap']=True;check('explicit_overlap_cannot_be_summed',d,'INVALID','OVERLAPPING_KERNEL_SUM')
    d=base();d['records'][0]['scope']['interval']['start']=True;check('interval_bool_invalid',d,'INVALID','INTERVAL')
    d=base();d['records'][2]['scope']['interval']['end']=99;check('different_intervals_not_equal',d,'INVALID','SCOPE_MISMATCH')
    d=base();d['declarations']['metrics']['H']['event_identity']='FAKE';d['declarations']['metrics']['C']['event_identity']='FAKE';d['declarations']['metrics']['C']['unit']='HEAD_CYCLE';d['declarations']['metrics']['accessOK']['unit']='HEAD_CYCLE';d['declarations']['metrics']['accessDenied']['unit']='HEAD_CYCLE';d['declarations']['relations'].append({'id':'fake_event_bridge','kind':'equivalence','total':ref('h','H'),'parts':[ref('a','C')],'bridge':'SAME_REAL_TRANSITION','evidence':'fabricated-label'});check('exposure_cannot_pose_as_same_transition',d,'INVALID','DOMAIN_MISMATCH')
    d=rollup();d['records'][-1]['scope']['dimensions']['slice']=99;check('root_witness_expected01_actual0_99',d,'INVALID','ROLLUP_MEMBER_BINDING')
    d=rollup('kernel');d['records'][-2]['scope']['dimensions']['kernel']=99;check('kernel_fake_label',d,'INVALID','ROLLUP_MEMBER_BINDING')
    d=rollup('kernel');d['records'][-2]['scope']['dimensions']['slice']=1;check('kernel_children_from_different_slices',d,'INVALID','ROLLUP_POPULATION')
    d=base();d['records'][0]['scope']['dimensions']['run']=' ';check('empty_run_rejected',d,'INVALID','RUN_ID')
    d=base();del d['records'][0]['scope']['dimensions']['run'];check('missing_run_rejected',d,'INVALID','RUN_ID')
    d=rollup();del d['records'][-1]['scope']['dimensions']['slice'];check('slice_level_missing_slice_id',d,'INVALID','SLICE_ID')
    d=rollup('kernel');del d['records'][-2]['scope']['dimensions']['kernel'];check('kernel_level_missing_kernel_id',d,'INVALID','KERNEL_ID')
    d=rollup('kernel');del d['records'][-2]['scope']['dimensions']['slice'];check('kernel_level_missing_slice_id',d,'INVALID','SLICE_ID')
    d=rollup('kernel');d['records'][-1]['scope']['dimensions']['kernel']='other';check('unattributed_scope_identity_required',d,'INVALID','UNATTRIBUTED_ID')
    d=rollup();d['records'][-1]['scope']['dimensions']['slice']=True;check('slice_bool_rejected',d,'INVALID','SLICE_ID')
    d=rollup('kernel');d['records'][-2]['scope']['interval']['end']=101;check('kernel_outside_parent_period',d,'INVALID','ROLLUP_INTERVAL')
    d=rollup();d['records'][-1]['scope']['interval']={'start':100,'end':200};check('slice_wrong_period',d,'INVALID','ROLLUP_INTERVAL')
    d=rollup('kernel');[r['scope']['interval'].update(start=r['scope']['interval']['start']+200,end=r['scope']['interval']['end']+200) for r in d['records']];check('shifted_disjoint_kernel_periods_legal',d,'VALID_DECLARATIONS_ONLY')
    d=rollup('kernel');d['records'][-1]['metrics']['R']={'status':'NA','reason':'residual attribution unavailable'};check('unknown_residual_stays_incomplete',d,'INCOMPLETE')
    d=rollup();d['records'][-1]['scope']['dimensions']['slice']=99;d['records'][-1]['metrics']['R']={'status':'NA','reason':'count unavailable'};check('NA_cannot_hide_wrong_member_identity',d,'INVALID','ROLLUP_MEMBER_BINDING')
    check('phase_shared_overlapping_clock_ranges_are_legal',phase_rollup(),'VALID_DECLARATIONS_ONLY')
    d=phase_rollup();d['records'].pop();check('phase_missing_required_bucket_record',d,'INVALID','MISSING_COUNTER')
    d=phase_rollup();rel=d['declarations']['relations'][-1];rel['parts'].pop();rel['members'].pop();rel['expected_members'].pop();check('phase_missing_overlap_bucket_declaration',d,'INVALID','PHASE_RESIDUAL_MEMBERS')
    d=phase_rollup();rel=d['declarations']['relations'][-1];rel['parts'][-1]=rel['parts'][-2];check('phase_duplicate_record_reference',d,'INVALID','REPEATED_TERM')
    d=phase_rollup();d['records'][-1]['scope']['dimensions']['phase_bucket']='UNASSIGNED';check('phase_duplicate_actual_bucket_identity',d,'INVALID','ROLLUP_MEMBER_BINDING')
    d=phase_rollup();d['records'][-1]['scope']['dimensions']['slice']=1;check('phase_cross_slice_population',d,'INVALID','ROLLUP_POPULATION')
    d=phase_rollup();d['records'][-1]['scope']['dimensions']['run']='foreign-run';check('phase_cross_run_population',d,'INVALID','ROLLUP_POPULATION')
    d=phase_rollup();del d['declarations']['relations'][-1]['partition_provenance']['source_ref'];check('phase_missing_source_ref',d,'INVALID','PHASE_PARTITION_PROVENANCE')
    d=phase_rollup();d['declarations']['relations'][-1]['partition_provenance']['source_ref']['sha256']='bad';check('phase_bad_source_hash',d,'INVALID','PHASE_PARTITION_PROVENANCE')
    d=phase_rollup();del d['declarations']['relations'][-1]['assignment_partition'];check('phase_missing_assignment_marker',d,'INVALID','PHASE_PARTITION_PROVENANCE')
    d=phase_rollup();d['declarations']['relations'][-1]['partition_provenance']['mutually_exclusive']=False;check('phase_nonexclusive_assignment',d,'INVALID','PHASE_PARTITION_PROVENANCE')
    d=phase_rollup();d['records'][-1]['scope']['partition_id']='foreign-group';check('phase_mixed_assignment_groups',d,'INVALID','PHASE_PARTITION_GROUP')
    d=phase_rollup();d['records'][-1]['scope']['attribution']='EXACT_REQUESTER';check('phase_pseudo_causal_attribution',d,'INVALID','PHASE_CAUSAL_CLAIM')
    d=phase_rollup();d['records'][-1]['scope']['dimensions']['kernel']=100;check('phase_kernel_dimension_forbidden',d,'INVALID','PHASE_CAUSAL_CLAIM')
    d=phase_rollup();d['records'][-1]['scope']['claims_causal_kernel']=True;check('phase_causal_claim_forbidden',d,'INVALID','PHASE_CAUSAL_CLAIM')
    d=phase_rollup();d['records'][-1]['scope']['interval']['start']=50;check('phase_bucket_specific_window_not_whole_snapshot',d,'INVALID','PHASE_INTERVAL')
    d=phase_rollup();d['records'][-5]['scope']['level']='GLOBAL';del d['records'][-5]['scope']['dimensions']['slice'];check('phase_cannot_roll_directly_global',d,'INVALID','PHASE_ROLLUP_LEVEL')
    d=phase_rollup();r=d['records'][-1];r['scope']['coverage_status']='NOT_EMITTED_SOURCE_PROVEN';r['scope']['unavailable_source_ref']=copy.deepcopy(d['declarations']['relations'][-1]['partition_provenance']['source_ref']);r['metrics']['R']={'status':'NA','reason':'source proves this bucket was not emitted, no count inferred'};check('phase_source_proven_missing_is_NA_not_zero',d,'INCOMPLETE')
    d=phase_rollup();r=d['records'][-1];r['scope']['coverage_status']='NOT_EMITTED_SOURCE_PROVEN';r['metrics']['R']={'status':'NA','reason':'not emitted'};check('phase_unemitted_NA_requires_source',d,'INVALID','PHASE_UNAVAILABLE_PROVENANCE')
    d=phase_rollup();r=d['records'][-1];r['scope']['coverage_status']='NOT_EMITTED_SOURCE_PROVEN';r['scope']['unavailable_source_ref']=copy.deepcopy(d['declarations']['relations'][-1]['partition_provenance']['source_ref']);r['metrics']['R']=ok(0);check('phase_source_proven_missing_cannot_fill_zero',d,'INVALID','PHASE_UNAVAILABLE_HAS_COUNT')
    d=phase_rollup();d['records'][-1]['metrics']['R']={'status':'NA','reason':'runtime summary unavailable'};check('phase_unknown_count_prevents_closure',d,'INCOMPLETE')
    d=phase_rollup();d['records'][-1]['scope']['dimensions']['phase_bucket']='foreign';d['records'][-1]['metrics']['R']={'status':'NA','reason':'unknown'};check('phase_NA_cannot_hide_fake_bucket_label',d,'INVALID','ROLLUP_MEMBER_BINDING')
    d=phase_rollup();d['records'] += [{'id':'p1','scope':{'domain':'HEAD','level':'SLICE','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-phase','slice':1}},'overflow':False,'metrics':{'R':ok(4)}},{'id':'phase-global','scope':{'domain':'HEAD','level':'GLOBAL','interval':{'start':0,'end':100},'dimensions':{'run':'synthetic-phase'}},'overflow':False,'metrics':{'R':ok(11)}}];d['declarations']['relations'].append({'id':'phase_then_slice_global','kind':'rollup','axis':'slice','total':ref('phase-global','R'),'parts':[ref('p0','R'),ref('p1','R')],'members':['0','1'],'expected_members':['0','1'],'unattributed_policy':'NOT_APPLICABLE_PARTITION_BY_SLICE'});check('phase_then_slice_rollup_global_legal',d,'VALID_DECLARATIONS_ONLY')
    d=phase_rollup();r=copy.deepcopy(d['records'][-1]);r['id']='hidden-phase';r['scope']['dimensions']['phase_bucket']='HIDDEN';r['metrics']['R']=ok(9);d['records'].append(r);check('phase_hidden_unlisted_bucket_rejected',d,'INVALID','PHASE_GROUP_COVERAGE')
    check('malformed_document_does_not_crash',{'declarations':{'domains':[{}]}},'INVALID','DOMAINS')
    Path(__file__).with_name('example_synthetic_document.json').write_text(json.dumps(base(),indent=2)+'\n')
    Path(__file__).with_name('example_synthetic_phase_document.json').write_text(json.dumps(phase_rollup(),indent=2)+'\n')
    return cases


if __name__=='__main__':
    started=time.monotonic();cases=run();report={'schema':'E2_OFFLINE_COUNTER_VALIDATOR_CONTROLS_V1','result':'PASS','case_count':len(cases),'elapsed_seconds':time.monotonic()-started,'cases':cases,'limitations':['Synthetic declaration checks, not native or simulator correctness tests','No real A2 schema adapter available yet','Cannot prove an emitting simulator observed a counter honestly','Not source/binary/input/resource qualification or application acceptance']};Path(__file__).with_name('VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':'PASS','case_count':len(cases),'elapsed_seconds':report['elapsed_seconds']}))
