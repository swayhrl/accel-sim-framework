"""V8 separates runtime validity from token/logprob observations."""
import math
def compare(a,b,with_probs=True):
 ai=a['tokens'];bi=b['tokens'];n=min(len(ai),len(bi));prefix=next((j for j in range(n) if ai[j]!=bi[j]),n)
 rows=[]
 if with_probs:
  for j in range(min(len(a['logprobs']),len(b['logprobs']),n)):
   at,bt=ai[j],bi[j];x=a['logprobs'][j].get(str(at));y=b['logprobs'][j].get(str(bt))
   rows.append(dict(step=j,token_same=at==bt,common_prefix_before_step=j<=prefix,reference=x,actual=y,
      abs_error=None if x is None or y is None else abs(y-x),allowed=None if x is None else .05+.01*abs(x),
      old_gate_pass=None if x is None or y is None else abs(y-x)<=.05+.01*abs(x)))
 return dict(tokens_exact=ai==bi,first_divergence=None if ai==bi else prefix,common_prefix_tokens=prefix,
   equal_length=len(ai)==len(bi),sampled_logprobs=rows,logprob_observable=with_probs,
   old_logprob_all_pass=all(x['old_gate_pass'] for x in rows) if rows else None,
   comparison_semantics='SAME_TOKEN_SEQUENCE' if ai==bi else 'FIXED_LENGTH_REAL_SEQUENCE_DIVERGENCE')
def validate(row,expected,count,logprobs):
 assert row['returned_prompt_token_ids']==expected,'Input/request-source identity mismatch'
 assert len(row['completions'])==1,'Unexpected completion count'
 c=row['completions'][0];assert len(c['tokens'])==count,'Wrong generated output length'
 assert all(type(x)is int for x in c['tokens'])
 if logprobs is not None:
  assert len(c['logprobs'])==count,'Missing returned logprobs'
  assert all(math.isfinite(v) for step in c['logprobs'] for v in step.values()),'Nonfinite returned logprob'
  assert all(str(tok) in c['logprobs'][i] for i,tok in enumerate(c['tokens'])),'Selected token absent from logprobs'
 else:assert c['logprobs']==[],'Unexpected logprob payload for None path'
