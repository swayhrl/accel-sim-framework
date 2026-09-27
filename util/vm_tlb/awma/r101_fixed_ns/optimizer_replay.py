#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,statistics,time,traceback
from pathlib import Path
import torch
from safetensors import safe_open
from himuon.optimizers.himuon import HiMuon

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors')
NAMES=['model.layers.0.self_attn.q_proj.weight',
       'model.layers.0.mlp.up_proj.weight',
       'model.layers.0.mlp.down_proj.weight']

def sha_tensor(t):return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()

def load_authority():
    micro=torch.load(ROOT/'raw/discovery_gradient_microstate.pt',weights_only=True,map_location='cpu')
    with safe_open(MODEL,framework='pt',device='cpu') as f:
        originals={name:f.get_tensor(name).clone().contiguous() for name in NAMES}
    gradients={name:micro[name]['grad'].clone().contiguous() for name in NAMES}
    assert all(originals[name].dtype==gradients[name].dtype==torch.bfloat16 for name in NAMES)
    receipt=json.loads((ROOT/'R101_GRADIENT_MICROSTATE_RECEIPT_DISCOVERY.json').read_text())
    assert all(sha_tensor(gradients[name])==receipt['parameters'][name]['gradient_sha256'] for name in NAMES)
    return originals,gradients

def make_optimizer(edge,originals,gradients,graph,names=NAMES):
    params=[]
    for name in names:
        p=torch.nn.Parameter(originals[name].detach().clone().to('cuda:0'))
        p.grad=gradients[name].to('cuda:0')
        params.append(p)
    opt=HiMuon(params,lr=0.02,momentum=0.95,nesterov=True,weight_decay=0.1,
      tile_size=edge,ns_steps=5,b_hw=None,cuda_graph=graph,cuda_graph_warmup=3)
    return opt,params

def reset(opt,params,originals,names=NAMES):
    for name,p in zip(names,params):
        p.data.copy_(originals[name].to('cuda:0'))
        buf=opt.state[p].get('momentum_buffer')
        if buf is None:raise ValueError('momentum buffer not initialized')
        buf.zero_()
    torch.cuda.synchronize()

def compare(reference,params,names=NAMES):
    checks={};passed=True
    for name,p,ref in zip(names,params,reference):
        delta=(p.float()-ref.float()).abs()
        good=bool(torch.allclose(p,ref,rtol=1e-2,atol=1e-2))
        checks[name]={'allclose':good,'max_abs':float(delta.max()),
                      'mean_abs':float(delta.mean()),'output_sha256':sha_tensor(p)}
        passed=passed and good
    return passed,checks

def compact_plan(opt):
    rows=[]
    for b in opt.xlayer_plan():
        rows.append({'bucket_key':str(b['bucket_key']),'B_total':b['B_total'],
                     'B_hw':b['B_hw'],'chunk_sizes':b['chunk_sizes'],
                     'n_calls':b['n_calls'],'tile_count_per_param':b['tile_count_per_param']})
    return rows

def make_graph_arm(edge,originals,gradients,names=NAMES):
    eager,eager_params=make_optimizer(edge,originals,gradients,False,names)
    with torch.no_grad():eager.step()
    torch.cuda.synchronize()
    ref=[p.detach().clone() for p in eager_params]
    opt,params=make_optimizer(edge,originals,gradients,True,names)
    with torch.no_grad():
        for _ in range(3):opt.step()
        if opt._cached_plan is None:raise ValueError('plan not cached after warmup')
        concat_before={str(k):(tuple(v.shape),int(v.data_ptr())) for k,v in opt._concat_buffers.items()}
        opt.step()  # author capture step
        if opt._cuda_graph is None:raise ValueError('author optimizer graph not captured')
        reset(opt,params,originals,names)
        opt.step()  # first frozen-state graph replay
    torch.cuda.synchronize()
    passed,checks=compare(ref,params,names)
    if not passed:raise ValueError(f'graph first-state output differs from author eager T{edge}: {checks}')
    if not all(torch.equal(opt.state[p]['momentum_buffer'],p.grad) for p in params):
        raise ValueError(f'first-step momentum buffer differs from gradient T{edge}')
    concat_after={str(k):(tuple(v.shape),int(v.data_ptr())) for k,v in opt._concat_buffers.items()}
    if concat_before!=concat_after:raise ValueError('cached concat pointer changed')
    canary={'tile_edge':edge,'graph_captured':True,'first_state_author_eager_allclose':passed,
            'parameter_checks':checks,'cross_layer_plan':compact_plan(opt),
            'cached_plan_reused':True,'concat_buffers_stable':True,
            'concat_buffers':concat_after,
            'grad_pointers_stable':{name:int(p.grad.data_ptr()) for name,p in zip(names,params)},
            'graph_scope':'author momentum/tile/NS/untile graph; WD/LR outside graph'}
    return opt,params,ref,canary

def measure(edge,opt,params,originals,reference,kind,rep,names=NAMES):
    reset(opt,params,originals,names)
    torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
    host_start=time.perf_counter_ns();start.record()
    with torch.no_grad():opt.step()
    end.record();torch.cuda.synchronize();host_end=time.perf_counter_ns()
    passed,_=compare(reference,params,names)
    if not passed:raise ValueError(f'optimizer replay output drift T{edge}/{kind}/{rep}')
    return {'arm':f'L{edge}_AUTHOR_GRAPH_OPTIMIZER','run_status':kind,'rep':rep,
      'tile_edge':edge,'complete_selected_optimizer_gpu_ms':start.elapsed_time(end),
      'host_elapsed_ms_secondary':(host_end-host_start)/1e6,
      'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
      'selected_parameter_count':3,'first_frozen_state_output_allclose':True,
      'plan_cached':opt._cached_plan is not None,'graph_replay_active':opt._cuda_graph is not None}

def main():
    prereg=json.loads((ROOT/'OPTIMIZER_REPLAY_PREREGISTRATION.json').read_text())
    assert prereg['tile_edges']==[256,512]
    original_cpu,gradient_cpu=load_authority()
    originals={k:v.to('cuda:0') for k,v in original_cpu.items()}
    arms={};canaries={}
    for edge in [256,512]:
        opt,params,ref,canary=make_graph_arm(edge,originals,gradient_cpu)
        arms[edge]=(opt,params,ref)
        canaries[str(edge)]=canary
    (ROOT/'OPTIMIZER_REPLAY_CANARY.json').write_text(json.dumps(canaries,indent=2,sort_keys=True)+'\n')
    for warmup in range(2):
        for edge in [256,512]:
            opt,params,ref=arms[edge]
            measure(edge,opt,params,originals,ref,'WARMUP',warmup)
    formal=[]
    for rep in range(7):
        order=[256,512] if rep%2==0 else [512,256]
        for edge in order:
            opt,params,ref=arms[edge]
            row=measure(edge,opt,params,originals,ref,'FORMAL',rep)
            formal.append(row)
            print(json.dumps({'edge':edge,'rep':rep,'gpu_ms':row['complete_selected_optimizer_gpu_ms']}))
    with (ROOT/'OPTIMIZER_REPLAY_RESULTS.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(formal[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(formal)
    summary={}
    for edge in [256,512]:
        vals=[r['complete_selected_optimizer_gpu_ms'] for r in formal if r['tile_edge']==edge]
        med=statistics.median(vals)
        summary[str(edge)]={'median_gpu_ms':med,'values_ms':vals,
          'max_relative_jitter':max(abs(v-med) for v in vals)/med,
          'median_host_ms_secondary':statistics.median(r['host_elapsed_ms_secondary'] for r in formal if r['tile_edge']==edge)}
    (ROOT/'OPTIMIZER_REPLAY_ANALYSIS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,sort_keys=True))

if __name__=='__main__':main()
