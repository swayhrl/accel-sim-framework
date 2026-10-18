"""IO-only regression for retained attempt files. No compiler, RTL or EDA call."""
from pathlib import Path
import sys,json,hashlib,gzip,tempfile,datetime
wt=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-r3b-owner-cost-v1');book=Path('/workspace/ep_l2_rtl_r3_metadata_cost');sys.path.insert(0,str(wt/'rtl/ep_l2/flow'));from artifact_attempt_r3 import attempt_directory,verify_binary_archive
expected=json.loads((book/'SOURCE_CANDIDATES.json').read_text())['R3B_FINAL']['five_RTL_files'];actual={p:hashlib.sha256((wt/p).read_bytes()).hexdigest() for p in expected};assert actual==expected
checks=[]
with tempfile.TemporaryDirectory(prefix='evidence-io-',dir=book) as temp:
 root=Path(temp);old=root/'compressed-interruption';old.mkdir();payload=b'unreceived stopped executable fixture';original={'B16.vvp.gz':gzip.compress(payload,mtime=0),'B16-compile.log':b'original compile output','B16-run.log':b'original interrupted run'}
 for name,raw in original.items():(old/name).write_bytes(raw)
 new=attempt_directory(old,'B16');assert new!=old
 for name in original:(new/name).write_bytes(b'NEW ATTEMPT; must not touch previous attempt')
 assert {n:(old/n).read_bytes() for n in original}==original;checks.append('compressed interruption without raw VVP: prior archive/logs unchanged by retry output')
 again=attempt_directory(old,'B16');assert again not in (old,new);assert (new/'B16-run.log').read_bytes()==b'NEW ATTEMPT; must not touch previous attempt';checks.append('second retry uses another unique directory; previous retry unchanged')
 rawroot=root/'raw-interruption';rawroot.mkdir();(rawroot/'UNIFIED.vvp').write_bytes(payload);attempt=attempt_directory(rawroot,'UNIFIED');assert attempt!=rawroot and (rawroot/'UNIFIED.vvp').read_bytes()==payload;checks.append('raw interrupted VVP is retained and not unlinked')
 clean=root/'clean';clean.mkdir();assert attempt_directory(clean,'S64')==clean;checks.append('first new mode retains legacy layout')
 default=old/'B16.vvp.gz';row={'binary_sha256':hashlib.sha256(payload).hexdigest()};verify_binary_archive(row,default);verify_binary_archive({**row,'archive':str(default)});verify_binary_archive({**row,'exact_binary_archive':str(default)});checks.append('legacy/default and explicit archived binary digest paths verified')
 bad=root/'tampered.vvp.gz';bad.write_bytes(gzip.compress(b'different stopped executable',mtime=0))
 try:verify_binary_archive({**row,'archive':str(bad)})
 except AssertionError:checks.append('changed accepted archive rejected')
 else:raise AssertionError('tampered binary unexpectedly accepted')
receipt={'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'EVIDENCE_IO_ONLY_REGRESSION_PASS','scope':'file collision/immutability and gzip digest verification only; no RTL/C++/Yosys/STA execution, no hardware PASS or resource admission inferred','checks':checks,'hardware_five_RTL_unchanged':actual==expected,'actual_hardware_five_RTL_sha256':actual,'source_files':{str(p.relative_to(wt)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [wt/'rtl/ep_l2/flow'/n for n in ('artifact_attempt_r3.py','run_functional.py','run_lane3_bytes_r2.py','run_concurrency_r3.py','run_owner_stress_r3.py')]}};(book/'EVIDENCE_RESUME_IO_RECEIPT_r1.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
