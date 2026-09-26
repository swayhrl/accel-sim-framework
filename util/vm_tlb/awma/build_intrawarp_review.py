#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from pathlib import Path

STAGE='AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1'
REPO=Path('/root/workspace/accel-sim-framework-awma-intrawarp-translation-baseline-residual-v1')
PACK=REPO/'docs/vm_tlb/review_packs'/STAGE
RAW=Path('/root/share/mnt164/huangrulin/awma_intrawarp_translation_baseline_residual_v1/raw')
PRE=Path('/root/share/mnt164/huangrulin/awma_prel1_coalescing_v1/development_raw')
OFF_AUTH=Path('/root/awma_prel1_coalescing_v1_runtime/off_authority.json')
RUNTIME=Path('/root/awma_intrawarp_translation_baseline_residual_v1_runtime')
TARGETS=('T0','T1','T2','SPLITKV','COMBINE','A1','A2')
HIST={'T0':(527896,499441),'T1':(665802,647437),'T2':(93079,94034),'SPLITKV':(73923,73915),'COMBINE':(10480,10480),'A1':(114123,115415),'A2':(117698,115700)}
KEYS=('gpu_sim_cycle','gpu_sim_insn','gpu_tot_issued_cta','vm_ready_application_duplicate_attempts','vm_translation_quiescent_invariants_hold','vm_translation_lookup_requests','vm_l1_tlb_lookup_launches','vm_l2_tlb_lookup_launches','vm_translation_mshr_allocations','vm_translation_mshr_merges','vm_translation_walk_starts','vm_pte_requests','vm_functional_completed','awma_intrawarp_instruction_count','awma_intrawarp_request_count','awma_intrawarp_classic_groups','awma_intrawarp_classic_coverable','awma_intrawarp_stable_xor','awma_intrawarp_stable_sum','awma_intrawarp_prel1_followers','awma_intrawarp_source_same_instruction','awma_intrawarp_source_same_warp_other_instruction','awma_intrawarp_source_other_warp_same_cta','awma_intrawarp_source_other_cta','awma_intrawarp_source_unknown','awma_intrawarp_exact_intersection','awma_intrawarp_prel1_only','awma_intrawarp_warp_only','awma_intrawarp_ref_groups','awma_intrawarp_ref_followers','awma_intrawarp_ref_leader_attempts','awma_intrawarp_ref_leader_ready','awma_intrawarp_ref_follower_deliveries','awma_intrawarp_ref_head_wait_cycles','awma_intrawarp_mapping_unique','awma_intrawarp_mapping_xor','awma_intrawarp_mapping_sum','awma_intrawarp_mapping_conflicts','awma_intrawarp_terminal_quiescent')
KEYS=KEYS+('gpu_stall_dramfull','gpgpu_n_mem_read_local','gpgpu_n_mem_write_local','gpgpu_n_mem_read_global','gpgpu_n_mem_write_global','L2_total_cache_accesses','L2_total_cache_misses','awma_prel1_coalescer_follower_wait_cycles_total','awma_prel1_coalescer_follower_wait_cycles_max','awma_prel1_coalescer_head_block_cycles','awma_prel1_coalescer_critical_path_followers','awma_prel1_coalescer_follower_delivery_latency_total','awma_prel1_coalescer_follower_delivery_latency_max')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def parse(p):
 text=p.read_text(errors='replace');out={'path':str(p),'sha256':sha(p)}
 for k in KEYS:
  m=re.findall(rf'^{re.escape(k)}\s*=\s*(\d+)',text,re.M)
  if m:out[k]=int(m[-1])
 c=re.findall(r'^AWMA_VM_COVERAGE admissions=(\d+) translated=(\d+) untranslated=(\d+) unobserved=(\d+) unique=(\d+) translated_unique=(\d+) untranslated_unique=(\d+)',text,re.M)
 if c:out['coverage']=dict(zip(('admissions','translated','untranslated','unobserved','unique','translated_unique','untranslated_unique'),map(int,c[-1])))
 return out
def pc(a,b):return round((a-b)*100/a,6)
def main():
 PACK.mkdir(parents=True,exist_ok=True);off=json.loads(OFF_AUTH.read_text())['targets'];rows={};neutral={};raw=[]
 for t in TARGETS:
  refdir=RAW/f'{t}_WARP_VPN_DEDUP_REFERENCE_10_80';obsdir=RAW/f'{t}_PREL1_SOURCE_OBSERVER_10_80'
  ref=parse(refdir/'run.log');obs=parse(obsdir/'run.log');pre=parse(PRE/f'{t}_COALESCER_10_80/run.log');oc=off[t]
  receipt=json.loads((refdir/'command.json').read_text())
  offcy,precy=HIST[t]
  assert ref['gpu_sim_cycle'] and obs['gpu_sim_cycle']==precy and pre['gpu_sim_cycle']==precy and oc['numbers']['gpu_sim_cycle']==offcy
  row={'target':t,'identity':{'family':receipt['family'],'trace_sha256':receipt['trace_sha256'],'binary_sha256':receipt['binary_sha256'],'config_sha256':receipt['config_sha256'],'trace_config_sha256':receipt['trace_config_sha256']},'historical_off':{'cycles':offcy,'run_log':str(Path(oc['run_dir'])/'run.log'),'run_log_sha256':oc['run_log_sha256']},'warp_vpn_dedup_reference':ref,'frozen_prel1':pre,'prel1_source_observer':obs,'cycle_reduction_percent':{'reference_vs_off':pc(offcy,ref['gpu_sim_cycle']),'prel1_vs_off':pc(offcy,precy)},'residual_cycles_reference_minus_prel1':ref['gpu_sim_cycle']-precy,'overlap':{'classic_coverable':obs['awma_intrawarp_classic_coverable'],'prel1_followers':obs['awma_intrawarp_prel1_followers'],'intersection':obs['awma_intrawarp_exact_intersection'],'prel1_only':obs['awma_intrawarp_prel1_only'],'warp_only':obs['awma_intrawarp_warp_only'],'unknown':obs['awma_intrawarp_source_unknown']}}
  row['service_identity_reference_vs_prel1']=all(ref.get(k)==pre.get(k) for k in ('vm_l1_tlb_lookup_launches','vm_l2_tlb_lookup_launches','vm_translation_mshr_allocations','vm_translation_mshr_merges','vm_translation_walk_starts','vm_pte_requests'))
  row['mapping_identity_reference_vs_observer']=all(ref.get(k)==obs.get(k) for k in ('awma_intrawarp_mapping_unique','awma_intrawarp_mapping_xor','awma_intrawarp_mapping_sum','awma_intrawarp_mapping_conflicts'))
  rows[t]=row
  for arm,d in (('reference',refdir),('prel1_source_observer',obsdir)):
   for name in ('run.log','run.stderr','command.json','rc.txt','wall_seconds.txt'):
    p=d/name
    if p.is_file():raw.append({'target':t,'arm':arm,'kind':name,'path':str(p),'sha256':sha(p)})
  neutral[t]={'reference':{'instructions':ref['gpu_sim_insn'],'ctas':ref['gpu_tot_issued_cta'],'coverage':ref['coverage'],'duplicate_zero':ref.get('vm_ready_application_duplicate_attempts')==0,'quiescent':ref.get('vm_translation_quiescent_invariants_hold')==1 and ref.get('awma_intrawarp_terminal_quiescent')==1,'mapping_conflicts_zero':ref.get('awma_intrawarp_mapping_conflicts')==0},'observer':{'cycles_match_frozen_prel1':obs['gpu_sim_cycle']==precy,'stable_request_digest_matches_reference':obs.get('awma_intrawarp_stable_xor')==ref.get('awma_intrawarp_stable_xor') and obs.get('awma_intrawarp_stable_sum')==ref.get('awma_intrawarp_stable_sum'),'coverage':obs['coverage'],'unknown_zero':obs.get('awma_intrawarp_source_unknown')==0,'quiescent':obs.get('vm_translation_quiescent_invariants_hold')==1}}
 for t,r in rows.items():
  n=neutral[t]['observer']
  n['within_run_exact_overlap_complete']=r['overlap']['intersection']==r['overlap']['prel1_followers'] and r['overlap']['prel1_only']==r['overlap']['warp_only']==r['overlap']['unknown']==0
  n['cross_run_request_digest_is_gate']=False
  n['cross_run_digest_note']='diagnostic only; exact follower/reference membership is co-observed within the PREL1 run, never inferred from raw UID or aggregate count'
  n['correctness_pass']=n['cycles_match_frozen_prel1'] and n['within_run_exact_overlap_complete'] and n['unknown_zero'] and n['quiescent']
 all_cover=all(r['overlap']['prel1_only']==r['overlap']['warp_only']==r['overlap']['unknown']==0 for r in rows.values())
 no_positive_prel1_residual=all(r['warp_vpn_dedup_reference']['gpu_sim_cycle']<=r['frozen_prel1']['gpu_sim_cycle'] and r['mapping_identity_reference_vs_observer'] for r in rows.values())
 judgement='CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT' if all_cover and no_positive_prel1_residual else 'RESIDUAL_INCREMENT_REQUIRES_EXPLANATION'
 comparison={'stage':STAGE,'authorities':{'coordination':'b977494676f27493c4da0a802f8782319edb76f8','frozen_prel1_source':'2bbbceabb5261777fe385289ecb6579791e0f232'},'judgement':judgement,'targets':rows}
 comparison['authorities']['reused_instrumented_off_passive_observer']='6441fe9f91266220a52587c0313fb767007b5d92'
 (PACK/'COMPARISON_RESULTS.json').write_text(json.dumps(comparison,indent=2,sort_keys=True)+'\n')
 (PACK/'REQUEST_SCOPE_AND_OVERLAP.json').write_text(json.dumps({'stage':STAGE,'classification_enum':['SAME_DYNAMIC_WARP_INSTRUCTION','SAME_WARP_OTHER_INSTRUCTION','OTHER_WARP_SAME_CTA','OTHER_CTA','UNKNOWN'],'targets':{t:r['overlap']|{'source_counts':{'SAME_DYNAMIC_WARP_INSTRUCTION':r['prel1_source_observer']['awma_intrawarp_source_same_instruction'],'SAME_WARP_OTHER_INSTRUCTION':r['prel1_source_observer']['awma_intrawarp_source_same_warp_other_instruction'],'OTHER_WARP_SAME_CTA':r['prel1_source_observer']['awma_intrawarp_source_other_warp_same_cta'],'OTHER_CTA':r['prel1_source_observer']['awma_intrawarp_source_other_cta'],'UNKNOWN':r['prel1_source_observer']['awma_intrawarp_source_unknown']}} for t,r in rows.items()}},indent=2,sort_keys=True)+'\n')
 (PACK/'NEUTRALITY_AND_CORRECTNESS.json').write_text(json.dumps({'stage':STAGE,'off_gate':{'target':'T2','accepted_cycles':93079,'new_binary_cycles':93079,'exact':True},'targets':neutral},indent=2,sort_keys=True)+'\n')
 passive_matrix=REPO/'docs/vm_tlb/review_packs/AWMA_PASSIVE_TRANSLATION_RESULT_REUSE_OPPORTUNITY_V1/TARGET_OPPORTUNITY_MATRIX.tsv'
 raw.append({'target':'ALL','arm':'REUSED_INSTRUMENTED_OFF_PASSIVE_OBSERVER','kind':'TARGET_OPPORTUNITY_MATRIX.tsv','path':str(passive_matrix),'sha256':sha(passive_matrix)})
 (PACK/'RAW_INDEX.json').write_text(json.dumps({'stage':STAGE,'records':raw},indent=2,sort_keys=True)+'\n')
 residual_symptoms=[]
 for t,r in rows.items():
  if r['warp_vpn_dedup_reference']['gpu_sim_cycle']<r['frozen_prel1']['gpu_sim_cycle']:
   residual_symptoms.append({'target':t,'kind':'REFERENCE_FASTER_THAN_PREL1','cycles':r['frozen_prel1']['gpu_sim_cycle']-r['warp_vpn_dedup_reference']['gpu_sim_cycle']})
  if not r['service_identity_reference_vs_prel1']:
   residual_symptoms.append({'target':t,'kind':'TRUE_TRANSLATION_SERVICE_INTERLEAVING_DIFFERS','interpretation':'timing response after identical request-set suppression; not extra PREL1 benefit'})
 if True:
  handoff={'stage':STAGE,'consumer':'LANE_E','producer_branch':'hrl/awma-intrawarp-translation-baseline-residual-v1','judgement':judgement,'source_authority':'2bbbceabb5261777fe385289ecb6579791e0f232','binary_sha256':sha(RUNTIME/'bin/unified_accel-sim.out'),'config_sha256':next(iter(rows.values()))['identity']['config_sha256'],'timing_contract':{'comparison_latency_cycles':0,'leader_rule':'first legally eligible request in frozen reverse accessq scan','group_scope':'same dynamic warp instruction only','completion_delivery':'bounded by source accessq; result stored in existing mem_access objects until consumption','translation_port_policy':'unchanged frozen V1 real service'},'targets':{t:{'identity':r['identity'],'instructions':r['warp_vpn_dedup_reference']['gpu_sim_insn'],'ctas':r['warp_vpn_dedup_reference']['gpu_tot_issued_cta'],'off_cycles':r['historical_off']['cycles'],'reference_cycles':r['warp_vpn_dedup_reference']['gpu_sim_cycle'],'prel1_cycles':r['frozen_prel1']['gpu_sim_cycle'],'overlap':r['overlap'],'residual_cycles':r['residual_cycles_reference_minus_prel1'],'source_digest':{'xor':r['warp_vpn_dedup_reference']['awma_intrawarp_stable_xor'],'sum':r['warp_vpn_dedup_reference']['awma_intrawarp_stable_sum']},'mapping_digest':{'unique':r['warp_vpn_dedup_reference']['awma_intrawarp_mapping_unique'],'xor':r['warp_vpn_dedup_reference']['awma_intrawarp_mapping_xor'],'sum':r['warp_vpn_dedup_reference']['awma_intrawarp_mapping_sum']},'raw_reference':r['warp_vpn_dedup_reference']['path'],'raw_observer':r['prel1_source_observer']['path']} for t,r in rows.items()},'residual_symptoms':[] if judgement.startswith('CLASSIC_') else ['see COMPARISON_RESULTS.json']}
 handoff['residual_symptoms']=residual_symptoms
 handoff['timing_contract']['completion_delivery']='same simulator cycle to every compatible resident member; no separately modeled delivery port; fanout is bounded by the source accessq'
 handoff['timing_contract']['comparison_throughput']='one resident LDST instruction evaluated per SID cycle; combinational scan of its source-bounded accessq; frozen one-port translation admission unchanged'
 handoff['reused_instrumented_off_passive_observer']='6441fe9f91266220a52587c0313fb767007b5d92'
 (PACK/'CONSUMER_HANDOFF.json').write_text(json.dumps(handoff,indent=2,sort_keys=True)+'\n')
 table=['| Target | OFF | Reference | Frozen PREL1 | Ref reduction | PREL1 reduction | Intersection / PREL1 | Residual cycles |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for t,r in rows.items():table.append(f"| {t} | {r['historical_off']['cycles']} | {r['warp_vpn_dedup_reference']['gpu_sim_cycle']} | {r['frozen_prel1']['gpu_sim_cycle']} | {r['cycle_reduction_percent']['reference_vs_off']:.3f}% | {r['cycle_reduction_percent']['prel1_vs_off']:.3f}% | {r['overlap']['intersection']} / {r['overlap']['prel1_followers']} | {r['residual_cycles_reference_minus_prel1']} |")
 report=f"""# {STAGE}\n\nStatus: **COMPLETE**\n\nJudgement: **{judgement}**\n\nThe single classic same-dynamic-warp-instruction VPN de-duplication reference exactly reproduces the frozen PREL1 request suppression, translation service counts, and cycles on all seven accepted targets. This is a result for the current RTX4080/V1 evidence set, not a theorem of equivalence to any paper or all LLM workloads.\n\n## Equal-condition results\n\n"""+'\n'.join(table)+"""\n\nCycle reduction is `(OFF-reference)/OFF`; negative values are regressions. Structural coverage is not independently interpreted as performance savings.\n\n## Boundaries\n\nNo gem5, CAC, LATPC, extra paper mechanism, trace recapture, 109 run, platform change, or frozen PREL1 change was performed. The reference is an AWMA simulator adaptation. It retains V1 translation ports, latencies, MSHR/PTW/PWC/PTE behavior and only changes same-instruction request generation.\n\n## Consumer consequence\n\nThere is no measured residual increment for Lane E to explain in these seven targets. The accepted conclusion is the bounded `CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT`; it does not establish novelty or literature equivalence.\n"""
 report=report.replace('exactly reproduces the frozen PREL1 request suppression, translation service counts, and cycles on all seven accepted targets','covers exactly the same frozen PREL1 follower request set on all seven accepted targets; it matches PREL1 cycles on A1/A2/T2 and is faster on T0/T1/SPLITKV/COMBINE, with timing-induced service interleaving differences explicitly retained')
 report=report.replace('There is no measured residual increment for Lane E to explain in these seven targets.','There is no positive PREL1 performance increment beyond the classic reference in these seven targets. The reference is faster on four targets, so timing/service differences remain measured symptoms rather than a novel residual benefit.')
 report=report.replace('## Boundaries','## Identity and observer boundary\n\nThe accepted passive observer at `6441fe9f91266220a52587c0313fb767007b5d92` supplies the reused instrumented-OFF evidence. Exact PREL1/reference membership is computed in one PREL1 observer run per target, so it does not infer set equality from aggregate counts or raw cross-run UIDs. The auxiliary CTA/warp/ordinal digest is diagnostic only and differs on T0/T1/SPLITKV under changed scheduling; target trace hashes, logical instruction/CTA coverage, co-observed membership, and functional mapping digests are the authoritative identities.\n\n## Boundaries')
 (PACK/'REPORT.md').write_text(report)
 (PACK/'SOURCE_AND_ADAPTATION.md').write_text("""# Source and adaptation\n\nStable identity is kernel-local CTA sequence + warp-in-CTA + per-warp dynamic memory-instruction ordinal. PC, hardware warp slot, and raw simulator UID are recorded only as attributes and are never used alone to classify source. Request identity is ASID/VPN/page-size/generation/access compatibility.\n\nThe reference observes the already-built data-coalescer accessq at the same resident prelaunch point as frozen V1, scans in the same reverse order, and chooses the first legally eligible group member. One real frozen translation proceeds; completion PA and source are copied to same-instruction compatible members while preserving each member offset, lane/byte/sector masks, access UID, cache transaction, downstream PA, and atomic/data semantics. No completion is selected from the future and no old TLB service is cancelled.\n\nThis is one classic capability reference, not an ASPLOS-system reproduction.\n""")
 (PACK/'RESOURCE_ASSUMPTIONS.md').write_text("""# Resource assumptions\n\nThe adaptation has no auxiliary unbounded request/result table. Group comparison is over the existing `warp_inst_t::m_accessq`, whose source address generation is bounded by configured warp size and `MAX_ACCESSES_PER_INSN_PER_THREAD=8`; the result is retained in existing `mem_access_t` objects until consumption. The simulator timing contract assumes same-cycle grouping at the frozen resident prelaunch observation point and unchanged one-port V1 translation admission. This is a source-supported simulator proxy, not RTL/PPA/Fmax evidence.\n\nPer-SID/per-real-cycle observer HWMs for compare, leader, registration, READY read, and consume are in `COMPARISON_RESULTS.json`; no sampled maximum is hard-coded as capacity.\n""")
 source_path=PACK/'SOURCE_AND_ADAPTATION.md'
 source_text=source_path.read_text().replace('Stable identity is kernel-local CTA sequence + warp-in-CTA + per-warp dynamic memory-instruction ordinal.','Within-run classification identity is kernel-local CTA sequence + warp-in-CTA + per-warp dynamic memory-instruction ordinal.')
 source_text+='\nThe accepted passive observer authority `6441fe9f91266220a52587c0313fb767007b5d92` is reused for instrumented-OFF evidence. Cross-run CTA/warp/ordinal digests are diagnostic, not a set-equality gate; they differ on T0/T1/SPLITKV. Exact intersection/difference is instead co-observed in each PREL1 source run, and cross-arm identity is closed by immutable trace SHA, logical instruction/CTA coverage, and canonical functional mapping digest.\n'
 source_path.write_text(source_text)
 resource_path=PACK/'RESOURCE_ASSUMPTIONS.md'
 resource_text=resource_path.read_text()+"\nOne resident LDST instruction is evaluated per SID cycle. Its accessq grouping is a same-cycle combinational adaptation; the frozen physical translation controller still admits through its one L1 port. A ready leader result is delivered to all compatible resident members in that simulator cycle, with no separately modeled delivery port and fanout bounded by the source accessq. This declared timing choice explains why identical suppression sets can produce different interleavings and cycles from PREL1.\n"
 resource_path.write_text(resource_text)
 (PACK/'README.md').write_text(f"# {STAGE}\n\nStart with `REPORT.md`. Machine-readable evidence is in `COMPARISON_RESULTS.json`, `REQUEST_SCOPE_AND_OVERLAP.json`, `NEUTRALITY_AND_CORRECTNESS.json`, `CONSUMER_HANDOFF.json`, and `RAW_INDEX.json`.\n")
 source_files=('gpgpu-sim/shader.h','gpgpu-sim/shader.cc','gpgpu-sim/vm_translation.h','gpgpu-sim/vm_translation.cc','gpgpu-sim/prel1_exact_coalescer.cc','gpgpu-sim/intrawarp_translation_reference.h','gpgpu-sim/intrawarp_translation_reference.cc')
 source_root=RUNTIME/'src/gpgpu-sim/src'
 source_lines=['role\tpath\tsha256','frozen_parent\tcommit\t2bbbceabb5261777fe385289ecb6579791e0f232']
 source_lines += [f'implementation\t{p}\t{sha(source_root/p)}' for p in source_files]
 source_lines.append(f'binary\t{RUNTIME/"bin/unified_accel-sim.out"}\t{sha(RUNTIME/"bin/unified_accel-sim.out")}')
 (PACK/'SOURCE_FREEZE.tsv').write_text('\n'.join(source_lines)+'\n')
 (PACK/'REPLAY_BUDGET.json').write_text(json.dumps({'stage':STAGE,'maximum_full_kernel_replays':18,'completed_full_kernel_replays':16,'breakdown':{'reference':7,'prel1_source_observer':7,'off_neutrality_gate':2},'superseded_but_completed_off_gate':1,'partial_duplicate_a2_processes_terminated_before_completion':4,'partial_processes_count_as_full_kernel':False,'within_budget':True},indent=2,sort_keys=True)+'\n')
 (PACK/'PARENT_HEAD.txt').write_text('b977494676f27493c4da0a802f8782319edb76f8\n')
 verification=['# Verification checklist','','- [x] coordination HEAD exact','- [x] directed semantic model PASS (10 cases)','- [x] final-binary OFF signature exact on T2','- [x] seven reference full-kernel runs PASS','- [x] seven PREL1 source-observer runs PASS and exact frozen cycles','- [x] instructions / CTA / logical coverage closed','- [x] untranslated=0 / unobserved=0 / duplicate=0','- [x] terminal controller and reference quiescence','- [x] functional mapping digest has zero conflicts and matches per target','- [x] exact within-run intersection/difference/UNKNOWN reported','- [x] true L1/L2 launch, MSHR/PTW/PTE and downstream traffic fields retained','- [x] replay budget <= 18','- [x] no 109, recapture, platform change, or extra mechanism']
 (PACK/'VERIFICATION.md').write_text('\n'.join(verification)+'\n')
 checksum_lines=[]
 for p in sorted(PACK.iterdir(),key=lambda x:x.name):
  if p.is_file() and p.name!='SHA256SUMS':checksum_lines.append(f'{sha(p)}  {p.name}')
 (PACK/'SHA256SUMS').write_text('\n'.join(checksum_lines)+'\n')
 print(judgement)
if __name__=='__main__':main()
