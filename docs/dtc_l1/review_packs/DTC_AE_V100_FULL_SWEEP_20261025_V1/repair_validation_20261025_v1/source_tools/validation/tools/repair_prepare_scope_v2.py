import pathlib,json,hashlib,datetime
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
first=R/'control/REPAIR_SCOPE_CANDIDATE_V1.json';sent=R/'control/SENTINEL_CASES_CANDIDATE_V1.json';base=read(first);candidates=read(sent);cases=candidates['cases'];assert len(base['points'])==13 and len(cases)==10;points=[]
for point in base['points']:points.append(dict(point,validation_kind='REPAIR_FAILED_OR_ENGINEERING_POINT',source_kind='ORIGINAL_CAPTURED_FULL_INPUT_REPAIR',operational_result_cap_bytes=256*1024**2))
for case in cases:
 assert case['cohort'].startswith('E2-AEREPAIR-SENT-') and case['validation_kind']=='COMPONENT_SENTINEL_NOT_FORMAL';assert sha(case['spec_template_path'])==case['spec_template_sha256'] and sha(case['input_binding_path'])==case['input_binding_sha256'];points.append(case)
assert len({p['cohort'] for p in points})==23
out=dict(base,schema='DTC_REPAIR_AND_NONFORMAL_SENTINEL_EXACT_SCOPE_V2',finite_budget=23,repair_points=13,nonformal_component_sentinels=10,maximum_repair_concurrency=13,maximum_sentinel_concurrency=10,counts_toward_original_40_limit=False,scope13_source_path=str(first),scope13_source_sha256=sha(first),sentinel_candidates_path=str(sent),sentinel_candidates_sha256=sha(sent),points=points,models_started=0,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());path=R/'control/REPAIR_SCOPE_CANDIDATE_V2.json';assert not path.exists();path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'scope_path':str(path),'scope_sha256':sha(path),'budget':23,'repair13':13,'sentinel10_nonformal':10,'models_started':0}))
