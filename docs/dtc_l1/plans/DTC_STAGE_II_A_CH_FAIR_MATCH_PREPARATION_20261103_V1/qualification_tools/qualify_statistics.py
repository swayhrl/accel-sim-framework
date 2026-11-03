import copy,json,math
from paired_statistics import quadruple,summarize,compare_f128_f256
checks=[]
def record(n,f):f();checks.append(dict(name=n,status='PASS'))
def bad(n,f):
 try:f()
 except ValueError:checks.append(dict(name=n,status='PASS_REJECTED_INVALID'))
 else:raise AssertionError(n)
def row(design,profile,cycles):return dict(design=design,profile=profile,cycles=cycles,accepted=True,source_role=('STAGEII_AUTHORIZED_CH'if design=='CH'and profile!='P0'else'ORIGINAL_PHASE_I_SLOT'),input_digest='a'*64,input_binding_sha='b'*64,roi_fingerprint='c'*64,build_fingerprint='d'*64,downstream_fingerprint=('e'if profile=='P0'else'f')*64,RESULT_sha256='0'*64)
q=[row('CH','P0',120),row('CH','F128',100),row('DH','P0',150),row('DH','F128',100)]
v=quadruple(*q);assert v['S_CH']==1.2 and v['S_DH']==1.5 and v['R']==1 and math.isclose(v['I'],v['R']/v['R_P0']);checks.append(dict(name='quadruple_exact_algebra_SYNTHETIC',status='PASS'))
for key,value in [('input_digest','9'*64),('input_binding_sha','9'*64),('roi_fingerprint','9'*64),('build_fingerprint','9'*64),('downstream_fingerprint','9'*64),('profile','F256'),('cycles',None),('cycles',0),('cycles',True),('accepted',False),('source_role','INCIDENT_RECOVERY_PERFORMANCE_TRIAL'),('source_role','SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'),('source_role','ORIGINAL_PHASE_I_SLOT'),('source_role','EP'),('source_role','PQ_PS')]:
 z=copy.deepcopy(q);z[1][key]=value;bad('reject_'+key+'_'+str(value),lambda z=z:quadruple(*z))
e=summarize({},['a','b']);assert e['GM']is None and e['n']==0 and len(e['missing'])==2;checks.append(dict(name='missing_not_zero_or_one',status='PASS'))
x=compare_f128_f256({'a':2,'b':.5},{'b':1,'c':4},['a','b','c']);assert x['F128']['population']==x['F256']['population']==['b']and x['marginal']['GM']==2;checks.append(dict(name='different_available_populations_common_only',status='PASS'))
bad('outside_frozen_population',lambda:summarize({'x':1},['a']))
bad('reject_zero_ratio',lambda:summarize({'a':0},['a']))
bad('reject_nan_ratio',lambda:summarize({'a':float('nan')},['a']))
z=copy.deepcopy(q);z[2]['source_role']='STAGEII_AUTHORIZED_CH';bad('new_CH_role_cannot_replace_DH',lambda:quadruple(*z))
bad('invalid_noncommon_F_ratio',lambda:compare_f128_f256({'a':0},{'b':1},['a','b']))
print(json.dumps(dict(schema='DTC_STAGE_IIA_CPU_PAIRED_STATISTICS_QUALIFICATION_V1',status='PASS',fixture='SYNTHETIC_CPU_ONLY_NOT_SCIENTIFIC_PERFORMANCE',checks=checks,model_starts=0,registrations=0)))
