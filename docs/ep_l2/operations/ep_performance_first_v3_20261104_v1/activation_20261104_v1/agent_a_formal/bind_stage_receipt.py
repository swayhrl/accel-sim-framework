from pathlib import Path as P
import json,hashlib
V=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1');F=V/'agent_a_formal';R=V/'runtimes/midtag'
p=R/'ep_perf_native_wv_modes_draft.py';t=p.read_text();needle="        need(len(prerequisite)==4,'exact four FWT predecessor cells')\n"
assert needle in t
t=t.replace(needle,needle+"""        stage=read(ROOT/'control/FWT4_ACCEPTED_STAGE_REVIEW.json')
        need(stage.get('schema')=='EP_MAIN_PFV3_MIDTAG_FWT4_ACCEPTED_STAGE_REVIEW_V1' and stage.get('status')=='MAIN_REVIEWED_FWT4_CLOSED_ACCEPTED_ARCHIVED_TWO_RESTORES' and stage.get('approved_by')=='EP-MAIN' and stage.get('request_id')==GOAL,'Main FWT4 stage receipt missing/mismatched')
        need(set(stage.get('accepted_point_refs',{}))==set(prerequisite) and set(stage.get('archive_receipt_refs',{}))==set(prerequisite),'Main FWT4 stage population')
        exact(stage['controller_manifest_ref'])
""")
needle="            row=q['consumed'].get(fwt,{})\n";t=t.replace(needle,needle+"""            need(stage['accepted_point_refs'][fwt]==row.get('accepted_point_ref') and stage['archive_receipt_refs'][fwt]==row.get('archive_receipt_ref'),'Main stage/current accepted identities differ')
""")
p.write_text(t)
def ref(p):return dict(path=str(p),sha256=hashlib.sha256(P(p).read_bytes()).hexdigest())
for p in (F/'spec_candidates').glob('*.json'):
 d=json.loads(p.read_text());d['host_engine_ref']=ref(R/'ep_perf_native_wv_modes_draft.py');d['pinned_files'][str(R/'ep_perf_native_wv_modes_draft.py')]=d['host_engine_ref']['sha256'];p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
p=F/'review_drafts/MAIN_HOST_QUALIFICATION_DRAFT.json';d=json.loads(p.read_text());d['modules']=[ref(x['path'])for x in d['modules']];p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
print('Main FWT4 controller stage receipt additionallybound')

