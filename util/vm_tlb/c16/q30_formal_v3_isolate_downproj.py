#!/usr/bin/env python3
import argparse,hashlib,json,os,torch
from pathlib import Path
from util.vm_tlb.c16.qwen3_30b.q30_s0_executor import Q30,thaw,load_blob,tinfo,REV,LAYER
def sha(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def capture(a):
 out=Path(a.out);out.mkdir(parents=True,exist_ok=False);call=load_blob(Path(a.bundle)/'call_boundary.pt');q=Q30(a.model_root);m=q.model.model.layers[LAYER];q.on(m,'model.layers.24.');cap={}
 def pre(mod,args):cap['input']=args[0].detach().cpu().contiguous()
 def post(mod,args,result):cap['output']=result.detach().cpu().contiguous()
 hs=[m.mlp.experts[21].down_proj.register_forward_pre_hook(pre),m.mlp.experts[21].down_proj.register_forward_hook(post)]
 try:
  with torch.inference_mode():
   full=m(call['hidden_states'].to('cuda'),**thaw(call));fullout=full[0].cpu()
 finally:
  [x.remove() for x in hs];q.off(m)
 torch.save({'input':cap['input'],'in_context_output':cap['output'],'full_layer_output_sha256':tinfo(fullout)['sha256'],'expert_id':21,'projection':'down_proj'},out/'EXACT_NATURAL_DOWNPROJ_STATE.pt')
 print(json.dumps({'status':'CAPTURED','input':tinfo(cap['input']),'output':tinfo(cap['output']),'sha256':sha(out/'EXACT_NATURAL_DOWNPROJ_STATE.pt')}))
def replay(a):
 p=Path(a.artifact);d=torch.load(p,map_location='cpu',weights_only=True);q=Q30(a.model_root);m=q.model.model.layers[LAYER];q.on(m,'model.layers.24.')
 try:
  with torch.inference_mode():
   inp=d['input'].to('cuda');mod=m.mlp.experts[21].down_proj;gpu=mod(inp);o=gpu.cpu()
   if a.address_context:
    qctx={'input':{'ptr':hex(inp.data_ptr()),'bytes':inp.numel()*inp.element_size(),'shape':list(inp.shape),'dtype':str(inp.dtype)},'weight':{'ptr':hex(mod.weight.data_ptr()),'bytes':mod.weight.numel()*mod.weight.element_size(),'shape':list(mod.weight.shape),'dtype':str(mod.weight.dtype)},'output':{'ptr':hex(gpu.data_ptr()),'bytes':gpu.numel()*gpu.element_size(),'shape':list(gpu.shape),'dtype':str(gpu.dtype)}}
    Path(a.address_context).write_text(json.dumps(qctx,sort_keys=True,indent=2)+'\n')
 finally:q.off(m)
 print(json.dumps({'status':'PASS' if torch.equal(o,d['in_context_output']) else 'FAIL','input':tinfo(d['input']),'output':tinfo(o),'expected':tinfo(d['in_context_output']),'bitwise':torch.equal(o,d['in_context_output'])}))
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('capture','replay'),required=True);p.add_argument('--model-root',required=True);p.add_argument('--bundle');p.add_argument('--out');p.add_argument('--artifact');p.add_argument('--address-context');a=p.parse_args();capture(a) if a.mode=='capture' else replay(a)
if __name__=='__main__':main()
