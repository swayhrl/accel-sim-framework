import pathlib,json,hashlib,csv,math,collections
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');D=V/'agents/D_independent_review_v1';R=V/'root_authority_math_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mf=R/'MANIFEST.json';assert sha(mf)=='77eca397a7d4133f96bd63f27bb695e87aad1020b44399b99b885692a2085cee'
m=json.loads(mf.read_text());checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
for x in m['files']:
 p=R/x.get('path',x.get('relative_path',x.get('name')));ck('Root math member '+p.name,sha(p)==x['sha256'])
rows=list(csv.DictReader((R/'CORE32_RECOMPUTED.csv').open()));summary=json.loads((R/'FULL32_REUSED_AUTHORITY_MATH.json').read_text())['summary'];out={}
ck('Exactly64 program-profile rows',len(rows)==64)
profiles={p:[r for r in rows if r['profile']==p] for p in ['F128','F256']}
ck('Both profiles same fixed32 complete identity set',{(r['program'],r['input_digest']) for r in profiles['F128']}=={(r['program'],r['input_digest']) for r in profiles['F256']} and len(profiles['F128'])==len(profiles['F256'])==32)
for p,rr in profiles.items():
 vals=collections.defaultdict(list)
 for r in rr:
  ch0,dh0,ch,dh=[int(r[k]) for k in ['CH_P0','DH_P0','CH_F','DH_F']];d={'S_CH':ch0/ch,'S_DH':dh0/dh,'R_P0':ch0/dh0,'R':ch/dh,'I':(dh0/dh)/(ch0/ch)}
  for k,v in d.items():ck(p+' '+r['program']+' '+k,math.isclose(v,float(r[k]),rel_tol=1e-14));vals[k].append(v)
 out[p]={}
 for k,a in vals.items():
  stats={'GM':math.exp(sum(math.log(v) for v in a)/len(a)),'n':len(a),'positive':sum(v>1 for v in a),'negative':sum(v<1 for v in a),'zero':sum(v==1 for v in a)}
  ck(p+' '+k+' GM',math.isclose(stats['GM'],summary[p][k]['GM'],rel_tol=1e-14));ck(p+' '+k+' counts',all(stats[t]==summary[p][k][t] for t in ['n','positive','negative','zero']));out[p][k]=stats
o={'schema':'DTC_V2_D_INDEPENDENT_REUSED_CORE32_INTEGER_MATH_CHECK','checks':checks,'summary':out,'source_manifest':str(mf),'source_manifest_sha256':sha(mf),'scope':'Recomputed integer-cycle ratios and common32 GM/counts; Root full192 RESULT SHA checks are source authority, not independently re-run raw or lifecycle here.','source_rows':64,'new_models':0,'new_registry_writes':0}
p=D/'INDEPENDENT_CORE32_MATH_REVIEW.json';assert not p.exists();p.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'sha256':sha(p)}))
