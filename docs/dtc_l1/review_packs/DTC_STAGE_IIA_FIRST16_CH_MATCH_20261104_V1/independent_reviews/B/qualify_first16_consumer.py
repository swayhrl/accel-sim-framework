from pathlib import Path
import copy,json,importlib.util,math,hashlib
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('consumer',B/'readonly_first16_consumer.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=json.loads((B/'ANALYSIS_CONTRACT.json').read_text());b=json.loads((B/'BASELINE_REFERENCES.json').read_text());by={(x['input_digest'],x['design'],x['profile']):x for x in b['references']};checks=[]
def check(name,condition):
 assert condition,name;checks.append({'name':name,'pass':True})
def synthetic(e):
 old=by[e['input_digest'],'CH','P0'];return {'program':e['program'],'suite':e['suite'],'input_digest':e['input_digest'],'design':'CH','profile':e['profile'],'cohort':e['cohort'],'request':e['request'],'source_role':'STAGEII_AUTHORIZED_CH','accepted':True,'cycles':old['cycles']+10+(1 if e['profile']=='F256' else 0),'input_binding_sha':e['input_binding']['sha256'],'roi_fingerprint':e['expected_roi_fingerprint'],'downstream_fingerprint':e['downstream_fingerprint'],'build_fingerprint':old['build_fingerprint'],'build':old['build'],'effective_options':e['effective_options'],'config_sha256':[x['sha256'] for x in e['configs']],'expected_ROI':e['expected'],'qualification':{x:True for x in m.QUAL_FLAGS},'sources':{x:{'path':'SYNTHETIC_FIXTURE_ONLY/'+x,'sha256':'1'*64} for x in m.SOURCE_KINDS},'RESULT_sha256':'1'*64,'status':'SYNTHETIC_ACCEPTED_FIXTURE'}
obs=[synthetic(x) for x in c['expected_CH']]
r=m.evaluate(c,b,[]);check('no_CH_is_no_invented_performance',all(x['CH_F'] is None and all(v is None for v in x['metrics'].values()) for x in r['rows']));check('fixed8_not35',r['scientific_population']=='FIRST8_PREDECLARED_SUBSET_NOT_35_OR_CORE32' and len(r['rows'])==16)
r=m.evaluate(c,b,obs);check('complete16_same8_both_F',len(r['common_F128_F256_population'])==8 and all(x['status']=='ACCEPTED_MATCHED_QUADRUPLE' for x in r['rows']));x=r['rows'][0];check('algebra_I_equals_R_over_R0',math.isclose(x['metrics']['I'],x['metrics']['R']/x['metrics']['R_P0'],rel_tol=1e-14))
for field,value in [('input_digest','0'*64),('input_binding_sha','0'*64),('build_fingerprint','0'*64),('downstream_fingerprint','0'*64),('source_role','IR'),('profile','PS'),('request','OLD_GOAL'),('cohort','OLD_UUID_RETRY')]:
 bad=copy.deepcopy(obs);bad[0][field]=value;v=m.evaluate(c,b,bad);check('reject_'+field,sum(x['status']=='ACCEPTED_MATCHED_QUADRUPLE' for x in v['rows'])==15)
bad=copy.deepcopy(obs);bad[0]['effective_options']['-gpgpu_clock_domains']=['1410.0:1410.0:1410.0:1700.0'];v=m.evaluate(c,b,bad);check('reject_DRAM_clock_change',v['rows'][0]['status']=='REJECTED_IDENTITY_OR_QUALIFICATION')
bad=copy.deepcopy(obs);bad[0]['qualification']['native_restore_verified']=False;v=m.evaluate(c,b,bad);check('reject_unrestored',v['rows'][0]['status']=='REJECTED_IDENTITY_OR_QUALIFICATION')
bad=copy.deepcopy(obs);bad[0]['accepted']=False;bad[0]['status']='ARCHIVED_NEGATIVE';bad[0]['cycles']=None;v=m.evaluate(c,b,bad);check('negative_not_imputed_or_dropped',v['rows'][0]['status']=='ARCHIVED_NEGATIVE' and v['rows'][0]['CH_F'] is None and len(v['rows'])==16);check('crossF_common_intersection7',len(v['common_F128_F256_population'])==7 and v['common_F128_F256_metrics']['F128']['I']['population']==v['common_F128_F256_metrics']['F256']['I']['population'])
bad=obs+[obs[0]]
try:m.evaluate(c,b,bad);ok=False
except ValueError as e:ok=str(e)=='DUPLICATE_FIRST16_RESULT_IDENTITY'
check('duplicate_identity_rejected',ok)
# Explicitly exercise numeric ties and negative outcomes without ranking profiles.
s=m.load_statistics().summarize({'a':1,'b':0.5,'c':2},['a','b','c','d']);check('ties_negative_missing_preserved',s['positive']==1 and s['neutral']==1 and s['negative']==1 and s['missing']==['d'] and s['GM']==1)
out={'schema':'DTC_STAGEIIA_FIRST16_CONSUMER_CPU_QA_V1','fixture_scope':'SYNTHETIC_CPU_LOGIC_ONLY; not measurements, no new result index or accepted science emitted','checks':checks,'all_pass':all(x['pass'] for x in checks),'new_models':0,'consumer_sha256':hashlib.sha256((B/'readonly_first16_consumer.py').read_bytes()).hexdigest()};(B/'CPU_CONSUMER_QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(len(checks),'PASS')
