"""Closed-evidence resource trajectories, no model/native/archive actions."""
from pathlib import Path
import json,gzip,hashlib,datetime,collections
P=Path;R=P('/root/data/dtc_stage_iia_first16_20261104_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');HERE=A/'root_resource_trajectory_v1';G=1024**3;M=1024**2
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def summarize():
 rows=[];timeline=[]
 for point in rd(R/'control/MATRIX.json')['points']:
  c=point['cohort'];dp=R/'control/qualification_ledger'/(c+'.DONE.json');rp=R/'analysis'/(c+'.RESULT.json');sp=R/'control/specs'/(c+'.json');spec=rd(sp);row=dict(cohort=c,program=point['program'],profile=point['profile'],input_digest=point['input_digest'],state=rd(rp)['state']if rp.exists()else'AWAIT_CLOSED_RESULT',performance_cycles=None,science_role='STAGEII_AUTHORIZED_CH')
  if not dp.exists():rows.append(row);continue
  done=rd(dp);out=P(done['output']);assert rd(out/'NATIVE_EXIT.json')==done;f=out/'RESOURCE_SAMPLES.jsonl.gz';samples=[];decisions=collections.Counter()
  with gzip.open(f,'rt')as h:
   for line in h:
    v=json.loads(line)
    if 'DTC_exact_original_policy'in v:decisions[v['DTC_exact_original_policy']['decision']['decision']]+=1
    if 'process_tree_observed_rss_bytes'in v:
     t={k:v.get(k)for k in ['utc','elapsed_seconds','host_MemAvailable_bytes','cgroup_effective_headroom_bytes','native_free_bytes','process_tree_observed_rss_bytes','required_free_bytes','physical_RAM_pass','physical_disk_pass','pressure_pause_new','admission_disk_pass']};t.update(cohort=c,program=point['program'],profile=point['profile']);samples.append(t);timeline.append(t)
  def vals(k):return [x[k]for x in samples if type(x.get(k))in[int,float]]
  def low(k):a=vals(k);return min(a)if a else None
  def high(k):a=vals(k);return max(a)if a else None
  if rp.exists()and row['state']=='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE':row['performance_cycles']=rd(rp)['cycles']
  row.update(uuid=done['uuid'],natural_done=done['stop_reason']is None and done['launcher_wait_returncode']==0,raw_returncode=done['launcher_wait_returncode'],stop_reason=done['stop_reason'],elapsed_seconds=done['elapsed_seconds'],observed_peak_RSS_bytes=done['peak_observed_rss_bytes'],resource_samples_peak_RSS_bytes=high('process_tree_observed_rss_bytes'),RSS_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],AS_cap_bytes=spec['limits']['max_process_tree_vms_bytes'],observed_peak_inflight_result_bytes=done['peak_result_logical_bytes'],output_cap_bytes=spec['limits']['max_result_directory_bytes'],host_min_MemAvailable_bytes=low('host_MemAvailable_bytes'),cgroup_min_headroom_bytes=low('cgroup_effective_headroom_bytes'),native_min_free_bytes=low('native_free_bytes'),physical_samples=len(samples),runtime_guard_decisions=dict(decisions),admission_only_disk_budget_not_met_samples=sum(x.get('admission_disk_pass')is False for x in samples),runtime_RAM_fail_samples=sum(x.get('physical_RAM_pass')is False for x in samples),runtime_actual_disk_fail_samples=sum(x.get('physical_disk_pass')is False for x in samples),sources={n:dict(path=str(p),sha256=sha(p))for n,p in [('DONE',dp),('RESOURCE_SAMPLES',f),('SPEC',sp)]},peak_is_periodic_observation_not_exact_continuous_HWM=True)
  row['observed_RSS_cap_exceeded']=row['observed_peak_RSS_bytes']>row['RSS_cap_bytes']
  row['observed_inflight_output_cap_exceeded']=row['observed_peak_inflight_result_bytes']>row['output_cap_bytes']
  assert row['observed_peak_RSS_bytes']>=row['resource_samples_peak_RSS_bytes']
  if row['state']=='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE':assert not row['observed_RSS_cap_exceeded']and not row['observed_inflight_output_cap_exceeded']
  # A genuine RSS/output-limit negative is retained with its observed excess,
  # not rejected by the report generator or changed into a passing result.
  rows.append(row)
 tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=HERE/'snapshots'/tag;out.mkdir(parents=True,exist_ok=False)
 report=dict(schema='DTC_STAGEII_FIRST16_CLOSED_RESOURCE_TRAJECTORY_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(__file__),population=16,closed_samples=sum('uuid'in x for x in rows),accepted=sum(x['performance_cycles']is not None for x in rows),rows=rows,missing_fields_are_null=True,scientific_promotion_by_resource_consumer=False,new_model_starts=0,notes=['Only DONE-closed resource streams are read; running files are never treated as complete.','Observed peaks depend on sampling cadence and are not exact continuously observed hardware high-water marks.','admission_disk_pass=false pauses future admission and differs from unsafe actual-runtime disk failure.','Raw closed results without strict/archive acceptance remain unaccepted with performance_cycles=null.'])
 (out/'RESOURCE_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'RESOURCE_TIMELINES.json.gz').write_bytes(gzip.compress((json.dumps(timeline,separators=(',',':'))+'\n').encode(),mtime=0))
 text=['# First16 closed-result resource observations','', 'Only naturally or explicitly negatively closed UUIDs are consumed. Peak RSS is a periodic observation. Missing values remain missing; this table does not grant performance acceptance.','', '| Program | F | Scientific state | Elapsed h | Observed RSS GiB | RSS cap GiB | Min native free GiB | Samples |','|---|---|---|---:|---:|---:|---:|---:|']
 for row in rows:
  if 'uuid'not in row:text.append('| '+row['program']+' | '+row['profile']+' | '+row['state']+' | MISSING | MISSING | MISSING | MISSING | 0 |');continue
  text.append(f"| {row['program']} | {row['profile']} | {row['state']} | {row['elapsed_seconds']/3600:.4f} | {row['observed_peak_RSS_bytes']/G:.4f} | {row['RSS_cap_bytes']/G:.2f} | {row['native_min_free_bytes']/G:.3f} | {row['physical_samples']} |")
 (out/'RESOURCE_SUMMARY.md').write_text('\n'.join(text)+'\n')
 manifest=dict(source_sha256=sha(__file__),files=[dict(path=str(p.relative_to(out)),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(out.iterdir())]);(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');(HERE/'LATEST.json').write_text(json.dumps(dict(snapshot=str(out),manifest_sha256=sha(out/'MANIFEST.json'),closed=report['closed_samples'],accepted=report['accepted']),indent=2)+'\n');print(json.dumps(dict(snapshot=str(out),manifest_sha256=sha(out/'MANIFEST.json'),closed=report['closed_samples'],accepted=report['accepted'],new_models_started=0)))
if __name__=='__main__':summarize()
