#!/usr/bin/env python3
import pathlib,lzma,json,re,collections,hashlib,subprocess,difflib
r=pathlib.Path('/data/c16/rtx4080_asset_pilot_20261024_v1')
p=next((r/'capture_attempt3/traces').glob('*.traceg.xz'))
c=collections.Counter();pcs=collections.Counter();ctas=set();warps=set();current=None;warp=None;terminal=collections.Counter();masks=collections.Counter();ibytes=0;active=0;body=0;perwarp=collections.Counter();headers=[]
with lzma.open(p,'rt') as f:
 for line in f:
  line=line.strip()
  if line.startswith('-'):headers.append(line)
  if line.startswith('thread block = '):current=line.split('=',1)[1].strip();ctas.add(current)
  if line.startswith('warp = '):warp=int(line.split('=')[1]);warps.add((current,warp))
  if re.match(r'^[0-9a-f]+ [0-9a-f]+ ',line):
   tok=line.split();pc,mask=tok[:2];nd=int(tok[2]);op=tok[3+nd];ns=int(tok[4+nd]);width=int(tok[5+nd+ns])
   n=int(mask,16).bit_count();active+=n;body+=1;perwarp[(current,warp)]+=1;c[op]+=1;pcs[pc]+=1;masks[mask]+=1
   if op=='EXIT' and n:terminal[(current,warp)]+=1
   if width:ibytes+=width*n
result={'status':'FULL_SINGLE_KERNEL_STRUCTURAL_COVERAGE_PASS','headers':headers,'ctas':len(ctas),'warps':len(warps),'trace_records':body,'active_lane_instruction_instances':active,'memory_payload_bytes_sum':ibytes,'opcode_record_counts':dict(c),'pc_counts':dict(pcs),'mask_counts':dict(masks),'warp_instruction_length_histogram':dict(collections.Counter(perwarp.values())),'terminal_exit_warps':len(terminal),'terminal_exit_count_histogram':dict(collections.Counter(terminal.values())),'kernel_members':1,'htod_copies':2,'htod_bytes':32000000,'expected':{'ctas':15625,'warps':125000,'records':2125000,'warp_records_each':17},'semantic_qualification':'NOT_GRANTED','semantic_gaps':['ULDC.64 UR4 constant access has no destination/source/address in trace','ISETP writes P0 but predicate destination/dependency is not explicit','IMAD.WIDE high destination and 64-bit address high-register dependencies are not fully explicit','no Ada/EP performance or runtime qualification inferred'],'failed_attempts':{'capture_attempt1':'native correct, tool loads, no callbacks/traces; log overwritten by attempt2 due wrapper-script path bug, receipt retained','capture_attempt2':'native correct, explicit device init does not fix; no callbacks/traces','capture_attempt3':'direct binary launch fixes wrapper LD_PRELOAD issue; successful'}}
assert len(ctas)==15625 and len(warps)==125000 and body==2125000
assert set(perwarp.values())=={17} and len(terminal)==125000 and set(terminal.values())=={1}
assert c['LDG.E']==250000 and c['STG.E']==125000 and masks['ffffffff']==2000000 and masks['00000000']==125000
(r/'evidence/TRACE_COVERAGE_AND_SEMANTICS.json').write_text(json.dumps(result,indent=2)+'\n')
(r/'source/HOST_ADAPTATION.patch').write_text(''.join(difflib.unified_diff((r/'source/vectorAdd.upstream.cu').read_text().splitlines(True),(r/'source/vectorAdd.cu').read_text().splitlines(True),fromfile='vectorAdd.upstream.cu',tofile='vectorAdd.cu')))
(r/'evidence/vectorAdd_final.sass').write_text(subprocess.check_output(['/usr/local/cuda-12.8/bin/cuobjdump','-sass',str(r/'bin/vectorAdd')],text=True))
print(json.dumps(result,indent=2))
