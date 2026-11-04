import pathlib,json,hashlib,subprocess
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');B=V/'agents/B_mechanisms_v1';D=V/'agents/D_independent_review_v1';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
pins=json.loads((B/'SOURCE_PINS_V2.json').read_text())['sourcefiles']
for x in pins:ck('B declared source SHA '+pathlib.Path(x['path']).name,sha(pathlib.Path(x['path']))==x['sha256'])
for i,x in enumerate(json.loads((B/'MECHANISM_SOURCE_EVIDENCE_V2.json').read_text())):
 p=pathlib.Path(x['source']['path']);lines=p.read_text().splitlines();numbered='\n'.join(f'{n+1}: {lines[n]}' for n in range(x['first_line']-1,x['last_line']));ck('B literal excerpt '+str(i),numbered==x['excerpt'])
 for root,commit in [('/root/data/dtc_failure_repair_20261025_v1/core','9eedb3131937748f0492fa83aad37d3691118d70'),('/root/data/dtc_failure_repair_20261025_v1/framework','02775fd795cde5aae1480d81cee6eb481d0a08f4')]:
  rr=pathlib.Path(root)
  if p.is_relative_to(rr):
   blob=subprocess.run(['git','-C',str(rr),'show',commit+':'+str(p.relative_to(rr))],capture_output=True,check=True).stdout;ck('B fixed Git excerpt source '+str(i),blob==p.read_bytes() and commit==x['fixed_commit'])
refs=[]
for name,expected in [('root_draft_v1','8ea9ea10419fc3902560faa994775785fc2ab4542ea67caf71a0fb647cf2b789'),('root_reproduction_v1','4fe6aa3c44d45cfe8ffe943901fc865f1cc489da5cb834c9eaa7d95b386d2420')]:
 folder=V/name;mf=folder/'MANIFEST.json';ck('Root frozen manifest '+name,sha(mf)==expected);mm=json.loads(mf.read_text())
 for x in mm['files']:
  p=folder/x.get('path',x.get('relative_path',x.get('name')));ck('Root member '+name+'/'+p.name,sha(p)==x['sha256'])
 refs.append({'path':str(mf),'sha256':expected})
nextdoc=(V/'root_draft_v1/NEXT_EXECUTION_GOAL_PENDING_APPROVAL.md').read_text();tagdoc=(V/'root_draft_v1/TAG_PARAMETER_FOLLOWUP_PENDING_APPROVAL.md').read_text();decision=(V/'root_draft_v1/V2_SCIENTIFIC_DECISION.md').read_text()
ck('No subset budget shrinking clause','or a separately documented approved subset' not in nextdoc)
ck('Exact16 one-use proposed scope','exactly16' in nextdoc and 'one-use' in nextdoc)
ck('Separate optional Tag approval boundary','does not approve these Tag candidates' in tagdoc)
ck('A2 not authorized or silently folded into originalCore','No A2 simulator binary' in tagdoc and 'not production Core9eed' in tagdoc)
ck('J complete source intersection','J requires all four accepted DH states' in decision)
ck('Wholedeclared trace/numeric boundary','NOT_NEWLY_CERTIFIED' in decision and 'UNPROVEN' in decision)
o={'checks':checks,'Root_manifests':refs,'B_manifest_sha256':'2e95b5d430ce9d3d0c012a60dc7043c82f5081e89fa622b3ac0141eb4cf7adb1','scope':'Source excerpts/literal fixed Git/sourceSHA plus CPU-only future scientific contract review. No approval of scientific execution.','new_models':0};p=D/'INDEPENDENT_B_SOURCE_AND_ROOT_CONTRACT_REVIEW.json';assert not p.exists();p.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'sha256':sha(p)}))
