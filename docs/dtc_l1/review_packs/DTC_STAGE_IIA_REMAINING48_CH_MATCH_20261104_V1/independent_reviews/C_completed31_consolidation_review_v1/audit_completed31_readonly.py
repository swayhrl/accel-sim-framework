from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import json,gzip,hashlib,datetime,math,collections
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');B=A/'root_completed31_consolidation_v1';R=A/'root_independent_cycle_statistics_v1/20261104T071015468833Z';O=A/'agents/C_completed31_consolidation_review_v1';rd=lambda p:json.loads(Path(p).read_bytes());gz=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'pass':True})
def close(a,b):return a is None and b is None or a is not None and b is not None and math.isclose(float(a),float(b),rel_tol=2e-12,abs_tol=1e-13)
for label,p,want in [('consolidation',B,'23fd901794b23c37b185aa29de3fb6db40a0e50a3b4cc58eca340aa1303a8c2f'),('Root40 audit',R,'60f89782895950134e3946333dbf78dd9fed3d102c131cb5db64435ae80c71bd')]:
 ck(label+' manifest',sha(p/'MANIFEST.json')==want)
 for x in rd(p/'MANIFEST.json')['files']:ck(label+' member '+x['path'],sha(p/x['path'])==x['sha256']and(p/x['path']).stat().st_size==x['bytes'])
v=gz(R/'AUDIT.json.gz');c=gz(B/'CONSOLIDATION.json.gz');contractpath=A/'agents/B_runtime_analysis_v1/CORE32_REFERENCE_CONTRACT.json';ck('immutable CORE32 source contract',sha(contractpath)=='9627c0fad4395ddf2414e958b897f8f4b73347cf29b70e31ca7f9fa912f0cc6b');contract=rd(contractpath);pop={x['input_digest']:x for x in contract['population']};sources={};aliases=0;roles=collections.Counter()
ck('frozen source audit184 slots40 endpoints not final',v['status']=='PASS'and v['accepted_slots_rechecked']==190 and v['new48_raw_cycle_endpoints_rechecked']==46 and len(v['raw_new48_cycle_endpoints'])==46 and not v['final_full32']and v['common_both_F_n']==31 and len(v['raw_sources'])==190)
for x in v['raw_sources']:
 d=rd(x['source_RESULT_path']);ck(x['program']+x['slot']+' accepted RESULT identity SHA/cycles',sha(x['source_RESULT_path'])==x['source_RESULT_sha256']and d['cycles']==x['cycles']and d['uuid']==x['uuid']and d['state']==x['source_state']);under=d;alias=x['legal_prior_P0_alias'];roles[x['role']]+=1
 if alias is not None:
  aliases+=1;under=rd(alias['underlying_RESULT_path']);ck(x['program']+x['slot']+' inherited legal alias identity preserved',alias['reuse_identity_unchanged']and sha(alias['underlying_RESULT_path'])==alias['underlying_RESULT_sha256']==d['reference_result_sha256']and alias['underlying_execution_uuid']==under['uuid']==d['uuid']and under['cycles']==d['cycles']and under['state']==x['underlying_PASS_state'])
 ck(x['program']+x['slot']+' accepted source/build/input domain',under['state'].startswith('PASS_')and under['proof']['performance_accepted']and under['proof']['input_digest']==x['input_digest']and under['proof']['core_commit']=='9eedb3131937748f0492fa83aad37d3691118d70'and under['proof']['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'and under['proof']['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')
 sources[x['input_digest'],x['slot']]=x
ck('six inherited P0 wrappers not new performance replacements',aliases==6 and roles['STAGEII_REMAINING48_AUTHORIZED_CH']==46 and sum(roles.values())==190)
rows=[];computed={}
for item in c['all_programs']:
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
ck('32 retained identities and28 common4pending',len(rows)==32 and set(x['input_digest']for x in rows)==set(pop)and sum(x['common']for x in rows)==31 and {x['program']for x in rows if not x['common']}=={'GESUMMV'})
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
ck('suite denominators9/7/6/6 of9/7/8/8',[(computed[k]['common_n'],computed[k]['expected_n'])for k in ['CUDA Samples','Parboil','PolyBench/GPU','Rodinia']]==[(9,9),(7,7),(7,8),(8,8)])
ck('consolidation does not select F or claim full32',c['final_core32_claim']is False and c['uniform_F_selected']is False and c['statistics']==v['statistics']and c['source_audit_manifest_sha256']==sha(R/'MANIFEST.json'))
# Verify each displayed table row independently against integer source values/rounded statistics.
text=(B/'REPORT.md').read_text();table_rows=[[z.strip()for z in line.strip('|').split('|')]for line in text.splitlines()if line.startswith('|')]
for r in rows:
 q=next(t for t in table_rows if t[0]==r['program']);expected=[r['program'],r['input_digest']]+[str(r['cycles'][f])if r['cycles'][f]is not None else chr(8212)for f in ['CH_P0','CH_F128','CH_F256','DH_P0','DH_F128','DH_F256']]+[f"{float(r['metrics'][p]['I']):.9f}"if p in r['metrics']else chr(8212)for p in ['F128','F256']]+[str(r['common'])];ck(r['program']+' displayed full32 row',q==expected)
for pf in ['F128','F256']:
 a=computed['CORE32']['common'][pf];q=next(t for t in table_rows if t[0]==pf and len(t)==7);ck(pf+' displayed GM28 common table',q==[pf,'31']+[f"{a[k]['GM']:.9f}"for k in ['S_CH','S_DH','R_P0','R','I']])
 for k in ['S_CH','S_DH','R','I']:
  d=a[k];q=next(t for t in table_rows if t[:2]==[pf,k]);ck(pf+k+' displayed integer-sign distribution',q==[pf,k,str(d['positive']),str(d['zero']),str(d['negative'])]+[f"{d[z]:.9f}"for z in ['minimum','median','maximum']])
for label,actual in computed.items():
 if label=='CORE32':continue
 for pf in ['F128','F256']:
  q=next(t for t in table_rows if t[0]==label and t[3]==pf);ck(label+pf+' displayed suite GM/coverage',q==[label,str(actual['common_n']),str(actual['expected_n']),pf]+[f"{actual['common'][pf][k]['GM']:.9f}"for k in ['S_CH','S_DH','R','I']])
for metric,d in computed['CORE32']['direct'].items():
 q=next(t for t in table_rows if t[0]==metric);ck(metric+' displayed matched directF table',q==[metric,'31',f"{d['GM']:.9f}",str(d['positive']),str(d['zero']),str(d['negative'])]+[f"{d[z]:.9f}"for z in ['minimum','median','maximum']])
ck('both I GMbelow1 distinct from R GMabove1',all(computed['CORE32']['common'][pf]['I']['GM']<1<computed['CORE32']['common'][pf]['R']['GM']for pf in ['F128','F256']))
clauses=['not final32/35/42 coverage','completion order is not a selection criterion','exact same31 accepted six-cell inputs','performance regression is retained accepted data','R>1 describes absolute DH advantage','I>1 describes incremental relative improvement','no program-specific bestF GM'if'no program-specific bestF GM'in text else'No program-specific bestF GM','not a unified effective96KiB cache or equal area','46-point resource coverage','No live progress preview contributes','final full48 archive/recovery audit','does not complete the Goal','EnglishLaTeXv0.23']
ck('narrative retains subset/negative/ratio/physical/permission boundaries',all(x in text for x in clauses))
# Exact closed supplement references and the specific Core coherence source fact remain immutable.
for name,want in [('C_completed_3mm_review_v1','4d1b892eea5a3af681f1d26535d9fa77917ddd7cccf3016e923cd8b38d5c0251'),('C_completed_myocyte_review_v1','e060ab9d4e89cadf40b2172a98e0adead5b6c17f72d777475c493b12f211aa64'),('C_completed_srad_review_v1','b035a78eb92ebffcf0620969dfa466d4784f836f3950b2884ed4f2ac294e993f')]:ck('closed C supplement '+name,sha(A/'agents'/name/'MANIFEST.json')==want and want in text)
ck('coherence fact binds actual source independently of candidateELF identity',sha(A/'agents/C_completed_myocyte_review_v1/FIXED_CORE_INVALIDATION_ENTRY_FACTS.json')=='72587e571dfde4f1b834f4cce48176205ec1d4e0ce64dd79ea78d26520fa5697'and all(x in text for x in ['flag0 takes the ordinary m_L1D invalidation path','does not exhaust every OO reset path or prove a stale-data bug','Downstream matching alone is not numerical-coherence certification','Candidate source/ELF/y/params binding and runtime OO upload coherence are separate unresolved questions']))
ck('srad/3MM/myocyte negative and source boundaries retained',all(x in text for x in ['myocyte issues exactly one32B read atom atK1','srad issues13 read atoms','extract phase retains a22cycle absolute DH regression','uninitialized E/F/G and uses +=','None of these limitations permits repairing or replacing frozen inputs']))
assert not O.exists();O.mkdir();res={'schema':'C_COMPLETED31_CONSOLIDATION_INDEPENDENT_NARROW_REVIEW_V1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_WITH_FORWARD_PERMISSION_AND_RATIO_WORDING_CLARIFICATIONS','checks':checks,'check_count':len(checks),'source_consolidation_manifest_sha256':sha(B/'MANIFEST.json'),'source_Root190_audit_manifest_sha256':sha(R/'MANIFEST.json'),'scope':{'fixed_programs':32,'matched_complete_programs':31,'accepted_RESULTs_rehashed':190,'new48_accepted':46,'pending_newCH_GESUMMV':2,'six_legal_P0_alias_underlying_RESULTs_rehashed':6,'raw_or_archive_payloads_scanned':False,'not_final48_or_fullCORE32_signoff':True},'recomputed_statistics':computed,'source_role_counts':dict(roles),'forward_clarifications':[{'original_scope':'Any numerical/native GPU validation,new instrumentation or simulation needs its own authorization.','interpretation':'Separate authorization is required for new scientific execution/capture/GPU tasks/instrumentation/simulation or a changed correctness/initial-state contract. Already authorized CPU-only read-only source, static mapping and numerical reasoning/checks remain permitted. This sentence creates no new approval gate for them.'},{'original_scope':'DirectF prose absolute DH/CH ratio','interpretation':'The defined R remains CH cycles divided by DH cycles, equivalently DH speed relative to CH. R_F256/R_F128>1 means this defined speed advantage increases. It is not the inverted DH-cycle/CH-cycle ratio.'}],'conclusion':'Both F rows use exactly the same31 accepted complete input identities. GM I is below1 while absolute CH-cycle/DH-cycle GM is above1; no full32 result, bestF choice, isoarea or numerical-coherence certification follows. Only GESUMMV newCH F128/F256 remain absent in this frozen snapshot.','frozen_Root_V1_bytes_changed':False,'new_models_owner_history_waiter_paper_Git_actions':0};(O/'REVIEW.json').write_text(json.dumps(res,indent=2)+'\n');(O/'README.md').write_text('Completed31 consolidation narrow independent review: PASS with two wording clarifications.\n\n190 accepted RESULT identities and6 legal P0 wrapper/underlying joins were rehashed. Independent exact Fractions/55digit Decimal GM reproduce same31 common-set statistics, exact signs, distributions, suites, directF values and all32 displayed input/cycle rows. Only GESUMMV CH-F128/F256 remain absent. No raw/archive payload or model was scanned.\n\nBoth F profiles have GMI<1 while GM(CHcycles/DHcycles)>1; these are distinct statements. Missing coverage, regressions, unequal hardware, modeled memcpy initial state and candidate-source versus runtime OO coherence limits remain explicit. RootV1 is unchanged.\n\nPermission clarification: new scientific execution/capture/GPU/instrumentation/simulation needs separate authority. Existing authorized CPU-only read-only source/static/numerical checks remain allowed; the sentence creates no additional approval requirement. Ratio clarification: defined R is CHcycles/DHcycles, equivalent to DH speed/CH speed. DirectF prose does not invert it to DHcycles/CHcycles.\n\nThis is neither final48 lifecycle/CORE32 signoff nor new execution approval. Source/owner/waiter/pins/ledger/Git/v0.23 remain unchanged.\n');print(json.dumps({'status':res['status'],'checks':len(checks),'review_sha256':sha(O/'REVIEW.json')}))

