"""Coordinator-only consistency checks. Reads delivered analysis; no simulation API."""
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(ok,label):
 checks.append({'check':label,'pass':bool(ok)})
 if not ok:raise AssertionError(label)
def read(rel):return json.loads((ROOT/rel).read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 A=read('agents/A/SUITE_PERFORMANCE_ANALYSIS.json')
 B=read('agents/B/WORKLOAD_FEATURE_MATRIX.json')
 C=read('agents/C/POSITIVE_CASE_MECHANISM_REPORT.json')
 E=read('agents/E/PQ_PS_INDEPENDENT_REVIEW.json')
 cells=read('agents/E/ACCEPTED_CELL_EVIDENCE.json')
 index=read('shared_address_index/INDEX.json')
 programs={r['program']:r for r in A['programs']}
 check(len(programs)==23,'23 original complete members')
 baseline=read('coordinator/BASELINE_INDEPENDENT_RECOMPUTATION.json')
 ratios=[]
 for p,r in programs.items():
  cycles=r['cycles'];check(all(cycles[k]>0 for k in ['CM','CH','DM','DH']),p+' positive model cycles')
  ratios.append(cycles['CH']/cycles['DH'])
  for mode,cell in r['cells'].items():
   check(cell['input_digest']==r['input_digest'],p+mode+' full input join')
   check(cell['accepted_cycles']==cycles[mode],p+mode+' accepted cycle join')
   check(cell['actual_core_commit']=='2e3bef4364e578cddd0e881c0baace2e51c55930',p+mode+' original Core retained')
   check(len(cell['actual_binary_sha256'])==64 and len(cell['raw_gzip_sha256'])==64,p+mode+' binary/raw SHA')
 gm=math.exp(statistics.mean(map(math.log,ratios)))
 check(math.isclose(gm,baseline['statistics']['CH_DH']['GM'],rel_tol=1e-13),'independent GM recomputation matches A')
 check(len(B['rows'])==23,'B same23 members')
 for r in B['rows']:
  p=r['program'];check(p in programs,p+' B membership')
  check(r['input_digest']==programs[p]['input_digest'],p+' B full input identity')
  check(r['original_four_configuration_cycles']==programs[p]['cycles'],p+' B/A all four original cycles')
 for r in C['cases']:
  p=r['program'];check(r['input_digest']==programs[p]['input_digest'],p+' C input identity')
  check(r['cycles']==programs[p]['cycles'],p+' C/A four original cycles')
 check(len(C['cases'])==5,'C all five predeclared positives')
 check(index['contract']['single_process'],'one shared address producer')
 check(index['observed']['total_trace_bytes_read']<=index['contract']['total_trace_bytes_limit'],'shared scan byte cap')
 check(index['observed']['wall_seconds']<=index['contract']['wall_limit_seconds'],'shared scan wall cap')
 check(index['observed']['max_RSS_KiB']*1024<=index['contract']['RLIMIT_AS_bytes'],'shared scan RSS cap')
 for r in index['rows']:
  check(r['input_digest']==programs[r['program']]['input_digest'],r['program']+' address identity')
  if r['program']in ['ATAX','MVT','BICG']:
   check(r['coverage']=='FULL_DECLARED_KERNEL'and r['full_SHA_reverified'],r['program']+' full strided kernel SHA scan')
  else:check(r['coverage']=='PREFIX_ONLY'and not r['full_SHA_reverified'],r['program']+' bounded prefix not promoted')
 check(len(cells)==E['accepted_cells'],'E accepted count')
 emap={(r['program'],r['cell'],r['profile']):r for r in cells}
 check(len(emap)==len(cells),'E unique accepted identities')
 for r in cells:
  check(r['input_digest']==programs[r['program']]['input_digest'],r['cohort']+' E same selected input')
  check(r['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70',r['cohort']+' separate repaired Core scope')
  check(r['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4',r['cohort']+' separate FW')
  check(sum(k['cycles']for k in r['kernels'])==r['cycles'],r['cohort']+' all kernel cycle sum')
  check(len(r['DONE_sha256'])==64 and len(r['result_sha256'])==64,r['cohort']+' DONE/result hashes')
 for r in E['matched_comparisons']:
  if r['status'].startswith('ACCEPTED'):
   a=emap[(r['program'],r['cell'],'P0')];b=emap[(r['program'],r['cell'],r['profile'])]
   check(math.isclose(a['cycles']/b['cycles'],r['speedup'],rel_tol=1e-13),r['program']+r['cell']+r['profile']+' E matched cycles')
   check(a['core_commit']==b['core_commit']and a['framework_commit']==b['framework_commit']and a['binary_sha256']==b['binary_sha256'],r['program']+r['cell']+r['profile']+' E model equality')
 for r in E['relative_recovery_factors']:
  required=[(r['program'],c,p)for c in ['CH','DH']for p in ['P0',r['profile']]]
  if not all(k in emap for k in required):check(r['status']=='PENDING'and r['K']is None,r['program']+r['profile']+' missing K not imputed')
 check(E['active_raw_reads']==0 and E['trace_reads']==0,'E independent allowed evidence only')
 check(E['new_simulator_starts']==0,'E no simulations')
 frozen=Path('D:/repo/tmp/DTC_P42_REPRESENTATIVE_FREEZE.json')
 check(sha(frozen)==A['freeze_sha256'],'original identity freeze unchanged')
 D=read('agents/D/STRIDED_WORKLOAD_ROOT_CAUSE_REPORT.json')
 check(len(D['programs'])==3,'D all three negative inputs')
 for r in D['programs']:
  p=r['program'];check(r['input_digest']==programs[p]['input_digest'],p+' D input')
  check(r['cycles']==programs[p]['cycles'],p+' D/A original cycles')
  f=r['accepted_read_traffic_factorization']
  check(math.isclose(f['accepted_request_factor']*f['accepted_miss_fraction_factor'],f['DRAM_read_atom_factor'],rel_tol=1e-12),p+' D exact accepted-traffic factorization')
 F=read('agents/F/SEVEN_UNRESOLVED_ADJUDICATION_REPORT.json')
 check(F['freeze_unchanged_verified']and F['frozen_count_unchanged']==35 and F['unresolved_count_unchanged']==7,'F no forced identity promotion')
 check(F['newly_frozen_inputs']==0 and F['current_commandlist_sha_matches']==F['input_count']==21,'F all21 commandlists preserve V1 identity')
 add=read('agents/E/LATEST_ACCEPTED_ADDENDUM.json')
 check(add['accepted_cells']==len(cells)+len(add['new_accepted_cells']),'E bounded latest addition count')
 for name,h in add['prior_files_sha256'].items():check(sha(ROOT/'agents/E'/name)==h,'E old cutoff preserved '+name)
 latest=emap|{(r['program'],r['cell'],r['profile']):r for r in add['new_accepted_cells']}
 for r in add['new_accepted_cells']:
  check(r['input_digest']==programs[r['program']]['input_digest'],'E add selected digest')
  check(r['core_commit']==E['core_commit']and r['binary_sha256']==E['binary_sha256'],'E add matched model identity')
  check(sum(k['cycles']for k in r['kernels'])==r['cycles'],'E add whole population cycles')
 for r in add['within_profile_CH_over_DH']:
  a=latest[(r['program'],'CH',r['profile'])];b=latest[(r['program'],'DH',r['profile'])]
  check(math.isclose(a['cycles']/b['cycles'],r['CH_over_DH'],rel_tol=1e-13),'E latest accepted profile pair '+r['program'])
 for r in add['relative_recovery_factors']:check(r['status']=='PENDING'and r['K']is None,'E latest K remains pending '+r['program']+r['profile'])
 # D/F are independently delivered and remain mandatory for completion.
 for agent,filename in [('D','STRIDED_WORKLOAD_ROOT_CAUSE_REPORT.json'),('F','SEVEN_UNRESOLVED_ADJUDICATION_REPORT.json')]:
  p=ROOT/'agents'/agent/filename;check(p.exists(),agent+' final report present');json.loads(p.read_bytes())
 out={'status':'PASS','checks':len(checks),'records':checks,'original_panel':23,'original_cells':92,'new_downstream_accepted_at_E_cutoff':len(cells),'new_downstream_pending_at_E_cutoff':E['pending_cells'],'latest_bounded_accepted':add['accepted_cells'],'latest_bounded_pending':add['pending_cells'],'latest_bounded_UTC':add['observed_UTC'],
  'GM_independently_recomputed':gm,'formal_panel_changed':False,'new_simulator_starts':0,'source_report_SHA256':{k:sha(ROOT/v)for k,v in {'A':'agents/A/SUITE_PERFORMANCE_ANALYSIS.json','B':'agents/B/WORKLOAD_FEATURE_MATRIX.json','C':'agents/C/POSITIVE_CASE_MECHANISM_REPORT.json','D':'agents/D/STRIDED_WORKLOAD_ROOT_CAUSE_REPORT.json','E':'agents/E/PQ_PS_INDEPENDENT_REVIEW.json','F':'agents/F/SEVEN_UNRESOLVED_ADJUDICATION_REPORT.json'}.items()}}
 (ROOT/'coordinator/CROSS_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in out.items()if k!='records'},ensure_ascii=False))

if __name__=='__main__':main()
