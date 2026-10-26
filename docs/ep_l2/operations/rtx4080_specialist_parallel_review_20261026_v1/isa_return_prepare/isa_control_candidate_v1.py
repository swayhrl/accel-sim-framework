"""CPU-only private operand-aware candidate. Never a producer admission or GPU proof."""
import re,copy
U64=(1<<64)-1
class Unsupported(ValueError):pass
def need(ok,reason):
 if not ok:raise Unsupported(reason)
def checked_add(a,b):
 need(type(a)is int and type(b)is int and 0<=a<=U64 and 0<=b<=U64-a,'uint64 target overflow/range')
 return a+b
def control_plan(sass,src,dst,owner,owner_pcs):
 """Only normalized numeric same-owner direct CALL / zero-anchor GPR64 RET."""
 need(isinstance(owner,str)and owner,'missing image/function owner identity')
 need(all(type(x)is int and 0<=x<=334 for x in src+dst)and len(src)==len(set(src))and len(dst)==len(set(dst)),'typed dependency namespace/duplicates')
 text=sass.strip().rstrip(';').strip()
 m=re.fullmatch(r'(?:(@!?)(P[0-6]|UP[0-6])\s+)?(\S+)\s+(.+)',text)
 need(m is not None,'unrecognized exact control grammar')
 sign,pred,op,operands=m.groups();guard=None
 if pred:guard=(328 if pred.startswith('UP')else 320)+int(pred[2:]if pred.startswith('UP')else pred[1:])
 common=dict(owner=owner,opcode=op,guard_token=guard,guard_negated=sign=='@!',ABI_summary_src=list(src),ABI_summary_dst=list(dst),CPU_only_candidate=True,dynamic_semantics_qualified=False)
 if op=='CALL.REL.NOINC':
  target=re.fullmatch(r'0x([0-9a-fA-F]+)',operands)
  need(target is not None,'REL indirect/register-target or ambiguous operands outside direct subset')
  offset=int(target[1],16);need(offset!=0,'direct target0 ambiguous/recursion outside subset')
  need(offset%16==0 and offset in owner_pcs,'target not in exact same-owner instruction closure')
  return dict(common,kind='DIRECT_OWNER_REL_CALL',target_offset=offset,physical_src=[]if guard is None else[guard],physical_dst=[])
 if op=='RET.REL.NODEC':
  ret=re.fullmatch(r'R(\d+)\s+0x([0-9a-fA-F]+)',operands)
  need(ret is not None,'return exact regpair+anchor grammar')
  reg,anchor=int(ret[1]),int(ret[2],16)
  need(reg%2==0 and 0<=reg<=252,'RET GPR64 pair boundary/alignment outside strict subset')
  need(anchor==0,'nonzero/cross-owner RET anchor outside measured subset')
  need(set(src)==({reg,reg+1}|({guard}if guard is not None else set()))and not dst,'RET exact physical pair/guard dependencies required')
  return dict(common,kind='ZERO_ANCHOR_OWNER_REL_RET64',return_pair=[reg,reg+1],anchor_offset=0,physical_src=[reg,reg+1]+([]if guard is None else[guard]),physical_dst=[])
 if op.startswith('CALL.ABS'):raise Unsupported('ABS indirect targets require actual raw64 loaded-image closure GPU evidence')
 raise Unsupported('unknown control suffix/opcode outside exact subset')
def old_call_target_candidate(sass):
 """Faithful isolated reproduction of old regex branch, not execution of old tool."""
 m=re.search(r'0x([0-9a-fA-F]+)',sass)
 return int(m[1],16)if m else None
class LaneOracle:
 """Pure fixture arithmetic/stack oracle; no claim about hardware or ABI."""
 def __init__(self,owner,base,pcs,launched=0xffffffff):
  need(base>=0 and base<=U64,'base range');self.owner=owner;self.base=base;self.pcs=set(pcs);self.live=launched
  self.stack=[[]for _ in range(32)];self.pending=[None]*32
 def step(self,pc,active,effective,plan=None,values=None,exit=False):
  need(pc in {checked_add(self.base,x)for x in self.pcs},'PC outside exact owner')
  need(active&~self.live==0 and effective&~active==0,'physical/active/effective mask')
  for lane in range(32):
   bit=1<<lane
   if active&bit and self.pending[lane]is not None:
    need(pc==self.pending[lane],'next active instruction successor mismatch');self.pending[lane]=None
  if plan:
   if plan['kind']=='ZERO_ANCHOR_OWNER_REL_RET64':need(values is not None and set(values)=={i for i in range(32)if effective>>i&1},'exact effective-lane return payload')
   need(plan['owner']==self.owner,'cross-owner control outside subset')
   for lane in range(32):
    if not effective>>lane&1:continue
    if plan['kind']=='DIRECT_OWNER_REL_CALL':
     target=checked_add(self.base,plan['target_offset']);ret=checked_add(pc,16)
     need(ret in {checked_add(self.base,x)for x in self.pcs},'return PC outside owner')
     self.stack[lane].append(ret);self.pending[lane]=target
    elif plan['kind']=='ZERO_ANCHOR_OWNER_REL_RET64':
     need(values is not None and lane in values,'missing captured low/high pair')
     low,high=values[lane];need(type(low)is int and type(high)is int and 0<=low<=0xffffffff and 0<=high<=0xffffffff,'raw pair value range')
     target=checked_add(self.base,(high<<32)|low)
     need(self.stack[lane]and self.stack[lane][-1]==target,'return full64 frame mismatch')
     self.stack[lane].pop();self.pending[lane]=target
    else:raise Unsupported('unknown plan kind')
  if exit:
   for lane in range(32):
    if effective>>lane&1:
     need(not self.stack[lane]and self.pending[lane]is None,'EXIT with unresolved frame');self.live&=~(1<<lane)
 def finish(self):
  need(self.live==0 and not any(self.stack)and not any(x is not None for x in self.pending),'missing terminal lanes/frames/successors')
