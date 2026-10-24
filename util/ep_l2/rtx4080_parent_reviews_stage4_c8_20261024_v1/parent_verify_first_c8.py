import pathlib,json,hashlib,importlib.util,lzma,re,struct,math,collections
C=pathlib.Path('/root/data/shared_sm70_trace_library_20261024_v1/control');R=pathlib.Path('/root/data/rtx4080_c8_parent_native_restore_20261024_v1');W=C.parent/'parent_first_c8_science_audit_v1';W.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(p,name,expected):
 assert sha(p)==expected
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
caps=module(R/'contract/qualify_input_capsule_v4.py','caps','7d00cf3524389ec5f9bfd28ec931cd9c88c45b3deaa4fb9ea0368c7cc0b58388')
handle=module(R/'tools/verify_c8_launch_handles_v1.py','handles','3506403600ce5d3ba450a5e8d72aa6a72fd7cf9fe5c1163b7029ec86bc5b32aa')
parser=module(R/'contract/validate_v7.py','parser','f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b')
qual=[]
for root,trace in [(R/'observer',False),(R,True)]:
 q=caps.qualify(root,200000,400000,trace);assert q['status']=='OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_CLOSED_SHA_QUALIFIED'and q['total_bytes']==400000 and len(q['copies'])==2
 assert all(c['bytes']==200000 and c['api']in ['cuMemcpyHtoD_v2','cuMemcpyHtoD_v2_ptds']for c in q['copies'].values())
 for c in q['copies'].values():
  assert all(math.isfinite(v[0])and 0<=v[0]<=1 for v in struct.iter_unpack('<f',(root/c['restorable_relative_path']).read_bytes()))
 j=handle.verify(root/'traces/ada-lifecycle.tsv',1);assert len(j)==1 and 'vectorAdd'in j[0]['function']
 assert 'Test PASSED'in(root/'stdout.log').read_text()
 qual.append({'root':str(root),'capsule':q,'handle_joins':j})
assert qual[0]['capsule']['ordered_input_identity_sha256']==qual[1]['capsule']['ordered_input_identity_sha256']
original=R/'contract/validate_v7_snapshot_v2.py';assert sha(original)=='175943e30d6c89daa9d8ec65c526029a6d7d689c40567c73933a1b5ca53df2e8'
src=original.read_text();needle="H=pathlib.Path('/data/c16/ada_trace_semantics_20261024_v1/frozen/ada7_contract_v1/validate_v7.py')";assert src.count(needle)==1
portable=W/'validate_v7_snapshot_portable.py';portable.write_text(src.replace(needle,'H=pathlib.Path('+repr(str(R/'contract/validate_v7.py'))+')'))
s=importlib.util.spec_from_file_location('portable',portable);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);full=m.validate(R,R/'map/manifest.json')
assert full['kernels']==1 and full['ctas']==196 and full['warps']==1568 and full['counts']['sass_records']==26601
# Independently join actual HtoD destination bases to every executed global lane address.
bases=[int(c['device_destination'],16)for c in qual[1]['capsule']['copies'].values()];assert len(set(bases))==2
loads={b:set()for b in bases};stores=set();Cbase=None;pcbases={};rawdict=collections.defaultdict(list)
raw=next((R/'traces').glob('*.trace.xz'));group=next((R/'traces').glob('*.traceg.xz'))
with lzma.open(raw,'rt')as f:
 for line in f:
  if not re.match(r'^\d+ \d+ \d+ \d+ ',line):continue
  toks=line.split(maxsplit=4);cta=tuple(map(int,toks[:3]));warp=int(toks[3]);rawdict[(cta,warp)].append(toks[4])
  q=parser.parse(toks[4])
  if not q['width']:continue
  assert q['width']==4 and cta[1:]==(0,0)
  for lane,addr in q['addrs'].items():
   i=cta[0]*256+warp*32+lane;assert 0<=i<50000
   base=addr-4*i
   if q['opcode'].startswith('LDG'):
    assert base in loads and i not in loads[base];loads[base].add(i);pcbases.setdefault(q['pc'],base);assert pcbases[q['pc']]==base
   elif q['opcode'].startswith('STG'):
    if Cbase is None:Cbase=base
    assert base==Cbase and i not in stores;stores.add(i)
   else:raise ValueError('unexpected memory op')
assert all(len(v)==50000 for v in loads.values())and len(stores)==50000
ranges=sorted((b,b+200000)for b in bases+[Cbase]);assert all(ranges[i][1]<=ranges[i+1][0]for i in range(2))
# Grouped records must preserve complete source warp instruction bytes, not only CRC/counts.
seen=set();cta=None;warp=None;remaining=0;records=0;tb=0;declared=None
with lzma.open(group,'rt')as f:
 for line in f:
  if line.startswith('thread block = '):cta=tuple(map(int,re.findall(r'\d+',line)));tb+=1
  elif line.startswith('warp = '):warp=int(line.split('=',1)[1]);assert(cta,warp)not in seen;seen.add((cta,warp));records=0
  elif line.startswith('insts = '):remaining=int(line.split('=',1)[1]);declared=remaining
  elif remaining:
   assert line==rawdict[(cta,warp)][records];records+=1;remaining-=1
   if remaining==0:assert records==len(rawdict[(cta,warp)])==declared
assert not remaining and tb==196 and seen==set(rawdict)
out={'status':'FIRST_C8_TRUE164_RESTORE_CAPS_HANDLE_FULLBODY_ADDRESS_GROUP_ALL_PASS','restore_root':str(R),'capsule_and_handle':qual,'observer_trace_input_identity':'MATCH','ordered_input_sha256':qual[1]['capsule']['ordered_input_identity_sha256'],'full_record':full,'portable_helper_original_sha256':sha(original),'portable_helper_executed_sha256':sha(portable),'portable_change':'Only frozen parser absolute path, sourcef4 SHA enforced','every_global_lane_address_join':{'two_HtoD_arrays':2,'elements_per_array':50000,'load_lane_addresses':100000,'store_lane_addresses':50000,'store_base_rule':'Observed contiguous output allocation base inferred from stores; not a device-state or output-value snapshot','no_input_output_overlap':True},'raw_grouped_complete_warp_byte_equality':{'ctas':196,'warps':1568,'records':26601},'numerical_scope':'Same-source fabs reportedpass only; actual input finite independently checked, output finite check not present. No consumer/timing grant','no_GPU_execution':True,'source_KEEP':True}
(C/'PARENT_FIRST_C8_NATIVE_COLD_REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'raw_records':26601,'loads':100000,'stores':50000,'SHA':sha(C/'PARENT_FIRST_C8_NATIVE_COLD_REVIEW.json')}))
