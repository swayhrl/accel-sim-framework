"""Independent EP-MAIN cold restore; no capture or simulator execution."""
from pathlib import Path
import sys,json,hashlib,subprocess,os,time,tarfile
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');sys.path.insert(0,str(R/'tools'));import library_copy_v8 as e
A=Path('/root/data/ada_trace_extensions_v8_20261024_v1')
script=A/'materialize_c8_capsule_v2.py';assert hashlib.sha256(script.read_bytes()).hexdigest()=='952e2120e8f8b430706db9d310b5969a586872b32c1e6b25a604e421171d7643'
T=e.NAS/'rtx4080_sm89/bulk_20261024_v1/objects/stage_evidence_input_capsule_c8_109_20261024_v1'
D=Path('/root/data/ada_input_capsule_c8_parent_restore_20261024_v1');assert not D.exists()
g=e.Resources();before=g(True)
argv=['python3','-B',str(script),str(T),str(D),'--expected-control-sha','54391026f49ef2d896fe9a1ec27560266555e6680eb3e74520ff4f700afadd42','--expected-manifest-sha','b4bec0a76fce01a73423aedb78c21300393d0ec13e1317294ad5d9dfd67eea73','--expected-commit-sha','fd82986b9f2056dc204173602fc9152cabe888e4fde9c142885e032d9cfc2381']
intent={'status':'PARENT_INDEPENDENT_COLD_RESTORE_STARTED','argv':argv,'materializer_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'before':before,'observed_unix':time.time(),'GPU_or_simulator_execution':False}
(R/'control/PARENT_C8_COLD_RESTORE_INTENT.json').write_text(json.dumps(intent,indent=2)+'\n')
with (R/'logs/parent_c8_cold_restore.log').open('xb') as out:cp=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT,timeout=240)
assert cp.returncode==0,'c8 materializer failed; preserve destination and log'
q=json.loads((D/'MATERIALIZED_C8_RESTORE_PROOF.json').read_text());assert q['status']=='TRUE164_TWO_OBJECT_FULL_MEMBER_SHA_MATERIALIZED_C8_RESTORE_AND_HANDLE_JOIN_PASS'
assert len(q['positive'])==10 and len(q['all30_structural_negatives_rejected'])==30 and q['verified_control_members']==536 and q['verified_old_members']==238
assert q['recovered_reference_bytes']==64001812 and q['GPU_or_simulator_executed'] is False
root=D/'109/ada_input_capsule_c8_release_20261024_v1'
pins={'frozen/CONTRACT.json':'315fb51c10ca6351421afee22d8712767c609bce0c7f38577d7e63b5aadf975b','frozen/producer.so':'c8cfa41fcabc90ff962159b77cda4a7b6c3ba0dd12236bf5d41849d159ad1352','frozen/qualify_input_capsule_v4.py':'7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388','frozen/INPUT_INITIALIZATION_SCOPE_ADDENDUM.json':'f7196678b81715dda1c2d45ebeed5b94351b29925f6450dbaa7bbab66dfc870a'}
for name,want in pins.items():assert e.hash_file(root/name)==want
joins=[]
for name,case in q['positive'].items():
 p=root/'attempts'/name;execution=json.loads((p/'EXECUTION.json').read_text());assert execution['tool_sha256']==pins['frozen/producer.so'] and execution['exit_code']==0
 assert len(case['function_handle_join'])==case['launches']==1
 joins.append({'case':name,'execution_sha256':hashlib.sha256((p/'EXECUTION.json').read_bytes()).hexdigest(),'journal_sha256':hashlib.sha256((p/'traces/ada-lifecycle.tsv').read_bytes()).hexdigest(),'function_handle_join':case['function_handle_join']})
# Independently scan every tar header through zero padding/concatenation. Every
# body was already full-SHA checked by the materializer; this pass bounds names
# and rejects hidden extra/link/duplicate members after the usual tar terminator.
strict=[]
for obj in [T,T.parent/'stage_evidence_input_capsule7_109_20261024_v1']:
 m=json.loads((obj/'MANIFEST.json').read_text());expected={x['member'] for x in m['files']};seen=set()
 with tarfile.open(obj/'payload.tar','r|',ignore_zeros=True,errorlevel=2) as tf:
  for ti in tf:
   pp=Path(ti.name);assert ti.isfile() and not pp.is_absolute() and '..' not in pp.parts and ti.name not in seen and ti.name in expected
   seen.add(ti.name)
 assert seen==expected;strict.append({'object':str(obj),'all_headers_through_zero_padding':len(seen),'no_links_extra_or_duplicate_members':True})
allocated=sum(p.lstat().st_blocks*512 for p in D.rglob('*') if not p.is_symlink());assert allocated<=256*e.MIB
review=Path('/root/share/rtx4080_cuda_polybench_20261024_v1/c8_independent_review_v1/INDEPENDENT_C8_REVIEW.json');assert review.exists()
proof={'status':'PASS_PARENT_INDEPENDENT_C8_DURABLE_FULL_RESTORE_AND_CODE_PINS','materialized_root':str(root),'cold_restore_proof_sha256':hashlib.sha256((D/'MATERIALIZED_C8_RESTORE_PROOF.json').read_bytes()).hexdigest(),'cold_restore_proof':q,'frozen_pins':pins,'independent_launch_identity_joins':joins,'strict_archive_header_checks':strict,'allocated_native_bytes':allocated,'separate_lane_review_path':str(review),'separate_lane_review_sha256':hashlib.sha256(review.read_bytes()).hexdigest(),'after':g(True),'GPU_or_simulator_execution':False,'scientific_upgrade':False,'parent_profile_release_still_separate':True,'observed_unix':time.time()}
(R/'control/PARENT_C8_COLD_RESTORE_PASS.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':proof['status'],'allocated_native_bytes':allocated,'restored_reference_bytes':q['recovered_reference_bytes'],'positive_cases':10,'negative_cases':30}))
