import pathlib,gzip,json,collections,datetime
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');p=A/'coordinator/large_job_aging_v1/decisions.jsonl.gz';last=None
try:
 with gzip.open(p,'rt')as h:
  for line in h:
   try:last=json.loads(line)
   except json.JSONDecodeError:break
except(EOFError,OSError):pass
assert last is not None;G=1024**3;print(json.dumps(dict(CST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),journal_mtime=p.stat().st_mtime,phase=last['phase'],target=last['target'],protected_GiB=last['protected_bytes']/G,safe_slack_GiB=last['current_slack_bytes']/G,backfill_cohort_count=len(last['backfill_cohorts']),feasibility=last['feasibility'],last_credit_events=last['new_credit_events']),indent=2))
