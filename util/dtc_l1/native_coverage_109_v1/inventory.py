#!/usr/bin/env python3
"""Read-only local availability audit; recorded paths are not payload."""
import csv, hashlib, json, pathlib, subprocess
repo=pathlib.Path(__file__).resolve().parents[3]
pack=repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1'
manifest=repo/'docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv'
rows=list(csv.DictReader(manifest.open(),delimiter='\t'))
fields=['workload','recorded_trace_root','recorded_members','recorded_bytes','recorded_list_sha256','local_root_exists','local_list_sha256','input_dimensions','dtype_width','targetSM_binary_sha','grid_block_shared_registers','executed_kernel_scope','load_forms_target_L1','steady_interval_L2_DRAM','evidence']
with (pack/'R0_FIXED_COHORT.tsv').open('w') as f:
 w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader()
 for r in rows:
  p=pathlib.Path(r['trace_root']); kl=p/'kernelslist.g'
  w.writerow(dict(workload=r['workload'],recorded_trace_root=str(p),recorded_members=r['traceg_members'],recorded_bytes=r['traceg_bytes'],recorded_list_sha256=r['kernelslist_g_sha256'],local_root_exists=p.is_dir(),local_list_sha256=hashlib.sha256(kl.read_bytes()).hexdigest() if kl.is_file() else 'UNAVAILABLE',**{k:'UNKNOWN_PAYLOAD_NOT_LOCAL' for k in fields[7:14]},evidence='RECORDED_MANIFEST_ONLY_NOT_VERIFIED_RUN'))
result={'framework':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'applications':len(rows),'recorded_members':sum(int(r['traceg_members']) for r in rows),'recorded_bytes':sum(int(r['traceg_bytes']) for r in rows),'local_trace_roots':sum(pathlib.Path(r['trace_root']).is_dir() for r in rows),'note':'629 ordered members are not 629 applications. Gaussian+LUD=604. NN=nearest neighbor. No sizes inferred from names. Historical source candidates are not exact captured binary/input identities.'}
(pack/'R0_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
