"""Independent raw-RESULT integer-cycle audit; no B statistics or native imports."""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,datetime,math,re,argparse,os,collections
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1')
DEFAULT_PROVIDER=A/'agents/B_runtime_analysis_v1/snapshot_runner_v1/PUBLICATION_PROVIDER.json'
CONTRACT=A/'agents/B_runtime_analysis_v1/CORE32_REFERENCE_CONTRACT.json'
CONTRACT_SHA='9627c0fad4395ddf2414e958b897f8f4b73347cf29b70e31ca7f9fa912f0cc6b'
FR='-gpgpu_frfcfs_dram_sched_queue_size'
def digest(b):return hashlib.sha256(b).hexdigest()
def source(p,s=None):
 b=Path(p).read_bytes()
 if s is not None:assert digest(b)==s,(str(p),'SHA')
 return b
def read(p,s=None):return json.loads(source(p,s))
def close(a,b):return a is None and b is None or a is not None and b is not None and math.isclose(float(a),float(b),rel_tol=2e-12,abs_tol=1e-14)
def dist(xs):
 xs=sorted(xs);n=len(xs)
 def quant(p):
  if not n:return None
  idx=Q(p)*(n-1);i=int(idx);j=min(n-1,i+1);return float(xs[i]+(xs[j]-xs[i])*(idx-i))
 return dict(n=n,GM=math.exp(math.fsum(math.log(float(x))for x in xs)/n)if n else None,positive=sum(x>1 for x in xs),negative=sum(x<1 for x in xs),zero=sum(x==1 for x in xs),minimum=float(xs[0])if n else None,maximum=float(xs[-1])if n else None,p25=quant(Q(1,4)),median=quant(Q(1,2)),p75=quant(Q(3,4)))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--provider',type=Path,default=DEFAULT_PROVIDER);parser.add_argument('--output-dir',type=Path);args=parser.parse_args()
 provider=read(args.provider);assert provider['source_qualified']is True and provider['summary']['expected_CH']==48
 assert provider['new_model_starts']==provider['native_scientific_writes']==0
 files={x['name']:x for x in provider['files']};x=files['STAGEIIA_REMAINING48_CORE32_RESULTS.json.gz'];data=json.loads(gzip.decompress(source(x['path'],x['sha256'])))
 sx=files['STAGEIIA_REMAINING48_SUMMARY.json.gz'];assert json.loads(gzip.decompress(source(sx['path'],sx['sha256'])))==provider['summary']
 contract=read(CONTRACT,CONTRACT_SHA);population={p['input_digest']:p for p in contract['population']};assert len(population)==32
 frozen={(r['input_digest'],r['source_cell']+'_'+r['source_profile']):r for r in contract['original128_references']+contract['first16_CH_references']};assert len(frozen)==144
 future={(r['input_digest'],'CH_'+r['source_profile']):r for r in contract['remaining48_candidates']};assert len(future)==48 and not(set(frozen)&set(future))
 assert set(r['input_digest']for r in data['all_programs'])==set(population)and len(data['all_programs'])==32
 source_audit=[];rows=[];cache={};raw_checks=[];checked_slots=0;architecture_patterns=collections.Counter()
 for row in data['all_programs']:
  ident=row['input_digest'];p=population[ident];assert row['program']==p['program']and row['suite']==p['suite']
  cs=row['six_source_cells'];assert set(cs)=={'CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256'}
  cycles={};opts={}
  for slot,c in cs.items():
   key=(ident,slot);assert c['input_digest']==ident and c['program']==p['program'];assert key in frozen or key in future
   if key in frozen:
    f=frozen[key]
    for k in ['source_RESULT_path','source_RESULT_sha256','source_registered_slot_cohort','source_profile','source_cell','source_role','cycles','accepted']:
     assert c[k]==f[k],(ident,slot,k)
   else:
    f=future[key];assert c['source_registered_slot_cohort']==f['cohort_expected']and c['source_role']=='STAGEII_REMAINING48_AUTHORIZED_CH'
   if not c['accepted']:
    assert c['cycles']is None;cycles[slot]=None;continue
   checked_slots+=1;path=c['source_RESULT_path'];s=c['source_RESULT_sha256'];r=read(path,s);proof=r['proof']
   assert type(r['cycles'])is int and r['cycles']>0 and r['cycles']==c['cycles']==proof['cycles']
   assert r['uuid']==c['source_uuid']==proof['uuid']
   assert r.get('input_digest',proof.get('input_digest'))==ident
   assert r['cohort']==c.get('source_RESULT_declared_cohort',c['source_registered_slot_cohort'])
   actual_profiles=[z for z in [r.get('profile'),proof.get('profile'),proof.get('downstream_profile')]if z is not None]
   assert proof['input_digest']==ident and proof['cell']==c['source_cell']and actual_profiles and all(z==c['source_profile']for z in actual_profiles)
   assert r['state']==c['source_state'],(p['program'],slot,r['state'],c['source_state'])
   alias=c.get('legal_prior_P0_alias');underlying=None
   if alias is not None:
    assert key in frozen and alias['reuse_identity_unchanged']is True and r['state']=='REFERENCE_ACCEPTED_NO_NEW_START'
    underlying=read(alias['underlying_RESULT_path'],alias['underlying_RESULT_sha256'])
    assert underlying['state'].startswith('PASS_')and underlying['cycles']==r['cycles']and underlying['uuid']==r['uuid']==alias['underlying_execution_uuid']
    assert underlying['cohort']==alias['underlying_RESULT_declared_cohort']and underlying['proof']['input_digest']==ident
    assert underlying['proof']['effective_options']==proof['effective_options']
   else:assert r['state'].startswith('PASS_')
   cycles[slot]=r['cycles'];opts[slot]=proof['effective_options']
   source_audit.append(dict(program=p['program'],input_digest=ident,slot=slot,source_RESULT_path=path,source_RESULT_sha256=s,source_state=r['state'],uuid=r['uuid'],cycles=r['cycles'],role=c['source_role'],legal_prior_P0_alias=alias,underlying_PASS_state=underlying['state']if underlying else None))
   if key in future:
    raw=Path(path).parent.parent/'DTC/run/results'/r['uuid']/'raw.log.gz';assert digest(source(raw))==proof['raw_gzip_sha256']
    totals=[]
    with gzip.open(raw,'rt',errors='strict')as handle:
     for lineno,line in enumerate(handle,1):
      match=re.match(r'^gpu_tot_sim_cycle\s*=\s*([0-9]+)\s*$',line)
      if match:totals.append((lineno,int(match.group(1))))
    assert totals and totals[-1][1]==r['cycles'],(raw,totals[-1:]if totals else'NO_TOTAL')
    raw_checks.append(dict(cohort=r['cohort'],uuid=r['uuid'],raw_path=str(raw),raw_gzip_sha256=proof['raw_gzip_sha256'],final_cycle_line=totals[-1][0],final_gpu_tot_sim_cycle=totals[-1][1],accepted_source_only=True))
  for design in ['CH','DH']:
   for profile,size in [('F128','128'),('F256','256')]:
    slot=design+'_'+profile;zero=design+'_P0'
    if slot in opts:
     diff={k:(opts[zero].get(k),opts[slot].get(k))for k in set(opts[zero])|set(opts[slot])if opts[zero].get(k)!=opts[slot].get(k)}
     assert diff=={FR:(['64'],[size])},(p['program'],slot,diff)
  architecture_patterns[json.dumps({k:[opts['CH_P0'].get(k),opts['DH_P0'].get(k)]for k in set(opts['CH_P0'])|set(opts['DH_P0'])if opts['CH_P0'].get(k)!=opts['DH_P0'].get(k)},sort_keys=True)]+=1
  metrics={};ratios={}
  for pf in ['F128','F256']:
   a,b,c,d=[cycles[z]for z in ['CH_P0','DH_P0','CH_'+pf,'DH_'+pf]]
   if any(x is None for x in [a,b,c,d]):assert row['metrics_by_profile'][pf]is None;metrics[pf]=None;continue
   metrics[pf]=dict(S_CH=Q(a,c),S_DH=Q(b,d),R_P0=Q(a,b),R=Q(c,d),I=Q(b*c,a*d))
   assert metrics[pf]['I']==metrics[pf]['R']/metrics[pf]['R_P0']
   for k,v in metrics[pf].items():assert close(v,row['metrics_by_profile'][pf][k]),(p['program'],pf,k)
   ratios[pf]={k:dict(numerator=v.numerator,denominator=v.denominator,value=float(v),sign='positive'if v>1 else'negative'if v<1 else'exact_zero')for k,v in metrics[pf].items()}
  common=all(v is not None for v in cycles.values());assert common==row['common_both_F_accepted'];direct=None
  if common:
   direct=dict(CH_F128_over_CH_F256=Q(cycles['CH_F128'],cycles['CH_F256']),DH_F128_over_DH_F256=Q(cycles['DH_F128'],cycles['DH_F256']),R_F256_over_R_F128=Q(cycles['CH_F256']*cycles['DH_F128'],cycles['DH_F256']*cycles['CH_F128']))
   for k,v in direct.items():assert close(v,row['direct_F_comparison'][k])
  rows.append(dict(program=p['program'],suite=p['suite'],input_digest=ident,cycles=cycles,common=common,metrics=metrics,direct=direct,exact_ratios=ratios))
 def verify_dist(expected,ratios):
  actual=dist(ratios)
  for key in ['n','positive','negative']:assert actual[key]==expected[key],(key,actual,expected)
  assert actual['zero']==expected['zero_within_1e_minus12'],('EXACT_VS_TOLERANCE_ZERO',actual,expected)
  for key in ['GM','minimum','maximum','p25','median','p75']:assert close(actual[key],expected[key]),(key,actual,expected)
  return actual
 aggregates={}
 for label,group,reported in [('CORE32',rows,data['all_core32'])]+[(suite,[r for r in rows if r['suite']==suite],entry)for suite,entry in data['by_suite'].items()]:
  common=[r for r in group if r['common']];assert reported['expected_population_n']==len(group)and reported['common_both_F']['n']==len(common)
  aggregate=dict(expected_n=len(group),common_n=len(common),common={},available={},direct={})
  for pf in ['F128','F256']:
   available=[r for r in group if r['metrics'][pf]is not None];assert reported['available_profile_specific'][pf]['n']==len(available)
   aggregate['common'][pf]={k:verify_dist(reported['common_both_F']['profiles'][pf][k],[r['metrics'][pf][k]for r in common])for k in ['S_CH','S_DH','R','R_P0','I']}
   aggregate['available'][pf]={k:verify_dist(reported['available_profile_specific'][pf]['metrics'][k],[r['metrics'][pf][k]for r in available])for k in ['S_CH','S_DH','R','R_P0','I']}
  for key in ['CH_F128_over_CH_F256','DH_F128_over_DH_F256','R_F256_over_R_F128']:aggregate['direct'][key]=verify_dist(reported['common_both_F']['direct_F'][key],[r['direct'][key]for r in common])
  aggregates[label]=aggregate
 common_ids={r['input_digest']for r in rows if r['common']};assert common_ids==set(data['same_input_both_F_ids'])
 assert checked_slots==data['coverage']['accepted_source_slots']==144+len(raw_checks)
 now=datetime.datetime.now(datetime.timezone.utc);tag=now.strftime('%Y%m%dT%H%M%S%fZ');out=args.output_dir or A/'root_independent_cycle_statistics_v1'/tag
 assert out.is_relative_to(A)and not out.exists();out.mkdir(parents=True)
 facts=dict(schema='DTC_ROOT_RAW_RESULT_INTEGER_CYCLE_STATISTICS_AUDIT_V1',UTC=now.isoformat(),status='PASS',source_provider=provider,contract_sha256=CONTRACT_SHA,fixed_core32=32,expected_slots=192,accepted_slots_rechecked=checked_slots,new48_raw_cycle_endpoints_rechecked=len(raw_checks),common_both_F_n=len(common_ids),final_full32=checked_slots==192 and len(common_ids)==32,raw_sources=source_audit,raw_new48_cycle_endpoints=raw_checks,all_programs=[{k:v for k,v in r.items()if k not in ['metrics','direct']}for r in rows],statistics=aggregates,architecture_difference_patterns=[dict(count=n,effective_option_differences=json.loads(k))for k,n in architecture_patterns.items()],verification_scope='Independent Fraction/integer recomputation from SHA-verified original RESULTs, plus final raw gpu_tot_sim_cycle for accepted new48. Full lifecycle/archive verification remains a separately required provider/C audit.',new_model_starts=0,native_writes=0)
 (out/'AUDIT.json.gz').write_bytes(gzip.compress((json.dumps(facts,indent=2,sort_keys=True)+'\n').encode(),mtime=0))
 (out/'README.md').write_text('# Independent integer-cycle scientific audit\n\n'+f'PASS. Accepted source slots {checked_slots}/192; new48 raw terminal cycle endpoints {len(raw_checks)}/48; common bothF {len(common_ids)}/32. '+('Complete fixed CORE32 data.'if facts['final_full32']else'Interim subset; no full32 conclusion.')+'\n\nAll32 frozen identities remain listed. Fractions and exact integer signs are independently recomputed from each SHA-verified raw RESULT. Available-subset and common-set suite GMs, distributions and directF values match the B report. Accepted CH/DH variants differ from their own P0 effective options only in the authorized FR queue setting; shared-credit coupling is still present. This verifies cycles/statistics, not a substitute for full lifecycle/archive/recovery review. No simulation/native mutation.\n')
 (out/'audit_source.py').write_bytes(Path(__file__).read_bytes());members=[dict(path=p.name,bytes=p.stat().st_size,sha256=digest(p.read_bytes()))for p in sorted(out.iterdir())]
 (out/'MANIFEST.json').write_text(json.dumps(dict(schema='DTC_ROOT_INDEPENDENT_CYCLE_AUDIT_MANIFEST_V1',files=members,new_models=0,native_writes=0),indent=2)+'\n')
 print(json.dumps(dict(output=str(out),manifest_sha256=digest((out/'MANIFEST.json').read_bytes()),status='PASS',accepted_slots=checked_slots,new48_raw_endpoints=len(raw_checks),common_n=len(common_ids),final_full32=facts['final_full32'])))
if __name__=='__main__':main()
