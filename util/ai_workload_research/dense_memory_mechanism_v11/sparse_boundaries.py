"""Sparse last-query rows in explicitly altered eager diagnostic;notnativeproof."""
from pathlib import Path
import hashlib
from persistence import save_json
class SparseBoundaries:
 def __init__(self,runner,model,path,torch):
  self.runner=runner;self.model=model;self.core=model.model;self.path=Path(path);self.torch=torch;self.handles=[];self.records=[];self.step=0;self.current=None;self.point='';self.bytes=0
 def begin(self,point):self.point=point;self.step=0
 def install(self):
  self.path.mkdir(exist_ok=False);self.original_forward=self.model.forward;self.original_sampler=type(self.runner.sampler).__call__;self.sampler_class=type(self.runner.sampler)
  def forward(*args,**kwargs):
   positions=kwargs.get('positions',args[1] if len(args)>1 else None)
   assert positions is not None
   p=positions.detach().cpu();indices=self.torch.nonzero(p==p.max(),as_tuple=False).flatten().long()
   self.current=dict(point=self.point,step=self.step,positions_max=int(p.max()),positions_shape=list(p.shape),indices=indices,boundaries={})
   return self.original_forward(*args,**kwargs)
  self.model.forward=forward
  targets=[('embedding',self.core.embed_tokens),('layer0',self.core.layers[0]),('layer17',self.core.layers[17]),('layer35',self.core.layers[35]),('norm',self.core.norm)]
  for label,module in targets:
   def hook(module,args,output,label=label):
    values=list(output) if isinstance(output,(tuple,list)) else [output]
    captured=[]
    for value in values:
     if self.torch.is_tensor(value):
      assert self.current is not None
      idx=self.current['indices'].to(value.device)
      assert int(idx.max())<value.shape[0]
      captured.append(value.detach().index_select(0,idx).cpu().clone())
     else:captured.append(None)
    self.current['boundaries'][label]=dict(tensors=captured,original_shapes=[list(v.shape) if self.torch.is_tensor(v) else None for v in values],
       semantic='hidden_plus_residual' if label.startswith('layer') else 'first_tensor')
   self.handles.append(module.register_forward_hook(hook))
  def sampler(instance,logits,batch):
   if instance is not self.runner.sampler:return self.original_sampler(instance,logits,batch)
   assert self.current is not None
   indices=batch.logits_indices.detach().cpu().long()
   assert self.torch.equal(indices,self.current['indices']),'Boundary/sample position identity mismatch'
   assert len(self.current['boundaries'])==5,'Boundary hooks did not execute'
   self.current.update(request_ids=list(batch.req_ids),num_tokens=batch.num_tokens,num_scheduled_tokens=batch.num_scheduled_tokens.tolist(),path='ALTERED_EAGER_NOT_NATIVE',logits_dtype=str(logits.dtype))
   result=self.original_sampler(instance,logits,batch)
   self.current['sampled_ids']=result.sampled_token_ids.detach().cpu().clone()
   f=self.path/(self.point+f'_step{self.step:02d}.pt');tmp=f.with_suffix('.writing');self.torch.save(self.current,tmp);tmp.replace(f);self.bytes+=f.stat().st_size
   assert self.bytes<16777216,'Sparse boundary tensor budget'
   self.records.append(dict(point=self.point,step=self.step,path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),request_ids=list(batch.req_ids),position_max=self.current['positions_max']))
   self.step+=1;self.current=None;return result
  self.sampler_class.__call__=sampler
 def finish(self,completion):save_json(self.path/'INDEX.json',self.receipt())
 def receipt(self):return dict(status='CAPTURED_ALTERED_EAGER',records=self.records,private_bytes=self.bytes,scope='Selectedlast-queryrowsonly;notglobalearliestlayerandnotnativecompiledcausality',registered_boundaries=['embedding','layer0','layer17','layer35','norm'])
 def restore(self):
  for h in self.handles:h.remove()
  self.model.forward=self.original_forward;self.sampler_class.__call__=self.original_sampler
