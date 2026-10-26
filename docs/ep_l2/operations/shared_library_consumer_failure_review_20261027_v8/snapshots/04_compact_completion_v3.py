"""Bounded V3 physical-lane completion state. No model/scheduler or per-grid Python objects."""
from array import array
import sys
PROFILE_ID='SM70_EXACT_PHYSICAL_LANE_COMPLETION_BITMAP_V3'
MAX_KEYS=8_000_000
MAX_STATE_BYTES=40*2**20
def need(v,m):
 if not v:raise ValueError('V3_COMPLETION_'+m)
def uint(text,maximum,name,base=10):
 need(isinstance(text,str)and 0<len(text)<= (16 if base==16 else 20),'INTEGER_WIDTH_'+name)
 chars='0123456789abcdefABCDEF'if base==16 else'0123456789'
 need(all(x in chars for x in text),'INTEGER_GRAMMAR_'+name)
 n=int(text,base);need(n<=maximum,'INTEGER_RANGE_'+name);return n
class CompactWarpCompletion:
 def __init__(self,grid,block,max_keys=1_000_000,max_bytes=MAX_STATE_BYTES):
  need(type(max_keys)is int and 0<max_keys<=MAX_KEYS,'KEY_CAP')
  need(type(max_bytes)is int and 0<max_bytes<=MAX_STATE_BYTES,'STATE_BYTE_CAP')
  need(len(grid)==len(block)==3 and all(type(x)is int and x>0 for x in (*grid,*block)),'GEOMETRY')
  self.grid=tuple(grid);self.block=tuple(block);self.ctas=grid[0]*grid[1]*grid[2];self.threads=block[0]*block[1]*block[2]
  need(self.threads<=1024,'BLOCK_THREADS')
  self.warps_per_cta=(self.threads+31)//32;self.keys=self.ctas*self.warps_per_cta
  need(0<self.keys<=max_keys,'GRID_WARP_KEYS')
  cb=(self.ctas+7)//8;wb=(self.keys+7)//8
  self.required_bytes=4*self.keys+cb+wb
  need(self.required_bytes<=max_bytes,'GRID_STATE_BYTES')
  probe=array('I',[0]);need(probe.itemsize==4,'UINT32_PLATFORM')
  self.exit_masks=probe*self.keys
  self.cta_seen=bytearray(cb);self.warp_seen=bytearray(wb)
  self.seen_ctas=0;self.seen_warps=0;self.complete_warps=0;self.exited_lanes=0
  self.max_keys=max_keys;self.max_bytes=max_bytes
 @staticmethod
 def bit_test_set(bitmap,index,limit):
  need(type(index)is int and 0<=index<limit,'BITMAP_INDEX')
  byte=index>>3;bit=1<<(index&7);was=bool(bitmap[byte]&bit);bitmap[byte]|=bit;return was
 def cta_index(self,coord):
  need(len(coord)==3 and all(type(coord[i])is int and 0<=coord[i]<self.grid[i]for i in range(3)),'CTA_BOUNDS')
  return coord[0]+self.grid[0]*(coord[1]+self.grid[1]*coord[2])
 def touch_cta(self,coord,unique=False):
  i=self.cta_index(coord);was=self.bit_test_set(self.cta_seen,i,self.ctas)
  need(not(unique and was),'DUPLICATE_CTA')
  if not was:self.seen_ctas+=1
  return i
 def touch_warp(self,coord,warp,unique=False):
  c=self.touch_cta(coord)
  need(type(warp)is int and 0<=warp<self.warps_per_cta,'WARP_BOUNDS')
  key=c*self.warps_per_cta+warp;was=self.bit_test_set(self.warp_seen,key,self.keys)
  need(not(unique and was),'DUPLICATE_WARP')
  if not was:self.seen_warps+=1
  return key
 def physical_mask(self,key):
  need(type(key)is int and 0<=key<self.keys,'WARP_KEY')
  lanes=min(32,self.threads-(key%self.warps_per_cta)*32)
  return (1<<lanes)-1
 def apply(self,key,mask,root):
  physical=self.physical_mask(key);need(type(mask)is int and 0<=mask<=0xffffffff,'ACTIVE_UINT32')
  need(mask&~physical==0,'ACTIVE_OUTSIDE_PHYSICAL_LANES')
  old=self.exit_masks[key];need(mask&old==0,'ACTIVE_OR_REEXIT_ALREADY_EXITED_LANE')
  # Zero mask is a structurally decoded zero-active record: no EXIT contribution,
  # no revival, and no claim that the physical machine emitted/scheduled it.
  if root=='EXIT'and mask:
   now=old|mask;self.exit_masks[key]=now;self.exited_lanes+=mask.bit_count()
   if old!=physical and now==physical:self.complete_warps+=1
  return mask
 def require_warp_complete(self,key):
  need(self.exit_masks[key]==self.physical_mask(key),'PHYSICAL_LANE_EXIT_COVERAGE')
 def finish(self):
  need(self.seen_ctas==self.ctas and self.seen_warps==self.keys,'WHOLE_GRID_WARP_COVERAGE')
  need(self.complete_warps==self.keys and self.exited_lanes==self.ctas*self.threads,'ALL_PHYSICAL_LANES_EXITED')
 def summary(self):
  return dict(profile=PROFILE_ID,grid_ctas=self.ctas,physical_threads_per_cta=self.threads,warp_keys=self.keys,seen_ctas=self.seen_ctas,seen_warps=self.seen_warps,fully_exited_warps=self.complete_warps,physical_lanes_exited=self.exited_lanes,array_payload_bytes=self.required_bytes,actual_Python_container_bytes=sum(sys.getsizeof(x)for x in [self.exit_masks,self.cta_seen,self.warp_seen]),max_state_keys=self.max_keys,max_state_bytes=self.max_bytes,representation='one uint32 EXIT mask/warp plus CTA+warp bitmaps; no per-grid tuple/set/dict',zero_mask_policy='Parsed/native-decoded zero-active metadata; no exit credit/revival. Trailing zero-active records permitted; all physical EXIT coverage still required.')
