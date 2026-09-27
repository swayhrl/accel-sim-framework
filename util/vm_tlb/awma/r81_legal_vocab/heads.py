#!/usr/bin/env python3
from __future__ import annotations
import math,time
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F
import triton
import triton.language as tl
import xgrammar as xgr

from test_masks import unpack_mask

VOCAB=151936
DIM=896
MASK_WORDS=(VOCAB+31)//32

@triton.jit
def _dense_fused_tiles(H,W,Mask,CandidateScores,CandidateIds,
                       B:tl.constexpr,V:tl.constexpr,D:tl.constexpr,
                       MASK_WORDS:tl.constexpr,NTILES:tl.constexpr,
                       BLOCK_M:tl.constexpr,BLOCK_N:tl.constexpr,BLOCK_K:tl.constexpr):
    tile=tl.program_id(0)
    m=tl.arange(0,BLOCK_M)
    n=tile*BLOCK_N+tl.arange(0,BLOCK_N)
    kk=tl.arange(0,BLOCK_K)
    acc=tl.full((BLOCK_M,BLOCK_N),0,tl.float32)
    for k in range(tl.cdiv(D,BLOCK_K)):
        feat=k*BLOCK_K+kk
        a=tl.load(H+m[:,None]*D+feat[None,:],mask=(m[:,None]<B)&(feat[None,:]<D),other=0)
        b=tl.load(W+n[None,:]*D+feat[:,None],mask=(n[None,:]<V)&(feat[:,None]<D),other=0)
        acc=tl.dot(a,b,acc)
    words=tl.load(Mask+m[:,None]*MASK_WORDS+(n[None,:]//32),
                  mask=(m[:,None]<B)&(n[None,:]<V),other=0)
    legal=((words>>(n[None,:]%32))&1)!=0
    score=tl.where(legal&((n[None,:])<V),acc.to(tl.bfloat16).to(tl.float32),float('-inf'))
    best=tl.max(score,axis=1)
    candidate=tl.where((score==best[:,None])&legal,n[None,:],2147483647)
    best_id=tl.min(candidate,axis=1)
    tl.store(CandidateScores+m*NTILES+tile,best,mask=m<B)
    tl.store(CandidateIds+m*NTILES+tile,best_id,mask=m<B)

@triton.jit
def _ragged_direct_groups(H,W,Indices,Rows,PartialScores,PartialIds,
                          K:tl.constexpr,G:tl.constexpr,D:tl.constexpr,
                          MAX_BLOCKS:tl.constexpr,
                          BLOCK_ROWS:tl.constexpr,BLOCK_K:tl.constexpr):
    block=tl.program_id(0)
    group_row=tl.program_id(1)
    row=tl.load(Rows+group_row,mask=group_row<G,other=0)
    offs=block*BLOCK_ROWS+tl.arange(0,BLOCK_ROWS)
    token=tl.load(Indices+offs,mask=offs<K,other=0)
    feat=tl.arange(0,BLOCK_K)
    accum=tl.full((BLOCK_ROWS,),0,tl.float32)
    for k in range(tl.cdiv(D,BLOCK_K)):
        d=k*BLOCK_K+feat
        w=tl.load(W+token[:,None]*D+d[None,:],
                  mask=(offs[:,None]<K)&(d[None,:]<D),other=0).to(tl.float32)
        h=tl.load(H+row*D+d,mask=d<D,other=0).to(tl.float32)
        accum+=tl.sum(w*h[None,:],axis=1)
    scores=tl.where(offs<K,accum.to(tl.bfloat16).to(tl.float32),float('-inf'))
    best=tl.max(scores,axis=0)
    best_id=tl.min(tl.where((scores==best)&(offs<K),token,2147483647),axis=0)
    tl.store(PartialScores+row*MAX_BLOCKS+block,best)
    tl.store(PartialIds+row*MAX_BLOCKS+block,best_id)

class HeadArms:
    def __init__(self,weight:torch.Tensor):
        if tuple(weight.shape)!=(VOCAB,DIM) or weight.dtype!=torch.bfloat16 or weight.device.type!='cuda':
            raise ValueError('R81 exact native BF16 head identity missing')
        self.weight=weight
        self.indexed_buffer=torch.empty_like(weight)
        self.a3_index_buffers=torch.empty((4,VOCAB),dtype=torch.int32,device=weight.device)
        self.max_blocks=triton.cdiv(VOCAB,32)
        self.a3_scores=torch.empty((4,self.max_blocks),dtype=torch.float32,device=weight.device)
        self.a3_tokens=torch.empty((4,self.max_blocks),dtype=torch.int32,device=weight.device)

    def _base(self,bitmask,done):
        legal_bool=unpack_mask(bitmask,VOCAB)
        legal_ids=[np.flatnonzero(legal_bool[i]).astype(np.int32,copy=False) for i in range(4)]
        active=[i for i in range(4) if not done[i]]
        if any(len(legal_ids[i])==0 for i in active):raise RuntimeError('EMPTY_LEGAL_SUPPORT')
        chosen=[None]*4;scores=[None]*4
        for i in active:
            if len(legal_ids[i])==1:chosen[i]=int(legal_ids[i][0])
        work=[i for i in active if len(legal_ids[i])>1]
        return legal_bool,legal_ids,active,work,chosen,scores

    def select(self,arm,hidden,bitmask,done):
        if hidden.shape!=(4,DIM) or hidden.dtype!=torch.bfloat16:raise ValueError('hidden identity')
        legal_bool,legal_ids,active,work,chosen,scores=self._base(bitmask,done)
        metadata={'active_rows':len(active),'head_rows':len(work),'singleton_rows':len(active)-len(work),
                  'metadata_cpu_ms':0.0,'gather_bytes':0,'group_count':0,'union_count':0}
        if not work:return chosen,scores,metadata
        if arm=='A0_DENSE_VENDOR':
            logits=F.linear(hidden[work],self.weight)
            mask_gpu=bitmask[work].contiguous().to(hidden.device)
            xgr.apply_token_bitmask_inplace(logits,mask_gpu,vocab_size=VOCAB,backend='cuda')
            local=torch.argmax(logits,dim=-1)
            ids=local.tolist()
            vals=logits[torch.arange(len(work),device=hidden.device),local].float().tolist()
            for j,i in enumerate(work):chosen[i]=int(ids[j]);scores[i]=float(vals[j])
        elif arm=='A1_DENSE_FUSED':
            h=hidden[work].contiguous()
            packed=bitmask[work].contiguous().to(hidden.device)
            ntiles=triton.cdiv(VOCAB,128)
            candidate_scores=torch.empty((len(work),ntiles),dtype=torch.float32,device=hidden.device)
            candidate_ids=torch.empty((len(work),ntiles),dtype=torch.int32,device=hidden.device)
            _dense_fused_tiles[(ntiles,)](h,self.weight,packed,candidate_scores,candidate_ids,
              len(work),VOCAB,DIM,MASK_WORDS,ntiles,16,128,32,num_warps=8)
            best_tile=candidate_scores.argmax(dim=1)
            ids=candidate_ids[torch.arange(len(work),device=hidden.device),best_tile].tolist()
            vals=candidate_scores[torch.arange(len(work),device=hidden.device),best_tile].tolist()
            for j,i in enumerate(work):chosen[i]=int(ids[j]);scores[i]=float(vals[j])
        elif arm=='A2_INDEXED_UNION':
            union=np.unique(np.concatenate([legal_ids[i] for i in work]))
            metadata['union_count']=len(union)
            metadata['gather_bytes']=len(union)*DIM*2
            ids_gpu=torch.from_numpy(union.astype(np.int64,copy=False)).to(hidden.device)
            selected_weight=self.indexed_buffer[:len(union)]
            torch.index_select(self.weight,0,ids_gpu,out=selected_weight)
            logits=F.linear(hidden[work],selected_weight)
            valid=np.stack([legal_bool[i,union] for i in work])
            valid_gpu=torch.from_numpy(valid).to(hidden.device)
            logits.masked_fill_(~valid_gpu,float('-inf'))
            local=logits.argmax(dim=1)
            selected_ids=ids_gpu[local].tolist()
            vals=logits[torch.arange(len(work),device=hidden.device),local].float().tolist()
            for j,i in enumerate(work):chosen[i]=int(selected_ids[j]);scores[i]=float(vals[j])
        elif arm=='A3_RAGGED_DIRECT':
            start=time.perf_counter_ns()
            groups=defaultdict(list)
            for i in work:
                groups[bitmask[i].numpy().tobytes()].append(i)
            metadata['group_count']=len(groups)
            metadata['metadata_cpu_ms']=(time.perf_counter_ns()-start)/1e6
            for group_index,row_ids in enumerate(groups.values()):
                legal=legal_ids[row_ids[0]]
                if any(not np.array_equal(legal,legal_ids[i]) for i in row_ids):
                    raise ValueError('identical-mask grouping collision')
                count=len(legal)
                buffer=self.a3_index_buffers[group_index,:count]
                buffer.copy_(torch.from_numpy(legal),non_blocking=False)
                gpu_rows=torch.tensor(row_ids,dtype=torch.int32,device=hidden.device)
                blocks=triton.cdiv(count,32)
                _ragged_direct_groups[(blocks,len(row_ids))](hidden,self.weight,buffer,gpu_rows,
                  self.a3_scores,self.a3_tokens,count,len(row_ids),DIM,self.max_blocks,32,128,num_warps=4)
            for i in work:
                blocks=triton.cdiv(len(legal_ids[i]),32)
                best=self.a3_scores[i,:blocks].argmax()
                chosen[i]=int(self.a3_tokens[i,best])
                scores[i]=float(self.a3_scores[i,best])
        else:raise ValueError(arm)
        for i in work:
            if chosen[i] is None or chosen[i] not in legal_ids[i]:
                raise ValueError(f'illegal selected token in {arm} row {i}: {chosen[i]}')
            if not math.isfinite(scores[i]):raise ValueError(f'nonfinite legal score in {arm} row {i}')
        return chosen,scores,metadata
