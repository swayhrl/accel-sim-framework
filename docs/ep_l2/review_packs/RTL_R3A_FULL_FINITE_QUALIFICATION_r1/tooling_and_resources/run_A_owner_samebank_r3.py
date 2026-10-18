"""New A-only directed coverage using exact already-frozen owner fixture.
Not a rerun of passed B source. A worktree and its published pack are read-only.
Caller holds ordinary central resource admission; no exception is used.
"""
from pathlib import Path
import json,hashlib,subprocess,gzip,argparse
book=Path('/workspace/ep_l2_rtl_r3_metadata_cost');art=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2');wt=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-r3-metadata-cost-v1');out=art/'R3A_OWNER_SAMEBANK_DIRECTED_r1';out.mkdir(exist_ok=False);prior=art/'R3B_FINAL_QUAL/owner-stress';ref=json.loads((prior/'OWNER_STRESS_RECEIPT.json').read_text());fixture=out/'owner_stress_tb.sv';fixture.write_bytes((prior/'owner_stress_tb.sv').read_bytes());assert hashlib.sha256(fixture.read_bytes()).hexdigest()==ref['fixture_sha256'];expected=json.loads((book/'SOURCE_CANDIDATES.json').read_text())['R3A']['five_RTL_files'];assert {p:hashlib.sha256((wt/p).read_bytes()).hexdigest() for p in expected}==expected;rows=[]
for mode,label in enumerate(('B16','UNIFIED','S64')):
 binary=out/(label+'.vvp');cmd=['iverilog','-g2012','-s','ep_l2_owner_r3_tb','-P',f'ep_l2_owner_r3_tb.MODE={mode}','-DEP_L2_FULL_TOP','-f','rtl/ep_l2/flow/full_slice_filelist.f','-o',str(binary),str(fixture)]
 with (out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=wt,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (out/(label+'-run.log')).open('w') as f:subprocess.run(['vvp',str(binary)],cwd=wt,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=900)
 text=(out/(label+'-run.log')).read_text();assert 'R3_SAME_BANK_INDEPENDENT_GEN' in text and 'R3_ACTUAL_OWNER_STRESS' in text and 'full-drain PASS' in text
 assert {p:hashlib.sha256((wt/p).read_bytes()).hexdigest() for p in expected}==expected and hashlib.sha256(fixture.read_bytes()).hexdigest()==ref['fixture_sha256']
 raw=binary.read_bytes();archive=binary.with_suffix('.vvp.gz');assert not archive.exists();archive.write_bytes(gzip.compress(raw,6,mtime=0));assert gzip.decompress(archive.read_bytes())==raw;binary.unlink();rows.append({'mode':label,'status':'ACTUAL_RTL_OWNER_REBIND_LATE_FILL_PIN_SNAPSHOT_BYTES_DRAIN_PASS','binary_sha256':hashlib.sha256(raw).hexdigest(),'archive':str(archive),'compile_command':cmd});(out/'OWNER_STRESS_RECEIPT.json').write_text(json.dumps({'rows':rows,'fixture_sha256':ref['fixture_sha256'],'source_RTL_sha256':expected,'scope':'NEW A-only full-size same-bank different-row double-GEN and held-pin/late-fill/byteWB test; exact frozen B fixture, compiled actual A hardware; B tests not repeated'},indent=2)+'\n');print('R3A',label,'same-bank double-GEN/owner actual PASS',flush=True)
