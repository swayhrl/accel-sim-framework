"""Freeze old terminal assertions honestly; current raw bytes are checked by the new V4 worker."""
import pathlib,json,hashlib,argparse,os
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('oldwork');ap.add_argument('raw_manifest');ap.add_argument('raw_manifest_sha256');ap.add_argument('output');a=ap.parse_args()
root=pathlib.Path(a.root).resolve();old=pathlib.Path(a.oldwork);out=pathlib.Path(a.output);proof=pathlib.Path(a.raw_manifest);assert sha(proof)==a.raw_manifest_sha256 and not out.exists()
source=json.loads(proof.read_text());known={pathlib.PurePosixPath(x['path']).name:x for x in source['raw_members']}
ctx=list((root/'traces').glob('kernelslist_ctx_*'));stats=list((root/'traces').glob('stats_ctx_*'));assert len(ctx)==len(stats)==1
controls={str(p):sha(p)for p in[root/'EXECUTION.json',root/'map/manifest.json',ctx[0],stats[0]]};portable=old/'delegated_validator_portable.py';rows=[]
for r in sorted(old.iterdir()):
 if not r.is_dir()or not(r/'FULL_RECORD_STREAM_VALIDATION.json').exists():continue
 try:q=json.loads((r/'stdout.log').read_text())
 except (ValueError,OSError):continue
 assert q==json.loads((r/'FULL_RECORD_STREAM_VALIDATION.json').read_text())and q['status']=='ADA7_ORDINARY_FULL_RECORD_PASS'
 assert q['validator_sha256']==sha(portable)and q['frozen_parser_sha256']=='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
 n=q['per_kernel'][0]['name'];raw=root/'traces'/n;st=raw.stat();x=known[n];assert st.st_size==x['bytes']and st.st_mtime_ns==x['mtime_ns']
 assert len(q['source_files'])==1 and next(iter(q['source_files'].values()))==x['sha256']
 files=[r/'FULL_RECORD_STREAM_VALIDATION.json',r/'stdout.log',r/'stderr.log',r/'EXECUTION.json',r/'traces'/ctx[0].name,r/'traces'/stats[0].name]
 rows.append({'name':n,'raw_fingerprint':[st.st_size,st.st_mtime_ns,x['sha256']],'receipt':str(files[0]),'stdout':str(files[1]),'proof_files':{str(p):sha(p)for p in files},'adoption_provenance':'TERMINAL_RESULT_ADOPTION_OLD_EXIT_NOT_SEPARATELY_RECORDED','current_raw_fullSHA_is_not_claimed_here':'New V4 supervised worker must re-read full current raw SHA before using this result'})
result={'schema':'ADA7_EXACT_CLOSED_KERNEL_RECEIPT_CACHE_V1','root':str(root),'source_control_files':controls,'map_sha256':sha(root/'map/manifest.json'),'delegated_original_validator_sha256':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','frozen_parser_sha256':'f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b','delegated_portable_validator_sha256':sha(portable),'kernels':rows,'source_expected_raw_sha_manifest':str(proof),'source_expected_raw_sha_manifest_sha256':sha(proof),'old_exit_not_separately_recorded':True,'source_KEEP':True}
with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'kernels':len(rows),'sha256':sha(out),'old_exit_not_separately_recorded':True}))
