"""CPU-only attribution from independently hashed,post-formal captured tensors."""
from pathlib import Path
import json,hashlib,math
import torch
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8"
def H(b):return hashlib.sha256(b).hexdigest()
def D(x):return H(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not torch.cuda.is_initialized()
 master=json.loads((OUT/'raw/BASE.json').read_text());secret=json.loads((OUT/'.private/BASE_private_outputs.json').read_text())
 observer=master['optional_observer'];lookup={};baseline={}
 for p in secret['samples']:
  if p['config']=='LOCAL_OBSERVER':
   for row in p['outputs']:lookup[(p['point'],row['request_id'])]=row
  if p['config']=='MAIN' and p['role']=='FORMAL':
   for row in p['outputs']:baseline.setdefault((p['point'],row['source']),row)
 entries={};perrow=[];representative=[];tensors=[]
 for rec in observer['records']:
  path=Path(rec['file']);assert H(path.read_bytes())==rec['sha256']
  data=torch.load(path,map_location='cpu',weights_only=True);assert data['logits'].device.type=='cpu'
  assert list(data['logits'].shape)==data['logits_shape'];assert len(data['request_ids'])==data['logits'].shape[0]
  tensors.append(dict(file=str(path),sha256=rec['sha256'],bytes=path.stat().st_size))
  for j,req in enumerate(data['request_ids']):
   external,suffix=req.rsplit('-',1);assert len(suffix)==8 and all(c in '0123456789abcdef' for c in suffix)
   row=lookup[(data['point'],external)];step=data['step'];values=data['logits'][j].float();ref32=torch.log_softmax(values,dim=-1);ref64=torch.log_softmax(values.double(),dim=-1)
   real=row['logprobs'][step];selected=row['tokens'][step]
   assert int(data['sampled_ids'][j,0])==selected,'Observer row selected token pairing mismatch'
   errs32=[abs(float(ref32[int(k)])-v) for k,v in real.items()];errs64=[abs(float(ref64[int(k)])-v) for k,v in real.items()]
   ids=data['head_token_ids'].long();w=data['head_weight_rows'].double();h=data['hidden_states'][j].double()
   dots=w@h;raw=data['logits'][j,ids].double()
   entry=dict(point=data['point'],step=step,source=row['source'],internal_request_id=req,external_request_id=external,logits_dtype=data['logits_dtype'],hidden_dtype=str(data['hidden_states'].dtype),
      logits_shape=data['logits_shape'],hidden_shape=list(data['hidden_states'].shape),num_tokens=data['num_tokens'],num_scheduled_tokens=data['num_scheduled_tokens'],
      actual_sampler_mode=data['sampler_mode'],needs_logits_processing=data['needs_logits_processing'],
      selected_raw_logit=float(values[selected]),selected_returned_logprob=real[str(selected)],selected_CPU_FP32_logprob=float(ref32[selected]),selected_CPU_FP64_logprob=float(ref64[selected]),
      CPU_FP32_max_abs_error_returned_top20=max(errs32),CPU_FP64_max_abs_error_returned_top20=max(errs64),
      selected_head_dot_FP64_rawscore_max_abs_error=float((dots-raw).abs().max()),
      head_dtype=data['head_dtype'],head_weight_dtype=data['head_weight_dtype'])
   perrow.append(entry);entries[(data['point'],step,row['source'])]=(data,j,row,entry)
   base=baseline[(data['point'],row['source'])]
   representative.append(dict(point=data['point'],step=step,source=row['source'],tokens_exact_to_MAIN=base['tokens']==row['tokens'],
       captured_step_top20_exact_to_MAIN=base['logprobs'][step]==row['logprobs'][step]))
 pairs=[]
 for source,b1 in [('TRAIN_A_DISCOVERY_00','P4'),('TRAIN_A_DISCOVERY_01','P5')]:
  for step in [0,1,15,31]:
   a,ia,ra,ea=entries[(b1,step,source)];b,ib,rb,eb=entries[('P6',step,source)]
   la=a['logits'][ia].double();lb=b['logits'][ib].double();ha=a['hidden_states'][ia].double();hb=b['hidden_states'][ib].double()
   common=sorted(set(ra['logprobs'][step])&set(rb['logprobs'][step]),key=int)
   wa={int(k):v.double() for k,v in zip(a['head_token_ids'],a['head_weight_rows'])};wb={int(k):v.double() for k,v in zip(b['head_token_ids'],b['head_weight_rows'])}
   decomposition=[]
   lsea=float(torch.logsumexp(la,0));lseb=float(torch.logsumexp(lb,0))
   for key in common:
    k=int(key);available=k in wa and k in wb
    if available:assert torch.equal(wa[k],wb[k])
    rawdelta=float(lb[k]-la[k]);hidden_delta=float(torch.dot(wa[k],hb-ha)) if available else None
    returned_delta=rb['logprobs'][step][key]-ra['logprobs'][step][key]
    decomposition.append(dict(token_id_sha256=H(key.encode()),B1_raw_logit=float(la[k]),B2_raw_logit=float(lb[k]),raw_logit_delta=rawdelta,
      CPU_FP64_hidden_driven_head_dot_delta=hidden_delta,head_FP64_reference_available=available,remaining_raw_delta_minus_hidden_dot=rawdelta-hidden_delta if available else None,
      B1_B2_logsumexp_delta=lseb-lsea,expected_normalized_delta=rawdelta-(lseb-lsea),returned_logprob_delta=returned_delta,
      normalized_delta_residual=returned_delta-(rawdelta-(lseb-lsea))))
   history_same=ra['tokens'][:step]==rb['tokens'][:step]
   pairs.append(dict(source=source,step=step,same_prior_token_history=history_same,current_token_same=ra['tokens'][step]==rb['tokens'][step],
     hidden_states_bitwise_equal=torch.equal(a['hidden_states'][ia].contiguous().view(torch.uint8),b['hidden_states'][ib].contiguous().view(torch.uint8)),
     hidden_states_max_abs_delta=float((hb-ha).abs().max()),hidden_states_relative_L2=float(torch.linalg.vector_norm(hb-ha)/torch.linalg.vector_norm(ha)),
     raw_logits_bitwise_equal=torch.equal(a['logits'][ia].contiguous().view(torch.uint8),b['logits'][ib].contiguous().view(torch.uint8)),raw_logits_max_abs_delta=float((lb-la).abs().max()),
     raw_logits_changed_count=int((lb!=la).sum()),raw_logits_count=len(la),
     max_abs_returned_delta_minus_CPU_logit_normalization=max(abs(x['normalized_delta_residual']) for x in decomposition),
     decomposition=decomposition))
 result=dict(status='POST_FORMAL_LOCAL_OBSERVATION_COMPLETE',records=len(observer['records']),rows=len(perrow),private_tensor_bytes=observer['private_tensor_bytes'],files=tensors,
   tensor_observations=perrow,paired_B1_B2=pairs,representativeness=representative,
   all_captured_step_top20_exact_to_uninstrumented_MAIN=all(x['captured_step_top20_exact_to_MAIN'] for x in representative),
   normalization_max_abs_error_FP32=max(x['CPU_FP32_max_abs_error_returned_top20'] for x in perrow),
   interpretation='Sampler-input rawlogits and lastselectedhiddenstates directlyobserved afterformal. CPU normalization can establish whetherreturned differences alreadyexistbeforelogsoftmax. PartialFP64headdotsarediagnosticreference,notchangedGPUprecisionorfulllogitqualityproof.',
   timing_excluded=True,profiler_used=False,CUDA_init_in_this_CPU_analysis=False)
 (OUT/'NUMERIC_ATTRIBUTION.json').write_text(json.dumps(result,indent=2)+'\n')
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(records=result['records'],rows=result['rows'],normalization_max_error=result['normalization_max_abs_error_FP32'],representative=result['all_captured_step_top20_exact_to_uninstrumented_MAIN'],
    pairs=[{k:v for k,v in p.items() if k!='decomposition'} for p in pairs],first_token_decomposition=[p['decomposition'][:2] for p in pairs if p['step']==0])))
if __name__=='__main__':main()
