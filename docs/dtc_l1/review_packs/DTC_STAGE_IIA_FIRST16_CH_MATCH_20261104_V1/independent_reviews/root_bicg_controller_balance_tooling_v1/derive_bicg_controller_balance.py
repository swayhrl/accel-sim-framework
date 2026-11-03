from pathlib import Path
import json,hashlib,math,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');B=A/'agents/B_bicg_f128_matched_v1';O=A/'root_bicg_controller_balance_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B/'MANIFEST.json')=='f2b1dfc69e860b56e96ec70f50490458d843a8808f5f7d598852571790401cba'
manifest=json.loads((B/'MANIFEST.json').read_bytes())
for r in manifest['files']:assert sha(B/r['path'])==r['sha256']
data=json.loads((B/'MATCHED_FOUR_SOURCE_DATA.json').read_bytes());rows=[]
for r in data['four_closed_sources']:
 prev={};previous_total=0
 for k in r['kernels']:
  now={str(i):v['n_rd']+v['n_rd_L2_A'] for i,v in k['DRAM_controllers_cumulative'].items()};assert len(now)==20
  if prev:assert set(now)==set(prev)
  delta={i:now[i]-prev.get(i,0)for i in now};assert all(v>=0 for v in delta.values())
  for scope,vals,total in [('K'+str(k['ordinal'])+'_PRINT_INTERVAL',delta,k['print_boundary_interval_additive']['DRAM_issued_read_atoms32B']),('CUMULATIVE_THROUGH_K'+str(k['ordinal']),now,k['cumulative_additive']['DRAM_issued_read_atoms32B'])]:
   assert sum(vals.values())==total
   n=len(vals);mean=total/n;cv=math.sqrt(sum((x-mean)**2 for x in vals.values())/n)/mean if mean else None
   rows.append(dict(design=r['cell'],profile=r['profile'],scope=scope,total_read_atoms32B=total,controllers=vals,minimum=min(vals.values()),maximum=max(vals.values()),mean=mean,population_CV=cv,maximum_share=max(vals.values())/total if total else None,maximum_over_mean=max(vals.values())/mean if mean else None,source_RESULT_sha256=r['RESULT_sha256'],source_raw_uncompressed_sha256=r['raw_uncompressed_sha256']))
  prev=now
report=dict(schema='DTC_STAGEIIA_BICG_CONTROLLER_READ_DISTRIBUTION_READONLY_V1',created_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_input_digest=data['full_input_digest'],source_package_manifest_sha256=sha(B/'MANIFEST.json'),source_data_sha256=sha(B/'MATCHED_FOUR_SOURCE_DATA.json'),rows=rows,limitations=['Counters measure issued read work over a print interval, not occupancy, waiting time or simultaneous load.','20-controller aggregation hides subpartition, DRAM-bank and temporal imbalance.','Interval arithmetic does not establish originating-kernel ownership of outstanding tails.','CH and DH upstream streams differ; this is not a same-request balance experiment.','Uniform totals would not rule out short-lived or bank-level bottlenecks.'],models_started=0)
O.mkdir(exist_ok=True)
assert not (O/'MANIFEST.json').exists(),'FROZEN_REPORT_ALREADY_EXISTS'
(O/'READ_DISTRIBUTION.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['# BICG closed-source DRAM controller read-work distribution','','This read-only projection consumes the frozen four-source BICG packet. Counts are32B issued-read atoms, not latency or occupancy. CV uses the20 controller totals. No missing controller is imputed and every interval sum is checked against the source total.','','| Design | F | Scope | Total reads | Min/controller | Max/controller | CV | Hottest share |','|---|---|---|---:|---:|---:|---:|---:|']
for r in rows:
 if r['scope'] in ['K2_PRINT_INTERVAL','CUMULATIVE_THROUGH_K2']:
  lines.append('| '+r['design']+' | '+r['profile']+' | '+r['scope']+' | '+str(r['total_read_atoms32B'])+' | '+str(r['minimum'])+' | '+str(r['maximum'])+' | '+format(r['population_CV'],'.6f')+' | '+format(r['maximum_share']*100,'.3f')+'% |')
lines+=['','The equal-share reference is5% per controller. These cumulative and print-boundary distributions alone do not establish a critical-path cause, actual queue contention, per-bank balance or scheduling fairness. Their limitations are listed in READ_DISTRIBUTION.json. Consume the original BICG packet together with its forward typed-field/active-path clarification. No experiment, input, owner, budget, historical file or manuscript is changed.','']
(O/'README.md').write_text('\n'.join(lines))
(O/'CPU_CHECKS.json').write_text(json.dumps(dict(status='PASS',all_source_manifest_members_SHA_verified=True,all_four_closed_sources=True,all_twenty_controller_IDs_each_boundary=True,nonnegative_deltas=True,all_sixteen_total_projections_exact=True,no_simulation_or_runtime_calls=True),indent=2)+'\n')
source=Path(__file__) if '__file__' in globals() else None
# The driver arrives through stdin; archive the exact Windows driver bytes separately before publication.
out=dict(schema='DTC_STAGEIIA_READ_DISTRIBUTION_MANIFEST_V1',files=[dict(path=str(p.relative_to(O)),sha256=sha(p),bytes=p.stat().st_size)for p in sorted(O.iterdir())if p.is_file()])
(O/'MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
print((O/'README.md').read_text());print(json.dumps(dict(path=str(O),manifest_sha256=sha(O/'MANIFEST.json'))))
