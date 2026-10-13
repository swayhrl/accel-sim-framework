"""Bounded numerical controls. All GPU invocations require actual inherited flock."""
import argparse,hashlib,importlib.util,json,math,os,sys,time
from collections import Counter
from pathlib import Path
import numpy as np
import torch
torch.set_num_threads(4)
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r27r2_history',HERE.parent/'r27r2_varied_batch_capacity/component.py');old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
r26=old.r26
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def load(p):return torch.load(p,map_location='cpu',weights_only=False)
def metrics(got,ref,ids=None,labels=None):
 assert got.shape==ref.shape and got.dtype==ref.dtype
 a=got.reshape(-1);b=ref.reshape(-1);first=[];tops=[];count=0;mx=total=dot=na=nb=0.;finite=True;allbit=True;maxrel=0.
 freq=Counter(ids.tolist()) if ids is not None else {};labfreq=Counter(labels.tolist()) if labels is not None else {}
 def coord(i,av,bv,d,e):
  row=i//ref.shape[-1] if ref.ndim>1 else i;col=i%ref.shape[-1] if ref.ndim>1 else 0
  return {'flat_index':int(i),'row':int(row),'column':int(col),'candidate':float(av),'reference':float(bv),'abs_diff':float(d),'allowed':float(d-e),'excess':float(e),'input_frequency':int(freq.get(row,0)),'label_frequency':int(labfreq.get(row,0))}
 for start in range(0,a.numel(),1<<18):
  av=a[start:start+(1<<18)].float().numpy();bv=b[start:start+(1<<18)].float().numpy();d=np.abs(av-bv);bound=.01+.01*np.abs(bv);ex=d-bound;bad=np.flatnonzero(ex>0);count+=len(bad);finite &= bool(np.isfinite(av).all() and np.isfinite(bv).all());allbit &= bool(np.array_equal(av,bv));mx=max(mx,float(d.max(initial=0)));total+=float(d.sum(dtype=np.float64));maxrel=max(maxrel,float(np.max(d/np.maximum(np.abs(bv),1e-30),initial=0)));aa=av.astype(np.float64);bb=bv.astype(np.float64);dot+=float(np.dot(aa,bb));na+=float(np.dot(aa,aa));nb+=float(np.dot(bb,bb))
  if len(bad):
   if len(first)<32:
    for k in bad[:32-len(first)]:first.append(coord(start+k,av[k],bv[k],d[k],ex[k]))
   if len(bad)>32:
    loc=np.argpartition(-ex[bad],31)[:32];cut=ex[bad[loc]].min();cand=bad[ex[bad]>=cut];order=np.lexsort((cand,-ex[cand]));take=cand[order[:32]]
   else:take=bad[np.lexsort((bad,-ex[bad]))]
   tops.extend(coord(start+k,av[k],bv[k],d[k],ex[k]) for k in take);tops.sort(key=lambda x:(-x['excess'],x['flat_index']));tops=tops[:32]
 return {'shape':list(ref.shape),'dtype':str(ref.dtype),'numel':a.numel(),'finite':finite,'qualified':finite and count==0,'bitwise_values_equal':allbit,'violations':count,'violation_fraction':count/a.numel() if a.numel() else 0.,'max_abs':mx,'mean_abs':total/a.numel() if a.numel() else 0.,'max_rel_secondary_nearzero_sensitive':maxrel,'cosine':dot/math.sqrt(na*nb) if na and nb else 1.,'first32_row_major':first,'top32_tolerance_excess':tops}
def trainer(a):
 assert os.environ.get('R27R3_GPU_LOCK_HELD')=='1'
 return old.VariedTiedWeightTrainer(a.model,a.bank,1,a.legacy,common_path=a.common)
def repeat(a):
 t=trainer(a);t.bind_step(0);torch.cuda.reset_peak_memory_stats();result=t.run_stream_step('b0',index=0,diagnostic=True);n=t.next_loss_at(1);s=t.snapshot_cpu('b0');s.update(result['diagnostic_tensors']);s.update({'loss':result['loss'],'next_loss':n,'run_id':a.run_id,'input_ids':t.bank[0,0,:127].clone(),'labels':t.bank[0,0,1:].clone()});p=Path(a.root)/'raw'/f'B0_{a.run_id}.pt';torch.save(s,p)
 env={'run_id':a.run_id,'pid':os.getpid(),'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(),'meta':t.meta,'common_file':a.common,'bank_file':a.bank,'step':s['step'],'cursor':s['stream_cursor'],'loss':s['loss'],'next_loss':n,'full_peak_allocated':torch.cuda.max_memory_allocated(),'result':{k:v for k,v in result.items() if k!='diagnostic_tensors'},'raw_path':str(p),'raw_bytes':p.stat().st_size,'tie':t.weight.data_ptr()==t.model.get_output_embeddings().weight.data_ptr()}
 dump(Path(a.root)/'raw'/f'B0_{a.run_id}_RECEIPT.json',env);t.close();print(json.dumps({'repeat':a.run_id,'completed':True,'raw_bytes':p.stat().st_size}),flush=True)
def compare_repeats(a):
 root=Path(a.root);ref=load(root/'raw/B0_a.pt');got=load(root/'raw/B0_b.pt');out={}
 for n in ('loss','next_loss'):
  d=abs(got[n]-ref[n]);out[n]={'reference':ref[n],'candidate':got[n],'abs_diff':d,'allowed':.01+.01*abs(ref[n]),'qualified':math.isfinite(got[n]) and d<=.01+.01*abs(ref[n])}
 for n in ('dH','gradient','weight','m','v'):out[n]=metrics(got[n],ref[n],ref['input_ids'],ref['labels'])
 for n in ('step','stream_cursor'):out[n]={'reference':ref[n],'candidate':got[n],'qualified':got[n]==ref[n]}
 receipts=[json.loads((root/'raw'/f'B0_{i}_RECEIPT.json').read_text()) for i in ('a','b')];ok=all(x['qualified'] for x in out.values()) and all(x['tie'] for x in receipts);dump(root/'raw/B0_REPEATABILITY.json',{'qualified':ok,'label':'B0_REPEATABLE' if ok else 'R27R3_B0_REFERENCE_NOT_REPEATABLE','metrics':out,'receipts':receipts,'no_selected_favorable_pair':True});print(json.dumps({'qualified':ok,'violations':{k:v.get('violations',0) for k,v in out.items()}}));return ok
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['repeat','compare_repeats'],required=True);p.add_argument('--root',required=True);p.add_argument('--model');p.add_argument('--bank');p.add_argument('--common');p.add_argument('--legacy');p.add_argument('--run-id');a=p.parse_args();repeat(a) if a.mode=='repeat' else compare_repeats(a)
if __name__=='__main__':main()
