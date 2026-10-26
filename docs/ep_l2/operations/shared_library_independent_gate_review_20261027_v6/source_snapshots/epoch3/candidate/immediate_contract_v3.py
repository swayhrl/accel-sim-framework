"""Exact ELF-owner/SASS typed-immediate gate; no generic ISA qualification."""
import pathlib,json,re,hashlib,struct
HERE=pathlib.Path(__file__).resolve().parent
PROFILE='SDK42_SIMPLETEMPLATES_EPOCH8_EXACT_V3'
MAP_SHA='242f6693ddfcbd0f4b4059671e322507e48c5520d835ed070c61f83f699842cc'
JSON_SHA='1eaa19a1f4c8db43fe2917a3b8f3002fcf9401119462151652e3bb902c74b29f'
ELF_SHA='ddb91dbf3f9d364fad64c398253b10e4312fba96ba7d53a2fbd31fb9af4dd551'
NVBIT_SHA='a83cd69d1bb6b1331885547dd3743b4b1d8e978b1a73e6d4485cc11225861789'
CONTRACT_SHA='64078f25123e2d9fa145289199880a4072aa757b9e5dd4aad5e527401fcf004b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,msg):
 if not x:raise ValueError(msg)
def canonical(x):return re.sub(r'[\s;,]','',x)
SHAPES={'MOV':[('REG','CBANK'),('REG','IMM_UINT64')],'S2R':[('REG','GENERIC_SR_TID_X')],'ULDC.64':[('UREG','CBANK')],'IMAD.WIDE.U32':[('REG','REG','REG','CBANK')],'LDG.E':[('REG','MREF')],'STG.E':[('MREF','REG')],'STS':[('MREF','REG')],'LDS':[('REG','MREF')],'IMAD':[('REG','REG','CBANK','REG')],'I2FP.F32.U32':[('REG','CBANK')],'FMUL':[('REG','REG','REG')],'BAR.SYNC':[('IMM_UINT64',)],'EXIT':[()],'BRA':[('BRANCH_TARGET',)],'NOP':[()]}
def typed(sass):
 op,*tail=sass.strip().rstrip(';').split(maxsplit=1)
 need(op in SHAPES,'opcode outside exact typed contract')
 # Commas are separators only outside balanced memory/CBANK brackets.
 operands=[];depth=0;start=0;t=tail[0] if tail else ''
 for i,c in enumerate(t):
  if c=='[':depth+=1
  if c==']':depth-=1;need(depth>=0,'unbalanced operand')
  if c==',' and depth==0:operands.append(t[start:i].strip());start=i+1
 need(depth==0,'unbalanced operand')
 if t:operands.append(t[start:].strip())
 out=[]
 for token in operands:
  if re.fullmatch(r'R(?:[0-9]+|Z)',token):kind='REG';value=None
  elif re.fullmatch(r'UR[0-9]+',token):kind='UREG';value=None
  elif re.fullmatch(r'c\[0x[0-9a-f]+\]\[0x[0-9a-f]+\]',token):kind='CBANK';value=None
  elif re.fullmatch(r'\[R[0-9]+\.(?:64|X4)\]',token):kind='MREF';value=None
  elif token=='SR_TID.X':kind='GENERIC_SR_TID_X';value=None
  elif re.fullmatch(r'0x[0-9a-f]+|0|[1-9][0-9]*',token):
   value=int(token,16 if token.startswith('0x') else 10);need(value<2**64,'uint64')
   kind='BRANCH_TARGET' if op=='BRA' else 'IMM_UINT64'
  else:raise ValueError('unsupported symbolic/float/signed/modified operand '+token)
  out.append(dict(kind=kind,text=token,value=value))
 kinds=tuple(x['kind'] for x in out);need(kinds in SHAPES[op],'operand-kind shape outside exact contract')
 values=[x['value'] for x in out if x['kind']=='IMM_UINT64'];need(len(values)<=1,'multiple immediate outside exact contract')
 return dict(opcode=op,ordered_operands=out,selected_immediate=values[-1] if values else 0,raw_eligible=op not in ('BRA','NOP'),extraction='last decoded IMM_UINT64; default0; CBANK/MREF/generic never selected')
def derive(base):
 base=pathlib.Path(base);mf=base/'preimages/map/manifest.json';jf=base/'preimages/map/simpleTemplates.sm_89.cubin.disasm.json';elf=base/'preimages/map/simpleTemplates.sm_89.cubin';nv=base/'preimages/nvbit/instr_types.h'
 need(sha(mf)==MAP_SHA and sha(jf)==JSON_SHA and sha(elf)==ELF_SHA and sha(nv)==NVBIT_SHA,'immutable immediate proof pins')
 producer_source_sha=sha(base/'candidate/tracer_tool.cu');inject_source_sha=sha(base/'candidate/inject_funcs.cu')
 need(producer_source_sha=='98cb40818b7e4c1b0188212cdf956667f3bc64b974636a64ce4ede33ff8d062f' and inject_source_sha=='856cb94ae8216c280aefef8ac5ef2c14501a09ae4e777f2518eaccb67a77eb48','unchanged typed producer extraction provenance')
 m=json.loads(mf.read_text());need(m['binary_sha256']=='24e15a483e3d1d8ec70dcdd6f8c601189148ee476db93e47c06e1162c1b55e47','binary identity')
 source={(x['function'],x['pc']):x for x in m['instructions']}
 eb=elf.read_bytes();need(eb[:6]==b'\x7fELF\x02\x01','ELF64 little-endian')
 shoff=struct.unpack_from('<Q',eb,40)[0];shsize,shnum,shstr=struct.unpack_from('<HHH',eb,58)
 headers=[struct.unpack_from('<IIQQQQIIQQ',eb,shoff+i*shsize) for i in range(shnum)]
 ss=headers[shstr];strings=eb[ss[4]:ss[4]+ss[5]];sections={}
 for sh in headers:
  name=strings[sh[0]:].split(b'\0',1)[0].decode()
  if name.startswith('.text.'):
   need(name not in sections,'ambiguous ELF owner');sections[name]=dict(file_offset=sh[4],bytes=sh[5],instruction_slots=sh[5]//16)
 need(len(sections)==2,'exact ELF owner universe')
 funcs=json.loads(jf.read_text())[1];need(len(funcs)==2,'exact two functions')
 rows=[]
 for f in funcs:
  need(f['start']==0 and f['length']==512 and len(f['sass-instructions'])==32 and sections['.text.'+f['function-name']]['bytes']==f['length'],'function ELF section owner and all64 slots')
  for index,j in enumerate(f['sass-instructions']):
   pc=index*16;r=source.get((f['function-name'],pc));sass=r['sass'] if r else 'NOP'
   need((r is not None) or j['opcode']=='NOP','unmapped nonNOP')
   need(canonical(sass)==canonical(j['opcode']+' '+j.get('operands','')),'JSON/fullSASS owner+PC join')
   row=dict(function=f['function-name'],pc=pc,sass=sass,semantic_mapped=r is not None,**typed(sass));rows.append(row)
 need(len(rows)==64 and sum(x['semantic_mapped'] for x in rows)==35,'complete static scope')
 return dict(schema='EPOCH8_EXACT_TYPED_IMMEDIATE_CONTRACT_V3',profile=PROFILE,binary_sha256=m['binary_sha256'],map_sha256=MAP_SHA,nvdisasm_json_sha256=JSON_SHA,cubin_sha256=ELF_SHA,nvbit_instr_types_sha256=NVBIT_SHA,producer_sha256='8b12d11ae2d8d176011d682b803e80e283afc1aa6365933e991c6cb9db7b53b8',producer_source_sha256=producer_source_sha,inject_source_sha256=inject_source_sha,actual_NVBit_operand_types_dynamic_proof=False,raw_branch_or_padding_qualified=False,ELF_owner_sections=sections,rows=rows)
def load_contract():
 p=HERE/'STATIC_IMMEDIATE_CONTRACT_V3.json';need(sha(p)==CONTRACT_SHA,'typed contract pin')
 value=json.loads(p.read_text());need(value==derive(HERE.parent),'independent full static contract derivation mismatch')
 return {(x['function'],x['pc']):x for x in value['rows']}
def check(table,function,row,record):
 x=table[(function,record['pc'])]
 need(x['raw_eligible'] and canonical(x['sass'])==canonical(row['sass']),'raw typed owner/PC/fullSASS/eligibility')
 need(record['imm']==x['selected_immediate'],'raw immediate differs from exact typed static extraction')
