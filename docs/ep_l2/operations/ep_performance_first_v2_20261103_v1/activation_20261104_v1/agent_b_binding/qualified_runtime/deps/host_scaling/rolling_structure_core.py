"""Bounded current-clock STRUCT scanner plus byte-identical frozen final math.
All raw bytes remain external/unchanged. This component does not grant acceptance.
"""
import ast,gzip,hashlib,importlib.util,json,pathlib,re
P=pathlib.Path
FROZEN_STRUCTURE=P(__file__).resolve().parent/'frozen_math/ft_lane5/parse_unified_terminal.py'
FROZEN_STRUCTURE_SHA='536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b'
FINAL_SUFFIX_SHA='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432'
KINDS=('BANK_PEAK','WB_QUOTA','CONFIG');EXPECTED={(k,s)for k in KINDS for s in range(64)}
class InvalidStructure(ValueError):pass
def need(ok,msg):
 if not ok:raise InvalidStructure(msg)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def open_raw(raw):
 p=P(getattr(raw,'p',raw));return gzip.open(p,'rb')if p.suffix=='.gz'else p.open('rb')
def frozen_final_math():
 need(sha(FROZEN_STRUCTURE)==FROZEN_STRUCTURE_SHA,'frozen structure source drift')
 text=FROZEN_STRUCTURE.read_text();node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='parse_structure');src=''.join(text.splitlines(keepends=True)[node.lineno-1:node.end_lineno]);suffix=src[src.index('    if set(records)!='):]
 need(hashlib.sha256(suffix.encode()).hexdigest()==FINAL_SUFFIX_SHA,'frozen final math suffix drift')
 ns={};exec(compile('def check(records,spec,final):\n'+suffix,'FROZEN_STRUCTURE_FINAL_SUFFIX','exec'),ns);return ns['check']

def validate_earlier(records,spec):
 # New explicit producer contract, stronger than the old final-only math:
 # every completedprintStats clock has64x3STRUCT rows. Early resourcesmaylive.
 need(set(records)==EXPECTED,'earlier STRUCT frame missing exact64x3 scope')
 f=spec['identity']['feature_vector'];need(not any(spec['identity'].get('ideal_vector',{}).values()),'ideal geometry not qualified by rolling contract')
 cap=f.get('nominal_payload_capacity_per_slice',f['payload_capacity_per_slice']);s64=f['static_s64'];ops=f['ops_per_bank_cycle']
 for sid in range(64):
  cfg=records['CONFIG',sid];bank=records['BANK_PEAK',sid];q=records['WB_QUOTA',sid]
  expected={'slice':sid,'static_s64':int(s64),'physical_slots':cap,'resident_nominal':1024,'bypass_capacity':80 if s64 else 128,'wb_begin':1104 if s64 else 1152,'static_wb_capacity':64 if s64 else 16,'legacy_wbuf':16,'bank_count':4,'bank_ops_per_physical_cycle':ops,'copy_latch_bytes':128}
  need(cfg==expected,'earlier STRUCT layout/config budget changed')
  need(bank['ops_per_physical_cycle']==ops and all(0<=bank['bank'+str(n)]<=ops for n in range(4)),'earlier STRUCT bank service budget exceeded')
  need(q['cap']==f['wb_local_cap'],'earlier STRUCT quota contract mismatch')
  if q['cap']:need(all(q[k]<=q['cap']for k in('reserved','live','total_peak','reserved_peak','live_peak')),'earlier STRUCT quota bound exceeded')

def scan_structure(raw,spec):
 records={};clock=None;frame_clock=None;closed_frames=0;unique=duplicates=structural=raw_lines=raw_bytes=clock_markers=0
 kinds={k:0 for k in KINDS};raw_hash=hashlib.sha256();wire_hash=hashlib.sha256();frame_chain=hashlib.sha256();first_clock=last_clock=None
 def close_current(early):
  nonlocal closed_frames,first_clock,last_clock
  need(frame_clock is not None,'STRUCT frame clock absent')
  if early:validate_earlier(records,spec)
  if first_clock is None:first_clock=frame_clock
  last_clock=frame_clock;closed_frames+=1
  frame_hash=hashlib.sha256()
  for key in sorted(records):frame_hash.update(canonical([key[0],key[1],records[key]])+b'\n')
  frame_chain.update(canonical({'frame_ordinal':closed_frames,'clock':frame_clock,'unique_rows':len(records),'canonical_frame_sha256':frame_hash.hexdigest()})+b'\n')
 with open_raw(raw)as f:
  for wire in f:
   raw_lines+=1;raw_bytes+=len(wire);raw_hash.update(wire)
   line=wire.decode('utf-8')
   match=re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*',line)
   if match:
    value=int(match[1]);clock_markers+=1;need(clock is None or value>=clock,'native clock regression')
    if clock is not None and value!=clock:
     # Even deleting allSTRUCT rows from an earlierprintStats is a detectablemissingframe.
     need(frame_clock==clock,'earlier native clock lacks STRUCT frame')
     close_current(True);records={};frame_clock=None
    clock=value
   if not line.startswith('EPL2STRUCTV1|'):continue
   need(clock is not None,'Structural cumulative snapshot lacks native clock context')
   parts=line.strip().split('|');need(len(parts)>=3 and parts[1]in KINDS,'unknown STRUCT kind')
   row={}
   for token in parts[2:]:
    need('='in token,'malformed STRUCT field');k,v=token.split('=',1);need(k not in row,'duplicate STRUCT field');need(re.fullmatch(r'\d+',v)is not None,'nonunsigned STRUCT field');row[k]=int(v);need(row[k]<(1<<64),'STRUCT uint64 overflow')
   need('slice'in row and 0<=row['slice']<64,'STRUCT physicalslice bound')
   key=(parts[1],row['slice']);frame_clock=clock
   if key in records:need(records[key]==row,'Conflicting structural terminal in one native clock context');duplicates+=1
   else:records[key]=row;unique+=1
   structural+=1;kinds[parts[1]]+=1;wire_hash.update(wire)
 need(clock is not None and frame_clock==clock,'final native clock lacks STRUCT frame')
 close_current(False)
 census={'schema':'EP_FULL_PERF_ROLLING_STRUCT_CENSUS_V1','raw_logical_sha256':raw_hash.hexdigest(),'raw_logical_bytes':raw_bytes,'raw_lines':raw_lines,'native_clock_markers':clock_markers,'validated_distinct_clock_frames':closed_frames,'first_frame_clock':first_clock,'final_frame_clock':last_clock,'structural_wire_records':structural,'unique_clock_kind_slice_rows':unique,'identical_duplicate_records':duplicates,'kind_populations':kinds,'structural_wire_sha256':wire_hash.hexdigest(),'ordered_frame_chain_sha256':frame_chain.hexdigest(),'max_retained_rows':len(EXPECTED),'actual_final_retained_rows':len(records),'all_earlier_frames_math':'EXPLICIT_NEW_COMPLETE_SCOPE_LAYOUT_BANK_QUOTA_CONTRACT; early reserved/live may be nonzero','final_math':'UNCHANGED_FROZEN_SUFFIX','discarded_semantic_population':0,'raw_modified_or_truncated':False}
 return records,census

def parse_structure_with_receipt(raw,spec,final):
 records,census=scan_structure(raw,spec);result=frozen_final_math()(records,spec,final)
 census['final_structural_projection_sha256']=hashlib.sha256(canonical(result)).hexdigest();return result,census

def parse_structure(raw,spec,final):return parse_structure_with_receipt(raw,spec,final)[0]

