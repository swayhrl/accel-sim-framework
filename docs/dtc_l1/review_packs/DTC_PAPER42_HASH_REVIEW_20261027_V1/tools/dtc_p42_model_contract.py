import pathlib,json,hashlib,subprocess,collections
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_paper42_hash_review_20261027_v1');D=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=P('/root/data/dtc_failure_repair_20261025_v1');L=json.loads((A/'evidence/LEDGER_AUDIT.json').read_bytes());repo=D/'telemetry_v2/framework';old='cfd3ff56d7ba6642dab6c7710ec4f6065168174e';new='3b362ab5c0934fdcea9697b10244c6de5c4a14ae';cmd=['git','-C',str(repo),'diff',old,new];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0;diff=r.stdout;assert [l for l in diff.splitlines()if l.startswith('diff --git')]==['diff --git a/gpu-simulator/ag7_policyb_progress.h b/gpu-simulator/ag7_policyb_progress.h'];qu=P(D/'telemetry_v2/CPU_PROTOCOL_QUALIFICATION.json');cpu=json.loads(qu.read_bytes());assert cpu['status']=='PASS_OBSERVATIONAL_CAP1M_CPU_PROTOCOL_NOT_SCIENTIFIC_MODEL'
checks=[];sources=collections.Counter();violations=[];pairs=[]
for row in L['current_original']:
 ms={k:v for k,v in row['modes'].items()if (v.get('result')or{}).get('state')=='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'}
 for mode,m in ms.items():
  s=m['strict'];b=m['DONE'];ok=s['cycles']==m['result']['cycles']and s['performance_accepted']and b['launcher_wait_returncode']==0 and b['stop_reason']is None and s['core_commit']=='2e3bef4364e578cddd0e881c0baace2e51c55930'and s['framework_commit']in [old,new];checks.append(dict(cohort=m['cohort'],status='PASS'if ok else'FAIL',source_sha=s['binary_sha256'],strict_status=s['status']));sources[(s['core_commit'],s['framework_commit'],s['binary_sha256'])]+=1
  if not ok:violations.append(m['cohort'])
 for a,b,allowed in [('CM','CH',{'-gpgpu_cache:dl1'}),('DM','DH',{'-gpgpu_dtc_l1_tag_hash_bankrow'})]:
  if a in ms and b in ms:
   aa=ms[a]['strict']['effective_options'];bb=ms[b]['strict']['effective_options'];delta={k:[aa.get(k),bb.get(k)]for k in set(aa)|set(bb)if aa.get(k)!=bb.get(k)};ok=set(delta)==allowed;pairs.append(dict(program=row['program'],input_digest=row['input_digest'],pair=[a,b],delta=delta,valid_exact_option_difference=ok))
   if not ok:violations.append([row['input_digest'],a,b])
assert not violations
core=F/'core';segments=[];commit='2e3bef4364e578cddd0e881c0baace2e51c55930'
for path,terms in [('src/gpgpu-sim/shader.cc',['DTC_SERVICE_V1_%s','void ldst_unit::dtc_l1_sample_service_occupancy','void ldst_unit::dtc_l1_service_retired','DTC_L1_oo_tag_evictions','ldst_unit::dtc_l1_oo_writeback_ready','m_dtc_service_retire','m_dtc_service_collect']),('src/gpgpu-sim/gpu-sim.cc',['gpu_stall_dramfull','gpu_stall_mem2icnt++','gpu_stall_icnt2mem++','m_perf_sim_memcpy','L2_total_cache_accesses']),('src/gpgpu-sim/dtc-l1-common.h',['bool collect(','m_tag_conflicts','m_tag_evictions','logical_tag_set'])]:
  z=subprocess.run(['git','-C',str(core),'show',commit+':'+path],capture_output=True);assert z.returncode==0;ls=z.stdout.decode().splitlines();ran=[]
  for n,line in enumerate(ls):
   if any(t in line for t in terms):
    lo=max(1,n-6);hi=min(len(ls),n+18)
    if ran and lo<=ran[-1][1]:ran[-1]=(ran[-1][0],max(ran[-1][1],hi))
    else:ran.append((lo,hi))
  segments.append(dict(commit=commit,path=path,file_sha256=hashlib.sha256(z.stdout).hexdigest(),ranges=[dict(start=lo,end=hi,text='\n'.join(f'{n+1}: {ls[n]}'for n in range(lo-1,hi)))for lo,hi in ran]))
remote=subprocess.run(['git','-C',str(core),'remote','get-url','origin'],capture_output=True,text=True)
out=dict(status='PASS_SAME_MODE_HASH_CONTROLS_AND_OBSERVATIONAL_FRAMEWORK_EQUIVALENCE',original_strict_cells=len(checks),source_groups=[dict(core=k[0],framework=k[1],binary=k[2],cells=n)for k,n in sources.items()],checks=checks,within_design_pairs=pairs,observational_framework_delta=diff,preexisting_cpu_qualification=dict(path=str(qu),sha256=hashlib.sha256(qu.read_bytes()).hexdigest(),content=cpu),cross_design_caveat='CM/CH has96KiB conventional data and768 line slots,PIB256/MSHR512/finite0. DM/DH has512 logical tag slots,640physical128B lines(80KiB),OO PIB128/MSHR conventional fallback32/finite1. Shared memory98304 configured; total SRAM ownership/area/timing equivalence is not established. No equal-area or pure-AE cross-design claim.',hash_family='For sets S=2^s, line=a>>7; bank=line&3; row=((line>>2)^(line>>s))&((S/4)-1); set=4*row+bank. CH S32 vs DH S64 use same family but configured index widths differ. One fixed mapping for all programs; no per-program choice.',core_remote=remote.stdout.strip(),source_excerpts=segments,new_model_starts=0)
(A/'evidence/MODEL_COMPARABILITY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],cells=len(checks),pairs=len(pairs),source_groups=out['source_groups'],diff=diff,core_remote=remote.stdout.strip())))
# Historical evidence stays separate, with original source/version and status labels.
base=D/'docs-worktree';paths=['docs/dtc_l1/review_packs/DTC_MAIN_NATIVE_ONBOARDING_20261023_V1/CURRENT_SCIENTIFIC_STATE.md','docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/tables/E_SENS_LOGICAL.tsv','docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/tables/E_SENS_PIB.tsv'];hist=[]
for rel in paths:
 p=base/rel;b=p.read_bytes();hist.append(dict(path=str(p),repository_path=rel,commit='b7a654356b75caeb45fbec392eb488151c600a9e',sha256=hashlib.sha256(b).hexdigest(),text=b.decode()))
(A/'evidence/HISTORICAL_BICG_CONTEXT.json').write_text(json.dumps(hist,indent=2)+'\n')
