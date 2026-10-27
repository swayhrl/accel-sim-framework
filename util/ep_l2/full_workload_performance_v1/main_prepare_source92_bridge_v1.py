"""Main engineering preparation: immutable new Source92 adapter and qualification.

No registry write, application permission, or simulator invocation.
"""
import copy, difflib, json, shutil, sys
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0,str(J/'tools'))
from ep_perf_common import *

DELTA_FUNCTION='''
def qualify_new_source(s, source):
    """Strict CPU SourceQ and independently scoped application NI gate."""
    adapter = module(s['validation_module_ref'], 'new_source92_native_qualification')
    need(adapter.SID == s['source_identity'], 'exact new Source92 required')
    adapter.qualify_history_spec(s)
    adapter.qualify_sourceq(s, s['source_qualification_ref']['path'], s['source_qualification_ref']['sha256'])
    need(source['source_identity'] == s['source_identity'], 'new SourceQ identity mismatch')
    if s['profile'] == 'SOURCE92_P1_APPLICATION_NI':
        need(s['cohort'] == 'EP_PERF_VECTOR4M_'+s['mode']+'_SOURCE92_P1_NI_V1', 'finite initial NI population')
        baseline_ref=s['scientific_option_contract']['old_source_engineering_NI_reference_spec_ref']
        baseline=exact(baseline_ref)
        need(baseline_ref['path'] == str(ROOT/'cases'/('EP_PERF_VECTOR4M_'+s['mode']+'_REF_V1')/'control/FROZEN_SPEC.json'), 'exact Source78 default NI reference')
        reg, unused=authority(); old=reg['registered_future_requests'][GOAL]['consumed'][baseline['cohort']]
        need(old['state']=='CLOSED_ACCEPTED', 'old default engineering reference not closed')
        need(s['mode'] in ['S','F'] and s['expected_effective_options']==baseline['expected_effective_options'], 'initial default P1 NI option match')
        need(s['input_identity_sha256']==baseline['input_identity_sha256'] and s['observer_env']==baseline['observer_env'] and s['geometry']==baseline['geometry'], 'initial default P1 NI population mismatch')
        need(s.get('source92_P1_application_NI_ref') is None, 'initial NI cannot claim inherited new application evidence')
    else:
        ni=exact(s['source92_P1_application_NI_ref'])
        need(ni['status']=='MAIN_SOURCE92_P1_VECTOR4M_S_F_APPLICATION_NI_PASS' and ni['source_identity']==s['source_identity'], 'new Source P1 applications must close before performance expansion')
        need(ni['qualified_by']=='EP-MAIN' and ni['all_endpoint_metrics_and_protocol_projections_equal'] is True, 'actual Main application NI missing')
        reg,unused=authority(); consumed=reg['registered_future_requests'][GOAL]['consumed']
        need(set(ni['new_source_cases'])=={'S','F'}, 'both new Source modes NI required')
        for mode,case in ni['new_source_cases'].items():
            need(case=='EP_PERF_VECTOR4M_'+mode+'_SOURCE92_P1_NI_V1' and consumed[case]['state']=='CLOSED_ACCEPTED', 'new Source NI not archived and accepted')
            point=exact(consumed[case]['accepted_point_ref'])
            need(point['source_identity']==s['source_identity'] and point['mode']==mode and point['hardware_drained'], 'actual new Source NI terminal identity')
    return True

'''

def main():
    delivery=exact(ref(J/'agent_b/source92_p1p2_math_v1/DELIVERY_MANIFEST.json'))
    src=Path(delivery['package_manifest_ref']['path']).parent
    dst=J/'tools/qualified_source92_p1p2_v1'
    need(not dst.exists(),'new exact adapter directory required')
    shutil.copytree(src,dst,ignore=shutil.ignore_patterns('__pycache__'))
    for p in src.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:need(sha(p)==sha(dst/p.relative_to(src)),'exact new math copy')
    adapter_ref=ref(dst/'source92_p1p2_terminal.py'); adapter=module(adapter_ref,'main_source92_exact_adapter')
    adapter.verify_pins(); adapter.verify_math_manifest(ref(dst/'PACKAGE_MANIFEST.json'))
    review=exact(ref(J/'control/MAIN_SOURCE92_PATCH_REVIEW.json'))
    review.update(schema='EP_FULL_PERF_P2_MAIN_SOURCE_REVIEW_V1',status='MAIN_SOURCE92_P1P2_MINIMAL_DIFF_REVIEW_PASS',qualified_by='EP-MAIN',
                  original_full_patch_review_ref=ref(J/'control/MAIN_SOURCE92_PATCH_REVIEW.json'),
                  new_math_review='Read full strict282 whitelist, whole64-owner snapshot occurrence policy, one inverse-checked P1 eligibility premise, original STRUCT ownership/drain equations and actual91 CPU controls; old78 raw rejected; P2 is distinct-slot safety-coupled policy, no application inheritance',
                  source_quali_release=False,utc=now())
    rr=put(J/'control/MAIN_SOURCE92_SOURCE_AND_MATH_REVIEW_V1.json',review,True)
    sq=exact(delivery['SourceQ_private_candidate_ref'])
    sq.update(status='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED',qualified_by='EP-MAIN',utc=now(),pending_Main_evidence=[],Main_source_and_math_review_ref=rr)
    sq['evidence_refs']['main_source_review']=rr
    sq['evidence_refs']['source_release']=ref(J/'agent_b/source92_release_v1/runs/a126627c-f6fd-4926-9330-83432937393c/SOURCE_RELEASE_BINDING.json')
    sq['evidence_refs']['host_math_package_manifest']=ref(dst/'PACKAGE_MANIFEST.json')
    sqr=put(J/'control/SOURCE_QUALIFICATION_SOURCE92_P1P2_V1.json',sq,True)
    old=J/'tools/ep_perf_native.py'; text=old.read_text()
    start=text.index("    need(source['status'] == 'EXACT_ACCEPTED_SOURCE_CPU_EVIDENCE_REUSED_NOT_NEW_APP_ACCEPTED'")
    end=text.index('    for path, digest in s[\'pinned_files\'].items():',start)
    text=text[:start]+"    qualify_new_source(s, source)\n    need(s['mode'] in ['S', 'F'], 'new Source92 qualified S/F only')\n"+text[end:]
    insertion=text.index('\ndef spec_for(case):')
    text=text[:insertion]+'\n'+DELTA_FUNCTION+text[insertion:]
    text=text.replace('New EP-only native entry. No import-time actors; all starts consume first.','Independent Source92 native engine. Frozen legacy engine preserved; all starts consume first.')
    new=J/'tools/ep_perf_native_source92_v1.py'
    with new.open('x') as f:f.write(text)
    compile(text,str(new),'exec')
    dr=put(J/'control/SOURCE92_NATIVE_ENGINE_VERSION_DELTA_V1.json',dict(status='NEW_IMMUTABLE_ENGINE_VERSION_ENGINEERING_ONLY_NO_START',utc=now(),legacy_engine_ref=ref(old),new_engine_ref=ref(new),
        original_engine_unchanged=True,unchanged_functions=['prepare','fresh_input','resource_gate','verify_actual','run_native','main'],
        only_changes='New Source92 strict adapter/SourceQ and real P1 app NI gate replace old78 reused-source block; finite initial P1 Vector S/F only; new engine retains every original consume/admission/resource/PID/maps/terminal check.',
        unified_diff=''.join(difflib.unified_diff(old.read_text().splitlines(True),text.splitlines(True),fromfile='frozen_native_v1',tofile='native_source92_v1'))),True)
    print(json.dumps(dict(SourceQ_ref=sqr,adapter_ref=adapter_ref,new_engine_ref=ref(new),review_ref=rr,delta_ref=dr)))

if __name__=='__main__':main()
