from pathlib import Path
import json,hashlib
P=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents');B=P/'B';C=P/'C';sha=lambda b:hashlib.sha256(b).hexdigest();m=json.loads((B/'MANIFEST.json').read_text());checks=[]
def ck(n,b,d=None):checks.append({'check':n,'PASS':bool(b),'detail':d})
ck('B frozen manifest hash',sha((B/'MANIFEST.json').read_bytes())=='3da95b8e185ae51a48fa9dc9f41e8eb015d13fde9f14956db36facc2c5fc986e')
ck('B all members hash',all(sha((B/x['path']).read_bytes())==x['sha256'] for x in m['files']),{'members':len(m['files'])})
d=json.loads((B/'PROGRAM_EVIDENCE.json').read_text());kernel=json.loads((B/'KERNEL_HYPOTHESIS_MATRIX.json').read_text());audit=json.loads((C/'INDEPENDENT_SET_AUDIT.json').read_text());by={(x['program'],x['profile']):x for x in audit['candidates']}
ck('Focus scope frozen 11 programs and 25 source kernel rows',len(d['programs'])==11 and len(kernel['rows'])==25)
rchecks=[]
for p in d['programs']:
 name=p['program'];orig=by[(name,'F128')]['original_status']|by[(name,'F256')]['original_status']
 for k,o in p['original_refs'].items():
  if k not in orig:continue
  rchecks.append({'program':name,'cell_profile':k,'PASS':orig[k]['cycles']==o.get('cycles') and orig[k]['RESULT_sha256']==o.get('RESULT_sha256')})
ck('44 runtime cycle and RESULT identities equal independent final originals',len(rchecks)==44 and all(x['PASS'] for x in rchecks),rchecks)
cchecks=[]
for p in d['programs']:
 for r in p['counter_rows']:
  key=r['cell']+'-'+r['profile'];o=p['original_refs'][key]
  cchecks.append({'program':p['program'],'key':key,'PASS':r['result_sha256']==o['RESULT_sha256'] and r['input_digest']==p['input_digest'] and 'NOT_PER_KERNEL' in r['measurement_level']})
ck('44 old counter projection rows bind final original identity and scope',len(cchecks)==44 and all(x['PASS'] for x in cchecks),cchecks)
ck('Per-kernel missingness not imputed',all(r['per_kernel_cycles'] is None and r['per_kernel_L2_queue_wait'] is None and r['per_kernel_MSHR_merge'] is None and r['capture_source_link']=='UNRESOLVED' and r['capture_elf_link']=='UNRESOLVED' and not r['new_runtime_measurement'] for r in kernel['rows']))
hy=next(p for p in d['programs'] if p['program']=='hybridsort');ck('Hybrid originalF128 stays missing despite named IR',hy['original_cycles']['DH-F128'] is None and hy['DH_speedup_F128'] is None and d['no_named_alternate_substitution'])
ck('No CH F result fabricated',all(p['CH_F128'] is None and p['CH_F256'] is None for p in d['programs']))
ck('Final report missing counters disclosed',d['counters_in_final_report']['availability']=='NOT_COLLECTED_BY_THIS_ANALYSIS' and not d['counters_in_final_report']['missing_means_zero'])
text=(B/'KERNEL_ANALYSIS_PREPARATION.md').read_text();ck('Causal counterexamples and source limits explicit',all(x in text for x in ['not a measured isolated L2','not measured persistence','not capture-producer certification','fewer failures disproves','do not establish actual MSHR merge','vectorAdd','M5']))
(C/'AGENT_B_INDEPENDENT_REVIEW.json').write_text(json.dumps({'schema':'DTC_STAGE_IIA_AGENT_B_INDEPENDENT_REVIEW_V1','preparation_status':'PASS' if all(x['PASS'] for x in checks) else 'HOLD','execution_status':'NOT_AUTHORIZED','all_checks_PASS':all(x['PASS'] for x in checks),'checks':checks,'reviewed_manifest_sha256':sha((B/'MANIFEST.json').read_bytes()),'reviewed_scientific_content':['Rows/columns CUDA filter staging and halo formulas have candidate-source anchors and cannot assign whole-program gain to a phase.','Scan 17first-pass+8middle+8uniform=33 launch interpretation retains host-scale mismatch.','ATAX and MVT lane16384B/4B directions differ from BICG phase order; algebraic independence and host serialization distinguished.','Static neighborhoods/broadcast/texture/load reuse do not prove hit or in-flight merge.','GEMM/3MM/particlefilter printed zero/two DRAM reads retained as observed counters with cache initialization and scope caveats.','VectorAdd F256 regression despite fewer failed requests prevents simplistic fewer-events=>faster reasoning.','11 program counters are trace-total associations; all25 per-kernel timing and merging values remain null.'],'required_corrections':[]},indent=2)+'\n')
print(json.dumps([{'check':x['check'],'PASS':x['PASS']} for x in checks],indent=2))

