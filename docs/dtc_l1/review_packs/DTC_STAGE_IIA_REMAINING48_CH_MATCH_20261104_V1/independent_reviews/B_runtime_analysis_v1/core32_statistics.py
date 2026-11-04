"""Pure CORE32 statistics; no simulator/controller/native-writer imports or actions.
Input future observations must already be strict/archive/native-restore verified by new adapter.
"""
from __future__ import annotations
import math,json,pathlib,hashlib
REQ='DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'
ROLE='STAGEII_REMAINING48_AUTHORIZED_CH'
PASS='PASS_STAGEII48_CH_STRICT_ARCHIVE_NATIVE_RESTORE';FAIL='FAIL_STAGEII48_CH_ARCHIVED_NO_RETRY'
QUAL=['strict_pass','actual_input_verified','actual_build_verified','actual_effective_options_verified','natural_exit_verified','true164_archive_verified','native_restore_verified']
METRICS=['S_CH','S_DH','R_P0','R','I']
def require(c,m):
 if not c:raise ValueError(m)
def gm(v):
 require(all(isinstance(x,(int,float))and math.isfinite(x)and x>0 for x in v),'INVALID_GM_RATIO')
 return math.exp(math.fsum(math.log(x)for x in v)/len(v))if v else None
def quantile(v,q):
 if not v:return None
 s=sorted(v);pos=q*(len(s)-1);lo=math.floor(pos);hi=math.ceil(pos);return s[lo]+(s[hi]-s[lo])*(pos-lo)
def summarize(v):
 return {'n':len(v),'GM':gm(v),'positive':sum(x>1+1e-12 for x in v),'zero_within_1e_minus12':sum(abs(x-1)<=1e-12 for x in v),'negative':sum(x<1-1e-12 for x in v),'minimum':min(v)if v else None,'p25':quantile(v,.25),'median':quantile(v,.5),'p75':quantile(v,.75),'maximum':max(v)if v else None}
def base_cell(r):
 return {'program':r['program'],'suite':r['suite'],'input_digest':r['input_digest'],'source_cell':r['source_cell'],'source_profile':r['source_profile'],'source_registered_slot_cohort':r['source_registered_slot_cohort'],'source_RESULT_declared_cohort':r['source_RESULT_declared_cohort'],'source_role':r['source_role'],'native_scientific_role':r.get('native_scientific_role'),'source_RESULT_path':r['source_RESULT_path'],'source_RESULT_sha256':r['source_RESULT_sha256'],'source_uuid':r['source_uuid'],'legal_prior_P0_alias':r.get('legal_prior_P0_alias'),'source_state':r['source_state'],'accepted':r['accepted'],'cycles':r['cycles'],'status':'FROZEN_ACCEPTED_REFERENCE'}
def normalize_future(e,r):
 out={'program':e['program'],'suite':e['suite'],'input_digest':e['input_digest'],'source_cell':'CH','source_profile':e['source_profile'],'source_registered_slot_cohort':e['cohort_expected'],'source_role':ROLE,'native_scientific_role':ROLE,'accepted':False,'cycles':None,'status':'AWAIT_ROOT_RESULT'}
 if r is None:return out
 require(r['cohort']==e['cohort_expected']and r['input_digest']==e['input_digest']and r['profile']==e['source_profile']and r['design']=='CH'and r['source_role']==ROLE and r['request']==REQ,'OBSERVATION_IDENTITY_MISMATCH')
 out.update(source_RESULT_path=r.get('sources',{}).get('RESULT',{}).get('path'),source_RESULT_sha256=r.get('RESULT_sha256',r.get('sources',{}).get('RESULT',{}).get('sha256')),source_uuid=r.get('uuid'),status=r['status'],reason=r.get('reason'),source_state=r.get('observed_native_state'))
 if r['status']==PASS:
  if r.get('accepted')is not True or type(r.get('cycles'))is not int or r['cycles']<=0 or not all(r.get('qualification',{}).get(k)is True for k in QUAL)or not out['source_RESULT_sha256'] or not r.get('archive_verification') or r.get('expected_ROI')!=e['expected'] or r.get('input_binding_sha')!=e['input_binding']['sha256']:
   out.update(status='HOLD_READONLY_VERIFICATION',reason='ACCEPTED_OBSERVATION_LACKS_QUALIFICATION_OR_SOURCE_SHA');return out
  out.update(accepted=True,cycles=r['cycles']);return out
 require(r.get('accepted')is not True and r.get('cycles')is None,'UNACCEPTED_HAS_PERFORMANCE')
 if r['status']==FAIL and(not r.get('archive_verification')or not out['source_RESULT_sha256']):out.update(status='HOLD_READONLY_VERIFICATION',reason='NEGATIVE_LACKS_CLOSED_ARCHIVE_WITNESS')
 return out

def evaluate(contract,observations):
 population=contract['population'];identities={p['input_digest']:p for p in population};require(len(identities)==len(population),'DUPLICATE_POPULATION_INPUT');expected={e['cohort_expected']:e for e in contract['remaining48_candidates']};require(len(expected)==len(contract['remaining48_candidates']),'DUPLICATE_EXPECTED_COHORT');observed={}
 for r in observations:
  require(r['cohort']in expected,'UNAUTHORIZED_OBSERVATION_COHORT');require(r['cohort']not in observed,'DUPLICATE_OBSERVATION_COHORT');observed[r['cohort']]=r
 cells={}
 for r in contract['original128_references']+contract['first16_CH_references']:
  key=(r['input_digest'],r['source_cell'],r['source_profile']);require(key not in cells,'DUPLICATE_FROZEN_SOURCE_SLOT');cells[key]=base_cell(r)
 for cohort,e in expected.items():
  key=(e['input_digest'],'CH',e['source_profile']);require(key not in cells,'NEW_SOURCE_OVERLAPS_FROZEN_SLOT');cells[key]=normalize_future(e,observed.get(cohort))
 require(len(cells)==6*len(population),'SIX_CELL_POPULATION_MEMBERSHIP_MISMATCH');records=[]
 for ident,p in identities.items():
  cs={c+'_'+pf:cells[ident,c,pf]for c in['CH','DH']for pf in['P0','F128','F256']};metrics={};missing={}
  for pf in['F128','F256']:
   keys=['CH_P0','DH_P0','CH_'+pf,'DH_'+pf];missing[pf]=[{'source_slot':k,'status':cs[k]['status'],'reason':cs[k].get('reason')}for k in keys if not cs[k]['accepted']]
   if not missing[pf]:
    a,b,c,z=[cs[k]['cycles']for k in keys];sc=a/c;sd=b/z;ratio=c/z;rel=sd/sc;require(math.isclose(rel,ratio/(a/b),rel_tol=1e-12),'R_I_ALGEBRA_DISAGREES');metrics[pf]={'S_CH':sc,'S_DH':sd,'R_P0':a/b,'R':ratio,'I':rel}
   else:metrics[pf]=None
  common=all(cs[k]['accepted']for k in cs);direct=None
  if common:direct={'CH_F128_over_CH_F256':cs['CH_F128']['cycles']/cs['CH_F256']['cycles'],'DH_F128_over_DH_F256':cs['DH_F128']['cycles']/cs['DH_F256']['cycles'],'R_F256_over_R_F128':metrics['F256']['R']/metrics['F128']['R']}
  records.append({**p,'six_source_cells':cs,'metrics_by_profile':metrics,'missing_by_profile':missing,'common_both_F_accepted':common,'direct_F_comparison':direct})
 common=[r for r in records if r['common_both_F_accepted']]
 def aggregate(rs,popn):
  return {'expected_population_n':popn,'available_profile_specific':{pf:{'n':sum(r['metrics_by_profile'][pf]is not None for r in rs),'denominator_rule':'PROFILE_SPECIFIC_AVAILABLE_ONLY; do not directly compare its GM with another profile unless sets equal','metrics':{k:summarize([r['metrics_by_profile'][pf][k]for r in rs if r['metrics_by_profile'][pf]is not None])for k in METRICS}}for pf in['F128','F256']},'common_both_F':{'n':sum(r['common_both_F_accepted']for r in rs),'denominator_rule':'Same complete six-cell accepted input intersection for both F profiles','profiles':{pf:{k:summarize([r['metrics_by_profile'][pf][k]for r in rs if r['common_both_F_accepted']])for k in METRICS}for pf in['F128','F256']},'direct_F':{k:summarize([r['direct_F_comparison'][k]for r in rs if r['common_both_F_accepted']])for k in['CH_F128_over_CH_F256','DH_F128_over_DH_F256','R_F256_over_R_F128']}}}
 suites={s:aggregate([r for r in records if r['suite']==s],sum(r['suite']==s for r in records))for s in sorted(set(r['suite']for r in records))};newcells=[cells[e['input_digest'],'CH',e['source_profile']]for e in expected.values()];coverage={'fixed_input_n':len(population),'source_slots_expected':len(cells),'accepted_source_slots':sum(c['accepted']for c in cells.values()),'remaining48_expected':len(newcells),'remaining48_accepted':sum(c['accepted']for c in newcells),'remaining48_archived_negative':sum(c['status']==FAIL for c in newcells),'remaining48_verification_HOLD':sum(c['status']=='HOLD_READONLY_VERIFICATION'for c in newcells),'remaining48_pending':sum(not c['accepted']and c['status']not in[FAIL,'HOLD_READONLY_VERIFICATION']for c in newcells),'common_both_F_n':len(common),'remaining48_terminal_verified':all(c['status']in[PASS,FAIL]for c in newcells)}
 return {'schema':'DTC_REMAINING48_CORE32_STATISTICS_V1','authority_commit':contract['authority_commit'],'coverage':coverage,'population_status':'FULL_CORE32_ONLY_WHEN_COMMON32; interim subset results descriptive, not full-suite conclusions','all_programs':records,'all_core32':aggregate(records,len(population)),'by_suite':suites,'same_input_both_F_ids':[r['input_digest']for r in common],'identity_rule':'source_profile is execution identity; comparison profile is only metric context','missingness':'All32rows retained. Negative/HOLD/pending never become cycles or accepted. No per-program bestF selection.','scientific_role_boundary':'128original+16firstCH+48remainingCH preserved independently','new_models_or_runtime_actions':0}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--observations');p.add_argument('--output',required=True);a=p.parse_args();contract=json.loads(pathlib.Path(a.contract).read_bytes());obs=json.loads(pathlib.Path(a.observations).read_bytes())['observations']if a.observations else[];report=evaluate(contract,obs);pathlib.Path(a.output).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['coverage']))
