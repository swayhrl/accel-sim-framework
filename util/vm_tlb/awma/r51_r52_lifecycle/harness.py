#!/usr/bin/env python3
from __future__ import annotations
import argparse,ctypes,hashlib,json,statistics,time
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.nn.attention import sdpa_kernel,SDPBackend

def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def stat(x):
 m=statistics.mean(x);return {'samples_ms':x,'median_ms':statistics.median(x),'min_ms':min(x),'max_ms':max(x),'mean_ms':m,'cv':statistics.pstdev(x)/m if m else 0.0}
def priority_range():
 lib=ctypes.CDLL('libcudart.so');least=ctypes.c_int();greatest=ctypes.c_int();rc=lib.cudaDeviceGetStreamPriorityRange(ctypes.byref(least),ctypes.byref(greatest))
 if rc:raise RuntimeError(f'cudaDeviceGetStreamPriorityRange={rc}')
 return least.value,greatest.value

class Workload:
 def __init__(self,payload,arm):
  self.h=payload['background_hidden'].cuda().contiguous();self.w=payload['background_weight'].cuda().contiguous();self.ref=payload['background_reference'].cuda().contiguous();self.q=payload['foreground_q'].cuda().contiguous();self.k=payload['foreground_k'].cuda().contiguous();self.v=payload['foreground_v'].cuda().contiguous();self.fref=payload['foreground_reference'].cuda().contiguous();self.arm=arm;self.chunks={'MONOLITHIC':1,'CHUNKED_GRAPH_8':8,'CHUNKED_GRAPH_32':32}[arm];least,greatest=priority_range();self.low=torch.cuda.Stream(priority=least);self.high=torch.cuda.Stream(priority=greatest);self.graph=None;self.graph_out=None
  # Materialize libraries and allocations before any measurement/capture.
  with torch.cuda.stream(self.low):tmp=F.linear(self.h,self.w)
  with torch.cuda.stream(self.high):tmpf=self.foreground()
  torch.cuda.synchronize()
  if self.chunks>1:self._capture_graph()
 def chunked(self):
  rows=self.w.shape[0]//self.chunks;outs=[]
  for i in range(self.chunks):outs.append(F.linear(self.h,self.w[i*rows:(i+1)*rows]))
  return torch.cat(outs,dim=-1)
 def _capture_graph(self):
  side=self.low
  with torch.cuda.stream(side):
   for _ in range(3):o=self.chunked()
  torch.cuda.synchronize();self.graph=torch.cuda.CUDAGraph()
  with torch.cuda.graph(self.graph,stream=side):self.graph_out=self.chunked()
  self.graph.replay();torch.cuda.synchronize()
 def background(self):
  if self.chunks==1:return F.linear(self.h,self.w)
  self.graph.replay();return self.graph_out
 def foreground(self):
  with sdpa_kernel(SDPBackend.FLASH_ATTENTION):return F.scaled_dot_product_attention(self.q,self.k,self.v,dropout_p=0.0,is_causal=False)
 def correctness(self,o,fo=None):
  torch.cuda.synchronize();r={'background_bitwise':bool(torch.equal(o,self.ref)),'background_output_sha256':tsha(o),'background_reference_sha256':tsha(self.ref)}
  if fo is not None:r.update(foreground_bitwise=bool(torch.equal(fo,self.fref)),foreground_output_sha256=tsha(fo),foreground_reference_sha256=tsha(self.fref))
  return r
 def graph_liveness(self):
  if self.graph is None:return {'applicable':False}
  original=self.h.clone();self.graph.replay();torch.cuda.synchronize();base=self.graph_out.clone();self.h.copy_(-original);self.graph.replay();torch.cuda.synchronize();changed=self.graph_out.clone();eager=F.linear(self.h,self.w);torch.cuda.synchronize();self.h.copy_(original);self.graph.replay();torch.cuda.synchronize();restored=self.graph_out.clone()
  return {'applicable':True,'base_bitwise_reference':bool(torch.equal(base,self.ref)),'changed_graph_bitwise_eager':bool(torch.equal(changed,eager)),'changed_differs_from_base':not torch.equal(changed,base),'restored_bitwise_reference':bool(torch.equal(restored,self.ref)),'changed_sha256':tsha(changed)}

def standalone(a,w):
 for _ in range(a.warmups):
  with torch.cuda.stream(w.low):o=w.background()
 torch.cuda.synchronize();gpu=[];wall=[]
 for i in range(a.reps):
  torch.cuda.nvtx.range_push(f'R51_STANDALONE;ARM={a.arm};KIND=FORMAL;REP={i}');start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True);t=time.perf_counter()
  with torch.cuda.stream(w.low):start.record();o=w.background();end.record()
  end.synchronize();gpu.append(start.elapsed_time(end));wall.append((time.perf_counter()-t)*1e3);torch.cuda.nvtx.range_pop()
 c=w.correctness(o);live=w.graph_liveness();least,greatest=priority_range();return {'mode':'STANDALONE','arm':a.arm,'chunks':w.chunks,'warmups':a.warmups,'repetitions':a.reps,'gpu_timing':stat(gpu),'wall_timing':stat(wall),'correctness':c,'graph_liveness':live,'stream_priority_least':least,'stream_priority_greatest':greatest,'low_stream_handle':w.low.cuda_stream,'high_stream_handle':w.high.cuda_stream}

def spin_until(deadline):
 while time.perf_counter_ns()<deadline:pass
def overlap(a,w):
 target_us=a.monolithic_median_ms*1000*a.arrival+a.spin_adjust_us;records=[];o=fo=None
 for kind,count in [('WARMUP',a.warmups),('FORMAL',a.reps)]:
  for i in range(count):
   torch.cuda.synchronize();host0=time.perf_counter_ns();torch.cuda.nvtx.range_push(f'R51_BG_SUBMIT;ARM={a.arm};ARRIVAL={a.arrival};KIND={kind};REP={i}')
   with torch.cuda.stream(w.low):o=w.background()
   torch.cuda.nvtx.range_pop();after_bg=time.perf_counter_ns();spin_until(after_bg+int(target_us*1000));ready_cpu=time.perf_counter_ns();torch.cuda.nvtx.range_push(f'R51_FG_SUBMIT;ARM={a.arm};ARRIVAL={a.arrival};KIND={kind};REP={i}')
   with torch.cuda.stream(w.high):fo=w.foreground()
   torch.cuda.nvtx.range_pop();submit_cpu=time.perf_counter_ns();torch.cuda.synchronize();records.append({'kind':kind,'rep':i,'host_bg_submit_start_ns':host0,'host_bg_submit_return_ns':after_bg,'host_ready_ns':ready_cpu,'host_fg_submit_return_ns':submit_cpu,'target_spin_us':target_us})
 c=w.correctness(o,fo);return {'mode':'OVERLAP','arm':a.arm,'chunks':w.chunks,'arrival_fraction':a.arrival,'target_spin_us':target_us,'spin_adjust_us':a.spin_adjust_us,'monolithic_median_ms':a.monolithic_median_ms,'warmups':a.warmups,'repetitions':a.reps,'host_records':records,'correctness':c,'low_stream_handle':w.low.cuda_stream,'high_stream_handle':w.high.cuda_stream}

def main():
 p=argparse.ArgumentParser();p.add_argument('--payload',required=True);p.add_argument('--mode',choices=['standalone','overlap'],required=True);p.add_argument('--arm',choices=['MONOLITHIC','CHUNKED_GRAPH_8','CHUNKED_GRAPH_32'],required=True);p.add_argument('--warmups',type=int,default=2);p.add_argument('--reps',type=int,default=7);p.add_argument('--arrival',type=float,default=.25);p.add_argument('--monolithic-median-ms',type=float,default=.4);p.add_argument('--spin-adjust-us',type=float,default=0.0);a=p.parse_args();torch.manual_seed(0);torch.cuda.set_device(0);payload=torch.load(a.payload,map_location='cpu',weights_only=True);w=Workload(payload,a.arm);r=standalone(a,w) if a.mode=='standalone' else overlap(a,w);print(json.dumps(r,sort_keys=True))
if __name__=='__main__':main()
