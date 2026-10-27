import json,pathlib
P=pathlib.Path;H=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
c=read(H/'LATEST_CAPTURE.json');run=P(c['run_path']);a=read(run/'ANALYSIS.json');s=read(run/'SUPPLEMENT.json')
wants={('ATAX','Q128'),('ATAX','M16'),('BICG','Q64'),('BICG','M16'),('MVT','Q128'),('MVT','F128'),('MVT','M8'),('histo','F256'),('convolutionSeparable','Q128'),('mri-q','Q128')}
out=[]
for p in a['all_matched_DH_pairs']:
 if (p['program'],p['profile'])not in wants:continue
 out.append(dict(program=p['program'],profile=p['profile'],P0_cycles=p['P0_cycles'],variant_cycles=p['variant_cycles'],speedup=p['DH_speedup'],
  counters=p['counter_changes'],reasons={k:v for k,v in p['raw_positive_reason_changes'].items()if k in ['GLOBAL_ACC_R:MISS_QUEUE_FULL','GLOBAL_ACC_R:MSHR_ENRTY_FAIL','GLOBAL_ACC_R:MSHR_MERGE_ENRTY_FAIL']},
  variant_cohort=p['variant_cohort'],variant_result_sha=p['variant_result_sha256']))
print(json.dumps(dict(cases=out,suite_expected=s['suite_expected'],suites={p:{suite:dict(n=v['available']['n'],GM=v['available']['GM'],pos=v['available']['positive'],neg=v['available']['negative'],neutral=v['available']['neutral'],common_n=v['common_all8']['n'],common_GM=v['common_all8']['GM'])for suite,v in data['suites'].items()}for p,data in s['profile_statistics'].items()}),indent=2))
