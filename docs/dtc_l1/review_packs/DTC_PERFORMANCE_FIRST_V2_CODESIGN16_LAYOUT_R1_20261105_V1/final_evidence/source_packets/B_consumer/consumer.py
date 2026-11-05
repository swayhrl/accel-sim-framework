#!/usr/bin/env python3
"""Report-only Codesign16; actual grant/closed RESULT required; never dispatch."""
from pathlib import Path
import argparse,collections,copy,csv,datetime,hashlib,json,math,uuid
import archive_witness as aw
import closed_reader as cr
import safety_hold_overlay as ho
D=Path(__file__).resolve().parent
F=json.loads((D/'FIXED_CONTRACT.json').read_bytes())
require=aw.require;sha=aw.sha;get=aw.get
js=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def pin(p):return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_bytes())
def matrix():
 p=D/'C_RESOURCE_CODESIGN_MATRIX.fixed.json';require(sha(p)==F['matrix_sha256'],'FIXED_MATRIX_SHA');m=read(p);cs=m['candidates'];require(len(cs)==16 and len({(c['input_digest'],c['profile'])for c in cs})==16,'FIXED16_IDENTITY');require(len({c['input_digest']for c in cs})==8 and {c['profile']for c in cs}=={'PHYS768_OOPIB192_TAG64x8','PHYS1024_OOPIB192_TAG64x8'},'FIXED8_TWO_UNIFORM');a=read(m['authority']['path']);require(sha(m['authority']['path'])==m['authority']['sha256'],'INPUT_AUTHORITY_SHA');base,brefs=cr.baselines(a);return m,cs,a,base,brefs

def runtime(candidates,binding=None):
 R=Path(F['root16']);cs={c['proposed_native_cohort']for c in candidates};ctx={'root':str(R),'archive':F['archive16'],'request':F['request16'],'budget':16,'source_qualified':False,'registration_granted':False,'status':'AWAIT_ACTUAL_REGISTRY_GRANT'}
 if binding is not None:
  b=read(binding)
  for k in ['root16','archive16','request16','prefix']:require(b[k]==F[k],'RUNTIME_BINDING_SCOPE:'+k)
  for x in b.get('pins',[]):require(sha(x['path'])==x['sha256'],'RUNTIME_BINDING_PIN:'+x['path'])
  ctx['runtime_binding']=pin(binding)
 reg,rr=get(F['registry']);epoch,er=get(F['epoch']);require(epoch['native_registry_sha256']==rr['sha256'],'ACTUAL_REGISTRY_EPOCH_RACE');q=reg.get('registered_future_requests',{}).get(F['request16']);ctx.update(registry=rr,epoch=er)
 if q is None:return ctx
 require(q['request']==F['request16']and q['budget']==16 and q.get('model_automatic_retries')==0,'ACTUAL_GRANT_SCOPE_RETRIES');require(set(q['admitted_specs'])==cs and set(q['consumed'])<=cs and q['remaining']==16-len(q['consumed']),'ACTUAL_GRANT_MEMBERSHIP_ACCOUNTING')
 pl,pr=get(R/'control/EXECUTION_PLAN.json');require(pr['sha256']==q['execution_plan_sha256'],'ACTUAL_REGISTERED_PLAN_SHA')
 for x in pl['source_pins']:require(sha(x['path'])==x['sha256'],'ACTUAL_SOURCE_PIN:'+x['path'])
 paths={k:R/'tools'/(F['prefix']+'_'+v+'.py')for k,v in [('engine_sha256','native'),('strict_sha256','strict'),('outbox_sha256','outbox')]}
 for k,p in paths.items():require(sha(p)==q[k],'ACTUAL_REGISTERED_SOURCE:'+k)
 lit=cr.strict_literals(paths['strict_sha256']);require(lit=={'schema':F['strict_schema'],'status':F['strict_status']},'ACTUAL_STRICT_SCHEMA_STATUS')
 mp=R/'control'/F['actual_matrix_filename'];actual,mr=get(mp);require({r['cohort']for r in actual['points']}==cs,'ACTUAL_MATRIX_COHORTS')
 for row in actual['points']:
  c=next(c for c in candidates if c['proposed_native_cohort']==row['cohort'])
  for k in ['input_digest','profile','program','suite']:require(row[k]==c[k],'ACTUAL_MATRIX_TYPED:'+k)
 ctx.update(source_qualified=True,registration_granted=True,status='ACTUAL_REGISTERED_SOURCE_QUALIFIED',execution_plan=pr,matrix=mr,source_pins=pl['source_pins'],strict_schema=lit['schema'],strict_status=lit['status'],outbox_sha256=q['outbox_sha256'],registry_state=q.get('state'),remaining=q['remaining'],consumed_n=len(q['consumed']),q=q);return ctx

def v1_references(provider,base):
 b=Path(provider).read_bytes();p=json.loads(b);require(p['schema']=='DTC_PERF_STRUCTURE48_READONLY_PUBLICATION_PROVIDER_V3' and p['baseline_source_qualified']and p['all_existing_closed_results_qualified']and p['admission_hold_metadata_qualified'],'V1_NOT_QUALIFIED_PROVIDER');mf=aw.get(p['manifest']['path'])[0];require(sha(p['manifest']['path'])==p['manifest']['sha256']and mf['files']==p['files'],'V1_MANIFEST')
 for x in p['files']:require(sha(x['path'])==x['sha256']and Path(x['path']).stat().st_size==x['bytes'],'V1_MEMBER_SHA_SIZE')
 snap=read(Path(p['snapshot'])/'SNAPSHOT.json');require(snap['report_overlay_source']['snapshot_source_sha256']=='9dfe6885ec7a7ec30608c677529dacabae78fc959dfd3befdbdc51d83471735e'and snap['report_overlay_source']['family_overlay_source_sha256']=='176e4a6f8c23b426fb0ff1a92ce4469567f841b7c2a3efd5665018ef7661b072','V1_READER_SOURCE_VERSION');out={}
 for row in snap['rows']:
  if row['variant']not in ['PHYS768_TAG64x8','PHYS1024_TAG64x8','OO_PIB192']:continue
  key=(row['input_digest'],row['variant']);r={k:row.get(k)for k in ['program','suite','input_digest','variant','status','accepted','cycles','source_RESULT','uuid','source_scientific_role']}
  if row.get('accepted'):
   v,vr=get(row['source_RESULT']['path']);require(vr==row['source_RESULT'],'V1_RESULT_SHA');q=v['proof'];dh=base[row['program'],'DH'];opt=copy.deepcopy(dh['effective_options']);option='-gpgpu_dtc_l1_oo_pib_entries'if row['variant']=='OO_PIB192'else'-gpgpu_dtc_l1_physical_lines';opt[option]=['192'if row['variant']=='OO_PIB192'else'768'if row['variant']=='PHYS768_TAG64x8'else'1024'];require(q['performance_accepted']is True and v['cycles']==row['cycles']and q['cycles']==row['cycles'],'V1_CLOSED_CYCLES');require(q['cell']=='DH'and q['input_digest']==row['input_digest']and q['profile']==row['variant']and q['structure_variant']==row['variant']and q['downstream_profile']=='P0'and q['effective_options']==opt,'V1_COMPONENT_IDENTITY')
   for k in ['core_commit','framework_commit','binary_sha256']:require(q[k]==dh['build'][k],'V1_COMPONENT_BUILD')
   r['canonical_RESULT']=vr;r['S_DH']=dh['cycles']/v['cycles'];r['source_witness']=row.get('archive_witness');r['original_scientific_role']=v['scientific_role']
  else:r['cycles']=None
  out[key]=r
 require(len(out)==24,'V1_FIXED8_THREE_SINGLE_FACTOR_REFERENCES');return out,{'provider_path':str(provider),'provider_sha256':hashlib.sha256(b).hexdigest(),'manifest':p['manifest'],'files':p['files'],'snapshot':p['snapshot'],'accepted_nonTag_points':p['summary']['accepted_new_points'],'older_C_frozen11_snapshot_replaced':False}

def closed_kernel_rows(row,dh,ch):
 proof0=read(dh['canonical_RESULT']['path'])['proof'];proofch=read(ch['canonical_RESULT']['path'])['proof'];ak=row.get('kernels');bk=proof0['kernels'];ck=proofch['kernels'];binding=read(dh['input_binding']['path']);qr=binding['qualification']['rows'];require(isinstance(ak,list)and len(ak)==len(bk)==len(ck)==len(qr),'KERNEL_ORDERED_ROI_LENGTH');out=[]
 for i,(x,y,z,q)in enumerate(zip(ak,bk,ck,qr),1):
  require(x['kernel']==y['kernel']==z['kernel']==q['kernel'],'KERNEL_ORDERED_ROI_SYMBOL');require(x.get('active_instructions',x.get('instructions'))==q['active_thread_instructions'],'KERNEL_ACTIVE_INSTRUCTIONS');out.append(dict(ordinal=i,kernel=x['kernel'],active_instructions=q['active_thread_instructions'],DH_P0_cycles=y['cycles'],CH_P0_cycles=z['cycles'],combo_cycles=x['cycles'],within_DH_cycle_delta=x['cycles']-y['cycles']))
 require(sum(x['combo_cycles']for x in out)==row['cycles']and sum(x['DH_P0_cycles']for x in out)==dh['cycles']and sum(x['CH_P0_cycles']for x in out)==ch['cycles'],'KERNEL_CYCLE_SUMS');return out

def metrics(combo,dh0,ch0,physical,pib):
 if combo is None:return dict(S_combo=None,R_combo=None,R_P0=ch0/dh0,I=None,S_physical=dh0/physical if physical else None,S_PIB=dh0/pib if pib else None,J=None,J_status='UNAVAILABLE_COMBO_NONPERFORMANCE_OR_PENDING')
 out=dict(S_combo=dh0/combo,R_combo=ch0/combo,R_P0=ch0/dh0,I=dh0/combo,S_physical=dh0/physical if physical else None,S_PIB=dh0/pib if pib else None,J=None,J_status='UNAVAILABLE_SINGLE_FACTOR_REFERENCE')
 if physical and pib:out['J']=physical*pib/(dh0*combo);require(abs(out['J']-out['S_combo']/(out['S_physical']*out['S_PIB']))<=1e-12,'J_ARITHMETIC');out['J_status']='ACTUAL_SAME_INPUT_CLOSED_TERMS'
 return out

def sign(row,k):
 c=row['cycles'];d=row['baseline_DH_cycles'];ch=row['baseline_CH_cycles']
 if k in ['S_combo','I']:a,b=d,c
 elif k=='R_combo':a,b=ch,c
 elif k=='J':a,b=row['V1_physical']['cycles']*row['V1_PIB']['cycles'],d*c
 else:raise ValueError(k)
 return (a>b)-(a<b)
def metric_stats(rows,k):
 rr=[r for r in rows if r.get(k)is not None];xs=[r[k]for r in rr];return {'n':len(xs),'GM':math.exp(sum(math.log(x)for x in xs)/len(xs))if xs else None,'positive_exact':sum(sign(r,k)>0 for r in rr),'negative_exact':sum(sign(r,k)<0 for r in rr),'zero_exact_arithmetic':sum(sign(r,k)==0 for r in rr),'missing':len(rows)-len(rr)}
def statset(rows):return {k:metric_stats(rows,k)for k in ['S_combo','R_combo','I','J']}
def summarize(rows):
 out={'planned_combo_cells':16,'fixed_program_inputs':8,'uniform_profiles':2,'sixteen_is_not_sixteen_programs':True,'CORE32_population':False,'status_counts':dict(collections.Counter(r['status']for r in rows)),'accepted':sum(r['accepted']for r in rows),'archived_negative':sum(r['status']=='ARCHIVED_NEGATIVE_NO_PERFORMANCE'for r in rows),'unused_safety_HOLD':sum(r['status']=='UNUSED_SAFETY_HOLD'for r in rows),'profiles':{},'new_models':0,'native_writes':0,'no_per_program_best_stitching':True}
 profiles=sorted({r['variant']for r in rows})
 for v in profiles:
  rr=[r for r in rows if r['variant']==v];out['profiles'][v]={'planned':8,'accepted':sum(r['accepted']for r in rr),'available_set':statset(rr),'by_suite':{s:statset([r for r in rr if r['suite']==s])for s in sorted({r['suite']for r in rr})},'not_full8_until_all_accepted':sum(r['accepted']for r in rr)!=8}
 common=set.intersection(*[{r['input_digest']for r in rows if r['variant']==v and r['accepted']}for v in profiles]);jc=set.intersection(*[{r['input_digest']for r in rows if r['variant']==v and r.get('J')is not None}for v in profiles]);out['common_combo_accepted_inputs']={'n':len(common),'ids':sorted(common),'profiles':{v:statset([r for r in rows if r['variant']==v and r['input_digest']in common])for v in profiles}};out['common_J_complete_terms_inputs']={'n':len(jc),'ids':sorted(jc),'profiles':{v:statset([r for r in rows if r['variant']==v and r['input_digest']in jc])for v in profiles}};out['all16_scientific_success']=out['accepted']==16;out['all16_closed_scientific_terminal']=sum(r['status']in['ACCEPTED_STRICT_ARCHIVE_RESTORE','ARCHIVED_NEGATIVE_NO_PERFORMANCE']for r in rows)==16;return out

def collect(v1_provider,binding=None):
 m,candidates,a,base,brefs=matrix();refs,vr=v1_references(v1_provider,base)
 try:ctx=runtime(candidates,binding)
 except Exception as e:ctx={'root':F['root16'],'archive':F['archive16'],'request':F['request16'],'source_qualified':False,'registration_granted':False,'status':'RUNTIME_SOURCE_VERIFICATION_HOLD','error':repr(e)}
 rows=[]
 for c in candidates:
  row={'program':c['program'],'suite':c['suite'],'input_digest':c['input_digest'],'variant':c['profile'],'design':'DH','downstream_profile':'P0','request':F['request16'],'route_key':'16','route':'CODESIGN16','cohort':c['proposed_native_cohort'],'accepted':False,'cycles':None,'status':ctx['status']};dh=base[c['program'],'DH'];ch=base[c['program'],'CH'];phy=refs[c['input_digest'],'PHYS768_TAG64x8'if c['physical_lines']==768 else'PHYS1024_TAG64x8'];pib=refs[c['input_digest'],'OO_PIB192'];options=dh['effective_options'];delta={k:{'from':options[k],'to':v}for k,v in c['expected_effective_options'].items()if options.get(k)!=v};require(set(delta)=={'-gpgpu_dtc_l1_physical_lines','-gpgpu_dtc_l1_oo_pib_entries'},'TWO_FACTOR_DELTA')
  if ctx['source_qualified']:
   try:
    rp=Path(F['root16'])/'analysis'/(row['cohort']+'.RESULT.json')
    if rp.exists():
     rv=read(rp)
     require(rv.get('validated_union_authorized')is False and rv.get('union_scope')=='EXPLORATORY_FIXED8_TWO_UNIFORM_COMBINATIONS_16_NOT_CORE32','EXACT16_EXPLORATORY_SCOPE')
     if rv['state']==F['FAIL16']:require(rv['proof']['status']==F['negative_proof_status'],'NEGATIVE_PROOF_IDENTITY')
    row=cr.qualify_closed(row,F,{'delta':delta,'configs':c['configs']},base,ctx)
    if row.get('accepted'):
     row['kernel_cycle_comparisons']=closed_kernel_rows(row,dh,ch);ev=read(row['native_EXIT']['path']);row['host_resource_diagnostic']={key:ev.get(key)for key in ['elapsed_seconds','peak_observed_rss_bytes','peak_result_logical_bytes','launcher_wait_returncode','stop_reason']};row['per_kernel_traffic_from_strict']='UNAVAILABLE; final cumulative totals are not per-kernel values'
    if row['status']=='AWAIT_CLOSED_RESULT':
     sp=Path(F['root16'])/'control/specs'/(row['cohort']+'.json');hold=ho.validate_unstarted(row,read(sp),candidates,ctx)
     if hold is not None:row.update(status='UNUSED_SAFETY_HOLD',accepted=False,cycles=None,uuid=None,unused_safety_hold_verification=hold)
   except Exception as e:row.update(status='VERIFICATION_HOLD',error=repr(e),accepted=False,cycles=None)
  row.update(baseline_DH_cycles=dh['cycles'],baseline_CH_cycles=ch['cycles'],baseline_DH_P0=dh['canonical_RESULT'],baseline_DH_bottom=dh['actual_bottom_RESULT'],baseline_CH_P0=ch['canonical_RESULT'],baseline_CH_bottom=ch['actual_bottom_RESULT'],V1_physical=phy,V1_PIB=pib)
  row.update(metrics(row['cycles']if row['accepted']else None,dh['cycles'],ch['cycles'],phy['cycles']if phy['accepted']else None,pib['cycles']if pib['accepted']else None));rows.append(row)
 accounting=ho.accounting(rows,ctx);pubctx={k:v for k,v in ctx.items()if k!='q'};return {'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_READONLY_SNAPSHOT_V1','authority_commit':F['authority_commit'],'matrix':pin(D/'C_RESOURCE_CODESIGN_MATRIX.fixed.json'),'fixed_contract':pin(D/'FIXED_CONTRACT.json'),'V1_dynamic_reference_source':vr,'runtime_context':pubctx,'baseline_sources':brefs,'rows':rows,'summary':dict(summarize(rows),**accounting),'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_models':0,'native_writes':0,'live_raw_reads':0,'consumer_sources':[pin(Path(__file__)),pin(D/'closed_reader.py'),pin(D/'archive_witness.py'),pin(D/'safety_hold_overlay.py')],'counter_boundary':'Proof kernels per-kernel cycles; final traffic typed cumulative; metrics mixed last-kernel/cumulative; missing!=0, gauges/peaks/means not differenced; no critical-time/area/numerical/coherence claim.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--v1-provider',required=True,type=Path);ap.add_argument('--runtime-binding',type=Path);ap.add_argument('--output-dir',required=True,type=Path);args=ap.parse_args();out=args.output_dir.resolve();require(out.is_relative_to(D/'snapshots')and not out.exists(),'NEW_OWN_SNAPSHOT_REQUIRED');s=collect(args.v1_provider,args.runtime_binding);out.mkdir(parents=True)
 def emit(n,v):(out/n).write_bytes(js(v))
 emit('SNAPSHOT.json',s);emit('SUMMARY.json',s['summary']);emit('V1_REFERENCE_SOURCE.json',s['V1_dynamic_reference_source']);emit('RUNTIME_CONTEXT.json',s['runtime_context'])
 with(out/'RESULTS.csv').open('w',newline='')as h:
  fields=['program','suite','input_digest','variant','cohort','status','cycles','baseline_DH_cycles','baseline_CH_cycles','S_combo','R_combo','R_P0','I','S_physical','S_PIB','J','J_status'];w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(s['rows'])
 with(out/'KERNEL_CYCLES.csv').open('w',newline='')as h:
  fields=['program','input_digest','variant','ordinal','kernel','active_instructions','DH_P0_cycles','CH_P0_cycles','combo_cycles','within_DH_cycle_delta'];w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore');w.writeheader()
  for r in s['rows']:
   for k in r.get('kernel_cycle_comparisons',[]):w.writerow(dict(program=r['program'],input_digest=r['input_digest'],variant=r['variant'],**k))
 (out/'README.md').write_text('Fixed8inputs x2uniform profiles=16cells. Strict/archive/native-restore closed accepted combos only yield S_combo/R_combo; J needs same-input accepted physical andPIB single factors. No product prediction, missing0, per-program best stitching or8-to-CORE32 promotion. Available-set statistics and common sets are separate; full uniform result requires all8. Fail/Root-typed unused safetyHOLD/pending preserved; all16actualclosed differs from all candidates accounted with verified unused credits. Final proof counters are mixed-scope; per-kernel cycles use proof.kernels. Consumer is CPU report-only; no model/registration/service action.\n')
 files=[dict(name=p.name,path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(out.iterdir())if p.is_file()];require(all(x['bytes']<=8*1024*1024 for x in files),'PUBLISHED_MEMBER_OVER8MIB');emit('MANIFEST.json',{'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_SNAPSHOT_MANIFEST_V1','files':files,'summary':s['summary'],'new_models':0,'native_writes':0});provider={'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_PUBLICATION_PROVIDER_V1','snapshot':str(out),'manifest':pin(out/'MANIFEST.json'),'files':files,'summary':s['summary'],'runtime_source_qualified':s['runtime_context'].get('source_qualified',False),'all16_candidates_accounted_verified':s['summary']['all16_candidates_accounted_verified'],'all16_actual_scientific_closed':s['summary']['all16_actual_scientific_closed'],'V1_dynamic_reference_source':s['V1_dynamic_reference_source'],'report_only':True,'new_models':0,'native_writes':0};emit('PUBLICATION_PROVIDER.json',provider);print(json.dumps({'output':str(out),'manifest':provider['manifest'],'summary':s['summary']}))
if __name__=='__main__':main()
