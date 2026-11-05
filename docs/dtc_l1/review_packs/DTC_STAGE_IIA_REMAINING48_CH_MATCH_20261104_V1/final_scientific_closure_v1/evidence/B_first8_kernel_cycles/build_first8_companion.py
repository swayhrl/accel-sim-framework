import csv,datetime,gzip,hashlib,json
from pathlib import Path

A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
F=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1')
O=A/'agents/B_first8_sixcell_kernel_cycles_companion_20261105_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
checks=[]
def ck(n,v,detail=None):
 checks.append({'check':n,'pass':bool(v),'detail':detail})
 if not v:raise AssertionError((n,detail))

O.mkdir(exist_ok=True)  # Own unfrozen build directory only; no original artifact writes.
assert not (O/'MANIFEST.json').exists(), 'Refuse to overwrite frozen companion'
provider_path=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json'
provider=json.loads(provider_path.read_bytes())
ck('qualified_final32',provider['source_qualified'] and provider['summary']['full_CORE32_complete_sixcell_accepted'])
cp=next(x for x in provider['files']if x['name']=='STAGEIIA_REMAINING48_CORE32_RESULTS.json.gz')
ck('provider_core_member_sha',sha(cp['path'])==cp['sha256'])
with gzip.open(cp['path'],'rt')as f:core=json.load(f)
B=next((A/'agents/B_final24_consumption_preparation_v1/updates').iterdir())
idx=json.loads((B/'public/CORE32_MECHANISM_EVIDENCE_INDEX.json').read_bytes())
first8=idx['first8_reviewed_evidence']['first8'];selected={x['program']:x for x in first8}
conv=F/'agents/A_convseparable_three_profiles_v1/MANIFEST.json'
authority={'original_first8_index':{'path':str(B/'public/CORE32_MECHANISM_EVIDENCE_INDEX.json'),'sha256':sha(B/'public/CORE32_MECHANISM_EVIDENCE_INDEX.json')},'first8_reused_scoped_packages':first8,'convolutionSeparable_six_source_forward_reference':{'path':str(conv),'sha256':sha(conv),'report':str(conv.parent/'REPORT.md'),'report_sha256':sha(conv.parent/'REPORT.md')},'GEMM_2DCONV_F256_counter_mechanism':'UNCONFIRMED_NOT_COVERED_BY_REUSED_F128_ONLY_PACKET; accepted cycle/trace geometry coverage is complete, no counter/causal promotion.'}
sources=[];records=[];comparisons={}
for p in core['all_programs']:
 if p['program']not in selected:continue
 matched={};signatures={}
 for cell,s in p['six_source_cells'].items():
  ck('accepted_source',s['accepted']is True,(p['program'],cell))
  q=Path(s['source_RESULT_path']);ck('RESULT_SHA',sha(q)==s['source_RESULT_sha256'],str(q));d=json.loads(q.read_bytes());proof=d['proof'];ks=proof['kernels']
  ck('cycles_identity',d['cycles']==proof['cycles']==s['cycles'],(p['program'],cell))
  ck('input_digest_identity',proof['input_digest']==s['input_digest']==p['input_digest'],(p['program'],cell))
  ck('actual_cell_identity',proof['cell']==s['source_cell']==cell.split('_')[0],(p['program'],cell))
  if 'input_digest'in d:ck('top_input_digest_if_present',d['input_digest']==proof['input_digest'],(p['program'],cell))
  if 'cell'in d:ck('top_cell_if_present',d['cell']==proof['cell'],(p['program'],cell))
  ck('source_uuid_identity',d['uuid']==s['source_uuid'],(p['program'],cell))
  ck('kernel_ordinals',[k['ordinal']for k in ks]==list(range(1,len(ks)+1)),(p['program'],cell))
  cumulative=0;prevcta=0
  source={'program':p['program'],'suite':p['suite'],'input_digest':p['input_digest'],'comparison_cell':cell,'source_identity':s,'RESULT_actual_cohort':d['cohort'],'RESULT_actual_profile':d.get('profile'),'proof_actual_profile':proof.get('downstream_profile'),'proof_status':proof.get('status'),'proof_core_commit':proof.get('core_commit'),'proof_framework_commit':proof.get('framework_commit'),'proof_binary_sha256':proof.get('binary_sha256'),'accepted_cycles':s['cycles'],'kernel_count':len(ks),'kernels':ks,'counter_mechanism_scope':'UNCONFIRMED_F256_COUNTERS'if p['program']in['GEMM','2DCONV']and cell.endswith('F256')else'REUSE_ONLY_ORIGINAL_SCOPED_COUNTER_AUTHORITY'}
  sources.append(source)
  for k in ks:
   cumulative+=k['cycles'];ck('kernel_cumulative_cycles',cumulative==k['total_cycles'],(p['program'],cell,k['ordinal']))
   ck('CTA_monotonic',k['cumulative_CTA']>=prevcta,(p['program'],cell,k['ordinal']))
   row={'program':p['program'],'suite':p['suite'],'input_digest':p['input_digest'],'comparison_cell':cell,'ordinal':k['ordinal'],'kernel':k['kernel'],'cycles':k['cycles'],'cumulative_cycles':k['total_cycles'],'active_instructions':k['active_instructions'],'cumulative_CTA':k['cumulative_CTA'],'interval_CTA':k['cumulative_CTA']-prevcta,'source_RESULT_path':str(q),'source_RESULT_sha256':s['source_RESULT_sha256'],'source_uuid':s['source_uuid'],'actual_source_profile':s['source_profile'],'actual_registered_slot_cohort':s['source_registered_slot_cohort'],'RESULT_actual_cohort':d['cohort'],'source_role':s['source_role'],'counter_mechanism_scope':source['counter_mechanism_scope']};records.append(row);prevcta=k['cumulative_CTA']
   key=(p['input_digest'],k['ordinal']);r=comparisons.setdefault(key,{'program':p['program'],'input_digest':p['input_digest'],'ordinal':k['ordinal'],'kernel':k['kernel'],'active_instructions':k['active_instructions'],'cumulative_CTA':k['cumulative_CTA'],'cycles':{}});r['cycles'][cell]=k['cycles']
  ck('kernel_sum_whole',cumulative==s['cycles'],(p['program'],cell))
  signatures[cell]=[(k['ordinal'],k['kernel'],k['active_instructions'],k['cumulative_CTA'])for k in ks]
  matched[cell]=s['cycles']
 ck('identical_sixcell_kernel_sequence',all(v==next(iter(signatures.values()))for v in signatures.values()),p['program'])
ck('sources48',len(sources)==48);ck('records264',len(records)==264);ck('positions44',len(comparisons)==44)
for k,r in comparisons.items():ck('position_all6',len(r['cycles'])==6,k)
put('FIRST8_SIX_CELL_KERNEL_CYCLES.json',{'schema':'DTC_CORE32_FIRST8_SIXCELL_KERNEL_CYCLE_COMPANION_V1','purpose':'Close kernel-cycle coverage only; no new raw scan or causal/counter qualification','provider':{'path':str(provider_path),'sha256':sha(provider_path),'manifest':provider['manifest']},'source_n':48,'first8_program_n':8,'per_source_kernel_records':264,'matched_kernel_positions':44,'sources':sources,'matched_kernel_cycles':list(comparisons.values()),'limits':{'input_scope':'Exact accepted registered trace/replay only; not native full-app/numerical proof','cycle_scope':'proof.kernels.cycles per actual kernel; total_cycles cumulative same replay','CTA_scope':'cumulative_CTA difference, explicit ordinal first baseline0; not SM residency or grid shape','source_identity':'comparison_cell never replaces actual source cohort/profile/legal P0 alias provenance','source_or_memory_hypotheses':'Existing fixed candidate source mechanism remains separately scoped; this companion makes no memory-access/counter cause inference','GEMM_2DCONV_F256':'Dynamic cycles qualified; detailed counter mechanism UNCONFIRMED/NOT_COVERED','runtime_actions':0}})
with(O/'FIRST8_SIX_CELL_KERNEL_CYCLES.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
put('REUSED_AUTHORITY_AND_SCOPE.json',authority)
put('CPU_VALIDATION.json',{'checks_passed':len(checks),'checks':checks,'raw_read':False,'models_started':0,'frozen_packages_changed':0})
names=[]
for name in selected:
 group=[s for s in sources if s['program']==name];names.append('|'+name+'|'+str(group[0]['kernel_count'])+'|'+str(sum(s['kernel_count']for s in group))+'|')
(O/'README.md').write_text('# First8 six-cell kernel-cycle companion\n\nThis forward packet complements the final24 report without changing either original package. It reads only48 SHA-verified accepted RESULT JSON proofs from the final fixed CORE32 provider; no raw log, simulation, service or original final consumer is invoked.\n\nEight programs cover44 actual kernel positions and264 source-kernel records. Every source has ordinal1..N, exact cumulative-cycle checkpoints and a kernel cycle sum equal to its accepted total. Six-cell kernel name/instruction/cumulative-CTA sequences match. These44 positions plus the final24 7,254 positions give7,298 fixed CORE32 kernel positions and43,788 source-kernel cycle rows across192 sources.\n\n|Program|Kernel instances per cell|Six-cell rows|\n|---|---:|---:|\n'+'\n'.join(names)+'\n\nFIRST8_SIX_CELL_KERNEL_CYCLES.json retains each actual RESULT source identity, including inherited P0 aliases, original proof kernels and compact six-cell comparisons. The CSV is the same264 actual cycle rows. Interval CTA is a difference of explicit cumulative counts, not inferred grid shape, active-SM placement or occupancy.\n\nREUSED_AUTHORITY_AND_SCOPE adds the existing convolutionSeparable six-source Rows/Columns report and manifest. It preserves the original first8 index unchanged. GEMM/2DCONV F256 detailed counter mechanism remains UNCONFIRMED/NOT_COVERED by the reused F128 control packet. Their accepted per-kernel cycles are available here; that does not establish a six-profile causal explanation or fill any missing counter.\n\nCandidate source/trace/ELF binding, numerical/full-application limits, mixed counter windows, missing-not-zero, initial prefill/coherence conditions and unequal CH/DH structures remain governed by the original scoped evidence and the forward completion audit. This packet computes no new cache-hit, merge, DRAM-latency or critical-path claim. Root alone publishes and decides final Goal closure.\n')
print(json.dumps({'output':str(O),'checks':len(checks),'sources':len(sources),'records':len(records)}))
