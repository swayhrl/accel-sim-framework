"""Derive paper tables only from successful, source-bound native intakes."""
import csv,datetime,hashlib,importlib.util,json,math,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
OLD=P.with_name('FT20261017_LANE6_R17_SAD_INTAKE_r1')
s=importlib.util.spec_from_file_location('frozen_intake_engine',OLD/'intake_engine.py');e=importlib.util.module_from_spec(s);s.loader.exec_module(e);e.R=R
helper=e.module('r18_bridge',P.with_name('FT20261016_LANE6_PAPER_PPA_r4')/'current_pair_intake.py');helper.live_head=e.live_reader();api=helper.vendor_api()
head=helper.live_head(R);e.git('fetch','--no-tags','--no-recurse-submodules','origin',head)
read=lambda name:e.git('show',head+':'+name);raw=read(api.MANIFEST);meta=json.loads(raw);state=api.bind_manifest(raw,{'kind':'FETCHED_GITHUB_BRANCH','publication_commit':head,'manifest_sha256':e.sha(raw),'generation':meta['generation'],'revision':meta['revision']},read);context=helper.bridge(R,state)
order=['sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21']
roots=[OLD,P/'intakes/vectorAdd_4M_attempt1',P/'intakes/cfd_097k_attempt1',P/'intakes/convolutionSeparable_attempt2',P/'intakes/FWT_7_21_attempt2']
def write(name,obj):
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(obj if isinstance(obj,str) else json.dumps(obj,indent=2,sort_keys=True)+'\n')
def csvwrite(name,rows):
 with (P/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
ftfields=['copy_lines','copy_bytes','staging_reads','wb_created','wb_completed','wb_lower_accept','wbuf_full','pool_full','borrow_resident','borrow_bypass','rollback','staging_lifetime']
appfields=['bank_logical_ops','bank_grants','bank_attempts','bank_retry_attempts','bank_true_conflict_ops','bank_true_conflict_events','bank_wait_cycles','c7d_wad_full_events','c7d_wad_hazard_events','c7d_wad_hazard_wait_cycles','c7d_payload_capacity_allocation_denial','c7d_payload_service_port_denial','c7d_missq_full_block','c7d_l2_to_dram_full_block','c7d_dram_scheduler_full_block','c7d_dram_credit_block','c7d_dram_returnq_block','c7d_dram_to_l2_full_block','c7d_dram_issue_eligible','c7d_dram_return_eligible','c7e_dram_issue_attempt','c7e_dram_scheduler_causal_block','c7e_dram_successful_read_bytes','c7e_dram_successful_write_bytes','c7e_dram_successful_read_issues','c7e_dram_successful_write_issues']
arms=[];packets=[];receipts=[];rowchecks=[];channel_evidence={}
for workload,root in zip(order,roots):
 if workload in ['convolutionSeparable','FWT_7_21']:assert json.loads((root/'INTAKE_RECEIPT.json').read_text())['status']=='PASS_COMPLETE_NATIVE_V2_R2_SEMANTIC_INTAKE'
 packet=json.loads((root/'SAD_NATIVE_INTAKE.json').read_text())['packet'];assert len(packet['runs'])==2;packets.append(packet)
 slices=json.loads((root/'SAD_64_SLICE_EVIDENCE.json').read_text());bound=json.loads((root/'SAD_IDENTITY_AND_CLOSURE.json').read_text())
 for run,identity in zip(packet['runs'],bound):
  assert run['workload']==workload;context.check_run(run);rowchecks.append(api.require_current_result(run['identity'],run['raw_log_sha256'],run['summary']['cycles'],run['summary']['instructions'],state))
  assert run['identity']==identity['identity'];assert identity['all64_slice_sets_checked'] is True
  source=slices[run['mode']];assert all(set(source[k])=={str(i) for i in range(64)} for k in ['summary','terminal','invariant','application_cumulative'])
  ft=source['summary'];app=source['application_cumulative'];assert all(x['scope']=='application' and x['interval']=='application_cumulative' for x in app.values())
  totals=lambda rows,k:sum(int(x[k]) for x in rows.values())
  row={'workload':workload,'mode':run['mode'],'run_key':run['run_key'],'cycles':run['summary']['cycles'],'instructions':run['summary']['instructions'],**{k:totals(ft,k) for k in ftfields},**{k:totals(app,k) for k in appfields}}
  for k in ['staged_max']:row[k+'_max_across_slices']=max(int(x[k]) for x in ft.values())
  for k in ['lowerq_max','c7d_dram_scheduler_occ_max']:row[k+'_max_across_slices']=max(int(x[k]) for x in app.values())
  # EPL2DRAMV1 application counters are printed at multiple kernel boundaries.
  # Use only the final cumulative observation per channel, never sum snapshots.
  channels={};snapshots=0
  channel_fields=['dram_cycles','scheduler_full_cycles','returnq_full_cycles','successful_read_issues','successful_write_issues','successful_read_bytes','successful_write_bytes','bandwidth_util_numerator_bytes','bandwidth_util_denominator_bytes']
  raw_path=Path(run['original_result']['allocation']['result_directory'])/'raw.log'
  assert e.sha(raw_path.read_bytes())==run['raw_log_sha256']
  for line in raw_path.open():
   if not line.startswith('EPL2DRAMV1|scope=application|'):continue
   values=dict(x.split('=',1) for x in line.strip().split('|')[1:]);cid=int(values['channel']);snapshots+=1
   if cid in channels:
    assert all(int(values[k])>=int(channels[cid][k]) for k in channel_fields),'Nonmonotonic application DRAM counter'
   channels[cid]=values
  assert set(channels)==set(range(32));channel_evidence[run['run_key']]={'workload':workload,'mode':run['mode'],'cumulative_snapshots_seen':snapshots,'selection':'last monotonic application cumulative observation per channel','channels':channels}
  for k in channel_fields:row['dram_channel_'+k]=totals(channels,k)
  assert row['dram_channel_successful_read_bytes']==row['c7e_dram_successful_read_bytes']
  assert row['dram_channel_successful_write_bytes']==row['c7e_dram_successful_write_bytes']
  assert row['dram_channel_bandwidth_util_numerator_bytes']==row['dram_channel_successful_read_bytes']+row['dram_channel_successful_write_bytes']
  row['dram_model_atom_utilization']=row['dram_channel_bandwidth_util_numerator_bytes']/row['dram_channel_bandwidth_util_denominator_bytes']
  row['dram_scheduler_full_channel_cycle_fraction']=row['dram_channel_scheduler_full_cycles']/row['dram_channel_dram_cycles']
  assert 0<=row['dram_model_atom_utilization']<=1 and 0<=row['dram_scheduler_full_channel_cycle_fraction']<=1
  assert row['wb_created']==row['wb_completed']==row['wb_lower_accept']==run['summary']['wb_completed'];assert row['bank_grants']==sum(totals(app,'c7d_bank'+str(i)+'_grants') for i in range(4))
  assert row['bank_logical_ops']==sum(totals(app,'c7d_bank'+str(i)+'_logical_ops') for i in range(4));assert row['bank_grants']<=4*64*row['cycles']
  arms.append(row)
 receipts.append({'workload':workload,'status':'PASS_CURRENT_FULL_NATIVE_INTAKE','intake_directory':str(root.relative_to(R)),'original_acceptance':json.loads((root/'SAD_NATIVE_INTAKE.json').read_text())['current_authority'],'publication_acceptance':state['binding'],'native_intake_sha256':e.sha((root/'SAD_NATIVE_INTAKE.json').read_bytes()),'identity_closure_sha256':e.sha((root/'SAD_IDENTITY_AND_CLOSURE.json').read_bytes()),'slice_evidence_sha256':e.sha((root/'SAD_64_SLICE_EVIDENCE.json').read_bytes()),'qualified_scope':'FULL_NATIVE_NONATOMIC_ONLY; symbolic32B/request/WB/resource closure; not numeric SASS output'})
 assert arms[-1]['instructions']==arms[-2]['instructions']
combined={**packets[0],'runs':[r for p in packets for r in p['runs']]};_,_,results=helper.legacy_modules(R);summary=results.summarize(combined,context)
assert summary['complete'] and summary['cohort_size']==5
pairs=[]
for i,workload in enumerate(order):
 b,u=arms[2*i:2*i+2];assert (b['mode'],u['mode'])==('B16_BANKED','U_WB16')
 pair={'workload':workload,'cycles_B':b['cycles'],'cycles_U':u['cycles'],'instructions_each':b['instructions'],'ratio_B_over_U':b['cycles']/u['cycles'],'cycle_reduction_percent':100*(b['cycles']-u['cycles'])/b['cycles']}
 for k in ftfields+appfields:pair[k+'_B']=b[k];pair[k+'_U']=u[k]
 for k in [k for k in b if k.startswith('dram_')]:pair[k+'_B']=b[k];pair[k+'_U']=u[k]
 pairs.append(pair)
geomean=math.exp(math.fsum(math.log(r['ratio_B_over_U']) for r in pairs)/5);assert abs(geomean-summary['whole_group_geomean'])<1e-12
context.assert_fresh();csvwrite('ARM_METRICS.csv',arms);csvwrite('PAIRED_RESULTS.csv',pairs)
write('DRAM_CHANNEL_EVIDENCE.json',channel_evidence)
write('PAPER_CURRENT_FIVE_PAIR_INTAKE.json',{'status':'PASS_ALL_FIVE_CURRENT_NATIVE_INTAKES','authority':state['binding'],'current_rows':rowchecks,'intakes':receipts,'independent_geomean_B_over_U':geomean,'legacy_result_intake_geomean':summary['whole_group_geomean'],'geomean_speedup_percent':100*(geomean-1),'workload_count':5,'numeric_SASS_output_verified':False,'simulators_or_new_experiments':0})
write('validation/PUBLICATION_ACCEPTANCE.json',raw.decode());write('validation/COMPLETE_LEGACY_SUMMARY.json',summary)
table='| Workload | B16 cycles | U-WB16 cycles | B/U | Cycle reduction (%) |\n|---|---:|---:|---:|---:|\n'+''.join(f'| {r["workload"]} | {r["cycles_B"]} | {r["cycles_U"]} | {r["ratio_B_over_U"]:.10f} | {r["cycle_reduction_percent"]:+.6f} |\n' for r in pairs)
write('FIVE_PAIR_RESULTS.md',f'# Independent five-pair paper results\n\n{table}\nGeomean B/U = **{geomean:.16f}x**; speed-ratio gain **{100*(geomean-1):.6f}%**. This is a ratio geomean, not a mean of cycle reduction percentages. All five predeclared complete inputs retained, including CFD regression. No repetitions/statistical inference, holdout/general GPU performance or independent capacity-performance claim.\n\nAll rows come from hash-bound native packet and64-slice raw counters, not Lane5 SUMMARY. ARM_METRICS.csv provides actual WB, copy, logical bank operations, successful model bank grants, per-operation waits, WBUF/WAD events, downstream admission events/DRAM bytes and eligible denominators. Counters are application cumulative over64 slices; cycles/instructions are native GPU totals, not slice sums. Maxima are max across slices, never sums of averages.\n\nLogical operations and successful model bank grants happen to match at drained termination for every arm; they remain separate measured fields. Neither count is elapsed GPU time or RTL service/energy. The B16/U difference in logical operations is not universally2×B16 copies because evictions, fills, retries and rollback work can differ. Completed WB and DRAM write bytes also differ; preserve those actual counts.\n\nWBUF-full falls to0 in all U arms; the three pressured B16 workloads vectorAdd/Convolution/FWT show much higher U L2-to-DRAM full-block attempts. This supports a downstream-pressure hypothesis, not proven causal migration or DRAM saturation. Such events count repeated slice/frontend admission denials and can overlap other reasons. Bank-wait totals are completed per-operation conflict waits. Do not add/subtract either from GPU cycles. SAD is a near-tie negative control. CFD loses169 cycles despite fewer copies/bank waits; WAD hazard events rise9841→13400, WB completed31123→31063, and bytes also change. These are competing explanations, not a diagnosis.\n\nThe original SAD pack is unchanged; its two rows were rebound to the live authority alongside the eight newly received rows. Initial prepared legacy adapters failed exact certificate-byte checks; attempt1 failures remain intact. The replacement metadata binds the actual official r2 certificate, full original body hashes and native zero-mask semantic proof without changing the scientific scope, producer, input or runtime config.\n')
write('METRIC_CONTRACT.md','''# Metric/source contract

All source paths below bind Core7b8e6ac70b8fe0f1bd37efca11acb5284938825d.

| Output | Raw source / reduction | Meaning and limit |
|---|---|---|
| cycles/instructions | Frozen Framework9bd17f9d parse_ft_terminal.py native cumulative terminal | End-to-end model cycles/active instructions; never slice-summed |
| copy/WB/WBUF/pool/borrow/rollback | EPL2FTV1 SUMMARY, each64 slices once, sum | Completed transfers/milestones vs repeated refusal events kept distinct |
| bank_logical_ops | EPL2B0V1 application_cumulative, sum64 | Unique modeled operations including work before rollback |
| bank_grants | same; per-bank sum cross-check | Successful modeled bank service, gpu-cache.h:2424/2450; at most1/bank/physical cycle by qualified release; no RTL timing inference |
| bank_wait_cycles | same | Sum of completed-operation conflict waits from first conflict to consumed grant, gpu-cache.h:2427; not GPU elapsed cycles |
| c7d_l2_to_dram_full_block | same | l2cache.cc:1326: exact frontend plan wants lower read while L2→DRAM queue full; repeated/overlapping attempts, not total queue delay or unique transactions |
| c7d_dram_scheduler_full_block | same | Scheduler blocked issue attempts; distinguish causal field c7e_dram_scheduler_causal_block and eligible attempts |
| c7e_dram_successful_*_bytes | same | Successful modeled requests' bytes, preserve actual B/U differences; not power |
| dram_channel_* | EPL2DRAMV1 application; final monotonic cumulative snapshot of each32 channels | Never sum kernel-boundary snapshots; byte totals cross-check64-slice observations |
| dram_model_atom_utilization | Sum issued bytes / sum(atom size × channel DRAM cycles) | Model atom-slot fraction, not measured external bandwidth or universal DRAM saturation |
| WAD hazard/full | same | Same-address/order/entry pressure events, independent of payload slot pressure |
| lowerq_max, scheduler_occ_max | max across64 per-slice maxima | Occupancy bound, not global or averaged utilization |

Missing raw fields raise KeyError; none are filled with0. Legacy C1 resident-headroom is excluded. No peak/reservation counter establishes additional tag-visible capacity or an independent elasticity speedup. Full per-slice observations remain in each native intake.
''')
write('FIGURE_PROVENANCE.json',{'authority':state['binding'],'source_csv':'PAIRED_RESULTS.csv','source_csv_sha256':e.sha((P/'PAIRED_RESULTS.csv').read_bytes()),'arm_csv':'ARM_METRICS.csv','arm_csv_sha256':e.sha((P/'ARM_METRICS.csv').read_bytes()),'Fig2a':{'columns':['cycles_B','cycles_U','cycle_reduction_percent'],'formula':'100*(B-U)/B; zero=B16; expanded axis, CFD retained'},'Fig2b':{'columns':['copy_lines_B','copy_lines_U'],'unit':'thousand completed128B copy transfers, no predicted cycles'},'Fig3a':{'columns':['wbuf_full_B','wbuf_full_U'],'unit':'million cumulative refusal events; small CFD value labeled5 events'},'Fig3b':{'columns':['bank_logical_ops_B','bank_logical_ops_U','bank_grants_B','bank_grants_U','bank_wait_cycles_B','bank_wait_cycles_U'],'formula':'100*(B-U)/B; logical/grant equality checked separately; wait is different denominator'},'Fig3c':{'columns':['c7d_l2_to_dram_full_block_B','c7d_l2_to_dram_full_block_U'],'unit':'million cumulative frontend denial events; not elapsed cycles'},'source_native_receipts':receipts,'no_new_experiments':True})
print(json.dumps({'status':'ALL_FIVE_CURRENT_PASS','geomean':geomean,'rows':len(arms),'authority':head}))
