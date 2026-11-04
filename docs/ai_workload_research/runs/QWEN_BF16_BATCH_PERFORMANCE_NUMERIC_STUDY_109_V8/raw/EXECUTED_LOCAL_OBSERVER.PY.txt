"""Separate post-formal observer; never attached to main/control timing."""
from pathlib import Path
import dataclasses,hashlib,json
from persistence import save_json
class LocalObserver:
 def __init__(self,runner,model,folder,torch):
  self.runner=runner;self.model=model;self.folder=Path(folder);self.torch=torch;self.records=[];self.step=0;self.point=None;self.pending=None;self.bytes=0;self.installed=False
 def begin(self,point):self.point=point;self.step=0;self.pending=None
 def install(self):
  if not type(self.runner.sampler).__module__.endswith('worker.gpu.sample.sampler'):raise NotImplementedError('Observer requires verified new GPU sampler path')
  self.folder.mkdir(exist_ok=False);self.original_logits=self.model.compute_logits;self.cls=type(self.runner.sampler);self.original_sampler=self.cls.__call__
  def logits(hidden_states):
   if self.step in [0,1,15,31]:self.pending=hidden_states.detach().cpu().clone()
   return self.original_logits(hidden_states)
  def sampler(instance,logits,input_batch):
   if instance is not self.runner.sampler:return self.original_sampler(instance,logits,input_batch)
   capture=self.step in [0,1,15,31];entry=None
   if capture:
    entry=dict(point=self.point,step=self.step,request_ids=list(input_batch.req_ids),num_reqs=input_batch.num_reqs,
      num_reqs_after_padding=input_batch.num_reqs_after_padding,num_tokens=input_batch.num_tokens,
      num_scheduled_tokens=input_batch.num_scheduled_tokens.tolist(),logits_shape=list(logits.shape),logits_dtype=str(logits.dtype),
      logits=logits.detach().cpu().clone(),hidden_states=self.pending,
      selected_positions=input_batch.positions[input_batch.logits_indices].detach().cpu().clone(),
      sampler_mode=instance.logprobs_mode,needs_logits_processing=instance.needs_logits_processing[input_batch.idx_mapping_np].tolist(),
      head_weight_dtype=str(self.model.lm_head.weight.dtype),head_dtype=str(getattr(self.model.logits_processor,'head_dtype',None)))
   out=self.original_sampler(instance,logits,input_batch)
   if capture:
    def cpu(v):
     if self.torch.is_tensor(v):return v.detach().cpu().clone()
     if dataclasses.is_dataclass(v):return {f.name:cpu(getattr(v,f.name)) for f in dataclasses.fields(v)}
     if isinstance(v,dict):return {str(k):cpu(x) for k,x in v.items()}
     if isinstance(v,(list,tuple)):return [cpu(x) for x in v]
     if hasattr(v,'tolist'):return v.tolist()
     if v is None or isinstance(v,(str,int,float,bool)):return v
     if hasattr(v,'__dict__'):return {k:cpu(x) for k,x in vars(v).items() if not k.startswith('_')}
     return str(type(v))
    entry['sampler_logprobs_output']=cpu(out.logprobs_tensors);entry['sampled_ids']=cpu(out.sampled_token_ids)
    ids=self.torch.unique(self.torch.topk(entry['logits'].float(),20,dim=-1).indices).long()
    entry['head_token_ids']=ids
    entry['head_weight_rows']=self.model.lm_head.weight.detach().index_select(0,ids.to(self.model.lm_head.weight.device)).cpu().clone()
    path=self.folder/(self.point+f"_step{self.step:02d}.pt");tmp=path.with_suffix('.writing')
    self.torch.save(entry,tmp);tmp.replace(path);self.bytes+=path.stat().st_size
    assert self.bytes<=33554432,'Observer private tensor budget exceeded'
    self.records.append(dict(point=self.point,step=self.step,file=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
       request_ids=entry['request_ids'],logits_shape=entry['logits_shape'],logits_dtype=entry['logits_dtype'],num_tokens=entry['num_tokens'],num_scheduled_tokens=entry['num_scheduled_tokens'],sampler_mode=entry['sampler_mode']))
    save_json(self.folder/'INDEX.json',self.receipt())
   self.step+=1;return out
  self.model.compute_logits=logits;self.cls.__call__=sampler;self.installed=True
 def finish(self):pass
 def restore(self):
  if self.installed:self.model.compute_logits=self.original_logits;self.cls.__call__=self.original_sampler;self.installed=False
 def receipt(self):return dict(status='CAPTURED' if self.records else 'NO_CAPTURE',records=self.records,private_tensor_bytes=self.bytes,timing_role='OBSERVER_NOT_FORMAL',unchanged_model_dtype=True)
