from __future__ import annotations
import hashlib,json,time
import torch
from transformers.cache_utils import DynamicCache
MASK=151665;STOP=151645
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def cache_select(c,idx):
 if c is None:return None
 z=DynamicCache([(k.index_select(0,idx),v.index_select(0,idx)) for k,v in zip(c.key_cache,c.value_cache)]);z._seen_tokens=c._seen_tokens;return z
def cache_scatter(dst,src,idx):
 for l in range(len(dst.key_cache)):dst.key_cache[l].index_copy_(0,idx,src.key_cache[l]);dst.value_cache[l].index_copy_(0,idx,src.value_cache[l])
def semantic_projection(e):
 z={k:e[k] for k in ('request_id','logical_step','block_idx','subblock_idx','cohort_id','request_finished','cohort_full_refresh_decision','cache_epoch','cache_action','commit_positions','commit_token_ids','forced_commit_positions','stop_transition','next_block_seed_token')}
 if z['cache_action']=='REUSE_PACKED':z['cache_action']='REUSE'
 return z
@torch.no_grad()
def generate(model,tokenizer,input_ids,seq_len,request_ids,arm='A0',block_size=32,max_new_tokens=512,small_block_size=8,threshold=.9,top_p=.95,temperature=0.,record=False):
 min_len=int(seq_len.min());num_blocks=max_new_tokens//block_size+int(seq_len.max())//block_size;batch_size=input_ids.shape[0];ledger=[];traj=[];logical=0;stats={'forward_calls':0,'input_token_rows':0,'logits_rows':0,'packed_rows':0,'scattered_rows':0,'metadata_ns':0,'pack_bytes':0};t0=time.perf_counter();completion={}
 def fw(ids,**kw):stats['forward_calls']+=1;stats['input_token_rows']+=ids.shape[0]*ids.shape[1];o=model.forward(input_ids=ids,**kw);stats['logits_rows']+=o.logits.shape[0]*o.logits.shape[1];return o
 if min_len>block_size:
  o=fw(input_ids[:,:min_len//block_size*block_size],use_cache=True,update_past_key_values=True,block_size=block_size);logits,past=o.logits,o.past_key_values
  if min_len%block_size==0:
   ix=seq_len==min_len;nextt=logits[ix,-1:,:].argmax(-1)
   if input_ids.shape[1]<=min_len:input_ids=torch.cat([input_ids,nextt],1)
   else:input_ids[ix,min_len]=nextt.squeeze(-1)
 else:past=None
 seq_block=seq_len//block_size;finished=torch.zeros(batch_size,device=input_ids.device,dtype=torch.bool);samples=torch.arange(batch_size,device=input_ids.device);done={};cache_epoch=0;start_block=min_len//block_size;nsmall=block_size//small_block_size
 for block_idx in range(start_block,num_blocks):
  if bool(finished.all()):break
  if bool((seq_block==block_idx).all()):
   x=torch.cat([input_ids,torch.full((input_ids.shape[0],block_size-input_ids.shape[1]%block_size),MASK,device=input_ids.device,dtype=torch.long)],1);input_ids=x
  else:x=input_ids[:,: (block_idx+1)*block_size]
  x[finished,-block_size:]=tokenizer.pad_token_id;x=x.clone();block_cache=None;step=0
  while True:
   mask=(x[:,-block_size:]==MASK)
   if int(mask.sum())==0:
    for j in range(x.shape[0]):
     if bool(finished[j]) and int(seq_len[j])<(block_idx+1)*block_size:
      nz=(x[j,int(seq_len[j]):]==STOP).nonzero();
      if len(nz):x[j,int(seq_len[j])+int(nz[0,0])+1:]=tokenizer.pad_token_id
    if bool(finished.all()):break
    o=fw(x[:,-block_size:],use_cache=True,past_key_values=past,update_past_key_values=True,block_size=block_size);logits,past=o.logits,o.past_key_values;nextt=logits[:,-1:,:].argmax(-1);nextt[finished]=tokenizer.pad_token_id;x=torch.cat([x,nextt],1);logical+=1;cache_epoch+=1
    if record:
     for j in range(x.shape[0]):
      ev={'domain':'','request_id':request_ids[int(samples[j])],'logical_step':logical,'block_idx':block_idx,'subblock_idx':-1,'cohort_id':','.join(map(str,[int(q) for q in samples.cpu()])),'active_request_count':x.shape[0],'request_active':True,'request_finished':bool(finished[j]),'mask_count_current_request':0,'cohort_mask_count':0,'cohort_full_refresh_decision':False,'request_has_current_subblock_work':False,'input_token_rows_executed':block_size,'logits_rows_materialized':block_size,'cache_epoch':cache_epoch,'cache_action':'COMMIT_BLOCK','commit_positions':'','commit_token_ids':'','forced_commit_positions':'','stop_transition':False,'graph_bucket_if_any':x.shape[0],'evidence_class':'COHORT_POLICY_REQUIRED_WORK','notes':'next-block seed','next_block_seed_token':int(nextt[j,0])};ledger.append(ev);traj.append(semantic_projection(ev))
    break
   for sb in range(nsmall):
    s=sb*small_block_size;e=s+small_block_size;start=-block_size+s;end=None if e==block_size else -block_size+e
    while True:
     mask=(x[:,-block_size:]==MASK);work=mask[:,start:end].any(1)
     if int(mask[:,start:end].sum())==0:break
     m0=time.perf_counter_ns();full=block_cache is None or bool((x[:,-block_size+s]==MASK).any());stats['metadata_ns']+=time.perf_counter_ns()-m0;before=x[:,start:end].clone();forced=[]
     if full:
      o=fw(x[:,-block_size:],use_cache=True,past_key_values=past,update_past_key_values=False,use_block_cache=True);logits,block_cache=o.logits,o.block_past_key_values;logits=torch.cat([logits[:,:1],logits[:,:-1]],1)[:,start:end];exec_idx=torch.arange(x.shape[0],device=x.device);rows_exec=block_size
     elif arm=='A1_PACKED' and not bool(work.all()):
      idx=work.nonzero().flatten();stats['packed_rows']+=int(idx.numel());stats['scattered_rows']+=int(idx.numel());stats['pack_bytes']+=int(idx.numel())*small_block_size*8;subpast=cache_select(past,idx);subblock=cache_select(block_cache,idx);o=fw(x.index_select(0,idx)[:,start:end],use_cache=True,past_key_values=subpast,update_past_key_values=False,use_block_cache=True,block_past_key_values=subblock,replace_position=s);cache_scatter(block_cache,o.block_past_key_values,idx);logits=torch.cat([o.logits[:,:1],o.logits[:,:-1]],1);exec_idx=idx;rows_exec=small_block_size
     else:
      o=fw(x[:,start:end],use_cache=True,past_key_values=past,update_past_key_values=False,use_block_cache=True,block_past_key_values=block_cache,replace_position=s);logits=torch.cat([o.logits[:,:1],o.logits[:,:-1]],1);block_cache=o.block_past_key_values;exec_idx=torch.arange(x.shape[0],device=x.device);rows_exec=small_block_size
     probs=torch.softmax(logits.float(),-1);pred=probs.argmax(-1);conf=torch.gather(probs,-1,pred.unsqueeze(-1)).squeeze(-1);local_mask=mask.index_select(0,exec_idx)[:,start:end];conf=torch.where(local_mask,conf,-torch.inf);unmask=conf>threshold;mx=conf.argmax(-1);unmask[torch.arange(pred.shape[0],device=x.device),mx]=True;forced_mask=torch.zeros_like(unmask);forced_mask[torch.arange(pred.shape[0],device=x.device),mx]=True;forced_mask &= local_mask & ~(conf>threshold);unmask &= local_mask;seg=x.index_select(0,exec_idx)[:,start:end].clone();seg[unmask]=pred[unmask];x[exec_idx,start:end]=seg;fr=((pred==STOP)&unmask).any(1);finished[exec_idx]|=fr;logical+=1
     if record:
      for j in range(x.shape[0]):
       oid=int(samples[j]);selected=(exec_idx==j).nonzero().flatten();executed=len(selected)>0;pos=[];vals=[];fpos=[]
       if executed:
        q=int(selected[0]);uu=unmask[q].nonzero().flatten().tolist();pos=[s+int(u) for u in uu];vals=[int(pred[q,int(u)]) for u in uu];fpos=[s+int(u) for u in forced_mask[q].nonzero().flatten().tolist()]
       ev={'domain':'','request_id':request_ids[oid],'logical_step':logical,'block_idx':block_idx,'subblock_idx':sb,'cohort_id':','.join(map(str,[int(q) for q in samples.cpu()])),'active_request_count':x.shape[0],'request_active':True,'request_finished':bool(finished[j]),'mask_count_current_request':int(mask[j].sum()),'cohort_mask_count':int(mask.sum()),'cohort_full_refresh_decision':full,'request_has_current_subblock_work':bool(work[j]),'input_token_rows_executed':rows_exec if executed else 0,'logits_rows_materialized':rows_exec if executed else 0,'cache_epoch':cache_epoch,'cache_action':'FULL_REFRESH' if full else ('REUSE_PACKED' if arm=='A1_PACKED' and not bool(work.all()) else 'REUSE'),'commit_positions':','.join(map(str,pos)),'commit_token_ids':','.join(map(str,vals)),'forced_commit_positions':','.join(map(str,fpos)),'stop_transition':bool(fr[int(selected[0])]) if executed else False,'graph_bucket_if_any':1 if len(exec_idx)==1 else (2 if len(exec_idx)<=2 else 4),'evidence_class':'REQUIRED_ACTIVE_WORK' if bool(work[j]) else ('COHORT_POLICY_REQUIRED_WORK' if full else ('LEGALLY_OMITTABLE_IN_SCOPE' if arm=='A1_PACKED' and not executed else 'PASSIVE_EXECUTION_CANDIDATE')),'notes':'SAFE_BUCKET_PRESERVES_A0_PHYSICAL_COHORT' if arm=='A1_SAFE_BUCKET' and not bool(work.all()) else '','next_block_seed_token':-1};ledger.append(ev);traj.append(semantic_projection(ev))
     step+=1
  if input_ids.shape[1]==x.shape[1]:input_ids=x
  else:
   input_ids[:,: (block_idx+1)*block_size]=x[:,:-1]
   if bool((seq_block==block_idx).all()):input_ids=torch.cat([input_ids,x[:,-1:]],1)
   elif input_ids.shape[1]<=(block_idx+1)*block_size:input_ids=x
   else:input_ids[seq_block==block_idx,(block_idx+1)*block_size]=x[seq_block==block_idx,(block_idx+1)*block_size]
  seq_block[seq_block==block_idx]=block_idx+1
  if bool(finished.any()):
   for j in range(x.shape[0]):
    if bool(finished[j]):oid=int(samples[j]);done[oid]=x[j].clone();completion[request_ids[oid]]=time.perf_counter()-t0
   keep=~finished;samples=samples[keep];input_ids=input_ids[keep];seq_block=seq_block[keep];seq_len=seq_len[keep];x=x[keep]
   for l in range(len(past)):past.key_cache[l]=past.key_cache[l][keep];past.value_cache[l]=past.value_cache[l][keep]
   finished=finished[keep]
  if len(samples)==0:break
 if len(done)<batch_size:
  for j in range(x.shape[0]):oid=int(samples[j]);done[oid]=x[j].clone();completion[request_ids[oid]]=time.perf_counter()-t0
 return done,ledger,traj,stats,completion
