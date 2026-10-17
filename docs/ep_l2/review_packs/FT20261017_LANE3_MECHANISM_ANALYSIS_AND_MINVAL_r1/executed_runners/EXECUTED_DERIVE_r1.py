#!/usr/bin/env python3
"""Read-only accepted-results derivation; never launches/changes a simulation."""
import argparse,collections,csv,datetime,hashlib,json,re,subprocess
from pathlib import Path
L5=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1')
SHARED=Path('/workspace/ep_l2_ft20261016_shared')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def csvwrite(path,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def parse(raw):
 app={};ft={};kernels={};windows=[];h=hashlib.sha256()
 with raw.open('rb') as stream:
  for data in stream:
   h.update(data);line=data.decode(errors='strict').rstrip()
   if line.startswith('EPL2B0V1|scope='):
    r=dict(p.split('=',1) for p in line.split('|')[1:]);scope=r['scope']
    if scope=='application':app[int(r['slice'])]=r
    elif scope=='kernel':kernels[(r['kernel_uid'],r['slice'])]=r
    elif scope=='window':windows.append(r)
   elif line.startswith('EPL2FTV1|SUMMARY|'):
    r=dict(p.split('=',1) for p in line.split('|')[2:]);ft[int(r['slice'])]=r
 assert set(app)==set(range(64)) and set(ft)==set(range(64))
 def total(key):return sum(int(r[key]) for r in app.values()) if all(key in r for r in app.values()) else None
 metrics={k:total(k) for k in ['samples','bank_logical_ops','bank_wait_cycles','bank_true_conflict_ops','c7d_wad_full_events','c7d_wad_hazard_events','c7d_wad_hazard_wait_cycles','c7d_dram_issue_eligible','c7d_dram_scheduler_full_block','c7e_dram_issue_attempt','c7d_l2_to_dram_full_block','c7d_descriptor_pool_full_block','c7d_line_mshr_full_block','block_payload','block_lower']}
 metrics.update({k:sum(int(r[k]) for r in ft.values()) for k in ['wb_created','wb_completed','wb_lower_accept','wbuf_full','pool_full','pin_block','bank_block','issue_block','copy_lines','copy_bytes','staging_reads','borrow_resident','borrow_bypass','rollback','version_checks','wb_occupancy_sum','observed_cycles']})
 metrics.update(staged_record_peak=max(int(r['staged_max']) for r in ft.values()),WAD_peak=max(int(r['wad_max']) for r in app.values()),WAD_lifetime_unweighted_truncated_slice_average=sum(int(r['c7d_wad_lifetime_avg']) for r in app.values())/64)
 metrics['physical_WB_role_mean']=metrics['wb_occupancy_sum']/metrics['observed_cycles']
 metrics['scheduler_refusal_per_actual_issue_attempt']=metrics['c7d_dram_scheduler_full_block']/metrics['c7d_dram_issue_eligible'] if metrics['c7d_dram_issue_eligible'] else None
 metrics['L2_lower_full_per_sampled_slice_cycle']=metrics['c7d_l2_to_dram_full_block']/metrics['samples'] if metrics['samples'] else None
 for b in range(4):
  metrics[f'bank{b}_logical_ops']=total(f'c7d_bank{b}_logical_ops');metrics[f'bank{b}_wait_cycles']=total(f'c7d_bank{b}_wait_cycles')
 intervals=[]
 for uid in sorted({k[0] for k in kernels},key=int):
  rows=[r for (u,s),r in kernels.items() if u==uid];assert len(rows)==64
  boundaries={(r['start_cycle'],r['completion_cycle']) for r in rows};assert len(boundaries)==1
  start,end=map(int,next(iter(boundaries)));intervals.append({'kernel_uid':uid,'start_cycle':start,'completion_cycle':end,'shared_interval_length':end-start,'overlap_detected':max(int(r['overlap_detected']) for r in rows),'slice_sample_count':sum(int(r['samples']) for r in rows),'bank_logical_ops':sum(int(r['bank_logical_ops']) for r in rows),'bank_wait_cycles':sum(int(r['bank_wait_cycles']) for r in rows),'wad_hazard_events':sum(int(r['c7d_wad_hazard_events']) for r in rows),'interpretation':'Shared resource interval, not exclusive per-kernel execution/stall time'})
 ordered=sorted(intervals,key=lambda r:r['start_cycle']);overlap=any(b['start_cycle']<a['completion_cycle'] for a,b in zip(ordered,ordered[1:]));metrics['kernel_interval_overlap_detected']=overlap or any(r['overlap_detected'] for r in intervals)
 return h.hexdigest(),metrics,intervals,app,windows

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=False)
 c=json.loads((SHARED/'CLIENT_CONTRACT.json').read_text());binding=c['scientific_acceptance'];path=Path(binding.get('snapshot_path',binding['path']));data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==binding['sha256']
 # Exact published snapshot bytes, not staged mutable current files.
 relative=path.relative_to(L5);published=subprocess.check_output(['git','show',binding['publication_commit']+':'+str(relative)],cwd=L5);assert published==data
 write(out/'AUTHORITY.json',{'contract':'f1980a84c8e637ff2050048bd11b3c1fa5362583','pointer':binding,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(__file__),'scope':'Only CURRENT_ACCEPTED exact rows. No full trace body hashes recomputed.'})
 (out/'SCIENTIFIC_ACCEPTANCE_SNAPSHOT.json').write_bytes(data);accept=json.loads(data);registry=json.loads((SHARED/'RUN_REGISTRY.json').read_text());accepted=[r for r in accept['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'];catalog=[];metrics=[];kernels=[];inputs=[];sources=[]
 for row in accepted:
  ident=row['identity'];review=L5/row['independent_review']['path'];assert sha(review)==row['independent_review']['sha256'];directory=Path(registry['runs'][row['run_key']]['result_directory']);raw=directory/'raw.log'
  got,m,ki,app,windows=parse(raw);assert got==row['raw_log_sha256']
  # Local physical-path data only. End-to-end ALL_DATA requires another parser.
  profile=row.get('profile',row['mode']);regime=row.get('regime','H0');base={'run_key':row['run_key'],'workload':row['workload'],'condition':regime,'profile':profile,'mode':row['mode'],'cycles':row['observed_cycles'],'instructions':row['instructions'],'core':ident['core_source_commit'],'framework':ident['framework_source_commit'],'binary':ident['binary_sha256'],'config':ident['runtime_config_sha256'],'trace':ident['trace_content_sha256'],'scientific_scope':row.get('scientific_scope','FINITE_NATIVE_SYMBOLIC_SECTOR'),'raw_log':str(raw),'raw_sha256':got}
  catalog.append(base);metrics.append({**base,**m});kernels.extend({**base,**k} for k in ki)
  audit=directory/'input_audit.json';spec=directory/'input_spec.json';s=json.loads(spec.read_text());ia=json.loads(audit.read_text());trace_files=s['trace_files'];entry=next(t for t in trace_files if t['name']==s['entry_trace_name']);commandlist=Path(entry['path']).read_text();bodies=[t for t in trace_files if t['name']!=s['entry_trace_name']];run_script=Path(entry['path']).parent.parent/'run.sh'
  inputs.append({'workload':row['workload'],'trace':ident['trace_content_sha256'],'source_run_key':row['run_key'],'entry':entry['path'],'commandlist_literal':commandlist,'declared_trace_body_files':len(bodies),'literal_capture_script':run_script.read_text() if run_script.is_file() else 'NOT_DISCLOSED_IN_LOCATED_CAPTURE_MATERIAL','capture_script_path':str(run_script) if run_script.is_file() else None,'directory_version_label':'/9.1/' if '/9.1/' in entry['path'] else 'NOT_DISCLOSED','runtime_instruction_count':row['instructions'],'timing_boundary':'Native full-application terminal gpu_tot_sim_cycle including modeled launch/drain. Not host walltime or sum of slice/kernel samples. Original commandlist need not be source default iteration count.','atomic_scope':ia.get('atomic_input_scope',s.get('atomic_input_scope')),'trace_file_manifest':ia.get('trace_files'),'no_new_trace_scan':True})
  sources.append({'run_key':row['run_key'],'review_path':str(review),'review_sha256':sha(review),'input_spec':str(spec),'input_spec_sha256':sha(spec),'input_audit_sha256':sha(audit)})
 pairs=[]
 for b in catalog:
  if b['mode']!='B16_BANKED' or b['profile'] not in ['B16_BANKED','B16_OFF']:continue
  matches=[u for u in catalog if u['mode']=='U_WB16' and all(u[k]==b[k] for k in ['workload','condition','core','framework','binary','trace'])]
  if not matches:continue
  assert len(matches)==1;u=matches[0];assert b['instructions']==u['instructions'];pairs.append({'workload':b['workload'],'condition':b['condition'],'binary':b['binary'],'trace':b['trace'],'B_cycles':b['cycles'],'U_cycles':u['cycles'],'S_EP':b['cycles']/u['cycles'],'delta_B_minus_U':b['cycles']-u['cycles'],'B_key':b['run_key'],'U_key':u['run_key']})
 for r in pairs:
  h=next((x for x in pairs if x['workload']==r['workload'] and x['binary']==r['binary'] and x['condition']=='H0'),None)
  r['J_vs_same_binary_H0']=r['S_EP']/h['S_EP'] if h else None;r['B_absolute_speedup_vs_H0']=h['B_cycles']/r['B_cycles'] if h else None;r['U_absolute_speedup_vs_H0']=h['U_cycles']/r['U_cycles'] if h else None
 ideals=[]
 for point in catalog:
  if not point['profile'].startswith('I_'):continue
  anchors=[r for r in catalog if r['profile']=='B16_OFF' and all(r[k]==point[k] for k in ['workload','condition','binary','trace','core','framework'])];assert len(anchors)==1;anchor=anchors[0]
  ideals.append({'workload':point['workload'],'profile':point['profile'],'binary':point['binary'],'anchor_cycles':anchor['cycles'],'ideal_cycles':point['cycles'],'operational_headroom':anchor['cycles']/point['cycles'],'delta_anchor_minus_ideal':anchor['cycles']-point['cycles'],'anchor_key':anchor['run_key'],'point_key':point['run_key'],'interpretation':'Same-binary operational ideal diagnostic; not EP speedup or strict universal bound'})
 availability=[]
 for work in ['convolutionSeparable','FWT_7_21','cfd_097k','vectorAdd_4M']:
  for prof in ['S64','U_CAP16','I_WB','I_META','I_WB_META','I_READ_HIT','I_MEM_ALL_DATA']:
   found=[r for r in catalog if r['workload']==work and r['profile']==prof];availability.append({'workload':work,'profile':prof,'status':'CURRENT_ACCEPTED' if found else 'NO_CURRENT_ACCEPTED_POINT','cycles':found[0]['cycles'] if len(found)==1 else None,'binary':found[0]['binary'] if len(found)==1 else None,'missing_is_not_zero':True})
 csvwrite(out/'accepted_runs.csv',catalog);csvwrite(out/'finite_pairs.csv',pairs);csvwrite(out/'pressure_and_banks.csv',metrics);csvwrite(out/'kernel_shared_intervals.csv',kernels);csvwrite(out/'local_ideal_endpoints.csv',ideals);csvwrite(out/'strong_static_and_ideal_availability.csv',availability)
 # Deduplicate inputs by workload/content identity. No claim about default source loop count.
 write(out/'INPUT_SCOPE.json',list({(r['workload'],r['trace']):r for r in inputs}.values()));write(out/'SOURCE_MANIFEST.json',sources)
 write(out/'DERIVATION_RECEIPT.json',{'status':'PASS_IDENTITY_BOUND_DERIVATION','accepted_rows':len(catalog),'matched_finite_pairs':len(pairs),'same_binary_ideal_comparisons':len(ideals),'raw_logs_read':len(catalog),'new_full_apps':0,'trace_body_scans':0,'rules':['No cross-binary pairing','Final cumulative row per64slices only','Shared kernel intervals retain overlap flags; no sum as exclusive time','Retry events, bank wait and resource pressures are separate units; no total-stall summation','Missing pending endpoints stay null','Physical sampled WB-role occupancy differs from staged record peak','B/U staging_lifetime starts differ; not used for cross-mode duration comparison']})
 print(json.dumps({'status':'PASS','accepted':len(catalog),'pairs':len(pairs),'ideals':len(ideals),'out':str(out)}))
if __name__=='__main__':main()
