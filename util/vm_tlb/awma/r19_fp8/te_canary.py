#!/usr/bin/env python3
"""Native SM89 TE FP8 real-payload and numerical admission canary."""
import hashlib
import json
import math
import os
import time
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT=Path('/data/c16/awma/r19_fp8_readiness_20261001')
PAYLOAD=ROOT/'raw/QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt'
ATOL=0.0675
RTOL=0.125

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def summarize_tensor(x):
    if not torch.is_tensor(x):return None
    out={'shape':list(x.shape),'dtype':str(x.dtype),'device':str(x.device),
         'bytes':x.numel()*x.element_size()}
    if x.numel()<=16:out['values']=x.detach().float().cpu().reshape(-1).tolist()
    return out

def main():
    assert os.environ.get('R19_GPU_LOCK_HELD')=='1'
    bound=json.loads((ROOT/'raw/REAL_PROJECTION_INPUT_RECEIPT.json').read_text())
    assert sha(PAYLOAD)==bound['payload_sha256']
    assert torch.cuda.get_device_capability(0)==(8,9)
    import transformer_engine
    import transformer_engine.pytorch as te
    import transformer_engine_torch as tex
    from transformer_engine.common import recipe
    available,reason=te.is_fp8_available(return_reason=True)
    cublaslt=int(tex.get_cublasLt_version())
    assert available and cublaslt>=120103,(available,reason,cublaslt)
    obj=torch.load(PAYLOAD,map_location='cpu',weights_only=True)
    x=obj['input'].to('cuda:0');w=obj['weight'].to('cuda:0')
    assert tuple(x.shape)==(1,256,896) and tuple(w.shape)==(4864,896)
    layer=te.Linear(896,4864,bias=False,params_dtype=torch.bfloat16,device='cuda:0').eval()
    with torch.no_grad():layer.weight.copy_(w)
    layer.requires_grad_(False)
    fp8_recipe=recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    torch.cuda.synchronize()
    with torch.no_grad():reference=F.linear(x,w)
    torch.cuda.synchronize()
    start=time.perf_counter()
    with torch.no_grad(),te.autocast(enabled=True,recipe=fp8_recipe):
        first=layer(x,is_first_microbatch=True)
    torch.cuda.synchronize()
    first_call_ms=(time.perf_counter()-start)*1000
    for _ in range(8):
        with torch.no_grad(),te.autocast(enabled=True,recipe=fp8_recipe):
            candidate=layer(x,is_first_microbatch=False)
    torch.cuda.synchronize()
    assert torch.isfinite(reference).all() and torch.isfinite(candidate).all()
    y=candidate.float();r=reference.float()
    error=(y-r).abs();relative=error/(r.abs()+1e-6)
    cosine=float(F.cosine_similarity(y.flatten(),r.flatten(),dim=0).item())
    close=bool(torch.allclose(y,r,atol=ATOL,rtol=RTOL))
    workspaces=getattr(layer,'_fp8_workspaces',{})
    cache={str(k):{'type':type(v).__name__,
                   'data':summarize_tensor(getattr(v,'_data',getattr(v,'data',None))),
                   'scale':summarize_tensor(getattr(v,'_scale',getattr(v,'scale',None))),
                   'amax':summarize_tensor(getattr(v,'_amax',getattr(v,'amax',None)))}
           for k,v in workspaces.items()}
    quantizers={}
    for k,values in getattr(layer,'quantizers',{}).items():
        quantizers[str(k)]=[{'type':type(q).__name__,
            'scale':summarize_tensor(getattr(q,'scale',None)),
            'amax':summarize_tensor(getattr(q,'amax',None))} for q in values]
    # Read-only diagnostic cast with the very same input quantizer already
    # selected by the normal TE operator; it is not a performance arm.
    qinput=None
    if 'scaling_fwd' in getattr(layer,'quantizers',{}):
        quantizer=layer.quantizers['scaling_fwd'][0]
        qinput=quantizer(x)
    native_fp8=bool(getattr(layer,'fp8',False)) and any('Float8' in x['type'] for x in cache.values())
    native_fp8=native_fp8 and qinput is not None and 'Float8' in type(qinput).__name__
    result={'stage':'AWMA_R19_FP8_READINESS_109_V1',
      'status':'NATIVE_FP8_NUMERIC_QUALIFIED' if native_fp8 and close else 'CANARY_NOT_QUALIFIED',
      'TE_version':transformer_engine.__version__,'torch':torch.__version__,
      'torch_cuda':torch.version.cuda,'device_capability':list(torch.cuda.get_device_capability(0)),
      'cublasLt_version':cublaslt,'is_fp8_available':available,'is_fp8_reason':reason,
      'recipe':'Float8CurrentScaling E4M3 default per-tensor non-power-of-two scales',
      'source_commit':'5e52befd5262c06289106338c308079d6adb391f',
      'input_payload_sha256':sha(PAYLOAD),'input_shape':list(x.shape),'weight_shape':list(w.shape),
      'weight_cache':cache,'quantizers':quantizers,
      'input_quantized_type':type(qinput).__name__ if qinput is not None else 'UNAVAILABLE',
      'input_quantized_data':summarize_tensor(getattr(qinput,'_data',None)) if qinput is not None else None,
      'layer_fp8_flag':bool(getattr(layer,'fp8',False)),'native_FP8_tensor_path_verified':native_fp8,
      'weight_cache_keys':[str(k) for k in workspaces],
      'first_call_ms_not_primary':first_call_ms,'first_output_dtype':str(first.dtype),
      'steady_output_dtype':str(candidate.dtype),
      'numerical_tolerance':{'atol':ATOL,'rtol':RTOL,'source':'TE v2.19 tests/pytorch/utils.py E4M3, unchanged from excluded canary'},
      'max_abs':float(error.max()),'mean_abs':float(error.mean()),
      'max_rel_eps1e6':float(relative.max()),'cosine':cosine,
      'all_finite':True,'numerical_allclose':close,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(0),
      'peak_reserved_bytes':torch.cuda.max_memory_reserved(0)}
    (ROOT/'raw/TE_NATIVE_FP8_CANARY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('weight_cache','quantizers')},sort_keys=True))
    if not native_fp8 or not close:raise SystemExit(2)

if __name__=='__main__':main()
