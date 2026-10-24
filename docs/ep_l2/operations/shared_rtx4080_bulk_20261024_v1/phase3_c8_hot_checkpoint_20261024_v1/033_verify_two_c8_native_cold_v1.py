import pathlib,json,hashlib,importlib.util,lzma,re,struct,math,subprocess,os,collections,time
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');BASE=C.parent/'c8_two_vector_native_cold_v1';assert not BASE.exists();BASE.mkdir()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def module(p,name,expected):
 assert sha(p)==expected
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
rows=[]
for N in [4000000,6000000]:
 ident=f'C8_SDK42_VECTOR_SIZE{N}_A001';R=BASE/ident;W=BASE/(ident+'_audit');W.mkdir()
 with(W/'PUBLIC_RESTORE.log').open('x')as f:p=subprocess.run(['/root/workspace/assets/bin/trace-assets-rtx4080','restore',ident,'--dest',str(R),'--max-bytes',str(256*2**20)],stdout=f,stderr=subprocess.STDOUT,timeout=900)
 assert p.returncode==0
 caps=module(R/'contract/qualify_input_capsule_v4.py','caps'+str(N),'7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388')
 handle=module(R/'tools/verify_c8_launch_handles_v1.py','handle'+str(N),'3506403600ce5d3ba450a5e8d72aa6a72fd7cf9fe5c1163b7029ec86bc5b32aa')
 parser=module(R/'contract/validate_v7.py','parser'+str(N),'f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b')
 pairs=[]
 for root,trace in [(R/'observer',False),(R,True)]:
  q=caps.qualify(root,N*4,N*8,trace);assert q['total_bytes']==N*8 and len(q['copies'])==2
  for cp in q['copies'].values():
   assert cp['bytes']==N*4 and cp['api']in ['cuMemcpyHtoD_v2','cuMemcpyHtoD_v2_ptds']
   with(root/cp['restorable_relative_path']).open('rb')as f:
    for b in iter(lambda:f.read(2**20),b''):assert all(math.isfinite(v[0])and 0<=v[0]<=1 for v in struct.iter_unpack('<f',b))
  h=handle.verify(root/'traces/ada-lifecycle.tsv',1);assert len(h)==1 and 'VecAdd'in h[0]['function']
  assert 'SDK42_HOST_ADAPTER_QA_PASSED'in(root/'stdout.log').read_text()
  pairs.append(q)
 assert pairs[0]['ordered_input_identity_sha256']==pairs[1]['ordered_input_identity_sha256']
 original=R/'contract/validate_v7_snapshot_v2.py';assert sha(original)=='175943e30d6c89daa9d8ec65c526029a6d7d689c40567c73933a1b5ca53df2e8'
 src=original.read_text();needle="H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')";assert src.count(needle)==1
 portable=W/'validate_snapshot_portable.py';portable.write_text(src.replace(needle,'H=pathlib.Path('+repr(str(R/'contract/validate_v7.py'))+')'))
 s=importlib.util.spec_from_file_location('full'+str(N),portable);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);full=m.validate(R,R/'map/manifest.json')
 assert full['kernels']==1 and full['ctas']==(N+255)//256 and full['warps']==((N+255)//256)*8
 bases=[int(cp['device_destination'],16)for cp in pairs[1]['copies'].values()];assert len(set(bases))==2
 seen={b:bytearray(N)for b in bases};written=bytearray(N);outbase=None;rawhash={};rawcounts=collections.Counter()
 with lzma.open(next((R/'traces').glob('*.trace.xz')),'rt')as f:
  for line in f:
   if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
   toks=line.split(maxsplit=4);cta=tuple(map(int,toks[:3]));warp=int(toks[3]);key=(cta,warp);rawhash.setdefault(key,hashlib.sha256()).update(toks[4].encode());rawcounts[key]+=1
   q=parser.parse(toks[4])
   if not q['width']:continue
   assert q['width']==4 and cta[1:]==(0,0)
   for lane,addr in q['addrs'].items():
    i=cta[0]*256+warp*32+lane;assert 0<=i<N;base=addr-4*i
    if q['opcode'].startswith('LDG'):
     assert base in seen and not seen[base][i];seen[base][i]=1
    elif q['opcode'].startswith('STG'):
     if outbase is None:outbase=base
     assert base==outbase and not written[i];written[i]=1
    else:raise ValueError('unexpected memory domain')
 assert all(sum(v)==N for v in seen.values())and sum(written)==N
 ranges=sorted((b,b+N*4)for b in bases+[outbase]);assert all(ranges[i][1]<=ranges[i+1][0]for i in range(2))
 done=set();remaining=0;counter=0;tb=0;key=None;digest=None
 with lzma.open(next((R/'traces').glob('*.traceg.xz')),'rt')as f:
  for line in f:
   if line.startswith('thread block = '):cta=tuple(map(int,re.findall(r'\d+',line)));tb+=1
   elif line.startswith('warp = '):
    assert remaining==0;key=(cta,int(line.split('=',1)[1]));assert key not in done;done.add(key);digest=hashlib.sha256();counter=0
   elif line.startswith('insts = '):remaining=int(line.split('=',1)[1]);assert remaining==rawcounts[key]
   elif remaining:
    digest.update(line.encode());counter+=1;remaining-=1
    if remaining==0:assert counter==rawcounts[key]and digest.digest()==rawhash[key].digest()
 assert not remaining and tb==full['ctas']and done==set(rawhash)
 row={'id':ident,'status':'TRUE164_PUBLIC_BOUNDED_RESTORE_CAPS_HANDLE_FULLBODY_ADDRESS_GROUP_PASS','elements':N,'input_byte_identity':'MATCH','ordered_input_sha256':pairs[1]['ordered_input_identity_sha256'],'full_record':full,'raw_grouped_all_warp_instruction_byte_hashes_equal':True,'global_address_join':{'loads':N*2,'stores':N,'all_indices_exactly_once':True,'nonoverlap':True},'portable_helper_original_sha256':sha(original),'portable_helper_executed_sha256':sha(portable),'portable_change':'Frozen parser absolute path only','source_reported_fabs_QA_limitation':'No explicit output isfinite check; no output snapshot/consumer/timing grant','source_KEEP':True,'GPU_executions':0}
 with(W/'PROOF.json').open('x')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 rows.append({'id':ident,'status':row['status'],'proof':str(W/'PROOF.json'),'proof_sha256':sha(W/'PROOF.json')})
 with(C/'C8_TWO_VECTOR_NATIVE_COLD_READBACK_V1.json.tmp').open('w')as f:json.dump({'rows':rows},f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(C/'C8_TWO_VECTOR_NATIVE_COLD_READBACK_V1.json.tmp',C/'C8_TWO_VECTOR_NATIVE_COLD_READBACK_V1.json')
print(json.dumps(rows))
