"""CPU-only conversion and full-batch persistence; no numeric acceptance here."""
import hashlib,json,math
from persistence import save_json
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def capture_batch(responses,sources,prompts,sample,raw,secret,path,private_path,execution,persist=None):
    private=dict(point=sample['point'],role=sample['role'],round=sample['round'],outputs=[])
    sample.update(execution);sample['returned_requests']=len(responses);sample['outputs']=[]
    raw['samples'].append(sample);secret['samples'].append(private)
    for i,response in enumerate(responses):
        row=dict(source=sources[i] if i<len(sources) else None,request_id=str(getattr(response,'request_id',None)),
                 returned_prompt_token_ids=list(response.prompt_token_ids),expected_source_index=i,
                 finished=getattr(response,'finished',None),num_cached_tokens=getattr(response,'num_cached_tokens',None),completions=[])
        public=dict(source=row['source'],request_id=row['request_id'],prompt_token_sha256=digest(row['returned_prompt_token_ids']),completion_count=len(response.outputs),num_cached_tokens=row['num_cached_tokens'])
        for out in response.outputs:
            ids=[int(x) for x in out.token_ids]
            probs=[{str(k):float(v.logprob) for k,v in step.items()} for step in out.logprobs] if out.logprobs is not None else []
            meta=[{str(k):dict(rank=getattr(v,'rank',None),logprob=float(v.logprob)) for k,v in step.items()} for step in out.logprobs] if out.logprobs is not None else []
            row['completions'].append(dict(index=getattr(out,'index',None),tokens=ids,logprobs=probs,logprob_metadata=meta,
                  finish_reason=getattr(out,'finish_reason',None),stop_reason=getattr(out,'stop_reason',None),
                  cumulative_logprob=getattr(out,'cumulative_logprob',None),
                  sampled_token_logprobs=[probs[j].get(str(token)) if j<len(probs) else None for j,token in enumerate(ids)]))
        if len(row['completions'])==1:
            x=row['completions'][0];row.update(tokens=x['tokens'],logprobs=x['logprobs'])
            public.update(token_count=len(x['tokens']),token_sha256=digest(x['tokens']),logprob_sha256=digest(x['logprobs']))
        private['outputs'].append(row);sample['outputs'].append(public)
    sample['capture_complete_before_numeric_gate']=True
    writer=persist or save_json
    writer(private_path,secret);writer(path,raw)
    return private
