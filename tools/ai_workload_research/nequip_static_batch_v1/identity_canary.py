"""Frozen V1 identity and canary gates. Run only under supervise.py gpu."""
import os,pathlib,json,hashlib,traceback,sys,time
root=pathlib.Path(os.environ['TASK_DATA']);raw=root/'raw';status={'stage':'identity_canary','status':'RUNNING','checks':[]}
def save(): (raw/'identity_canary.json').write_text(json.dumps(status,indent=2,default=str)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 assert 'TASK_GPU_LOCK_START_MONOTONIC' in os.environ
 assert not any(k.startswith('NEQUIP_') and k.endswith('_MODEL_TOL') for k in os.environ)
 import torch
 import numpy as np
 import ase.io
 from nequip.utils.global_state import set_global_state
 set_global_state(allow_tf32=False)
 torch.set_default_dtype(torch.float32)
 torch.set_num_threads(8)
 assert torch.__version__=='2.10.0+cu126'
 assert torch.get_default_dtype()==torch.float32
 assert not torch.is_autocast_enabled()
 assert torch.backends.fp32_precision=='ieee'
 from nequip.model.saved_models.load_utils import load_saved_model
 from nequip.data import AtomicDataDict as A
 from nequip.data.transforms import NeighborListTransform,ChemicalSpeciesToAtomTypeMapper
 modelpath=root/'inputs/NequIP-OAM-S-0.1.nequip.zip'
 assert hashlib.md5(modelpath.read_bytes()).hexdigest()=='399a98bf36fc4550bc85d48f35451c6c'
 assert sha(root/'inputs/sitraj.xyz')=='c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770'
 atoms=ase.io.read(root/'inputs/sitraj.xyz',index=':');assert len(atoms)==110
 selected=[(2*i+1)*110//64 for i in range(32)]
 geoms=[]
 for i,a in enumerate(atoms):
  assert len(a)==64 and (a.numbers==14).all()
  assert np.isfinite(a.positions).all() and np.isfinite(a.cell.array).all()
  assert np.linalg.det(a.cell.array)>0 and a.pbc.all()
  geoms.append(hashlib.sha256(a.positions.tobytes()+a.cell.array.tobytes()+a.pbc.tobytes()).hexdigest())
 manifest={'input_sha256':sha(root/'inputs/sitraj.xyz'),'bytes':(root/'inputs/sitraj.xyz').stat().st_size,'canary':[0,109],'formal':selected,'frames':110,'atoms_per_frame':64,'species':'Si','duplicate_geometry_groups':[[i for i,h in enumerate(geoms) if h==g] for g in sorted(set(geoms)) if geoms.count(g)>1],'geometry_sha256':geoms,'dtype':'float32','source_commit':'8f90935ba42fd9e03df323cf03428c456d87b881'}
 (raw/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 status['checks'].append({'gate':'input_geometry','status':'PASS'});save()
 model=load_saved_model(str(modelpath),compile_mode='eager');model.eval()
 metadata=model.metadata;types=model.type_names
 status['model']={'metadata':metadata,'type_names':types,'model_class':str(type(model)),'model_dtype':str(model.model_dtype),'floating_parameter_dtypes':sorted({str(p.dtype) for p in model.parameters() if p.is_floating_point()}),'floating_buffer_dtypes':sorted({str(p.dtype) for p in model.buffers() if p.is_floating_point()}),'parameter_count':sum(p.numel() for p in model.parameters()),'model_sha256':sha(modelpath),'torch':torch.__version__,'cuda':torch.version.cuda,'tf32':torch.backends.fp32_precision,'autocast':torch.is_autocast_enabled(),'module_classes':{n:str(type(m)) for n,m in model.named_modules()}};save()
 assert model.model_dtype==torch.float32 and metadata['model_dtype']=='float32'
 assert all(p.dtype==torch.float32 for p in model.parameters() if p.is_floating_point())
 assert float(metadata['r_max'])==4.5 and 'Si' in types
 # Native ZBL prefactor distinguishes eV/Angstrom (metal) from kcal/mol (real).
 zbl=[(n,m) for n,m in model.named_modules() if hasattr(m,'_qqr2exesquare')]
 units=[{'module':n,'prefactor_half':m._qqr2exesquare.detach().cpu().item(),'native_expected_metal_half':torch.tensor(14.399645/2,dtype=m._qqr2exesquare.dtype).item()} for n,m in zbl]
 status['units']={'native_units':'eV, Angstrom, eV/Angstrom forces, eV/Angstrom^3 stress','basis':'Packaged ZBL source metal prefactor 14.399645/2 plus native force/stress coordinate/cell derivatives','zbl_prefactors':units};save()
 assert units and all(x['prefactor_half']==x['native_expected_metal_half'] for x in units),'UNITS_IDENTITY_UNRESOLVED'
 fields=[A.PER_ATOM_ENERGY_KEY,A.TOTAL_ENERGY_KEY,A.FORCE_KEY,A.STRESS_KEY]
 assert all(k in model.irreps_out for k in fields)
 assert not any('_tp_scatter_oeq' in str(type(m)) for m in model.modules())
 mapper=ChemicalSpeciesToAtomTypeMapper(model_type_names=types)
 nl=NeighborListTransform(r_max=4.5,backend='matscipy')
 def data(i):
  a=atoms[i]
  d={A.POSITIONS_KEY:torch.tensor(a.positions,dtype=torch.float32),A.CELL_KEY:torch.tensor(a.cell.array,dtype=torch.float32).reshape(1,3,3),A.PBC_KEY:torch.tensor(a.pbc).reshape(1,3),A.ATOMIC_NUMBERS_KEY:torch.tensor(a.numbers,dtype=torch.long)}
  return nl(mapper(d))
 # Preserve unmodified reference outputs from two five-trial arms.
 model=model.to('cuda')
 batches={};means={}
 for arm in ['reference_a','reference_b']:
  batches[arm]={}
  for i in [0,109]:
   rows={k:[] for k in fields}
   for trial in range(5):
    d=A.to_(data(i),'cuda');out=model(d)
    for k in fields:
     x=out[k].detach().cpu();assert torch.isfinite(x).all();rows[k].append(x)
   batches[arm][i]={k:torch.stack(v) for k,v in rows.items()}
  torch.save(batches[arm],raw/(arm+'.pt'))
 def compare(left,right,label):
  results=[]
  for i in [0,109]:
   for k in fields:
    a=left[i][k].double().mean(0);b=right[i][k].double().mean(0);delta=(a-b).abs();ok=torch.isclose(a,b,atol=5e-5,rtol=5e-5)
    item={'frame':i,'field':k,'shape':list(a.shape),'max_abs_diff':delta.max().item(),'pass':bool(ok.all()),'failures':[{'index':idx.tolist(),'reference':a[tuple(idx)].item(),'candidate':b[tuple(idx)].item(),'abs_diff':delta[tuple(idx)].item()} for idx in (~ok).nonzero()[:100]]};results.append(item)
  status['checks'].append({'gate':label,'results':results,'status':'PASS' if all(r['pass'] for r in results) else 'FAIL'});save()
  if not all(r['pass'] for r in results):raise RuntimeError(label)
 compare(batches['reference_a'],batches['reference_b'],'REFERENCE_REPEATABILITY')
 # Compiler takes a tensor container. Its batch transform duplicates this canary frame.
 d=data(0);d=A.batched_from_list([d])
 class TensorContainer(torch.nn.Module):
  def __init__(self,d):
   super().__init__()
   for k,v in d.items():self.register_buffer(k,v)
  def forward(self,x):return x
 torch.jit.trace(TensorContainer(d),torch.zeros(1)).save(str(root/'canary_tensor_container.pt'))
 status['compile_example_input_shapes']={k:list(v.shape) for k,v in d.items()}
 from nequip.scripts._compile_utils import batched_data_settings
 status['compile_transformed_shapes']={k:list(v.shape) for k,v in batched_data_settings(d).items()};save()
 # Native modifier retains its own verification; do not patch the model.
 from nequip.model.modify_utils import modify
 import openequivariance
 oeq=load_saved_model(str(modelpath),compile_mode='eager').eval().to('cuda')
 oeq=modify(oeq,[{'modifier':'enable_OpenEquivariance'}])
 classes={n:str(type(m)) for n,m in oeq.named_modules()};status['oeq_module_classes']=classes;save()
 assert any('_tp_scatter_oeq' in v for v in classes.values())
 rowsall={}
 for i in [0,109]:
  rows={k:[] for k in fields}
  for trial in range(5):
   out=oeq(A.to_(data(i),'cuda'))
   for k in fields:
    x=out[k].detach().cpu();assert torch.isfinite(x).all();rows[k].append(x)
  rowsall[i]={k:torch.stack(v) for k,v in rows.items()}
 torch.save(rowsall,raw/'eager_oeq_canary.pt');compare(batches['reference_a'],rowsall,'REFERENCE_VS_EAGER_OEQ')
 status['status']='PASS_PRECOMPILE';save()
except Exception as e:
 status.update(status='STOP',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save();print(status['traceback'],flush=True);sys.exit(1)
print(json.dumps({'status':status['status'],'metadata':status.get('model',{}).get('metadata')}),flush=True)
