#!/usr/bin/env python3
"""Audit immutable SpMV with real frozen CPU parser; never admits an ISA."""
import collections,csv,hashlib,json,lzma,pathlib,re,subprocess
repo=pathlib.Path(__file__).resolve().parents[3];root=pathlib.Path('/data/c16/dtc_sm89_admission_feasibility_109_v1');pack=repo/'docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1';producer=pathlib.Path('/data/c16/dtc_native_coverage_109_v1');pin='18a68dcccd795f1b6cda75504e9450d00c9cee02'
def blob(ref,p):return subprocess.check_output(['git','show',ref+':'+p],cwd=repo)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(n,x):(pack/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
index=json.loads(blob('890fb0be7e681a60419c49ca0a7aa85731d8c164','docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/RAW_PAYLOAD_INDEX.json'));index={x['relative_path']:x for x in index}
consumer=json.loads(blob('e3dbe3dbf2abb49b923244538d2a3d1828024d4f','docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/producer109_v1/SPMV_TRACE_OPCODE_AUDIT_V1.json'))
source=blob(pin,'gpu-simulator/trace-driven/trace_driven.cc').decode();mapping={r:(o,c) for r,o,c in re.findall(r'\{"([A-Z0-9]+)", OpcodeChar\((OP_\w+), (\w+)\)\}',blob(pin,'gpu-simulator/ISA_Def/ampere_opcode.h').decode())}
c16=json.loads(blob('2fa207fbc37a48f12641d810319b03ba1cf4e381','docs/vm_tlb/review_packs/C16_E1_TRACE_ADDRESS_NAMESPACE_INTEGRATION_174NEW_V1/SM89_TO_AMPERE_FULL_BUNDLE_OPCODE_AUDIT.json'))
sass=producer/'raw/spmv.sass';assert sha(sass)==index['raw/spmv.sass']['sha256'];static={int(pc,16):t.strip() for pc,t in re.findall(r'/\*([0-9a-f]+)\*/\s+(.+?);',sass.read_text())}
coverage=collections.defaultdict(lambda:dict(records=0,active_threads=0,masks=set(),dest_shapes=set(),src_shapes=set(),widths=set(),pcs=set(),addr_modes=set(),sample=''))
receipt={'status':'CPU_PARSE_PASS_WITH_CONFIRMED_SEMANTIC_GAPS_NOT_ADMISSION','gpu_lock_requested':False,'native_restarted':False,'simulator_run':False,'header_modified':False,'producer':'890fb0be7e681a60419c49ca0a7aa85731d8c164','framework':pin,'kernels':[],'checks':[]};witnesses=[];allrecords=[]

def parse_line(s):
 tok=s.split();pc=int(tok[0],16);mask=int(tok[1],16);nd=int(tok[2]);assert 0<=nd<=1;dest=tok[3:3+nd];op=tok[3+nd];ns=int(tok[4+nd]);assert 0<=ns<=4;src=tok[5+nd:5+nd+ns];p=5+nd+ns;width=int(tok[p]);p+=1;addr={};mode=None
 if width:
  mode=int(tok[p]);p+=1;active=[x for x in range(32) if mask&(1<<x)]
  if mode==0:
   for lane in active:addr[lane]=int(tok[p],16);p+=1
  elif mode==1:
   base=int(tok[p],16);stride=int(tok[p+1]);p+=2
   for j,lane in enumerate(active):addr[lane]=base+j*stride
  elif mode==2:
   base=int(tok[p],16);p+=1
   for j,lane in enumerate(active):
    if j:base+=int(tok[p]);p+=1
    addr[lane]=base
  else:raise ValueError('unsupported compression')
 imm=int(tok[p])&((1<<64)-1);p+=1;assert p==len(tok),'unconsumed/truncated record'
 return dict(pc=pc,mask=mask,dest=dest,src=src,op=op,width=width,mode=mode,addr=addr,imm=imm,line=s)

members=sorted((producer/'traces_env_ready/SpMV/traces').glob('*.traceg.xz'))
assert len(members)==4
for order,path in enumerate(members):
 rel=str(path.relative_to(producer));assert sha(path)==index[rel]['sha256']==consumer['kernels'][order]['sha256'];header={};parsed=[];tb=None;warp=None;declared=None;seen=0;blocks=set();warps=set();pending={}
 for line in lzma.open(path,'rt'):
  s=line.strip()
  if s.startswith('-') and '=' in s:k,v=s[1:].split('=',1);header[k.strip()]=v.strip()
  elif s.startswith('thread block ='):tb=s.split('=')[1].strip();blocks.add(tb)
  elif s.startswith('warp ='):
   if declared is not None:assert seen==declared and parsed[-1]['op']=='EXIT'
   warp=int(s.split('=')[1]);assert (tb,warp) not in warps;warps.add((tb,warp));seen=0;declared=None;pending={}
  elif s.startswith('insts ='):declared=int(s.split('=')[1])
  elif re.match(r'^[0-9a-f]+ [0-9a-f]{8} ',s):
   r=parse_line(s);r.update(tb=tb,warp=warp);parsed.append(r);seen+=1;c=coverage[r['op']];c['records']+=1;c['active_threads']+=r['mask'].bit_count();c['masks'].add(f'{r["mask"]:08x}');c['dest_shapes'].add(','.join(r['dest']) or 'NONE');c['src_shapes'].add(','.join(r['src']) or 'NONE');c['widths'].add(r['width']);c['pcs'].add(r['pc']);c['sample']=c['sample'] or s
   if r['mode'] is not None:c['addr_modes'].add(r['mode'])
   if r['pc'] in [0x310,0x320] and r['op']=='LDC.64':pending[17 if r['pc']==0x310 else 3]=r
   if r['pc'] in [0x360,0x410]:
    high=17 if r['pc']==0x360 else 3
    if high in pending and 'R'+str(high) in r['src']:
     load=pending[high];witnesses.append(dict(kernel=order,tb=tb,warp=warp,load_pc=hex(load['pc']),consumer_pc=hex(r['pc']),missing_high_register='R'+str(high),captured_destinations=load['dest'],consumer_sources=r['src'],static_load=static[load['pc']],static_consumer=static[r['pc']],load_trace=load['line'],consumer_trace=r['line'],observation='frozen decoder forwards only captured destinations; no expansion for LDC.64'))
 assert seen==declared and parsed[-1]['op']=='EXIT' and header['binary version']=='89' and header['accelsim tracer version']=='5' and len(blocks)==len(warps)==36
 inp='\n'.join(x['line'] for x in parsed)+'\n';cp=subprocess.run([str(root/'build/parser_probe')],input=inp,text=True,capture_output=True,check=True);outputs=cp.stdout.splitlines();assert len(outputs)==len(parsed)
 for r,line in zip(parsed,outputs):
  pc,mask,op,ds,ss,width,addr,imm,converted_ds,converted_ss=line.split('\t');assert (int(pc),int(mask),op,int(width),int(imm))==(r['pc'],r['mask'],r['op'],r['width'],r['imm']), (r['line'],line)
  assert ds==','.join('0:'+x[1:] for x in r['dest']) and ss==','.join('0:'+x[1:] for x in r['src'])
  got={int(t.split(':')[0]):int(t.split(':')[1]) for t in addr.split(',') if t};assert got==r['addr']
  assert converted_ds==','.join(str(int(x[1:])+1) for x in r['dest']) and converted_ss==','.join(str(int(x[1:])+1) for x in r['src'])
 (root/'raw'/f'PARSER_KERNEL_{order}.tsv').write_text(cp.stdout)
 active=sum(r['mask'].bit_count() for r in parsed);assert active==88314
 receipt['kernels'].append(dict(order=order,path=str(path),sha256=sha(path),header_binary=89,tracer=5,CTAs=36,warps=36,records=len(parsed),active_thread_instructions=active,real_frozen_parser='PASS_PC_MASK_OPCODE_REGS_WIDTH_ACTIVE_ADDRESSES_IMMEDIATE',semantic_admission='HOLD'))
 allrecords.extend(parsed)
assert len(allrecords)==11708 and sum(x['active_thread_instructions'] for x in receipt['kernels'])==353256
checklist=['FOUR_IMMUTABLE_PRODUCER_AND_CONSUMER_HASHES_MATCH','HEADER89_AND_TRACER5_PRESERVED','ALL_CTAS_WARPS_DECLARED_RECORD_COUNTS','11708_RECORDS_353256_ACTIVE_THREAD_INSTRUCTIONS','REAL_FROZEN_PARSER_FIELDS_MATCH_INDEPENDENT_DECOMPRESSOR','NO_NATIVE_NO_GPU_LOCK_NO_SIMULATOR','ALL_WARPS_TERMINAL_EXIT']
assert witnesses
# Existing classifier facts; no new Ada category is invented.
rows=[]
for op,c in sorted(coverage.items()):
 base=op.split('.')[0];enum,cat=mapping[base];notes=[]
 if base=='LDC':notes=['constant address absent in trace','LDC.64 width/destination pair not modeled: current decoder data_size=4, one captured destination']
 elif base=='ULDC':notes=['uniform destination/constant dependency omitted in producer; current class uniform ALU, no constant-memory request']
 elif base=='IMAD' and 'WIDE' in op:notes=['64-bit output pair and constant input not fully explicit; captured base GPR only']
 elif base=='ISETP':notes=['predicate destination absent; dynamic active mask present, predicate scoreboard not modeled']
 elif base in ['BSSY','BSYNC','BRA']:notes=['dynamic sequence/mask supplied; convergence barrier/predicate state not reconstructed; existing branch-unit timing remains modeling decision']
 elif base in ['LDG','STG']:notes=['recorded 4-byte global addresses preserved; 64-bit address/uniform dependencies only partially represented; cache interpretation not hardware timing calibration']
 elif op=='FFMA.FTZ':notes=['arithmetic results not re-executed; FTZ spelling not in prior full-spelling C16 audit; SP timing inherited, not Ada calibration']
 else:notes=['captured vector GPR dependencies only; static constant/system/zero operands not reconstructed as dependencies']
 timing='int latency/init config' if cat in ['ALU_OP','INTP_OP'] else 'SP latency/init config' if cat=='SP_OP' else 'specialized unit 1 latency/init' if cat=='SPECIALIZED_UNIT_1_OP' else 'specialized unit 4 latency/init' if cat=='SPECIALIZED_UNIT_4_OP' else 'default initial latency/init=1 plus memory hierarchy' if cat in ['LOAD_OP','STORE_OP'] else 'default initial latency/init=1'
 rows.append(dict(opcode=op,root=base,warp_records_all4=c['records'],active_thread_instructions_all4=c['active_threads'],PCs=','.join(hex(x) for x in sorted(c['pcs'])),observed_masks=','.join(sorted(c['masks'])),captured_dest_shapes=';'.join(sorted(c['dest_shapes'])),captured_src_shapes=';'.join(sorted(c['src_shapes'])),trace_memory_widths=','.join(map(str,sorted(c['widths']))),compression_modes=','.join(map(str,sorted(c['addr_modes']))),frozen_opcode_enum=enum,frozen_category=cat,existing_C16_exact_spelling=op in c16['opcode_counts'],dynamic_decided='PC/order/active mask; recorded global lane addresses',remaining_interpretation='; '.join(notes),timing_source=timing,support='CLASSIFIER_FACT_ONLY_NOT_SM89_ADMISSION',sample_record=c['sample']))
with (pack/'OPCODE_COVERAGE.tsv').open('w') as f:w=csv.DictWriter(f,list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
dump('PAIR_DEPENDENCY_WITNESSES.json',dict(witness_count=len(witnesses),counts_by_kernel=dict(collections.Counter(str(w['kernel']) for w in witnesses)),counts_by_high_register=dict(collections.Counter(w['missing_high_register'] for w in witnesses)),examples=[next(w for w in witnesses if w['kernel']==k and w['missing_high_register']==r) for k in range(4) for r in ['R17','R3']],scope='SASS/liveness and captured record gap; no data repair or performance prediction'))
# Read-only negative fixtures exercise the audit, not producer files.
rejected=[]
for label,line in [('TRUNCATED','0000 ffffffff 1 R2 LDG.E 1 R4 4 1 0x1000'),('UNKNOWN_COMPRESSION','0000 ffffffff 1 R2 LDG.E 1 R4 4 9 0x1000 0'),('TRAILING_GARBAGE','0000 ffffffff 0 EXIT 0 0 0 garbage')]:
 try:parse_line(line)
 except (AssertionError,ValueError,IndexError):rejected.append(label)
assert len(rejected)==3
# Negative unsupported-opcode guard rejects a synthetic string, not an edited trace.
def exact_spelling_guard(op):
 if op not in coverage:raise ValueError('not in immutable observed SpMV full-opcode set')
for r in allrecords:exact_spelling_guard(r['op'])
try:exact_spelling_guard('LDG.NOT_OBSERVED')
except ValueError:rejected.append('UNREGISTERED_FULL_OPCODE')
assert len(rejected)==4
receipt['negative_fixtures_rejected']=rejected
# Frozen register-conversion behavior: typed synthetic fields, no trace mutation.
fixture='0000 ffffffff 1 UR4 ULDC.64 0 0 0\n0010 ffffffff 1 P0 ISETP.GE.AND 1 R2 0 0\n0020 ffffffff 1 R16 LDC.64 0 0 0\n'
f=subprocess.run([str(root/'build/parser_probe')],input=fixture,text=True,capture_output=True,check=True).stdout;(root/'raw/TYPED_DEPENDENCY_FIXTURES.tsv').write_text(f);ls=[x.split('\t') for x in f.splitlines()];assert [x[8] for x in ls]==['0','0','17'];assert all(x[5]=='0' for x in ls)
receipt['typed_conversion_probe']='UR/P become dependency0; captured R16 becomes17 only; LDC.64 remains memadd_info=null'
results=[]
for exe in ['dispatch_original','dispatch_fail_closed']:
 for version in [35,60,61,70,75,80,86,89,90,999]:
  p=subprocess.run([str(root/'build'/exe),str(version)],text=True,capture_output=True);unsupported=version in [89,999];assert p.returncode==(1 if unsupported and exe=='dispatch_fail_closed' else 0);assert ('CPU_DISPATCH_SENTINEL_ONLY' in p.stdout)==(not unsupported);results.append(dict(probe=exe,binary_version=version,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,interpretation='CPU_CONTROL_FLOW_ONLY_NO_SIMULATOR_EXECUTION'))
dump('DISPATCH_FAIL_CLOSED_TESTS.json',results);receipt['checks']=checklist+['STATIC_SASS_BOUND_TO_EXISTING_BINARY','LDC64_HIGH_REGISTER_CONSUMERS_CONFIRMED','FOUR_NEGATIVE_FIXTURES_REJECTED','TYPED_REGULAR_ONLY_DEPENDENCY_CONVERSION_CONFIRMED','20_DISPATCH_CONTROL_FLOW_TESTS','ORIGINAL89_EXIT0_IS_REJECTION_PATCHED89_EXIT1_IS_REJECTION'];receipt['pair_dependency_witnesses']=len(witnesses);receipt['opcode_spellings']=len(rows);receipt['new_vs_C16_exact_spellings']=[x['opcode'] for x in rows if not x['existing_C16_exact_spelling']];dump('CPU_TEST_RECEIPTS.json',receipt)
print(json.dumps({k:v for k,v in receipt.items() if k!='kernels'},indent=2))
