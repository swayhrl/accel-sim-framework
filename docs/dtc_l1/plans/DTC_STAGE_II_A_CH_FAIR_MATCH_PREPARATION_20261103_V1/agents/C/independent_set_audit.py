from pathlib import Path
import subprocess,json,gzip,hashlib,collections,math
W=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/docs-worktree')
R=Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
OUT=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_preparation_20261103_v1/agents/C');OUT.mkdir(parents=True,exist_ok=True)
COMMIT='361fa6fa0700825bb9cda43e25b9fd1f60e0b262';P='docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1/periodic/20261103T141515Z_b7b31bf3/approved_analysis/AUTO_DERIVED35_V1_REPORT.json.gz'
sha=lambda b:hashlib.sha256(b).hexdigest()
b=subprocess.check_output(['git','-c','safe.directory='+str(W),'show',COMMIT+':'+P],cwd=W);d=json.loads(gzip.decompress(b));rows=d['derived35']['rows'];z=collections.defaultdict(dict);checks=[]
def check(name,ok,detail):checks.append({'check':name,'PASS':bool(ok),'detail':detail})
for r in rows:z[r['key']['program']][(r['key']['cell'],r['key']['profile'])]=r
valid=lambda n,c,p:bool(z[n][(c,p)]['original'].get('valid'))
orig=sum(r['original']['valid'] for r in rows);named=sum(bool(r['selected']) for r in rows)
check('Original 350 identity rows',len(rows)==350 and len(z)==35,{'rows':len(rows),'programs':len(z)})
check('Original accepted separate from named',orig==331 and named==336,{'original':orig,'named':named})
result_verification=[]
for r in rows:
 o=r['original'];p=o.get('RESULT_path');expected=o.get('RESULT_sha256')
 if p and expected:
  actual=sha(Path(p).read_bytes());result_verification.append({'cohort':r['original_cohort'],'path':p,'expected':expected,'actual':actual,'PASS':actual==expected})
check('All present original RESULT bytes match published hashes',all(x['PASS'] for x in result_verification),{'verified':len(result_verification),'not_present_in_report':350-len(result_verification)})
cert=d['coverage']['original_terminal_certificates'];cv=[]
for c,x in cert.items():cv.append({'cohort':c,'path':x['path'],'sha256':sha(Path(x['path']).read_bytes()),'PASS':sha(Path(x['path']).read_bytes())==x['sha256']})
check('Original missing RESULT is typed engineering terminal negative',len(cv)==1 and all(x['PASS'] for x in cv),cv)
states=collections.Counter(r['original'].get('raw_state') for r in rows)
check('18 original archived negatives',states['FAIL_L2MLP_ARCHIVED_NO_RETRY']==18,dict(states))
core=sorted(n for n in z if all(valid(n,c,p) for c,p in [('CH','P0'),('DH','P0'),('DH','F128'),('DH','F256')]))
candidates=[]
for n in sorted(z):
 for f in ['F128','F256']:
  if n in core:classification='CORE_FOURWAY';reason='Original CH-P0, DH-P0 and both DH F128/F256 accepted; fixed common population.'
  elif n=='hybridsort' and f=='F256':classification='SUPPLEMENTAL';reason='Original F256 and both P0 accepted; original DH-F128 negative; IR cannot fill original common six-cell population.'
  elif n=='lavamd' and f=='F128':classification='SUPPLEMENTAL';reason='Original DH-F128 and DH-P0 accepted; CH-P0 negative. Only same-F128 CH/DH absolute comparison after new CH acceptance; CH-own speedup and fourway improvement unavailable.'
  else:classification='DEFERRED';reason='Original required DH profile or P0 missing/negative; restore prerequisite requires separate authorized identity, never overwrite.'
  rs=z[n];candidates.append({'program':n,'profile':f,'input_digest':next(iter(rs.values()))['key']['input_digest'],'classification':classification,'reason':reason,'original_status':{c+'-'+p:{'valid':rs[(c,p)]['original']['valid'],'cohort':rs[(c,p)]['original_cohort'],'cycles':rs[(c,p)]['original'].get('cycles'),'RESULT_sha256':rs[(c,p)]['original'].get('RESULT_sha256')} for c,p in [('CH','P0'),('DH','P0'),('DH',f)]}})
cc=collections.Counter(x['classification'] for x in candidates)
check('Candidate split from original identity only',cc=={'CORE_FOURWAY':64,'SUPPLEMENTAL':2,'DEFERRED':4},dict(cc))
sets={}
for f in ['F128','F256']:
 sets[f]={'DH_self':sorted(n for n in z if valid(n,'DH','P0') and valid(n,'DH',f)),'fourway_prerequisites':sorted(n for n in z if valid(n,'CH','P0') and valid(n,'DH','P0') and valid(n,'DH',f))}
sets['F128_F256_common_DH_self']=sorted(set(sets['F128']['DH_self']) & set(sets['F256']['DH_self']))
sets['F128_F256_common_sixcell_prerequisites']=core
check('F128/F256 common original population fixed before new runs',len(core)==32 and len(sets['F128_F256_common_DH_self'])==32, {k:({j:len(v) for j,v in x.items()} if isinstance(x,dict) else len(x)) for k,x in sets.items()})
alt=[{'key':r['key'],'selected_cohort':r['selected']['cohort'],'role':r['selected']['scientific_role']} for r in rows if r['selected'] and r['selected']['cohort']!=r['original_cohort']]
check('Five named-view alternates not original replacements',len(alt)==5 and all(x['key']['program'] in ['hybridsort','scan'] for x in alt),alt)
verified=[r['original'] for r in rows if r['original'].get('valid')]
for field,expected in [('core_commit','9eedb3131937748f0492fa83aad37d3691118d70'),('framework_commit','02775fd795cde5aae1480d81cee6eb481d0a08f4'),('binary_sha256','02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d')]:
 vals=collections.Counter(x.get(field) for x in verified);check('Accepted source anchor '+field,set(vals)=={expected},dict(vals))
# Known six ratified reference schemas have missing profile/suite proof fields; use exact input digest and frozen bindings, no same-name joins.
for n in core:
 keys=[z[n][k]['original'] for k in [('CH','P0'),('DH','P0'),('DH','F128'),('DH','F256')]]
 check('Core full identity '+n, len({x['input_digest'] for x in keys})==1 and len({json.dumps(x['expected_ROI'],sort_keys=True) for x in keys})==1,{'input_digest':keys[0]['input_digest'],'ROI':keys[0]['expected_ROI']})
source={'commit':COMMIT,'git_path':P,'sha256':sha(b),'scope_path':str(R/'control/SCOPE.json'),'scope_sha256':sha((R/'control/SCOPE.json').read_bytes()),'reported_counter_availability':d['hardware_counters'],'mode':'READ_ONLY_GIT_BLOB_AND_SMALL_RESULT_HASH_JOIN_NO_MODEL_NO_REGISTRATION'}
out={'schema':'DTC_STAGE_IIA_INDEPENDENT_SET_AUDIT_V1','source':source,'all_checks_pass':all(x['PASS'] for x in checks),'checks':checks,'candidates':candidates,'sets':sets,'original_RESULT_hash_join':result_verification,'typed_engineering_negative':cv,'named_alternates_not_original':alt}
(OUT/'INDEPENDENT_SET_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'OUT':str(OUT),'checks':len(checks),'all_PASS':out['all_checks_pass'],'classes':dict(cc),'source':source},indent=2))
