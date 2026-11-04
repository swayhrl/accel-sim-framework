import pathlib,json,hashlib,subprocess,os,resource
V=pathlib.Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_cpu_preparation_20261105_v1');A=V/'agents/A_tag_liveness_v1';D=V/'agents/D_independent_review_v1';checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
mf=A/'MANIFEST.json';ck('A frozen final manifest',sha(mf)=='3158c5a34324d53decef3ad26914e2ad07ae82e99fc71cfa023cf39b01326696')
for x in json.loads(mf.read_text())['files']:
 p=A/x.get('path',x.get('relative_path',x.get('name')));ck('A member '+str(p.relative_to(A)),sha(p)==x['sha256'])
assert 132 in os.sched_getaffinity(0)
def restricted():
 os.nice(19);os.sched_setaffinity(0,{132});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
private=D/'private_cpu_A_replay';private.mkdir(exist_ok=False)
ref=json.loads((A/'CPU_EXECUTION_RESULTS.json').read_text());runs=[]
for ver,macro in [('original',0),('global_idle_lru_v2cpu',1)]:
 exe=private/('unit_'+ver);args=['g++','-std=c++17','-O1','-Wall','-Wextra','-DGLOBAL_IDLE='+str(macro),'-I'+str(A/'include'/ver),str(A/'tag_liveness_cpu.cpp'),'-o',str(exe)];cp=subprocess.run(args,preexec_fn=restricted,capture_output=True,text=True,timeout=60);ck(ver+' independent compile',cp.returncode==0);(private/(ver+'.compile.stderr')).write_text(cp.stderr)
 run=subprocess.run([str(exe)],preexec_fn=restricted,capture_output=True,text=True,timeout=60);ck(ver+' independent directed replay',run.returncode==0);(private/(ver+'.stdout.jsonl')).write_text(run.stdout);(private/(ver+'.stderr')).write_text(run.stderr);cases=[json.loads(z) for z in run.stdout.splitlines() if z.strip()];expected=next(z for z in ref['runs'] if z['header']==ver);ck(ver+' exact expected classifications and assertions',cases==expected['cases']);ck(ver+' all bounded casesPASS',all(z['PASS'] for z in cases));runs.append({'header':ver,'cases':cases,'case_count':len(cases),'compile_argv':args,'execution_argv':[str(exe)],'private_binary_sha256':sha(exe),'CPU':132,'nice':19,'max_AS':2*1024**3,'new_models':0})
patch=(A/'global_idle_lru_v2cpu.patch').read_text();h=(A/'include/global_idle_lru_v2cpu/dtc-l1-common.h').read_text();original=(A/'include/original/dtc-l1-common.h').read_text()
ck('Original copied header exact frozen Core SHA',sha(A/'include/original/dtc-l1-common.h')=='dab2df3ec8e1fd1c8953ac146eba3c93906c84af8cce66051e5728afe9963fa1')
ck('Original LaneX invalidate function byte untouched',original[original.index('  lookup_invalidation_result invalidate_lookup'):original.index('  io_access_result access',original.index('  lookup_invalidation_result invalidate_lookup'))]==h[h.index('  lookup_invalidation_result invalidate_lookup'):h.index('  io_access_result access',h.index('  lookup_invalidation_result invalidate_lookup'))])
for token in ['!physical.allocated','!physical.ready','!physical.tag_valid','physical.ref_count','!physical.waiters.empty()','physical.generation != tag.physical.generation','if (pending_return) continue;','if (m_cross_reclaim_cycle == cycle) return false;','release(identity, cycle);']:
 ck('Global idle conservative eligibility '+token,token in patch)
ck('Both Tag organizations retained512 count','shape512_128x4' in str(runs) and 'shape512_32x16' in str(runs))
o={'checks':checks,'runs':runs,'A_manifest':{'path':str(mf),'sha256':sha(mf)},'prototype_scope':'Isolated new reclamation mechanism plus fixture-only reservation protocol. Directed replay includes private-state fault injection and API-only adversarial states; no universal safety/liveness theorem, real LDST integration, functional values or hardware cost proof.','scientific_HOLD':['Original1024Tag640 physical16 cells unchanged HOLD','A2 production/science HOLD pending independently versioned integration and finite search/arbiter timing/cost','API-only multiple-partial case not asserted production reachable'],'actual_simulator_or_GPU_starts':0,'production_core_or_V1_writes':0}
p=D/'INDEPENDENT_A_SOURCE_AND_CPU_REPLAY_REVIEW.json';assert not p.exists();p.write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'checks':len(checks),'PASS':True,'replayed_cases':sum(r['case_count'] for r in runs),'sha256':sha(p)}))
