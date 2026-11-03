"""CPU-only paired-statistics rules. No files, models, registration or dispatch."""
import math
ALLOWED_ROLES={'ORIGINAL_PHASE_I_SLOT','STAGEII_AUTHORIZED_CH'}
def check(row,design,profile):
 if row.get('accepted')is not True or type(row.get('cycles'))is not int or row['cycles']<=0:raise ValueError('UNACCEPTED_OR_INVALID_CYCLES')
 if row.get('source_role')not in ALLOWED_ROLES:raise ValueError('FORBIDDEN_PERFORMANCE_LINEAGE')
 if row['source_role']!=('STAGEII_AUTHORIZED_CH'if design=='CH'and profile!='P0'else'ORIGINAL_PHASE_I_SLOT'):raise ValueError('ROLE_NOT_ALLOWED_FOR_SLOT')
 if row.get('design')!=design or row.get('profile')!=profile:raise ValueError('DESIGN_OR_PROFILE_MISMATCH')
 for k in ['input_digest','input_binding_sha','roi_fingerprint','build_fingerprint','downstream_fingerprint','RESULT_sha256']:
  v=row.get(k)
  if not isinstance(v,str)or len(v)!=64 or any(c not in '0123456789abcdef'for c in v):raise ValueError('MISSING_IDENTITY '+k)
def quadruple(ch0,chf,dh0,dhf):
 f=chf.get('profile')
 if f not in ['F128','F256']:raise ValueError('F_NOT_AUTHORIZED_PROFILE')
 for x,design,p in [(ch0,'CH','P0'),(chf,'CH',f),(dh0,'DH','P0'),(dhf,'DH',f)]:check(x,design,p)
 for key in ['input_digest','input_binding_sha','roi_fingerprint','build_fingerprint']:
  if len({x[key]for x in [ch0,chf,dh0,dhf]})!=1:raise ValueError('PAIR_IDENTITY_MISMATCH '+key)
 if ch0['downstream_fingerprint']!=dh0['downstream_fingerprint']or chf['downstream_fingerprint']!=dhf['downstream_fingerprint']:raise ValueError('UNMATCHED_DOWNSTREAM')
 sch=ch0['cycles']/chf['cycles'];sdh=dh0['cycles']/dhf['cycles'];r0=ch0['cycles']/dh0['cycles'];rf=chf['cycles']/dhf['cycles']
 return dict(S_CH=sch,S_DH=sdh,R=rf,I=sdh/sch,R_P0=r0)
def summarize(values,expected):
 if len(set(expected))!=len(expected)or not set(values)<=set(expected):raise ValueError('POPULATION_MISMATCH')
 if any(not isinstance(v,(int,float))or isinstance(v,bool)or not math.isfinite(v)or v<=0 for v in values.values()):raise ValueError('INVALID_RATIO')
 vals=list(values.values());return dict(n=len(vals),expected_n=len(expected),population=sorted(values),missing=sorted(set(expected)-set(values)),GM=math.exp(sum(math.log(v)for v in vals)/len(vals))if vals else None,positive=sum(v>1 for v in vals),neutral=sum(v==1 for v in vals),negative=sum(v<1 for v in vals))
def compare_f128_f256(f128,f256,expected):
 if not(set(f128)|set(f256))<=set(expected):raise ValueError('OUTSIDE_FROZEN_POPULATION')
 summarize(f128,expected);summarize(f256,expected)
 common=set(f128)&set(f256);return dict(F128=summarize({i:f128[i]for i in common},expected),F256=summarize({i:f256[i]for i in common},expected),marginal=summarize({i:f256[i]/f128[i]for i in common},expected))
