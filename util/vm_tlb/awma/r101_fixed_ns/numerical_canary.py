#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gc,hashlib,json,traceback
from pathlib import Path
import torch
import torch.nn.functional as F
from himuon.optimizers.himuon import HiMuon
from himuon.triton_kernels import ns5_smem

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
COEFS=(3.4445,-4.7750,2.0315)
STEPS=5

def sha_tensor(t):return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

@torch.no_grad()
def fp32_reference(X):
    a,b,c=COEFS
    x=X.float()
    x=x/(x.norm(dim=(-2,-1),keepdim=True)+1e-7)
    for _ in range(STEPS):
        A=x@x.mT
        B=b*A+c*(A@A)
        x=a*x+B@x
    return x

def cosine(x,y):
    return float(F.cosine_similarity(x.float().flatten().unsqueeze(0),
                                     y.float().flatten().unsqueeze(0),dim=-1)[0])

def main(which):
    binding=json.loads((ROOT/f'R101_TILE_INPUT_RECEIPT_{which.upper()}.json').read_text())
    receipt={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
      'fixture':which,'source_commit':'af89eda9a0176effed99e1fe19cc1f8a1a2c9588',
      'same_map_pair':'S128 F128 ns5_smem versus K128 author compiled three-kernel',
      'five_steps':5,'coefficients':COEFS,'norm_epsilon':1e-7,
      'pair_rtol':1e-2,'pair_atol':1e-2,'status':'RUNNING','arms':{}}
    outputs={}
    rows=[]
    try:
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        torch.set_float32_matmul_precision('highest')
        edges=(128,256,512) if which=='discovery' else (128,512)
        for edge in edges:
            path=ROOT/'raw'/f'{which}_tiles_T{edge}.pt'
            if sha_file(path)!=binding['tiles'][str(edge)]['payload_sha256']:
                raise ValueError(f'tile payload hash mismatch T{edge}')
            x=torch.load(path,map_location='cpu',weights_only=True).to('cuda:0')
            if tuple(x.shape)!=tuple(binding['tiles'][str(edge)]['shape']) or x.dtype!=torch.bfloat16:
                raise ValueError(f'tile shape/dtype mismatch T{edge}')
            ref=fp32_reference(x)
            if not torch.isfinite(ref).all():raise ValueError(f'nonfinite FP32 reference T{edge}')
            if edge==128:
                fused=ns5_smem(x,persistent=False)
                compiled=HiMuon._newton_schulz_3kernel(x,steps=STEPS)
                torch.cuda.synchronize()
                finite=bool(torch.isfinite(fused).all() and torch.isfinite(compiled).all())
                pair_allclose=bool(torch.allclose(fused,compiled,rtol=1e-2,atol=1e-2))
                difference=(fused.float()-compiled.float()).abs()
                rows.extend([
                    {'fixture':which,'arm':'F128','tile_edge':edge,'tile_count':len(x),
                     'output_finite':bool(torch.isfinite(fused).all()),
                     'cosine_vs_fp32_reference':cosine(fused,ref),
                     'output_sha256':sha_tensor(fused),
                     'same_map_pair_allclose':pair_allclose,
                     'pair_max_abs':float(difference.max()),'pair_mean_abs':float(difference.mean())},
                    {'fixture':which,'arm':'K128','tile_edge':edge,'tile_count':len(x),
                     'output_finite':bool(torch.isfinite(compiled).all()),
                     'cosine_vs_fp32_reference':cosine(compiled,ref),
                     'output_sha256':sha_tensor(compiled),
                     'same_map_pair_allclose':pair_allclose,
                     'pair_max_abs':float(difference.max()),'pair_mean_abs':float(difference.mean())},
                ])
                receipt['same_map_pair_pass']=finite and pair_allclose
                outputs['F128']=fused.cpu().contiguous()
                outputs['K128']=compiled.cpu().contiguous()
                del fused,compiled,difference
            else:
                compiled=HiMuon._newton_schulz_3kernel(x,steps=STEPS)
                torch.cuda.synchronize()
                rows.append({'fixture':which,'arm':f'L{edge}','tile_edge':edge,'tile_count':len(x),
                  'output_finite':bool(torch.isfinite(compiled).all()),
                  'cosine_vs_fp32_reference':cosine(compiled,ref),
                  'output_sha256':sha_tensor(compiled),
                  'same_map_pair_allclose':'NOT_APPLICABLE_DIFFERENT_TILE_MAP',
                  'pair_max_abs':'','pair_mean_abs':''})
                outputs[f'L{edge}']=compiled.cpu().contiguous()
                del compiled
            del x,ref
        output_path=ROOT/'raw'/f'{which}_numerical_outputs.pt'
        torch.save(outputs,output_path)
        receipt['outputs_payload_sha256']=sha_file(output_path)
        receipt['outputs_payload_bytes']=output_path.stat().st_size
        receipt['torch']=torch.__version__
        receipt['torch_cuda']=torch.version.cuda
        receipt['gpu']=torch.cuda.get_device_name(0)
        receipt['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
        receipt['status']='CANARY_COMPLETE'
    except Exception as exc:
        receipt['status']='CANARY_FAILED';receipt['error']=repr(exc);receipt['traceback']=traceback.format_exc()
        raise
    finally:
        with (ROOT/f'NUMERICAL_QUALIFICATION_{which.upper()}.tsv').open('w',newline='') as f:
            if rows:
                w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
                w.writeheader();w.writerows(rows)
        (ROOT/f'R101_NUMERICAL_CANARY_RECEIPT_{which.upper()}.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        if torch.cuda.is_initialized():torch.cuda.synchronize()
        gc.collect()
        if torch.cuda.is_initialized():torch.cuda.empty_cache()
    print(json.dumps({'fixture':which,'status':receipt['status'],
      'same_map_pair_pass':receipt.get('same_map_pair_pass'),
      'arms':{r['arm']:{'finite':r['output_finite'],'cos_vs_fp32':r['cosine_vs_fp32_reference']}
              for r in rows}},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--which',choices=['discovery','holdout'],required=True)
    main(p.parse_args().which)
