import pathlib,json,hashlib,csv,argparse,os
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('oldwork');ap.add_argument('output');ap.add_argument('--parser',required=True);a=ap.parse_args()
root=pathlib.Path(a.root).resolve();old=pathlib.Path(a.oldwork);out=pathlib.Path(a.output);parser=pathlib.Path(a.parser)
assert not out.exists()
ctx=list((root/'traces').glob('kernelslist_ctx_*'));stats=list((root/'traces').glob('stats_ctx_*'));assert len(ctx)==len(stats)==1
controls={str(p):sha(p)for p in [root/'EXECUTION.json',root/'map/manifest.json',ctx[0],stats[0]]}
portable=old/'delegated_validator_portable.py';assert portable.exists()
rows=[]
for r in sorted(old.iterdir()):
 if not r.is_dir()or not(r/'FULL_RECORD_STREAM_VALIDATION.json').exists():continue
 try:q=json.loads((r/'stdout.log').read_text())
 except (ValueError,OSError):continue
 assert q==json.loads((r/'FULL_RECORD_STREAM_VALIDATION.json').read_text())
 name=q['per_kernel'][0]['name'];raw=root/'traces'/name;st=raw.stat()
 # Exact bytes of complete receipts and their single-kernel execution views are frozen.
 proofs=[r/'FULL_RECORD_STREAM_VALIDATION.json',r/'stdout.log',r/'stderr.log',r/'EXECUTION.json',r/'traces'/ctx[0].name,r/'traces'/stats[0].name]
 rows.append({'name':name,'raw_fingerprint':[st.st_size,st.st_mtime_ns,sha(raw)],'receipt':str(proofs[0]),'stdout':str(proofs[1]),'proof_files':{str(p):sha(p)for p in proofs}})
result={'schema':'ADA7_EXACT_CLOSED_KERNEL_RECEIPT_CACHE_V1','root':str(root),'source_control_files':controls,'map_sha256':sha(root/'map/manifest.json'),'delegated_original_validator_sha256':'f9f8a05ca7e0f8afe60e7d9a34f4884a9d1cb920b2212e41ed9a4faf19975af1','frozen_parser_sha256':sha(parser),'delegated_portable_validator_sha256':sha(portable),'kernels':rows,'partial_incomplete_stdout_excluded':True,'source_KEEP':True}
with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'kernels':len(rows),'sha256':sha(out),'path':str(out)}))
