"""V1 compiled canary and formal observation; no profiler, hooks, or fallback."""
import os,sys,pathlib,json,time,hashlib,traceback,signal,csv
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';phase=sys.argv[1];procid=int(sys.argv[2]) if len(sys.argv)>2 else -1
check={'phase':phase,'process':procid,'status':'RUNNING','edge_checks':[],'numeric_checks':[]}
def save(): (raw/f'{phase}_{procid}_checks.json').write_text(json.dumps(check,indent=2,default=str)+'\n',encoding='utf-8')
def fail(msg):raise RuntimeError(msg)
try:
 assert 'TASK_GPU_LOCK_START_MONOTONIC' in os.environ
 import torch, numpy as np, ase.io
 from nequip.utils.global_state import set_global_state
 set_global_state(allow_tf32=False);torch.set_default_dtype(torch.float32);torch.set_num_threads(8)
 assert torch.__version__=='2.10.0+cu126' and torch.backends.fp32_precision=='ieee' and not torch.is_autocast_enabled()
 assert not any(k.startswith('NEQUIP_') and k.endswith('_MODEL_TOL') for k in os.environ)
 from nequip.data import AtomicDataDict as A
 from nequip.data.transforms import NeighborListTransform,ChemicalSpeciesToAtomTypeMapper
 from nequip.model.saved_models.load_utils import load_saved_model
 from nequip.model.modify_utils import modify
 import openequivariance
 from nequip.model.inference_models.aotinductor import load_aotinductor_model
 modelpath=root/'inputs/NequIP-OAM-S-0.1.nequip.zip';product=root/'OAM-S.nequip.pt2'
 ref=load_saved_model(str(modelpath),compile_mode='eager').eval().to('cuda')
 eager=load_saved_model(str(modelpath),compile_mode='eager').eval().to('cuda');eager=modify(eager,[{'modifier':'enable_OpenEquivariance'}])
 compiled,meta=load_aotinductor_model(str(product),'cuda');compiled.eval()
 assert float(meta['r_max'])==4.5 and meta['model_dtype']=='float32' and meta['type_names']==ref.type_names
 check['compiled_sha256']=hashlib.sha256(product.read_bytes()).hexdigest();check['compiled_metadata']=meta;save()
 mapper=ChemicalSpeciesToAtomTypeMapper(model_type_names=ref.type_names)
 nlc=NeighborListTransform(r_max=4.5,backend='matscipy');nlg=NeighborListTransform(r_max=4.5,backend='alchemiops',backend_kwargs={'max_neighbors':128})
 atoms=ase.io.read(root/'inputs/sitraj.xyz',index=':');ids=[0,109] if phase=='compiled_canary' else [(2*i+1)*110//64 for i in range(32)]
 records={i:{'positions':np.asarray(atoms[i].positions,dtype=np.float32),'cell':np.asarray(atoms[i].cell.array,dtype=np.float32),'pbc':atoms[i].pbc.copy(),'numbers':atoms[i].numbers.copy()} for i in ids}
 for r in records.values():
  for a in r.values():a.flags.writeable=False
 fields=[A.PER_ATOM_ENERGY_KEY,A.TOTAL_ENERGY_KEY,A.FORCE_KEY,A.STRESS_KEY]
 def prep(group):
  ds=[]
  for i in group:
   r=records[i];ds.append({A.POSITIONS_KEY:torch.tensor(r['positions'],dtype=torch.float32),A.CELL_KEY:torch.tensor(r['cell'],dtype=torch.float32).reshape(1,3,3),A.PBC_KEY:torch.tensor(r['pbc']).reshape(1,3),A.ATOMIC_NUMBERS_KEY:torch.tensor(r['numbers'],dtype=torch.long)})
  return mapper(A.batched_from_list(ds))
 def graph(group,gpu):
  d=prep(group)
  if gpu:return nlg(A.to_(d,'cuda'))
  return nlc(d)
 def canon(d,group):
  e=d[A.EDGE_INDEX_KEY].detach().cpu().numpy();s=d[A.EDGE_CELL_SHIFT_KEY].detach().cpu().numpy();b=d[A.BATCH_KEY].detach().cpu().numpy().reshape(-1)
  assert np.isfinite(s).all() and np.array_equal(s,np.rint(s))
  assert e.shape[0]==2 and e.min()>=0 and e.max()<64*len(group)
  assert np.array_equal(b[e[0]],b[e[1]]),'CROSS_FRAME_EDGE'
  assert not ((e[0]==e[1]) & (s==0).all(1)).any(),'ZERO_SHIFT_SELF_EDGE'
  count=np.bincount(e[0],minlength=64*len(group));assert count.max()<=128,'NEIGHBOR_CAPACITY_EXCEEDED'
  rows=np.column_stack((np.asarray(group)[b[e[0]]],e[0]%64,e[1]%64,s.astype(np.int64)))
  rows=rows[np.lexsort(tuple(rows[:,j] for j in range(5,-1,-1)))]
  return rows,int(count.max())
 # Exact directed periodic edge multiset, including multiplicities, only outside timing.
 singles=[]
 for i in ids:
  d=graph([i],False);r,count=canon(d,[i]);singles.append(r)
 baseline=np.concatenate(singles);baseline=baseline[np.lexsort(tuple(baseline[:,j] for j in range(5,-1,-1)))]
 np.save(raw/f'{phase}_{procid}_cpu_single_edges.npy',baseline)
 def edgegate(B,gpu):
  collected=[];maxn=0
  for offset in range(0,len(ids),B):
   group=ids[offset:offset+B];d=graph(group,gpu);r,c=canon(d,group);collected.append(r);maxn=max(maxn,c)
  rows=np.concatenate(collected);rows=rows[np.lexsort(tuple(rows[:,j] for j in range(5,-1,-1)))]
  np.save(raw/f'{phase}_{procid}_{"G" if gpu else "C"}{B}_edges.npy',rows)
  ok=np.array_equal(rows,baseline);item={'B':B,'backend':'alchemiops' if gpu else 'matscipy','exact_multiset_equal':ok,'edges':len(rows),'max_neighbors':maxn}
  if not ok:
   item['reference_shape']=list(baseline.shape);item['candidate_shape']=list(rows.shape)
   if rows.shape==baseline.shape:
    idx=np.flatnonzero((rows!=baseline).any(1))[0];item['first_difference']={'index':int(idx),'cpu_single':baseline[idx].tolist(),'candidate':rows[idx].tolist()}
  check['edge_checks'].append(item);save()
  assert ok,'EDGE_MULTISET_MISMATCH'
 conditions=[('N-C2',2,False),('N-G2',2,True),('N-G4',4,True),('N-G8',8,True)] if phase=='formal' else [('N-C2',2,False),('N-G2',2,True)]
 for name,B,gpu in conditions:edgegate(B,gpu)
 def sweep(model,B,gpu,diagnostic=False):
  vals={k:[] for k in fields};stages=[]
  for offset in range(0,len(ids),B):
   group=ids[offset:offset+B]
   if diagnostic:torch.cuda.synchronize();t0=time.perf_counter_ns()
   d=prep(group)
   if diagnostic:t1=time.perf_counter_ns()
   if gpu:d=A.to_(d,'cuda')
   if diagnostic:torch.cuda.synchronize();t2=time.perf_counter_ns();ev0=torch.cuda.Event(enable_timing=True);ev1=torch.cuda.Event(enable_timing=True);ev0.record()
   d=(nlg if gpu else nlc)(d)
   if diagnostic:ev1.record();torch.cuda.synchronize();t3=time.perf_counter_ns();nlms=ev0.elapsed_time(ev1);t4start=time.perf_counter_ns()
   if not gpu:d=A.to_(d,'cuda')
   if diagnostic:torch.cuda.synchronize();t4=time.perf_counter_ns();ev0.record()
   out=model(d)
   if diagnostic:ev1.record();torch.cuda.synchronize();t5=time.perf_counter_ns();modelms=ev0.elapsed_time(ev1)
   for k in fields:
    v=out[k].detach().cpu();vals[k].append(v)
   if diagnostic:
    t6=time.perf_counter_ns();stages.append({'offset':offset,'prepare_ns':t1-t0,'input_transfer_ns':t2-t1,'neighbor_wall_ns':t3-t2,'graph_transfer_ns':t4-t4start,'model_wall_ns':t5-t4,'output_transfer_ns':t6-t5,'neighbor_event_ms':nlms if gpu else None,'model_event_ms':modelms})
  return {k:torch.cat(v,dim=0) for k,v in vals.items()},stages
 def trials(model,B,gpu,label):
  out=[]
  for _ in range(5):out.append(sweep(model,B,gpu)[0])
  v={k:torch.stack([o[k] for o in out]) for k in fields};assert all(torch.isfinite(x).all() for x in v.values()),'NONFINITE_OUTPUT';torch.save(v,raw/f'{phase}_{procid}_{label}.pt');return v
 def numeric(left,right,label):
  results=[]
  for k in fields:
   a=left[k].double().mean(0);b=right[k].double().mean(0);delta=(a-b).abs();ok=torch.isclose(a,b,atol=5e-5,rtol=5e-5)
   results.append({'field':k,'max_abs_diff':delta.max().item(),'pass':bool(ok.all()),'shape':list(a.shape),'failed_elements':int((~ok).sum()),'first_failures':[{'index':i.tolist(),'reference':a[tuple(i)].item(),'candidate':b[tuple(i)].item(),'abs_diff':delta[tuple(i)].item()} for i in (~ok).nonzero()[:100]]})
  check['numeric_checks'].append({'comparison':label,'results':results,'pass':all(r['pass'] for r in results)});save();assert all(r['pass'] for r in results),label
 reference=trials(ref,1,False,'reference_a');refb=trials(ref,1,False,'reference_b');numeric(reference,refb,'REFERENCE_REPEATABILITY')
 numeric(reference,trials(eager,1,False,'eager_oeq_single'),'REFERENCE_VS_EAGER_OEQ_SINGLE')
 numeric(reference,trials(eager,2,False,'eager_oeq_batch2'),'REFERENCE_VS_EAGER_OEQ_BATCH2')
 for name,B,gpu in conditions:numeric(reference,trials(compiled,B,gpu,name),'REFERENCE_VS_COMPILED_'+name)
 if phase=='compiled_canary':check['status']='PASS';save();sys.exit(0)
 # Every fresh formal process repeats all gates before its own timing.
 for name,B,gpu in conditions:
  for _ in range(2):sweep(compiled,B,gpu)
 torch.cuda.synchronize();check['warmup_status']='PASS';save()
 # AOT and Warp/OEQ cache snapshots detect compilation or new kernel files during observation.
 def cache_identity():
  result={}
  for folder in ['torch_extensions','torchinductor','warp']:
   for p in (root/'cache'/folder).rglob('*'):
    if p.is_file() and p.suffix in ['.so','.cubin','.ptx','.fatbin','.o']:
     result[str(p.relative_to(root))]={'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns}
  return result
 pre_cache=cache_identity();check['cache_before_timing']=pre_cache;save()
 names=[c[0] for c in conditions];mapping={name:(B,gpu) for name,B,gpu in conditions}
 samples=[];formal_start=time.monotonic()
 with (raw/f'timing_process_{procid}.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['process','block','order','condition','wall_ns','frames','atoms','batches']);w.writeheader()
  for block in range(12):
   shift=(block+procid)%4;order=names[shift:]+names[:shift]
   for oi,name in enumerate(order):
    B,gpu=mapping[name];torch.cuda.synchronize();start=time.perf_counter_ns();out,_=sweep(compiled,B,gpu);torch.cuda.synchronize();elapsed=time.perf_counter_ns()-start
    assert all(torch.isfinite(v).all() for v in out.values()),'NONFINITE_OUTPUT'
    row={'process':procid,'block':block,'order':oi,'condition':name,'wall_ns':elapsed,'frames':32,'atoms':2048,'batches':32//B};w.writerow(row);f.flush();samples.append(row)
   if cache_identity()!=pre_cache:fail('TIMING_CONTAMINATED_NEW_COMPILE_OR_KERNEL')
 check['timing_samples']=len(samples);check['timing_seconds']=time.monotonic()-formal_start;save()
 # Post-timing consistency remains subject to the same five-trial FP32 gate.
 for name,B,gpu in conditions:numeric(reference,trials(compiled,B,gpu,'post_'+name),'POST_REFERENCE_VS_COMPILED_'+name)
 diagnostics=[]
 for name,B,gpu in (conditions if procid==2 else []):
  torch.cuda.reset_peak_memory_stats()
  for trial in range(3):
   out,stages=sweep(compiled,B,gpu,diagnostic=True)
   for stage in stages:diagnostics.append({'process':procid,'condition':name,'sweep':trial,**stage,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved()})
 (raw/f'diagnostics_{procid}.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
 check['status']='PASS';check['cache_after_timing']=cache_identity();save()
except Exception as e:
 check.update(status='STOP',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save();print(check['traceback'],flush=True);sys.exit(1)
