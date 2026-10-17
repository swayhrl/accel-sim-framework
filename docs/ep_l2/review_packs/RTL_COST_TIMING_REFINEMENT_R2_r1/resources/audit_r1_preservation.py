from pathlib import Path
import json,hashlib,subprocess,gzip,datetime
repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-v1');pack=repo/'docs/ep_l2/review_packs/RTL_COST_OPEN_FLOW_V1_r1';root=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_OPEN_FLOW_V1_lane2_r1');out=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3/R1_PRESERVATION_AUDIT.json');frozen='09de19579c0708f6542dfd65e1f3aae8a9a8b841'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==frozen;assert not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
count=0
for line in (pack/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split(None,1);name=name.strip().lstrip('*');p=pack/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(name,'R1 public asset changed');count+=1
idx=json.loads((root/'ARTIFACT_ARCHIVE_INDEX.json').read_text());archives=[]
for row in idx['files']:
 p=root/row['archive_relative_path'];assert p.stat().st_size==row['archive_bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['archive_sha256'];archives.append(row['archive_relative_path'])
current=[]
for receipt in (pack/'functional/pin_admission_r1/NEW_GREEN_FUNCTIONAL_RECEIPT.json',pack/'functional/unified_last_physical_r1/FUNCTIONAL_RECEIPT.json'):
 for row in json.loads(receipt.read_text()):
  p=Path(row['exact_binary_archive'])
  with gzip.open(p,'rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
  assert actual==row['binary_sha256'];current.append({'archive':str(p),'original_binary_sha256':actual})
result={'frozen_R1_commit':frozen,'R1_cost_worktree_clean':True,'public_manifest_files_verified':count,'large_original_R1_archives_verified':archives,'accepted_original_R1_functional_binaries_verified':current,'no_R1_file_written_by_audit':True,'no_original_R1_test_rerun':True,'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};out.write_text(json.dumps(result,indent=2)+'\n');print('R1 immutable public assets',count,'large archives',len(archives),'accepted binaries',len(current),'verified read-only')
