from pathlib import Path
import json,hashlib,gzip,subprocess,datetime
repo=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2-fanout-v3');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3');canonical='f54d3c054a6a03c85b40a1c5018751958c78a129';refs=[]
for mode in ('B16','S64','UNIFIED'):
 r=json.loads((art/'cost-vector'/mode/'FLOW_RECEIPT.json').read_text())
 assert r['mapping_effort']=='fast-clean' and r['parameters']['N_TAG']==1024 and r['parameters']['N_PAYLOAD']==1168 and r['parameters']['N_WAD']==128 and r['parameters']['GEN_W']==32 and r['parameters']['P']==1
 for f in r['RTL_files']:assert hashlib.sha256(subprocess.check_output(['git','show',canonical+':'+f['path']],cwd=repo)).hexdigest()==f['sha256']
 refs.append(r)
assert all(x['RTL_files']==refs[0]['RTL_files'] and x['library_sha256']==refs[0]['library_sha256'] and x['sdc_sha256']==refs[0]['sdc_sha256'] for x in refs)
base=json.loads((art/'qualification-vector/functional/FUNCTIONAL_RECEIPT.json').read_text());oracle=json.loads((art/'qualification-vector/lane3-bytes/LANE3_BYTE_RECEIPT.json').read_text());rows=[]
for row in base:
 assert row['returncode']==0
 for f in refs[0]['RTL_files']:assert row['RTL_sha256'][f['path']]==f['sha256']
 p=Path(row['exact_binary_archive'])
 with gzip.open(p,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['binary_sha256']
 rows.append({'archive':str(p),'binary_sha256':row['binary_sha256'],'exact_decoded_bytes':True})
for row in oracle['rows']:
 p=art/'qualification-vector/lane3-bytes'/(row['mode']+'.vvp.gz')
 with gzip.open(p,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['binary_sha256']
 rows.append({'archive':str(p),'binary_sha256':row['binary_sha256'],'exact_decoded_bytes':True})
assert all(oracle['RTL_sha256'][f['path']]==f['sha256'] for f in refs[0]['RTL_files'])
(art/'IDENTITY_PREFLIGHT_FINAL.json').write_text(json.dumps({'canonical_RTL':canonical,'three_modes_same_actual_RTL_library_SDC_mapping_effort':True,'all_cost_capacities_full':True,'base_four_plus_Lane3_three_binaries':rows,'stimulus_sha256':oracle['stimulus_sha256'],'reference_sha256':oracle['reference_sha256'],'highest_boundary':'IN_PROGRESS_NOT_CLAIMED_BY_THIS_PREFLIGHT','UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n');print('identity preflight:3mapped modes/7executed binaries exact; last-boundary not yet claimed')
