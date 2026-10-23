"""Declared synthetic arithmetic/population tests; never reads live model raw."""
import copy,importlib.util,json,pathlib
P=pathlib.Path(__file__).parent/'aefair_analysis.py';s=importlib.util.spec_from_file_location('finite_result_consumer',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def matrix(c0,c1,d0,d1):
 r={}
 for c,n in zip(m.CELLS,[c0,c1,d0,d1]):
  options={'-gpgpu_cache:dl1':['N:32:128:24,L:T:m:L:B,A:512:8,16:0,32' if c=='CH' else 'N:32:128:24,L:T:m:L:L,A:512:8,16:0,32'],'-gpgpu_dtc_l1_tag_hash_bankrow':['1' if c=='DH' else '0']}
  r[c]={'performance_accepted':True,'cycles':n,'instructions':739246080,'CTA':1024,'kernel_count':1,'core_commit':'SYNTHETIC_SAME_CORE','framework_commit':'SYNTHETIC_SAME_FRAMEWORK','uuid':'SYNTHETIC_'+c,'effective_options':options}
 return r
checks=[]
r=m.aggregate(matrix(200,100,300,100));assert r['interaction_R']['exact']=='3/2';checks.append('exact multiplicative interaction')
r2=m.aggregate(matrix(1400,700,2100,700));assert r2['interaction_R']==r['interaction_R'];checks.append('common scale invariance')
assert m.aggregate(matrix(200,200,300,300))['interaction_R']['exact']=='1';checks.append('neutral controls')
assert m.aggregate(matrix(200,100,100,200))['bounded_disposition']=='AE_GAIN_NOT_OBSERVED_OR_REVERSED_IN_THIS_FRESH_GEMM_TUPLE';checks.append('adverse DTC result retained')
cases=[]
r=matrix(200,100,300,100);del r['CH'];cases.append(('missing arm',r))
r=matrix(200,100,300,100);r['DH']['performance_accepted']=False;cases.append(('unaccepted arm',r))
r=matrix(200,100,300,100);r['DH']['cycles']=1.5;cases.append(('noninteger cycles',r))
r=matrix(200,100,300,100);r['DH']['core_commit']='DIFFERENT';cases.append(('mixed Core',r))
r=matrix(200,100,300,100);r['DH']['framework_commit']='DIFFERENT';cases.append(('mixed Framework',r))
r=matrix(200,100,300,100);r['DH']['uuid']=r['DM']['uuid'];cases.append(('reused attempt',r))
r=matrix(200,100,300,100);r['DH']['instructions']=99;cases.append(('incomplete input',r))
r=matrix(200,100,300,100);r['DH']['effective_options']['-clock']=['2'];cases.append(('extra nonhash option',r))
for name,r in cases:
 try:m.aggregate(r);raise AssertionError('accepted '+name)
 except ValueError:checks.append('expected rejection:'+name)
print(json.dumps({'status':'PASS_POSTCOHORT_CONSUMER_SYNTHETIC_ONLY','checks':checks,'actual_model_results_consumed':0,'scientific_starts':0},indent=2))
