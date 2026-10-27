"""Coverage dependencies and existing accepted wall times; no raw rescan."""
import hashlib,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def read(p):return json.loads(P(p).read_bytes())
capture=read(HERE/'LATEST_CAPTURE.json');run=P(capture['run_path']);r=read(run/'report.json')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');rows=[];unpaired=0
for digest,program in sorted(r['programs'].items(),key=lambda x:(x[1]['suite'],x[1]['program'])):
 cells=r['table'][digest];missing=[]
 for design in ('CH','DH'):
  value=cells['P0'][design]
  if not value['accepted']:missing.append(dict(design=design,cohort=value['cohort'],state=value['state'],
   execution_class='RUNNING_CONFIRMED'if value['state']=='RUNNING_CONFIRMED'else'UNSTARTED_AT_SNAPSHOT'if value['state']=='PENDING'else'OTHER_UNACCEPTED'))
 if not missing:continue
 accepted=[]
 for profile,designs in cells.items():
  if profile=='P0':continue
  value=designs.get('DH',{})
  if not value.get('accepted'):continue
  c=value['cohort'];rp=P(value['result_path']);raw=rp.read_bytes();assert hashlib.sha256(raw).hexdigest()==value['result_sha256']
  result=json.loads(raw);dp=R/'control/qualification_ledger'/(c+'.DONE.json');done=read(dp)
  assert done['uuid']==result['uuid']and done['stop_reason']is None and done['launcher_wait_returncode']==0
  accepted.append(dict(profile=profile,cohort=c,uuid=result['uuid'],cycles=result['cycles'],same_design_natural_elapsed_seconds=done['elapsed_seconds'],
   peak_RSS_bytes=done['peak_observed_rss_bytes'],DONE_path=str(dp),DONE_sha256=hashlib.sha256(dp.read_bytes()).hexdigest(),RESULT_path=str(rp),RESULT_sha256=value['result_sha256']))
 blocked=len(accepted)if not cells['P0']['DH']['accepted']else 0
 unpaired+=blocked;rows.append(dict(**program,missing_P0=missing,accepted_nonP0_DH_count=len(accepted),
  blocked_DH_self_pairs_due_missing_DH_P0=blocked,existing_same_design_natural_completions=accepted))
out=dict(schema='DTC_L2_MLP_BASELINE_COVERAGE_DEPENDENCIES_V1',utc=r['utc'],rows=rows,
 total_blocked_DH_pairs_due_missing_DH_P0=unpaired,selection_rule='P0 scheduling priority only by coverage dependency and existing cost; never speedup-selected workload',
 no_new_models=True,no_raw_logs_opened=True)
(run/'BASELINE_DEPENDENCIES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(total_blocked=unpaired,rows=[dict(program=x['program'],missing=x['missing_P0'],accepted_nonP0=x['accepted_nonP0_DH_count'],blocked=x['blocked_DH_self_pairs_due_missing_DH_P0'],
 walls=[dict(profile=t['profile'],seconds=t['same_design_natural_elapsed_seconds'])for t in x['existing_same_design_natural_completions']])for x in rows]),indent=2))
