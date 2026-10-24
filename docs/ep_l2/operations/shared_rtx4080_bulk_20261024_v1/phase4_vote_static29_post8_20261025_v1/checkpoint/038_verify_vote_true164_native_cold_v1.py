import pathlib,json,hashlib,importlib.util,subprocess,lzma,re,collections,os
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');BASE=C.parent/'c8_vote_native_cold_v1';ID='C8_CUDA118_SIMPLEVOTE_DEFAULT_A001';R=BASE/'restore';W=BASE/'audit';assert not BASE.exists();W.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(p,name,h):
 assert sha(p)==h;s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
with(W/'PUBLIC_RESTORE.log').open('x')as f:p=subprocess.run(['/root/workspace/assets/bin/trace-assets-rtx4080','restore',ID,'--dest',str(R),'--max-bytes',str(16*2**20)],stdout=f,stderr=subprocess.STDOUT,timeout=300)
assert p.returncode==0
caps=module(R/'contract/qualify_input_capsule_v4.py','caps','7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388');handles=module(R/'tools/verify_c8_launch_handles_v1.py','handles','3506403600ce5d3ba450a5e8d72aa6a72fd7cf9fe5c1163b7029ec86bc5b32aa');parser=module(R/'contract/validate_v7.py','parse','f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b')
model=[(512,'f44453b2d61aeef3f143e47df5a59283d70b4926695c5d2385beba935b2d3037'),(288,'2d5565fb483d8ea4525a7a9229677d1038ad34b6e22c8d5152e1d7f7b9817597')];pairs=[]
for root,trace in[(R/'observer',False),(R,True)]:
 q=caps.qualify(root,512,800,trace);assert len(q['copies'])==2 and q['total_bytes']==800
 for i,(size,h)in enumerate(model,1):
  row=q['copies'][str(i)];assert row['bytes']==size and row['sha256']==h and sha(root/row['restorable_relative_path'])==h
 js=handles.verify(root/'traces/ada-lifecycle.tsv',3);assert len(js)==3
 for j,name in zip(js,['VoteAnyKernel1','VoteAllKernel2','VoteAnyKernel3']):assert name in j['function']
 stdout=(root/'stdout.log').read_text();assert len(re.findall(r'^\s*OK\s*$',stdout,re.M))==3
 commands=next((root/'traces').glob('kernelslist_ctx_*')).read_text().splitlines();kernels=[l for l in commands if l.startswith('kernel-')]
 if trace:assert len(commands)==5 and len(kernels)==3;order=[('copy',1),('kernel',0),('kernel',1),('copy',2),('kernel',2)]
 else:assert len(commands)==2 and not kernels;order=[('copy',1),('copy',2)]
 for line,(kind,index)in zip(commands,order):
  if kind=='kernel':assert line==kernels[index]
  else:
   fields=line.split(',');row=q['copies'][str(index)];assert fields[0]=='MemcpyHtoD'and int(fields[1],16)==int(row['device_destination'],16)and int(fields[2])==row['bytes']
 pairs.append(q)
assert pairs[0]['ordered_input_identity_sha256']==pairs[1]['ordered_input_identity_sha256']
original=R/'contract/validate_v7_snapshot_v2.py';assert sha(original)=='175943e30d6c89daa9d8ec65c526029a6d7d689c40567c73933a1b5ca53df2e8';source=original.read_text();needle="H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')";assert source.count(needle)==1
portable=W/'validate_snapshot_portable.py';portable.write_text(source.replace(needle,'H=pathlib.Path('+repr(str(R/'contract/validate_v7.py'))+')'));m=module(portable,'full',sha(portable));full=m.validate(R,R/'map/manifest.json');assert(full['kernels'],full['ctas'],full['warps'],full['counts']['sass_records'])==(3,3,11,153)
input_base=int(pairs[1]['copies']['1']['device_destination'],16);info_base=int(pairs[1]['copies']['2']['device_destination'],16);addresses=0;bytejoins=[];rawrecords={}
for ordinal,k in enumerate(full['per_kernel'],1):
 raw=R/'traces'/k['name'];group=raw.with_name(raw.name.replace('.trace.xz','.traceg.xz'));seen_load=set();seen_store=set();outbase=None;instructions=collections.defaultdict(list)
 with lzma.open(raw,'rt')as f:
  for line in f:
   if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
   fields=line.split(maxsplit=4);cta=tuple(map(int,fields[:3]));warp=int(fields[3]);assert cta==(0,0,0);instructions[(cta,warp)].append(fields[4]);q=parser.parse(fields[4])
   if not q['width']:continue
   for lane,addr in q['addrs'].items():
    tid=warp*32+lane;addresses+=1
    if ordinal<=2:
     assert q['width']==4 and tid<128
     if q['opcode'].startswith('LDG'):assert addr==input_base+4*tid and tid not in seen_load;seen_load.add(tid)
     elif q['opcode'].startswith('STG'):
      base=addr-4*tid
      if outbase is None:outbase=base
      assert base==outbase and tid not in seen_store;seen_store.add(tid)
     else:raise ValueError('unexpected explicit memory')
    else:
     assert q['width']==1 and q['opcode'].startswith('STG')and tid<96
     delta=addr-info_base;assert delta//3==tid and delta not in seen_store;seen_store.add(delta)
 if ordinal<=2:assert seen_load==seen_store==set(range(128))and(outbase+512<=input_base or input_base+512<=outbase)
 else:assert not seen_load and seen_store=={3*t+i for t in range(96)for i in [0,1]}|{3*t+2 for t in range(64,96)}
 seen=set();remaining=0;pos=0;cta=None;warp=None;count=0
 with lzma.open(group,'rt')as f:
  for line in f:
   if line.startswith('thread block = '):cta=tuple(map(int,re.findall(r'\d+',line)))
   elif line.startswith('warp = '):warp=int(line.split('=',1)[1]);assert(cta,warp)not in seen;seen.add((cta,warp));pos=0
   elif line.startswith('insts = '):remaining=int(line.split('=',1)[1]);assert remaining==len(instructions[(cta,warp)])
   elif remaining:assert line==instructions[(cta,warp)][pos];pos+=1;remaining-=1;count+=1
 assert remaining==0 and seen==set(instructions);bytejoins.append({'kernel':k['name'],'warps':len(seen),'records':count,'every_instruction_line_byte_equal':True})
assert addresses==736
report={'status':'TRUE164_PUBLIC_NATIVE_COLD_VOTE_FULL153_CAPS_MODEL_HANDLES_COMMANDS_ADDRESSES_GROUP_PASS','asset_id':ID,'full_record':full,'capsule_pair_identity':'MATCH','ordered_input_sha256':pairs[1]['ordered_input_identity_sha256'],'exact_model_copy_bytes':[512,288],'handle_joins':3,'instrumented_commandlist_order':'copy1,k1,k2,copy2,k3 directly observed','observer_order_scope':'Two copy commands plus three handle joins; cross-log interleaving only original sequential host-source rule','global_lane_addresses_all_joined':736,'third_kernel_zero_initialized_output_store_indices':224,'raw_group_byte_joins':bytejoins,'source_QA':'First2 group-sum checks and thirdall288bool source reference; no independently saved DtoH arrays, consumer or timing grant','input_allocations_may_be_reused_across_tests':'No cross-lifetime nonoverlap inference; per-kernel input/output scopes checked','portable_original_sha256':sha(original),'portable_executed_sha256':sha(portable),'source_KEEP':True,'GPU_or_SIM_runs':0,'new_full_source_coverage_increment':1}
with(C/'C8_VOTE_TRUE164_NATIVE_COLD_READBACK_V1.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'status':report['status'],'proof_sha256':sha(C/'C8_VOTE_TRUE164_NATIVE_COLD_READBACK_V1.json')}))
