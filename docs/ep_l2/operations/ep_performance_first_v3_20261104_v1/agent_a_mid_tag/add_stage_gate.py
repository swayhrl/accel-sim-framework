from pathlib import Path as P
import json,hashlib
A=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/agent_a_mid_tag');R=A/'runtime_candidate'
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text();needle="    family_row=scope.family_row(s)\n";assert needle in t
add="""    family_row=scope.family_row(s)
    # Preparation can overlap; consumption of any GEMM waits for all four FWT closures.
    if require_release and '_GEMM_' in case:
        prerequisite=[x for x in ALLOWED_COHORTS if '_FWT_' in x]
        need(len(prerequisite)==4,'exact four FWT predecessor cells')
        for fwt in prerequisite:
            row=q['consumed'].get(fwt,{})
            need(row.get('state')=='CLOSED_ACCEPTED','FWT four accepted/archive gate before GEMM')
            pt=exact(row['accepted_point_ref']);ar=exact(row['archive_receipt_ref'])
            need(pt.get('cohort')==fwt and pt.get('status')=='EP_FULL_PERF_APPLICATION_ACCEPTED' and pt.get('hardware_drained')is True,'FWT accepted input/drain')
            need(pt.get('spec_ref')==ref(spec_path(fwt)) and pt.get('source_identity')==s['source_identity'],'FWT exact Source/spec')
            need(ar.get('cohort')==fwt and ar.get('uuid')==row.get('uuid')==pt.get('uuid') and ar.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and ar.get('source_keep')is True,'FWT archive closure')
            rs=ar.get('native_restores',[])
            need(len(rs)==2 and len({r['target']for r in rs})==2 and all(r.get('status')=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' and r.get('archive_sha256')==ar['archive_ref']['sha256']for r in rs),'FWT two independent restores')
"""
t=t.replace(needle,add);p.write_text(t)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
qpath=A/'evidence/HOST_CANDIDATE_QUALIFICATION.json';q=json.loads(qpath.read_text())
for r in q['modules']:
 if r['path']==str(p):r['sha256']=sha(p)
put(qpath,q)
for p in (A/'spec_candidates').glob('*.json'):
 d=json.loads(p.read_text());d['host_engine_ref']['sha256']=sha(R/'ep_perf_native_wv_modes_draft.py');d['host_qualification_ref']['sha256']=sha(qpath);d['pinned_files'][str(R/'ep_perf_native_wv_modes_draft.py')]=d['host_engine_ref']['sha256'];put(p,d)
p=A/'test_runtime_candidate.py';t=p.read_text().replace("e.spec_for(case)['cohort']","e.spec_for(case,require_release=False)['cohort']")
needle="check('PARSER_FROZEN_NUMERIC_MATH',lambda:parser.numeric_math()[1])"
t=t.replace(needle,"for case in cases:\n if '_GEMM_' in case:check('GEMM_BEFORE_FOUR_FWT_DENIED_'+case,lambda case=case:e.spec_for(case),False)\n"+needle);p.write_text(t)
idxpath=A/'MID_TAG_FAMILY_SCOPE.json';idx=json.loads(idxpath.read_text())
for row in idx['points']:row['spec_ref']['sha256']=sha(row['spec_ref']['path']);row['spec_ref']['bytes']=P(row['spec_ref']['path']).stat().st_size
put(idxpath,idx)
print('FWT four closure prerequisite now enforced in engine before consumption')

