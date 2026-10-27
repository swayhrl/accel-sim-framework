import json,pathlib
P=pathlib.Path;H=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
c=read(H/'LATEST_CAPTURE.json');run=P(c['run_path']);a=read(run/'ANALYSIS.json');r=read(run/'report.json');new=read(run/'NEW_RAW_REASONS.json')['rows']
pair=[{k:p[k]for k in ['program','profile','P0_cycles','variant_cycles','DH_speedup','counter_changes','raw_positive_reason_changes']}for p in a['new_or_newly_matched_pairs']]
by={(p['input_digest'],p['profile']):p for p in a['all_matched_DH_pairs']}
same=[dict(program=p['program'],input_digest=d,cycles=p['variant_cycles'],same=p['variant_cycles']==by[(d,'E768')]['variant_cycles'])for(d,prof),p in by.items()if prof=='E384'and(d,'E768')in by]
print(json.dumps(dict(new_rows=[dict(program=x['program'],cell=x['cell'],profile=x['profile'],cycles=x['cycles'])for x in new],new_pairs=pair,
 E384_E768=dict(n=len(same),same_cycles=sum(v['same']for v in same),different=[v for v in same if not v['same']]),
 reused=a['previous_identity_validation_reused_count'],newly_identity_checked=a['new_pair_identity_validated_count']),indent=2))
