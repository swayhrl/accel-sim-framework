"""Same-arm accepted OFF/ON artifact comparison only. No model or registry writes."""
import copy,json,sys
from ep_perf_common_v2 import *
from ep_perf_native_wv_modes_draft import EXACT_COHORTS, spec_for

def projection(bundle):
    model=copy.deepcopy(bundle['model'])
    need('raw_log_sha256' in model,'raw logical identity field absent')
    model.pop('raw_log_sha256')
    application=bundle['application']
    return dict(**{k:bundle[k]for k in ['cycles','instructions','CTA','kernel_count','hardware_drained']},
        model=model,application={k:application[k]for k in ['actual_options','ordered_kernel_catalog','application_scopes']})

def compare(off,on):
    need(off in EXACT_COHORTS and '_OFF_'in off and on==off.replace('_OFF_','_ON_'), 'same exact arm pair only')
    a,b=spec_for(off),spec_for(on)
    for key in ['source_identity','input_identity_sha256','geometry','expected_effective_options','mode','T','M','ordinary_ro_tag_relief','input_binding_ref','ro_qualification_ref','binary_path','static_library_path']:
        need(a[key]==b[key],'NI different '+key)
    need(a['observer_profile']=='T3_PRIMARY_OFF'and b['observer_profile']=='T3_DIAG_ON','NI profile identity')
    delta={k:(a['observer_env'].get(k),b['observer_env'].get(k))for k in set(a['observer_env'])|set(b['observer_env'])if a['observer_env'].get(k)!=b['observer_env'].get(k)}
    need(delta=={'EPL2_DETACH_DIAG':('0','1'),'EPL2_TAGPRESSURE_DIAG':('0','1')},'NI only two declared observer changes')
    registry,_=authority();q=registry['registered_future_requests'][GOAL]
    bundles=[];rows=[];proofs=[]
    for c in [off,on]:
        row=q['consumed'][c]
        need(row['state']=='CLOSED_ACCEPTED','NI both accepted and archived required')
        point=exact(row['accepted_point_ref']);archive=exact(row['archive_receipt_ref'])
        need(archive['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'and len(archive['native_restores'])==2,'NI archive/restore closure')
        need(point['source_identity']==a['source_identity'],'NI accepted Source drift')
        bundles.append(exact(point['validation_ref']));rows.append(row)
        proofs.append(dict(cohort=c,accepted_point_ref=row['accepted_point_ref'],archive_receipt_ref=row['archive_receipt_ref']))
    aa,bb=map(projection,bundles)
    keys=sorted(set(aa)|set(bb));same={k:aa.get(k)==bb.get(k)for k in keys}
    done0,done1=(exact(r['done_ref'])for r in rows)
    wall0,wall1=done0['elapsed_seconds'],done1['elapsed_seconds']
    return dict(schema='EP_T3_SAME_ARM_APPLICATION_NI_RESULT_V1',status='PASS_ACCEPTED_SAME_ARM_COMPACT_SEMANTICS'if all(same.values())else'FAIL_SEMANTIC_DIFFERENCE_NO_RETRY',
       off=off,on=on,source_identity=a['source_identity'],input_identity_sha256=a['input_identity_sha256'],equal=same,proofs=proofs,
       observer_delta=delta,OFF_host_elapsed_seconds=wall0,ON_host_elapsed_seconds=wall1,host_elapsed_ratio=wall1/wall0 if wall0 else None,
       host_overhead_interpretation='descriptive single-pair host wall; external load may differ; not GPU speedup',
       ordered_request_trace_NI='NOT_INSTRUMENTED',strict_demand_NEW='NOT_INSTRUMENTED',later_UID_completion_chain='NOT_MEASURED',
       scientific_starts=0,registry_writes=0,automatic_retry=False)

if __name__=='__main__':
    need(len(sys.argv)==3,'exact OFF ON cohort arguments')
    print(json.dumps(compare(*sys.argv[1:]),sort_keys=True))
