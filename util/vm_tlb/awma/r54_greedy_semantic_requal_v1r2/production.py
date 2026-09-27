#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,re,time,traceback
from pathlib import Path
import torch
from transformers import Qwen3_5ForConditionalGeneration,DynamicCache
from semantic_gate import config,semantic,thash

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
MODEL=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927/model/Qwen3_5_0_8B_c6046cd1')
ARMS=['P0','P1_D512','P2_D512','P1_D2048','P2_D2048']
IDS=json.loads((ROOT/'prefix/PREFIX_DISCOVERY_4096.json').read_text())

class Context:
    def __init__(self,model):
        self.model=model
        self.last_cache=None
        self.parts=[torch.tensor([IDS[j*512:(j+1)*512]],dtype=torch.long,device='cuda:0') for j in range(8)]
        self.gdn=[]
        for name,module in model.named_modules():
            if module.__class__.__name__=='Qwen3_5GatedDeltaNet':
                index=int(re.search(r'layers\.(\d+)\.linear_attn$',name).group(1))
                self.gdn.append((index,module))
        assert len(self.gdn)==18
        self.active=None
        self.handles=[]
        for index,module in self.gdn:
            self.handles.append(module.register_forward_pre_hook(self.pre_hook,with_kwargs=True))
            self.handles.append(module.register_forward_hook(self.post_hook,with_kwargs=True))

    def pre_hook(self,module,args,kwargs):
        c=self.active
        if c is None:return
        c['hook_invocations']+=1
        if c['kind']=='P2':
            i=module.layer_idx
            done=c['last_done'].pop(i,None)
            if done is not None:
                torch.cuda.current_stream().wait_event(done)
                c['source_reuse_waits']+=1

    def post_hook(self,module,args,kwargs,output):
        c=self.active
        if c is None:return
        c['hook_invocations']+=1
        if c['kind']!='P2' or c['slot_idx'] is None:return
        t0=time.perf_counter_ns()
        i=module.layer_idx
        layer=c['cache'].layers[i]
        slot=c['slots'][c['slot_idx']][i]
        ready=c['events'][c['slot_idx']][i]['ready']
        copy_start=c['events'][c['slot_idx']][i]['copy_start']
        copy_end=c['events'][c['slot_idx']][i]['copy_end']
        ready.record(torch.cuda.current_stream())
        with torch.cuda.stream(c['snapshot_stream']):
            c['snapshot_stream'].wait_event(ready)
            copy_start.record(c['snapshot_stream'])
            slot['conv'].copy_(layer.conv_states[0],non_blocking=True)
            slot['recurrent'].copy_(layer.recurrent_states[0],non_blocking=True)
            copy_end.record(c['snapshot_stream'])
        c['last_done'][i]=copy_end
        c['all_copies'].append((c['slot_idx'],i))
        c['host_copy_schedule_ns']+=time.perf_counter_ns()-t0

def make_slot(sample_cache):
    return {i:{'conv':torch.empty_like(layer.conv_states[0]),
               'recurrent':torch.empty_like(layer.recurrent_states[0])}
            for i,layer in enumerate(sample_cache.layers) if hasattr(layer,'recurrent_states')}

def build_resources(sample_cache):
    resources={}
    for arm in ARMS:
        if arm=='P0':resources[arm]={'slots':[],'events':[],'snapshot_stream':None}
        else:
            density=512 if 'D512' in arm else 2048
            count=4096//density
            slots=[make_slot(sample_cache) for _ in range(count)]
            events=[]
            for slot in slots:
                events.append({i:{key:torch.cuda.Event(enable_timing=True) for key in
                                  ['ready','copy_start','copy_end']} for i in slot})
            resources[arm]={'slots':slots,'events':events,
                            'snapshot_stream':torch.cuda.Stream() if arm.startswith('P2') else None}
    return resources

def reference_boundary_hashes(cache):
    return {i:{field:thash(getattr(layer,f'{field}_states')[0])
                for field in ('conv','recurrent')}
            for i,layer in enumerate(cache.layers) if hasattr(layer,'recurrent_states')}

def slot_hashes(slot):
    return {i:{field:thash(t) for field,t in parts.items()} for i,parts in slot.items()}

def run_once(ctx,resources,arm,kind,rep,collect_reference=False):
    density=512 if 'D512' in arm else 2048 if 'D2048' in arm else 0
    mode='P0' if arm=='P0' else arm[:2]
    r=resources[arm]
    cache=DynamicCache(config=ctx.model.config)
    copy_events=r['events']
    state={'kind':mode,'density':density,'cache':cache,'slots':r['slots'],
           'events':copy_events,'snapshot_stream':r['snapshot_stream'],
           'slot_idx':None,'last_done':{},'all_copies':[],
           'hook_invocations':0,'source_reuse_waits':0,'host_copy_schedule_ns':0}
    ctx.active=state
    stream=torch.cuda.current_stream()
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start=torch.cuda.Event(enable_timing=True)
    compute_done=torch.cuda.Event(enable_timing=True)
    total_done=torch.cuda.Event(enable_timing=True)
    ref_hashes=[]
    host_start=time.perf_counter_ns()
    start.record(stream)
    out=None
    try:
        with torch.inference_mode():
            for j in range(8):
                end=(j+1)*512
                boundary=density>0 and end%density==0
                state['slot_idx']=end//density-1 if boundary else None
                part=ctx.parts[j]
                out=ctx.model(input_ids=part,past_key_values=cache,use_cache=True,return_dict=True)
                assert out.past_key_values is cache
                if int(cache.get_seq_length())!=end:raise ValueError(f'cache length {cache.get_seq_length()} != {end}')
                if j==7:compute_done.record(stream)
                if collect_reference:
                    torch.cuda.synchronize()
                    ref_hashes.append(reference_boundary_hashes(cache))
                if mode=='P1' and boundary:
                    slot=r['slots'][state['slot_idx']]
                    for i,layer in enumerate(cache.layers):
                        if i not in slot:continue
                        events=copy_events[state['slot_idx']][i]
                        events['copy_start'].record(stream)
                        slot[i]['conv'].copy_(layer.conv_states[0],non_blocking=True)
                        slot[i]['recurrent'].copy_(layer.recurrent_states[0],non_blocking=True)
                        events['copy_end'].record(stream)
                        state['all_copies'].append((state['slot_idx'],i))
                    stream.synchronize()
            if mode=='P2':
                for slot_idx,i in state['all_copies']:
                    stream.wait_event(copy_events[slot_idx][i]['copy_end'])
            total_done.record(stream)
            torch.cuda.synchronize()
            host_end=time.perf_counter_ns()
            total_ms=start.elapsed_time(total_done)
            compute_ms=start.elapsed_time(compute_done)
            copy_gpu_ms=sum(copy_events[s][i]['copy_start'].elapsed_time(copy_events[s][i]['copy_end'])
                            for s,i in state['all_copies']) if mode!='P0' else 0.0
            overlap_ms=0.0
            if mode=='P2':
                for s,i in state['all_copies']:
                    a=start.elapsed_time(copy_events[s][i]['copy_start'])
                    b=start.elapsed_time(copy_events[s][i]['copy_end'])
                    overlap_ms+=max(0.0,min(b,compute_ms)-max(a,0.0))
            next_logits=out.logits[:,-1,:].detach()
            top8=torch.topk(next_logits,8).indices[0].tolist()
            finite=bool(torch.isfinite(next_logits).all())
            row={'arm':arm,'kind':kind,'rep':rep,'prefix_len':4096,'chunk_tokens':512,
                 'density':density,'total_gpu_ms':total_ms,'model_compute_complete_ms':compute_ms,
                 'checkpoint_ready_ms':total_ms,'host_elapsed_ms':(host_end-host_start)/1e6,
                 'host_snapshot_schedule_ms':state['host_copy_schedule_ns']/1e6,
                 'copy_gpu_ms_sum':copy_gpu_ms,'copy_compute_overlap_ms_sum':overlap_ms,
                 'snapshot_bytes_total':len(r['slots'])*19759104,
                 'snapshot_count':len(r['slots']),'snapshot_layer_copies':len(state['all_copies']),
                 'hook_invocations':state['hook_invocations'],
                 'source_reuse_waits':state['source_reuse_waits'],
                 'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
                 'peak_reserved_bytes':torch.cuda.max_memory_reserved(),
                 'cache_seq_length':int(cache.get_seq_length()),'top8_ids':json.dumps(top8,separators=(',',':')),
                 'top2_ids':json.dumps(top8[:2],separators=(',',':')),
                 'argmax_token_id':int(top8[0]),'logits_finite':finite}
            if kind in ('CANARY','PROFILE'):
                row['slot_hashes']=[slot_hashes(slot) for slot in r['slots']]
                if collect_reference:row['reference_boundary_hashes']=ref_hashes
                sem,_=semantic(ctx.model,out)
                row['continuation_tokens']=sem['tokens']
                row['continuation_tokens_sha256']=sem['tokens_sha256']
                row['continuation_top8_set']=sem['top8_set']
                row['continuation_top2']=sem['top2']
            ctx.last_cache=cache
            return row
    finally:
        ctx.active=None

def verify_canary(row,reference):
    if row['arm']=='P0':return {'semantic_pass':True,'snapshot_hash_pass':True}
    density=row['density']
    expected=[reference['reference_boundary_hashes'][boundary//512-1]
              for boundary in range(density,4097,density)]
    actual=row['slot_hashes']
    snapshot_ok=actual==expected
    semantic_ok=(row['continuation_tokens']==reference['continuation_tokens'] and
        json.loads(row['top8_ids']) and row['continuation_top8_set']==reference['continuation_top8_set'] and
        row['continuation_top2']==reference['continuation_top2'] and
        row['cache_seq_length']==reference['cache_seq_length'])
    return {'semantic_pass':bool(semantic_ok),'snapshot_hash_pass':bool(snapshot_ok)}

def load_model():
    return Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL,local_files_only=True,dtype=torch.bfloat16,
        device_map={'':'cuda:0'},use_kernels=True,kernel_config=config()).eval()

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        fields=list(rows[0])
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['formal','profile'],required=True)
    p.add_argument('--arm',choices=ARMS)
    args=p.parse_args()
    model=load_model()
    ctx=Context(model)
    with torch.inference_mode():sample=prefill_sample(model)
    resources=build_resources(sample.past_key_values)
    if args.mode=='profile':
        if args.arm is None:raise ValueError('--arm required')
        torch.cuda.nvtx.range_push(f'R54_PRODUCTION_PROFILE_{args.arm}')
        try:
            row=run_once(ctx,resources,args.arm,'PROFILE',0)
        finally:
            torch.cuda.nvtx.range_pop()
        out=ROOT/'raw'/'production_profile'/args.arm
        out.mkdir(parents=True,exist_ok=True)
        (out/'CANARY.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'arm':args.arm,'total_ms':row['total_gpu_ms'],'copy_gpu_ms_sum':row['copy_gpu_ms_sum']}))
        return
    canaries={}
    canaries['P0']=run_once(ctx,resources,'P0','CANARY',0,collect_reference=True)
    for arm in ARMS[1:]:
        canaries[arm]=run_once(ctx,resources,arm,'CANARY',0)
    qualification={arm:verify_canary(canaries[arm],canaries['P0']) for arm in ARMS}
    qualified=all(all(x.values()) for x in qualification.values())
    (ROOT/'PRODUCTION_CANARY_RECEIPT.json').write_text(json.dumps({'qualified':qualified,
         'qualification':qualification,'canaries':canaries},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'canary_qualified':qualified,'qualification':qualification},sort_keys=True))
    if not qualified:return
    for warmup in range(2):
        for arm in ARMS:
            row=run_once(ctx,resources,arm,'WARMUP',warmup)
            if not row['logits_finite'] or row['cache_seq_length']!=4096:
                raise ValueError(f'Warmup invalid {arm}')
    formal=[]
    for rep in range(7):
        order=ARMS[rep%len(ARMS):]+ARMS[:rep%len(ARMS)]
        for arm in order:
            row=run_once(ctx,resources,arm,'FORMAL',rep)
            if not row['logits_finite'] or row['cache_seq_length']!=4096 or row['argmax_token_id']!=canaries['P0']['argmax_token_id']:
                raise ValueError(f'Formal identity invalid {arm} rep {rep}')
            formal.append(row)
            print(json.dumps({'arm':arm,'rep':rep,'total_gpu_ms':row['total_gpu_ms'],'copy_gpu_ms_sum':row['copy_gpu_ms_sum']}))
    write_tsv(ROOT/'SNAPSHOT_PRODUCTION_TIMING.tsv',formal)
    copy_rows=[{k:r[k] for k in ['arm','rep','density','snapshot_bytes_total','snapshot_layer_copies',
        'copy_gpu_ms_sum','copy_compute_overlap_ms_sum','host_snapshot_schedule_ms','source_reuse_waits']}
        for r in formal]
    write_tsv(ROOT/'SNAPSHOT_COPY_ACCOUNTING.tsv',copy_rows)

def prefill_sample(model):
    with torch.inference_mode():
        return model(input_ids=torch.tensor([IDS[:512]],dtype=torch.long,device='cuda:0'),use_cache=True,return_dict=True)

if __name__=='__main__':main()
