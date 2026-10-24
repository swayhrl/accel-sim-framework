from pathlib import Path
import json,hashlib,shutil,importlib.util,lzma,re
R=Path('/data/c16/ada_call_snapshot_nn_20261024_v1');N=R/'cpu_full_join_negatives_v2';N.mkdir()
p=R/'verify_nn_pair_full_bytes_v2.py';sp=importlib.util.spec_from_file_location('nnv2',p);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=['nan_output_with_matching_sha','wrong_finite_output_with_matching_sha','forged_output_base_consistent_journals','wrong_STG_address_validCRC','wrong_LDG_address_validCRC','extra_raw','wrong_stats_count','wrong_exit_function_handle','unknown_input_API','output_bytecount_wrong','truncated_input_capsule']
receipts=[]
for name in cases:
 D=N/name;D.mkdir();(D/'attempts/pair_A3_v1').mkdir(parents=True);T=D/'attempts/pair_A3_v1/trace'
 shutil.copytree(R/'attempts/pair_A3_v1/trace',T)
 shutil.copytree(R/'control',D/'control');shutil.copytree(R/'CPU_TOP5_trace_A3',D/'CPU_TOP5_trace_A3')
 Q=T/'traces';blob=Q/'nn-output-1.bin';out=Q/'ada-nn-output.tsv';args=Q/'ada-nn-kernel-args.tsv'
 if name.startswith(('nan_output','wrong_finite')):
  b=bytearray(blob.read_bytes());import struct
  b[800:804]=struct.pack('<f',float('nan')if name.startswith('nan')else 999.0);blob.write_bytes(b)
  words=out.read_text().strip().split('\t');words[7]=h(blob);out.write_text('\t'.join(words)+'\n')
 elif name.startswith('forged_output'):
  words=out.read_text().strip().split('\t');words[4]=format(int(words[4],16)+4,'x');out.write_text('\t'.join(words)+'\n')
  words=args.read_text().strip().split('\t');words[4]=format(int(words[4],16)+4,'x');args.write_text('\t'.join(words)+'\n')
 elif name.startswith(('wrong_STG','wrong_LDG')):
  raw=next(Q.glob('kernel*.trace.xz'));lines=lzma.open(raw,'rt').readlines();done=False
  for k,line in enumerate(lines):
   if (' STG.E 'if name.startswith('wrong_STG')else' LDG.E ')not in line:continue
   t=line.split();i=6;nd=int(t[i]);i+=1+nd;i+=1;ns=int(t[i]);i+=1+ns;i+=2
   t[i]=hex(int(t[i],16)+4);lines[k]=' '.join(t)+'\n';done=True;break
  assert done
  with lzma.open(raw,'wt')as f:f.writelines(lines)
  rp=T/'FULL_RECORD_V8_WARPSYNC_VALIDATION.json';j=json.loads(rp.read_text());j['source_files']={raw.name:h(raw)};rp.write_text(json.dumps(j)+'\n')
 elif name=='extra_raw':shutil.copyfile(next(Q.glob('kernel*.trace.xz')),Q/'kernel-999-extra.trace.xz')
 elif name=='wrong_stats_count':
  q=next(Q.glob('stats_ctx*'));q.write_text(q.read_text().replace('41503,41503','41504,41504'))
 elif name=='wrong_exit_function_handle':
  q=Q/'ada-lifecycle.tsv';lines=q.read_text().splitlines();t=lines[2].split('\t');t[5]=format(int(t[5],16)+16,'x');lines[2]='\t'.join(t);q.write_text('\n'.join(lines)+'\n')
 elif name=='unknown_input_API':
  q=Q/'ada-input.tsv';q.write_text(q.read_text().replace('cuMemcpyHtoD_v2','UNSUPPORTED_FAKE_COPY'))
 elif name=='output_bytecount_wrong':
  t=out.read_text().strip().split('\t');t[6]='171055';out.write_text('\t'.join(t)+'\n')
 elif name=='truncated_input_capsule':
  q=Q/'inputs/copy_000001.bin';q.write_bytes(q.read_bytes()[:-4])
 v.R=D
 try:v.verify('trace');reason=None
 except Exception as e:reason=type(e).__name__+': '+str(e)
 assert reason,'negative missed '+name
 receipts.append(dict(name=name,rejected=True,reason=reason,fixture_root=str(D)))
v.R=R
(R/'CPU_FULL_JOIN_NEGATIVE_QUALIFICATION_V2.json').write_text(json.dumps({'schema':'NN_ACTUAL_PAIR_MUTATION_NEGATIVES_V2','verifier_sha256':h(p),'cases':receipts,'all_rejected':True,'actual_pair_unmodified':True,'no_GPU_or_SIM':True},indent=2)+'\n')
print(json.dumps(receipts))
