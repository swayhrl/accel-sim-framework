#!/usr/bin/env python3
"""R82 paired P1 B0/C1 measurement; requires the campaign GPU lock externally."""
from __future__ import annotations
import argparse, hashlib, json, math, statistics, time
from pathlib import Path
import torch
import triton
import triton.language as tl


def tensor_sha(t: torch.Tensor) -> str:
    b = t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()
    return hashlib.sha256(b).hexdigest()


@triton.jit
def r82_b0_stage1(Q,K,V,PM,PL,PA,N:tl.constexpr,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_N:tl.constexpr):
    pid=tl.program_id(0);s=pid%NS;bh=pid//NS;n=s*BLOCK_N+tl.arange(0,BLOCK_N);d=tl.arange(0,D);mask=n<N
    q=tl.load(Q+bh*D+d).to(tl.float32);k=tl.load(K+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32)
    score=tl.sum(k*q[None,:],axis=1)*0.125;score=tl.where(mask,score,-float('inf'));m=tl.max(score,axis=0);p=tl.exp(score-m);p=tl.where(mask,p,0.0);l=tl.sum(p,axis=0)
    vv=tl.load(V+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32);acc=tl.sum(p[:,None]*vv,axis=0)
    tl.store(PM+bh*NS+s,m);tl.store(PL+bh*NS+s,l);tl.store(PA+(bh*NS+s)*D+d,acc)


@triton.jit
def r82_b0_stage2(PM,PL,PA,O,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_S:tl.constexpr):
    bh=tl.program_id(0);s=tl.arange(0,BLOCK_S);sm=s<NS;d=tl.arange(0,D);m=tl.load(PM+bh*NS+s,mask=sm,other=-float('inf'));gm=tl.max(m,axis=0);w=tl.exp(m-gm);l=tl.load(PL+bh*NS+s,mask=sm,other=0.0);den=tl.sum(w*l,axis=0);acc=tl.load(PA+(bh*NS+s[:,None])*D+d[None,:],mask=sm[:,None],other=0.0);num=tl.sum(w[:,None]*acc,axis=0);tl.store(O+bh*D+d,num/den)


@triton.jit
def r82_c1_stage1(Q,K,V,PM,PL,PA,N:tl.constexpr,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_N:tl.constexpr):
    pid=tl.program_id(0);s=pid%NS;bh=pid//NS;n=s*BLOCK_N+tl.arange(0,BLOCK_N);d=tl.arange(0,D);mask=n<N
    q=tl.load(Q+bh*D+d).to(tl.float32);k=tl.load(K+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32)
    score=tl.sum(k*q[None,:],axis=1)*0.125;score=tl.where(mask,score,-float('inf'));m=tl.max(score,axis=0);p=tl.exp(score-m);p=tl.where(mask,p,0.0);l=tl.sum(p,axis=0)
    vv=tl.load(V+(bh*N+n[:,None])*D+d[None,:],mask=mask[:,None],other=0.0).to(tl.float32);acc=tl.sum(p[:,None]*vv,axis=0,keep_dims=True)
    tl.store(PM+bh*NS+s,m);tl.store(PL+bh*NS+s,l);tl.store(PA+(bh*NS+s)*D+d[None,:],acc)


@triton.jit
def r82_c1_stage2(PM,PL,PA,O,H:tl.constexpr,D:tl.constexpr,NS:tl.constexpr,BLOCK_S:tl.constexpr):
    bh=tl.program_id(0);s=tl.arange(0,BLOCK_S);sm=s<NS;d=tl.arange(0,D);m=tl.load(PM+bh*NS+s,mask=sm,other=-float('inf'));gm=tl.max(m,axis=0);w=tl.exp(m-gm);l=tl.load(PL+bh*NS+s,mask=sm,other=0.0);den=tl.sum(w*l,axis=0);acc=tl.load(PA+(bh*NS+s[:,None])*D+d[None,:],mask=sm[:,None],other=0.0);num=tl.sum(w[:,None]*acc,axis=0,keep_dims=True);tl.store(O+bh*D+d[None,:],num/den)


class Arm:
    def __init__(self,name,q,k,v):
        self.name=name;self.q=q;self.k=k;self.v=v
        self.B,self.H,_,self.D=q.shape;self.N=k.shape[-2];self.split=256;self.ns=(self.N+self.split-1)//self.split
        self.pm=torch.empty((self.B,self.H,self.ns),device='cuda',dtype=torch.float32)
        self.pl=torch.empty_like(self.pm)
        self.pa=torch.empty((self.B,self.H,self.ns,self.D),device='cuda',dtype=torch.float32)
        self.o=torch.empty((self.B,self.H,1,self.D),device='cuda',dtype=q.dtype)
    def stage1(self):
        fn=r82_b0_stage1 if self.name=='B0' else r82_c1_stage1
        fn[(self.B*self.H*self.ns,)](self.q,self.k,self.v,self.pm,self.pl,self.pa,self.N,H=self.H,D=self.D,NS=self.ns,BLOCK_N=self.split,num_warps=8)
    def stage2(self):
        fn=r82_b0_stage2 if self.name=='B0' else r82_c1_stage2
        fn[(self.B*self.H,)](self.pm,self.pl,self.pa,self.o,H=self.H,D=self.D,NS=self.ns,BLOCK_S=triton.next_power_of_2(self.ns),num_warps=4)
    def run(self):
        self.stage1();self.stage2();return self.o


def load_input(payload: str, input_id: str):
    p=torch.load(payload,map_location='cpu',weights_only=True)['p1'][input_id]
    q=p['q'].cuda().contiguous();h=q.shape[1];hkv=p['k'].shape[1];groups=h//hkv
    k=p['k'].repeat_interleave(groups,dim=1).cuda().contiguous()
    v=p['v'].repeat_interleave(groups,dim=1).cuda().contiguous()
    return q,k,v,hkv


def time_batch(arm: Arm,iters: int) -> tuple[float,float]:
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    wall=time.perf_counter();start.record()
    for _ in range(iters):arm.run()
    end.record();end.synchronize()
    return start.elapsed_time(end)/iters,(time.perf_counter()-wall)*1000/iters


def summary(xs):
    return {'samples_ms':xs,'median_ms':statistics.median(xs),'min_ms':min(xs),'max_ms':max(xs),'mean_ms':statistics.mean(xs),'cv':statistics.pstdev(xs)/statistics.mean(xs)}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--payload',required=True);ap.add_argument('--input-id',default='S2_TEXT');ap.add_argument('--output',required=True);ap.add_argument('--warmups',type=int,default=2);ap.add_argument('--reps',type=int,default=7);ap.add_argument('--batch-iters',type=int,default=100);a=ap.parse_args()
    torch.manual_seed(0);torch.cuda.set_device(0)
    q,k,v,hkv=load_input(a.payload,a.input_id)
    arms={n:Arm(n,q,k,v) for n in ('B0','C1')}
    b0a=arms['B0'].run().detach().clone();b0b=arms['B0'].run().detach().clone();c1=arms['C1'].run().detach().clone();torch.cuda.synchronize()
    correctness={'baseline_repeatable':torch.equal(b0a,b0b),'candidate_bitwise_equal':torch.equal(b0a,c1),'shape_equal':b0a.shape==c1.shape,'dtype_equal':b0a.dtype==c1.dtype,'all_finite':bool(torch.isfinite(b0a).all() and torch.isfinite(c1).all()),'different_elements':int((b0a!=c1).sum()),'max_abs':float((b0a.float()-c1.float()).abs().max()),'b0_output_sha256':tensor_sha(b0a),'c1_output_sha256':tensor_sha(c1)}
    if not all(correctness[x] for x in ('baseline_repeatable','candidate_bitwise_equal','shape_equal','dtype_equal','all_finite')): raise RuntimeError(json.dumps(correctness,sort_keys=True))
    for _ in range(a.warmups):
        for n in ('B0','C1'):
            for _ in range(a.batch_iters): arms[n].run()
    torch.cuda.synchronize()
    samples={'B0':[],'C1':[]};wall={'B0':[],'C1':[]};orders=[]
    for i in range(a.reps):
        order=('B0','C1') if i%2==0 else ('C1','B0');orders.append(list(order))
        for n in order:
            g,w=time_batch(arms[n],a.batch_iters);samples[n].append(g);wall[n].append(w)
    final={n:arms[n].run().detach().clone() for n in arms};torch.cuda.synchronize()
    if not torch.equal(final['B0'],final['C1']): raise RuntimeError('post-timing outputs differ')
    out={'stage':'AWMA_R82_LAYOUT_TRANSFER_EXPLORATION_V1','target':'QWEN25_S2_TEXT_D16_L12_FIXED_SPLIT_256','input_id':a.input_id,'context':'REPEATED_MICROKERNEL_OPERATOR_REGION_NOT_APPLICATION','triton':triton.__version__,'torch':torch.__version__,'gpu':torch.cuda.get_device_name(0),'compute_capability':list(torch.cuda.get_device_capability(0)),'shape':{'q':list(q.shape),'k':list(k.shape),'v':list(v.shape),'q_heads':q.shape[1],'kv_heads':hkv,'N':k.shape[-2],'D':q.shape[-1],'NS':arms['B0'].ns},'hashes':{'q':tensor_sha(q),'k':tensor_sha(k),'v':tensor_sha(v)},'correctness':correctness,'measurement':{'warmups':a.warmups,'repetitions':a.reps,'batch_iterations':a.batch_iters,'orders':orders,'gpu':{n:summary(samples[n]) for n in samples},'wall':{n:summary(wall[n]) for n in wall}},'effect':{'c1_over_b0':statistics.median(samples['C1'])/statistics.median(samples['B0'])-1.0,'b0_over_c1_speedup':statistics.median(samples['B0'])/statistics.median(samples['C1'])-1.0}}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))

if __name__=='__main__':main()
