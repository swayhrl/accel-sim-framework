#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,math,time
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.nn.attention import sdpa_kernel,SDPBackend
import triton
import triton.language as tl

def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def stats(xs):
 import statistics
 m=statistics.mean(xs);return {'samples_ms':xs,'median_ms':statistics.median(xs),'min_ms':min(xs),'max_ms':max(xs),'mean_ms':m,'cv':statistics.pstdev(xs)/m if m else 0.0}
def timed(fn,warmups,reps,label):
 out=None
 for i in range(warmups):out=fn()
 torch.cuda.synchronize();gpu=[];wall=[]
 for i in range(reps):
  torch.cuda.nvtx.range_push(f'{label};ITER={i}')
  a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True);w=time.perf_counter();a.record();out=fn();b.record();b.synchronize();wall.append((time.perf_counter()-w)*1e3);gpu.append(a.elapsed_time(b));torch.cuda.nvtx.range_pop()
 return out,stats(gpu),stats(wall)

@triton.jit
def _split_stage1(Q,K,V,PM,PL,PA,N:tl.constexpr,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_N:tl.constexpr):
 pid=tl.program_id(0);s=pid%NS;bh=pid//NS;n=s*BLOCK_N+tl.arange(0,BLOCK_N);d=tl.arange(0,D);mask=n<N
 q=tl.load(Q+bh*D+d).to(tl.float32);k=tl.load(K+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32)
 score=tl.sum(k*q[None,:],axis=1)*0.125;score=tl.where(mask,score,-float('inf'));m=tl.max(score,axis=0);p=tl.exp(score-m);p=tl.where(mask,p,0.0);l=tl.sum(p,axis=0)
 vv=tl.load(V+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32);acc=tl.sum(p[:,None]*vv,axis=0)
 tl.store(PM+bh*NS+s,m);tl.store(PL+bh*NS+s,l);tl.store(PA+(bh*NS+s)*D+d,acc)

@triton.jit
def _split_stage2(PM,PL,PA,O,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_S:tl.constexpr):
 bh=tl.program_id(0);s=tl.arange(0,BLOCK_S);sm=s<NS;d=tl.arange(0,D);m=tl.load(PM+bh*NS+s,mask=sm,other=-float('inf'));gm=tl.max(m,axis=0);w=tl.exp(m-gm);l=tl.load(PL+bh*NS+s,mask=sm,other=0.0);den=tl.sum(w*l,axis=0);acc=tl.load(PA+(bh*NS+s[:,None])*D+d[None,:],mask=sm[:,None],other=0.0);num=tl.sum(w[:,None]*acc,axis=0);tl.store(O+bh*D+d,num/den)

class FixedSplit:
 def __init__(self,q,k,v,split=256):
  self.q=q;self.k=k;self.v=v;self.B,self.H,_,self.D=q.shape;self.N=k.shape[-2];self.split=split;self.ns=(self.N+split-1)//split
  self.pm=torch.empty((self.B,self.H,self.ns),device='cuda',dtype=torch.float32);self.pl=torch.empty_like(self.pm);self.pa=torch.empty((self.B,self.H,self.ns,self.D),device='cuda',dtype=torch.float32);self.o=torch.empty((self.B,self.H,1,self.D),device='cuda',dtype=q.dtype)
 def stage1(self):_split_stage1[(self.B*self.H*self.ns,)](self.q,self.k,self.v,self.pm,self.pl,self.pa,self.N,H=self.H,D=self.D,NS=self.ns,BLOCK_N=self.split,num_warps=8);return self.pm
 def stage2(self):_split_stage2[(self.B*self.H,)](self.pm,self.pl,self.pa,self.o,H=self.H,D=self.D,NS=self.ns,BLOCK_S=triton.next_power_of_2(self.ns),num_warps=4);return self.o
 def full(self):self.stage1();return self.stage2()

def make_batch(x,b,kind):
 xs=[x]
 for i in range(1,b):
  y=torch.roll(x,shifts=i*(3 if kind=='q' else 17),dims=-1 if kind=='q' else -2)
  xs.append(y)
 return torch.cat(xs,dim=0).contiguous()
def stock(q,k,v):
 with sdpa_kernel(SDPBackend.FLASH_ATTENTION):return F.scaled_dot_product_attention(q,k,v,dropout_p=0.0,is_causal=False)
def reference(q,k,v):return (torch.softmax(torch.matmul(q.float(),k.float().transpose(-1,-2))/math.sqrt(q.shape[-1]),dim=-1)@v.float()).to(q.dtype)

def p1(a,payload):
 logical_batch=a.batch;physical_batch=4 if a.arm=='PADDED_B4_FLASH_SDPA' else a.batch;src=payload['p1'];names=['S2_TEXT','S2_CODE','S2_STRUCTURED','S2_CODE_ROLL1_DERIVED_CONTROL'][:physical_batch];q=torch.cat([src[n]['q'] for n in names],0).cuda().contiguous();h=q.shape[1];hkv=src['S2_TEXT']['k'].shape[1];groups=h//hkv;k=torch.cat([src[n]['k'].repeat_interleave(groups,dim=1) for n in names],0).cuda().contiguous();v=torch.cat([src[n]['v'].repeat_interleave(groups,dim=1) for n in names],0).cuda().contiguous();fixed=FixedSplit(q,k,v)
 flash=a.arm in ('STOCK_FLASH_SDPA','PADDED_B4_FLASH_SDPA');fn=stock if flash else fixed.full
 torch.cuda.nvtx.range_push(f'QUAL=P1;ARM={a.arm};LOGICAL_B={logical_batch};PHYSICAL_B={physical_batch};PHASE=CANARY');o=fn(q,k,v) if flash else fn();torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
 call=(lambda:fn(q,k,v)) if flash else fn
 o,g,w=timed(call,a.warmups,a.reps,f'QUAL=P1;ARM={a.arm};B={a.batch};PHASE=MEASURE');ref=reference(q,k,v);target=o[0].detach().cpu();Path(a.output).parent.mkdir(parents=True,exist_ok=True);torch.save(target,a.output)
 r={'candidate':'P1','arm':a.arm,'logical_batch':logical_batch,'physical_batch':physical_batch,'warmups':a.warmups,'repetitions':a.reps,'gpu_timing':g,'wall_timing':w,'target_output_sha256':tsha(target),'full_output_sha256':tsha(o),'reference_max_abs':float((o.float()-ref.float()).abs().max()),'reference_max_rel':float(((o.float()-ref.float()).abs()/(ref.float().abs()+1e-8)).max()),'q_sha256':tsha(q[0]),'k_sha256':tsha(k[0]),'v_sha256':tsha(v[0]),'implementation':'PYTORCH_FLASH_SDPA' if flash else 'TRITON_FIXED_SPLIT_256_TWO_STAGE','grid_contract':f'B*{fixed.H}*{fixed.ns} producer programs; B*{fixed.H} combine programs' if not flash else 'runtime selected'}
 if not flash:
  _,s1,_=timed(fixed.stage1,a.warmups,a.reps,f'QUAL=P1;ARM={a.arm};COMPONENT=PRODUCER');fixed.stage1();_,s2,_=timed(fixed.stage2,a.warmups,a.reps,f'QUAL=P1;ARM={a.arm};COMPONENT=COMBINE');r['producer_gpu_timing']=s1;r['combine_gpu_timing']=s2;r['partial_result_bytes']=fixed.pm.numel()*4+fixed.pl.numel()*4+fixed.pa.numel()*4
 print(json.dumps(r,sort_keys=True));return r

def selector(q,kmin,kmax,top):
 scores=torch.maximum(q[:,None,:].float()*kmin.float(),q[:,None,:].float()*kmax.float()).sum(-1);idx=torch.argsort(scores,dim=-1,descending=True,stable=True)[:,:top];return idx,scores
def consume(q,kpages,vpages,idx):
 h,_,pg,d=kpages.shape;top=idx.shape[1];ii=idx[:,:,None,None].expand(h,top,pg,d);ks=torch.gather(kpages,1,ii).reshape(h,top*pg,d);vs=torch.gather(vpages,1,ii).reshape(h,top*pg,d)
 return stock(q[None,:,None,:],ks[None],vs[None]),ks,vs
def online(q,kmin,kmax,kpages,vpages,top):
 idx,scores=selector(q,kmin,kmax,top);o,_,_=consume(q,kpages,vpages,idx);return o,idx,scores

def p2(a,payload):
 src=payload['p2'];q=src['q'].cuda()[0,:,0,:].contiguous();h=q.shape[0];hkv=src['k'].shape[1];groups=h//hkv;k=src['k'].cuda()[0].repeat_interleave(groups,dim=0).contiguous();v=src['v'].cuda()[0].repeat_interleave(groups,dim=0).contiguous();n=8192;k=k[:,:n];v=v[:,:n];pages=n//a.page_size;kp=k.reshape(h,pages,a.page_size,64);vp=v.reshape_as(kp);kmin=kp.amin(2);kmax=kp.amax(2)
 if a.arm=='ONLINE_EAGER':fn=lambda:online(q,kmin,kmax,kp,vp,a.top_pages)
 elif a.arm=='READY_INDEX':
  idx=torch.load(a.indices,map_location='cuda',weights_only=True);fn=lambda:(consume(q,kp,vp,idx)[0],idx,None)
 elif a.arm=='STRONG_COMPILE_FULL':
  compiled=torch.compile(lambda q0,mi,ma,kk,vv:online(q0,mi,ma,kk,vv,a.top_pages),fullgraph=True,mode='reduce-overhead');fn=lambda:compiled(q,kmin,kmax,kp,vp)
 elif a.arm=='STRONG_CUDA_GRAPH':
  side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
  with torch.cuda.stream(side):
   for _ in range(3):captured=online(q,kmin,kmax,kp,vp,a.top_pages)
  torch.cuda.current_stream().wait_stream(side);g=torch.cuda.CUDAGraph()
  with torch.cuda.graph(g):captured=online(q,kmin,kmax,kp,vp,a.top_pages)
  fn=lambda:(g.replay() or captured)
 else:raise ValueError(a.arm)
 torch.cuda.nvtx.range_push(f'QUAL=P2;ARM={a.arm};TOP={a.top_pages};PHASE=CANARY');res=fn();torch.cuda.synchronize();torch.cuda.nvtx.range_pop();o,idx,scores=res
 o,g,w=timed(fn,a.warmups,a.reps,f'QUAL=P2;ARM={a.arm};TOP={a.top_pages};PHASE=MEASURE');out,idx,scores=o;Path(a.output).parent.mkdir(parents=True,exist_ok=True);torch.save(out[0].detach().cpu(),a.output)
 if a.arm=='ONLINE_EAGER':torch.save(idx.detach().cpu(),a.indices)
 r={'candidate':'P2','arm':a.arm,'top_pages':a.top_pages,'selected_fraction':a.top_pages/pages,'page_size_tokens':a.page_size,'context_tokens':n,'page_count':pages,'q_heads':h,'kv_heads':hkv,'warmups':a.warmups,'repetitions':a.reps,'gpu_timing':g,'wall_timing':w,'indices_sha256':tsha(idx),'selected_index_order':idx.detach().cpu().tolist(),'output_sha256':tsha(out),'logical_selected_kv_bytes':2*hkv*a.top_pages*a.page_size*64*2,'materialized_selected_kv_bytes':2*h*a.top_pages*a.page_size*64*2,'implementation':a.arm,'tie_break':'score descending; stable original page index ascending'}
 # Explanatory accounting uses the same eager semantic functions for every arm.
 _,sg,_=timed(lambda:selector(q,kmin,kmax,a.top_pages),a.warmups,a.reps,f'QUAL=P2;TOP={a.top_pages};COMPONENT=SELECTOR')
 paired=idx;_,cg,_=timed(lambda:consume(q,kp,vp,paired),a.warmups,a.reps,f'QUAL=P2;TOP={a.top_pages};COMPONENT=CONSUMER')
 _,_,_=consume(q,kp,vp,paired);ks=kp.shape
 r['selector_gpu_timing']=sg;r['consumer_gpu_timing']=cg
 print(json.dumps(r,sort_keys=True));return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',choices=['P1','P2'],required=True);p.add_argument('--payload',required=True);p.add_argument('--arm',required=True);p.add_argument('--output',required=True);p.add_argument('--indices');p.add_argument('--batch',type=int,default=1);p.add_argument('--page-size',type=int,default=16);p.add_argument('--top-pages',type=int,default=256);p.add_argument('--warmups',type=int,default=2);p.add_argument('--reps',type=int,default=7);a=p.parse_args();torch.manual_seed(0);torch.cuda.set_device(0);payload=torch.load(a.payload,map_location='cpu',weights_only=True);r=p1(a,payload) if a.candidate=='P1' else p2(a,payload)
if __name__=='__main__':main()
