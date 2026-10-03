#!/usr/bin/env python3
"""R27R2 varied-stream wrapper around the frozen R26 tied-W component."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
import torch

R26_DIR=Path(__file__).resolve().parents[1]/'r26_tied_weight_production_capacity';sys.path.insert(0,str(R26_DIR))
_r26_spec=importlib.util.spec_from_file_location('r26_frozen_component',R26_DIR/'component.py');r26=importlib.util.module_from_spec(_r26_spec);sys.modules[_r26_spec.name]=r26;_r26_spec.loader.exec_module(r26)

STAGE='AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1';BANK_SHA='7ad359882a1a7153cd7c0d9321af53ac38fa17908cff1355a89696aec2c61387'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(memoryview(t.detach().contiguous().cpu().view(torch.uint8).numpy())).hexdigest()
class VariedTiedWeightTrainer(r26.TiedWeightTrainer):
 def __init__(self,model_path,bank_path,batch,legacy_tokens_path,common_path=None,checkpoint=None):
  self._bank_ready=False
  super().__init__(model_path,legacy_tokens_path,batch,checkpoint=None)
  migration=None
  if common_path:
   legacy=r26.TiedWeightTrainer.load_checkpoint(self,common_path);migration={'source_path':str(common_path),'source_sha256':sha(common_path),'source_schema':legacy['schema'],'source_step':legacy['step'],'source_identity':legacy['identity'],'W_m_v_RNG_unchanged':True};del legacy
  obj=torch.load(bank_path,map_location='cpu',weights_only=False);bank=obj['bank']
  if tuple(bank.shape)!=(33,128,128) or bank.dtype!=torch.int64 or tsha(bank)!=BANK_SHA or obj.get('bank_sha256')!=BANK_SHA:raise RuntimeError('bank identity mismatch')
  self.bank_path=Path(bank_path);self.bank_file_sha=sha(bank_path);self.bank=bank.contiguous();self.bank_sha=BANK_SHA;self.stream_cursor=0;self.migration=migration
  self.input_ids=torch.empty((batch,127),dtype=torch.int64,device='cuda:0');self.labels=torch.empty((batch*127,),dtype=torch.int64,device='cuda:0');self.attention=torch.ones_like(self.input_ids);self.binding=None;self._bank_ready=True
  if checkpoint:self.load_checkpoint(checkpoint)
 def _checkpoint_identity(self):
  if not getattr(self,'_bank_ready',False):return super()._checkpoint_identity()
  return {'model_id':r26.MODEL_ID,'revision':r26.REVISION,'weight_shape':[r26.V,r26.H],'weight_dtype':'torch.bfloat16','optimizer_sha256':r26.canonical_sha(r26.OPTIMIZER),'bank_sha256':self.bank_sha,'bank_shape':[33,128,128],'step_semantics':'bank cursor k; input 0:127 labels 1:128'}
 def bind_step(self,index):
  if index<0 or index>32:raise RuntimeError(f'bank index {index}')
  cpu_i=self.bank[index,:self.batch,:127].contiguous();cpu_l=self.bank[index,:self.batch,1:].contiguous();self.input_ids.copy_(cpu_i);self.labels.copy_(cpu_l.reshape(-1));torch.cuda.synchronize();self.binding={'bank_index':index,'batch':self.batch,'input_shape':list(cpu_i.shape),'labels_shape':list(cpu_l.shape),'input_ids_sha256':tsha(cpu_i),'labels_sha256':tsha(cpu_l)};return self.binding
 def run_stream_step(self,policy='c1',index=None,diagnostic=False,timed=False):
  index=self.stream_cursor if index is None else index
  if index!=self.stream_cursor:raise RuntimeError(f'cursor mismatch requested={index} current={self.stream_cursor}')
  binding=self.bind_step(index);result=super().run_step(policy,diagnostic=diagnostic,timed=timed);self.stream_cursor=index+1;result.update({'stream_cursor_before':index,'stream_cursor_after':self.stream_cursor,'input_ids_sha256':binding['input_ids_sha256'],'labels_sha256':binding['labels_sha256']});return result
 @torch.no_grad()
 def next_loss_at(self,index):
  self.bind_step(index);return super().next_loss()
 def authority(self):
  x=super().authority();x.update({'stage':STAGE,'bank_path':str(self.bank_path),'bank_file_sha256':self.bank_file_sha,'bank_tensor_sha256':self.bank_sha,'bank_shape':[33,128,128],'stream_cursor':self.stream_cursor,'full_bank_GPU_mirror':False,'migration':self.migration});return x
 def snapshot_cpu(self,policy):
  x=super().snapshot_cpu(policy);x.update({'schema':'R27R2_VARIED_TIED_WEIGHT_CHECKPOINT_V1','identity':self._checkpoint_identity(),'stream_cursor':int(self.stream_cursor),'bank_sha256':self.bank_sha});return x
 def save_checkpoint(self,path,policy):
  state=self.snapshot_cpu(policy);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);torch.save(state,path);receipt={'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'step':state['step'],'stream_cursor':state['stream_cursor'],'policy_metadata':policy,'weight_sha256':tsha(state['weight']),'m_sha256':tsha(state['m']),'v_sha256':tsha(state['v']),'cpu_rng_sha256':tsha(state['cpu_rng']),'cuda_rng_sha256':tsha(state['cuda_rng']),'bank_sha256':self.bank_sha,'contains_GPU_tensor':False};return state,receipt
 def load_checkpoint(self,path):
  state=torch.load(path,map_location='cpu',weights_only=False)
  if state.get('schema')!='R27R2_VARIED_TIED_WEIGHT_CHECKPOINT_V1' or state.get('identity')!=self._checkpoint_identity() or state.get('bank_sha256')!=self.bank_sha:raise RuntimeError('varied checkpoint identity mismatch')
  for n in ('weight','m','v','cpu_rng','cuda_rng'):
   if not isinstance(state.get(n),torch.Tensor) or state[n].device.type!='cpu':raise RuntimeError(f'checkpoint tensor {n}')
  with torch.no_grad():self.weight.copy_(state['weight']);self.m.copy_(state['m']);self.v.copy_(state['v'])
  self.step=int(state['step']);self.stream_cursor=int(state['stream_cursor']);self.weight.grad=None;self.collector.reset();torch.set_rng_state(state['cpu_rng']);torch.cuda.set_rng_state(state['cuda_rng'],device='cuda:0');torch.cuda.synchronize();self._assert_tied();return state
 def restore_common(self,path):
  ready=self._bank_ready;self._bank_ready=False
  try:state=r26.TiedWeightTrainer.load_checkpoint(self,path)
  finally:self._bank_ready=ready
  self.stream_cursor=0;return state
