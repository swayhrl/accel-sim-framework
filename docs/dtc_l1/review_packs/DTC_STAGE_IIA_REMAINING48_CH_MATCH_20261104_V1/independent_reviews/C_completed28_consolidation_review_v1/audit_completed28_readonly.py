from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import json,gzip,hashlib,datetime,math,collections
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');B=A/'root_completed28_consolidation_v1';R=A/'root_independent_cycle_statistics_v1/20261104T043415364666Z';O=A/'agents/C_completed28_consolidation_review_v1';rd=lambda p:json.loads(Path(p).read_bytes());gz=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
def close(a,b):return a is None and b is None or a is not None and b is not None and math.isclose(float(a),float(b),rel_tol=2e-12,abs_tol=1e-13)
for label,p,want in [('consolidation',B,'f880b1388f0e8728fca8cfaf40de2ed3f39aa322c3b2c9c1353d3d5a8c323a8f'),('Root40 audit',R,'dd5076b738679dcd262689423bbef148fe1e7b20bb2bafb4cd8700e25df1a47d')]:
 ck(label+' manifest',sha(p/'MANIFEST.json')==want)
 for x in rd(p/'MANIFEST.json')['files']:ck(label+' member '+x['path'],sha(p/x['path'])==x['sha256']and(p/x['path']).stat().st_size==x['bytes'])
v=gz(R/'AUDIT.json.gz');c=gz(B/'CONSOLIDATION.json.gz');contractpath=A/'agents/B_runtime_analysis_v1/CORE32_REFERENCE_CONTRACT.json';ck('immutable CORE32 source contract',sha(contractpath)=='9627c0fad4395ddf2414e958b897f8f4b73347cf29b70e31ca7f9fa912f0cc6b');contract=rd(contractpath);pop={x['input_digest']:x for x in contract['population']};sources={};aliases=0;roles=collections.Counter()
ck('frozen source audit184 slots40 endpoints not final',v['status']=='PASS'and v['accepted_slots_rechecked']==184 and v['new48_raw_cycle_endpoints_rechecked']==40 and len(v['raw_new48_cycle_endpoints'])==40 and not v['final_full32']and v['common_both_F_n']==28 and len(v['raw_sources'])==184)
for x in v['raw_sources']:
 d=rd(x['source_RESULT_path']);ck(x['program']+x['slot']+' accepted RESULT identity SHA/cycles',sha(x['source_RESULT_path'])==x['source_RESULT_sha256']and d['cycles']==x['cycles']and d['uuid']==x['uuid']and d['state']==x['source_state']);under=d;alias=x['legal_prior_P0_alias'];roles[x['role']]+=1
 if alias is not None:
  aliases+=1;under=rd(alias['underlying_RESULT_path']);ck(x['program']+x['slot']+' inherited legal alias identity preserved',alias['reuse_identity_unchanged']and sha(alias['underlying_RESULT_path'])==alias['underlying_RESULT_sha256']==d['reference_result_sha256']and alias['underlying_execution_uuid']==under['uuid']==d['uuid']and under['cycles']==d['cycles']and under['state']==x['underlying_PASS_state'])
 ck(x['program']+x['slot']+' accepted source/build/input domain',under['state'].startswith('PASS_')and under['proof']['performance_accepted']and under['proof']['input_digest']==x['input_digest']and under['proof']['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and under['proof']['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and under['proof']['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')
 sources[x['input_digest'],x['slot']]=x
ck('six inherited P0 wrappers not new performance replacements',aliases==6 and roles['STAGEII_REMAINING48_AUTHORIZED_CH']==40 and sum(roles.values())==184)
rows=[];computed={}
for item in c['per_program']:
 ident=item['input_digest'];ck(item['program']+' frozen identity and original table join',ident in pop and item['program']==pop[ident]['program']and item['suite']==pop[ident]['suite']and item==next(r for r in v['all_programs']if r['input_digest']==ident))
 cyc={slot:sources.get((ident,slot),{}).get('cycles')for slot in ['CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256']};ck(item['program']+' exact six-cell cycles/missing preserved',cyc==item['cycles']and item['common']==all(x is not None for x in cyc.values()));metrics={};direct=None
 for pf in ['F128','F256']:
  a,b,d,e=cyc['CH_P0'],cyc['CH_'+pf],cyc['DH_P0'],cyc['DH_'+pf]
  if None in [a,b,d,e]:ck(item['program']+pf+' missing ratio not imputed',not item['exact_ratios'].get(pf));continue
  metrics[pf]={'S_CH':Q(a,b),'S_DH':Q(d,e),'R_P0':Q(a,d),'R':Q(b,e),'I':Q(d*b,a*e)}
  for name,q in metrics[pf].items():
   out=item['exact_ratios'][pf][name];ck(item['program']+pf+name+' exact fraction/sign',out['numerator']==q.numerator and out['denominator']==q.denominator and close(out['value'],q)and out['sign']==('positive'if q>1 else'negative'if q<1 else'exact_zero'))
 if item['common']:direct={'CH_F128_over_CH_F256':Q(cyc['CH_F128'],cyc['CH_F256']),'DH_F128_over_DH_F256':Q(cyc['DH_F128'],cyc['DH_F256']),'R_F256_over_R_F128':Q(cyc['CH_F256']*cyc['DH_F128'],cyc['DH_F256']*cyc['CH_F128'])}
 rows.append(dict(item,metrics=metrics,direct=direct))
ck('32 retained identities and28 common4pending',len(rows)==32 and set(x['input_digest']for x in rows)==set(pop)and sum(x['common']for x in rows)==28 and {x['program']for x in rows if not x['common']}==set(c['pending_fixed_inputs'])=={'3MM','GESUMMV','myocyte','srad_v1'})
def dist(vals):
 xs=sorted(vals);n=len(xs)
 def quant(q):
  if n==0:return None
  z=q*(n-1);i=z.numerator//z.denominator;t=z-i;return float(xs[i]+t*(xs[min(i+1,n-1)]-xs[i]))
 if not n:gm=None
 else:
  with localcontext()as ctx:
   ctx.prec=55;gm=float((sum((Decimal(x.numerator)/Decimal(x.denominator)).ln()for x in xs)/Decimal(n)).exp())
 return dict(n=n,positive=sum(x>1 for x in xs),negative=sum(x<1 for x in xs),zero=sum(x==1 for x in xs),GM=gm,minimum=float(xs[0])if n else None,maximum=float(xs[-1])if n else None,p25=quant(Q(1,4)),median=quant(Q(1,2)),p75=quant(Q(3,4)))
for label,report in c['statistics'].items():
 group=rows if label=='CORE32'else[r for r in rows if r['suite']==label];common=[r for r in group if r['common']];actual={'expected_n':len(group),'common_n':len(common),'available':{},'common':{},'direct':{}};ck(label+' fixed suite coverage',report['expected_n']==len(group)and report['common_n']==len(common))
 for kind in ['available','common']:
  for pf in ['F128','F256']:
   rs=[r for r in group if pf in r['metrics']]if kind=='available'else common;actual[kind][pf]={}
   for metric in ['S_CH','S_DH','R_P0','R','I']:
    calc=dist([r['metrics'][pf][metric]for r in rs]);actual[kind][pf][metric]=calc;ck(label+kind+pf+metric+' GM/distribution/integer signs',all(close(calc[k],report[kind][pf][metric][k])for k in calc))
 for metric in ['CH_F128_over_CH_F256','DH_F128_over_DH_F256','R_F256_over_R_F128']:
  calc=dist([r['direct'][metric]for r in common]);actual['direct'][metric]=calc;ck(label+metric+' matched directF distribution',all(close(calc[k],report['direct'][metric][k])for k in calc))
 computed[label]=actual
ck('suite denominators9/7/6/6 of9/7/8/8',[(computed[k]['common_n'],computed[k]['expected_n'])for k in ['CUDA Samples','Parboil','PolyBench/GPU','Rodinia']]==[(9,9),(7,7),(6,8),(6,8)])
ck('consolidation does not select F or claim full32',c['final_core32_claim']is False and c['uniform_F_selected']is False and c['statistics']==v['statistics']and c['source_audit_manifest_sha256']==sha(R/'MANIFEST.json'))
# Verify each displayed table row independently against integer source values/rounded statistics.
text=(B/'CURRENT_SCIENTIFIC_REPORT_40_OF_48.md').read_text();table_rows=[[z.strip()for z in line.strip('|').split('|')]for line in text.splitlines()if line.startswith('|')]
for r in rows:
 q=next(t for t in table_rows if t[0]==r['program']);expected=[r['program'],r['input_digest']]+[str(r['cycles'][f])if r['cycles'][f]is not None else'MISSING'for f in ['CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256']]+[f"{float(r['metrics'][p]['I']):.6f}"if p in r['metrics']else'MISSING'for p in ['F128','F256']]+[str(r['common'])];ck(r['program']+' displayed full32 row',q==expected)
for pf in ['F128','F256']:
 a=computed['CORE32']['common'][pf];q=next(t for t in table_rows if t[0]==pf and len(t)==7);ck(pf+' displayed GM28 common table',q==[pf,'28']+[f"{a[k]['GM']:.6f}"for k in ['S_CH','S_DH','R_P0','R','I']])
 for k in ['S_CH','S_DH','R','I']:
  d=a[k];q=next(t for t in table_rows if t[:2]==[pf,k]);ck(pf+k+' displayed integer-sign distribution',q==[pf,k,str(d['positive']),str(d['zero']),str(d['negative'])]+[f"{d[z]:.6f}"for z in ['minimum','median','maximum']])
for label,actual in computed.items():
 if label=='CORE32':continue
 for pf in ['F128','F256']:
  q=next(t for t in table_rows if t[0]==label and t[3]==pf);ck(label+pf+' displayed suite GM/coverage',q==[label,str(actual['common_n']),str(actual['expected_n']),pf]+[f"{actual['common'][pf][k]['GM']:.6f}"for k in ['S_CH','S_DH','R','I']])
clauses=['completed-subset analysis, not the final32/35/42-program result','completion order is not an input-selection rule','identical28 complete six-cell inputs','Performance regressions are accepted scientific data','not for choosing workloads','I>1 only means relative improvement from P0','not a unified96KiB effective cache or equal area','No live progress preview contributes','Full new48 lifecycle/archive/native recovery is separately required','does not approve final figures','v0.23 stays frozen']
ck('narrative scientific/coverage/permission boundaries',all(x in text for x in clauses))
assert not O.exists();O.mkdir();result={'schema':'C_COMPLETED28_CONSOLIDATION_INDEPENDENT_REVIEW_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_WITH_MINOR_FILE_LOCATOR_CLARIFICATION','checks':checks,'check_count':len(checks),'source_root_consolidation_manifest_sha256':sha(B/'MANIFEST.json'),'source_root40_audit_manifest_sha256':sha(R/'MANIFEST.json'),'scope':{'frozen_programs':32,'matched_complete_programs':28,'accepted_slots':184,'new48_accepted':40,'new48_pending':8,'inherited_P0_alias_wrappers':6,'original_and_first16_reference_slots':144,'full48_terminal_lifecycle_audit_performed':False,'raw40_endpoints_reused_at_qualified_Root_scope_not_reopened':True},'recomputed_statistics':computed,'source_role_counts':dict(roles),'minor_forward_clarification':'The report prose labels its machine data CONSOLIDATION.json; the actual manifest-pinned artifact is CONSOLIDATION.json.gz. Consume the gzip member without changing frozen V1 bytes. This is a file locator typo, not a cycle/statistics error.','conclusion':'The same28 matched inputs yield CH and DH self gains; GM I remains below1 for both F profiles. GM absolute CH/DH above1 is distinct from incremental F benefit. No full32 conclusion or optimalF choice follows.','new_models_or_live_raw_or_owner_history_Git_paper_changes':0};(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');(O/'README.md').write_text('Completed28 consolidation independent review: PASS, with one file-locator clarification.\n\n184 actual accepted RESULT identities and6 legal P0 wrapper→underlying joins were rehashed; source cycles and32 frozen identities match. Independent exact Fractions and55-digit Decimal GM calculations reproduce common/available/directF and all suite distributions, counts, quantiles, coverage and displayed tables. Both F profiles use the identical28 complete inputs. Four pending inputs remain listed without imputed cycles.\n\nThe report preserves regressions/zeros, partial-coverage limits, unequal L1 resource/area conditions and measured-versus-causal boundaries. GM I is below1 for both F profiles; absolute DH-versus-CH advantage is a separate comparison. No full32 or bestF conclusion is established. Existing raw40 endpoint qualification is reused; no live log, archive rescan, model/control/history/paper/Git mutation was performed. Not final48 lifecycle signoff.\n\nLocator clarification: prose CONSOLIDATION.json refers to the actual manifest-pinned CONSOLIDATION.json.gz. Root V1 remains byte-for-byte unchanged.\n');print(json.dumps({'status':result['status'],'checks':len(checks),'review_sha256':sha(O/'REVIEW.json')}))

