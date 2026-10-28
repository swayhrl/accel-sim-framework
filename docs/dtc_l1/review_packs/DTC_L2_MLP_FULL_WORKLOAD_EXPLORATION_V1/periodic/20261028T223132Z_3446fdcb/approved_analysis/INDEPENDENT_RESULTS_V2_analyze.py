"""One newly closed primary result only; old322 frozen proofs reused."""
import pathlib,json,hashlib,gzip,re,math,time,copy,os,collections
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');E=A/'agents/E/results_refresh_20261028_v4';V1=A/'agents/A/results_independent_20261028_v1';D=A/'agents/A/results_independent_20261029_v2';R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D.mkdir(exist_ok=True)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(n,v):(D/n).write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
old=read(V1/'SUMMARY.json');e=read(E/'EVIDENCE.json');snapshot=read(E/'PRIMARY_SNAPSHOT.json');assert sha(V1/'MANIFEST.json')=='f164bd79909b5d9a08c4e6810bb42de0994078303317698d0d116e4f7a3b301d'
c='E2-DTCL2MLP-09f94fcc7494a03b-DH-F256-V1';resultpath=R/'analysis'/(c+'.RESULT.json');v=read(resultpath);p=v['proof'];uuid=v['uuid'];out=R/'DTC/run/results'/uuid;inputid=p['input_digest'];source=[]
def pin(path):path=P(path);source.append(dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size));return sha(path)
assert v['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and p['performance_accepted']is True and p['status']=='L2_MLP_NATIVE_TRACE_PERFORMANCE_QUALIFIED'
assert p['cohort']==c and p['uuid']==uuid=='a09f56bb-8bb2-41ed-aab3-75d1ca3239c1'and p['program']=='hybridsort'and p['cell']=='DH'and p['profile']=='F256'
intentpath=R/'control/qualification_ledger'/(c+'.INTENT.json');donepath=R/'control/qualification_ledger'/(c+'.DONE.json');intent=read(intentpath);done=read(donepath);exitdoc=read(out/'NATIVE_EXIT.json');launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');spec=read(out/'DOWNSTREAM_FROZEN_SPEC.json');db=read(out/'DISPATCH_BINDING.json')
assert done==exitdoc and done['uuid']==uuid and done['cohort']==c and done['launcher_wait_returncode']==0 and done['stop_reason']is None and intent['uuid']==uuid
assert p['dispatch_binding_sha256']==intent['dispatch_binding_sha256']==sha(out/'DISPATCH_BINDING.json')==db.get('sha256',sha(out/'DISPATCH_BINDING.json'))
assert intent['spec_sha256']==sha(out/'DOWNSTREAM_FROZEN_SPEC.json')==db['canonical_spec_sha256']and spec['host_cpu']is None
assert db['host_cpu']==pid['host_cpu_affinity_actual'][0]and len(pid['host_cpu_affinity_actual'])==1
assert spec['input_digest']==inputid and spec['profile']=='F256'and spec['expected_options']==p['effective_options']and len(p['effective_options'])==270
assert spec['expected']==dict(CTA=p['CTA'],instructions=p['instructions'],kernels=p['kernel_count'])and len(p['kernels'])==p['kernel_count']==68
for k in ['binary_sha256','core_commit','framework_commit']:assert p[k]==spec[k]
for cfg in spec['configs']:assert sha(cfg['path'])==cfg['sha256'];pin(cfg['path'])
assert sha(spec['input_binding_path'])==spec['input_binding_sha256'];pin(spec['input_binding_path'])
for key in ['additional_cpu_spare_memory_admission_binding','additional_shared_json_io_binding','l2_mlp_execution_binding']:
 assert intent[key]==launch[key]==pid[key]
assert '--seccomp-bpf'not in launch['argv'] # engineering4 have not been started
for k in ['additional_cpu_spare_memory_admission_strict','additional_shared_json_io_strict']:
 x=p[k];assert sha(x['sidecar_path'])==x['sidecar_sha256'];pin(x['sidecar_path'])
rawpath=out/'raw.log.gz';raw=gzip.open(rawpath,'rb').read();text=raw.decode('utf-8',errors='replace')
assert sha(rawpath)==done['raw_sha256']==p['raw_gzip_sha256']and hashlib.sha256(raw).hexdigest()==done['raw_uncompressed_sha256']==p['raw_uncompressed_sha256']
assert int(re.findall(r'gpu_tot_sim_cycle\s*=\s*(\d+)',text)[-1])==v['cycles']==16370955
assert int(re.findall(r'gpu_tot_sim_insn\s*=\s*(\d+)',text)[-1])==p['instructions']==6276086260
assert 'GPGPU-Sim: *** simulation thread exiting ***'in text and 'GPGPU-Sim: *** exit detected ***'in text
receipt=v['archive']['receipt'];archive=P(receipt['target_mount_path']);native=P(receipt['native_restore']);manifest=read(archive/'SOURCE_MANIFEST.json');index=read(archive/'ARCHIVE_INDEX.json');commit=read(archive/'COMMIT.json');restore=read(archive/'RESTORE_VERIFIED_NATIVE_TARGET.json')
assert receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and manifest['cohort']==c and manifest['source_root']==str(out)and manifest['txid']==receipt['txid']==commit['txid']==restore['txid']
assert sha(archive/'SOURCE_MANIFEST.json')==receipt['manifest_sha256']==commit['manifest_sha256']and sha(archive/'ARCHIVE_INDEX.json')==commit['archive_index_sha256']
assert manifest['native_execution_receipt_sha256']==sha(out/'NATIVE_EXIT.json')and receipt['archive_sha256']==index['archive_sha256']
assert len(manifest['entries'])==len(restore['rows'])==v['archive']['independently_verified_entries']==26
archivehasher=hashlib.sha256();chunkbytes=0
for part in index['chunks']:
 path=archive/'chunks'/part['name'];data=path.read_bytes();assert len(data)==part['size']and hashlib.sha256(data).hexdigest()==part['sha256'];archivehasher.update(data);chunkbytes+=len(data);pin(path)
assert archivehasher.hexdigest()==index['archive_sha256']and chunkbytes==index['archive_bytes']==receipt['archive_bytes']
restored_files=[]
for entry in manifest['entries']:
 src=out/entry['path'];dst=native/entry['path']
 if entry['type']=='file':assert sha(src)==sha(dst)==entry['sha256'];restored_files.append(dict(path=entry['path'],sha256=entry['sha256'],native_dev=dst.stat().st_dev))
 elif entry['type']=='symlink':assert os.readlink(src)==os.readlink(dst)==entry['target']
assert all(x['native_dev']==2128 for x in restored_files)
for path in [resultpath,intentpath,donepath,out/'NATIVE_EXIT.json',out/'DOWNSTREAM_FROZEN_SPEC.json',out/'DISPATCH_BINDING.json',out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',rawpath,archive/'SOURCE_MANIFEST.json',archive/'ARCHIVE_INDEX.json',archive/'RECEIPT.json',archive/'RESTORE_VERIFIED_NATIVE_TARGET.json',archive/'COMMIT.json',V1/'MANIFEST.json',E/'MANIFEST.json']:pin(path)
qpath=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';q=read(qpath)['registered_future_requests'][spec['request']];qrow=q['consumed'][c];assert qrow['uuid']==uuid and qrow['execution_receipt']==done;pin(qpath)
base=next(x for x in e['all_cells']if x['input_digest']==inputid and x['profile']=='P0'and x['cell']=='DH');assert base['accepted']and base['cycles']==18563916
assert all(base[k]==p[k]for k in ['binary_sha256','core_commit','framework_commit'])
speed=base['cycles']/v['cycles'];profiles=list(old['statistics']);values={f:{r['input_digest']:r['DH_self_speedup']for r in e['pairs']if r['profile']==f and r['paired']}for f in profiles};values['F256'][inputid]=speed
common=set.intersection(*(set(x)for x in values.values()));assert common==set(e['fixed_common_population'])and len(common)==31
def agg(vals):
 vv=list(vals.values());sv=sorted(vv);n=len(vv);return dict(n=n,GM=math.exp(sum(math.log(x)for x in vv)/n),median=sv[n//2]if n%2 else(sv[n//2-1]+sv[n//2])/2,positive=sum(x>1 for x in vv),neutral=sum(x==1 for x in vv),negative=sum(x<1 for x in vv),population=sorted(vals))
stats={}
for f in profiles:
 stats[f]={}
 for suite in old['statistics'][f]:
  available={i:x for i,x in values[f].items()if suite=='ALL'or snapshot['programs'][i]['suite']==suite};fixed={i:x for i,x in available.items()if i in common};stats[f][suite]=dict(available=agg(available),common31=agg(fixed))
  assert abs(stats[f][suite]['common31']['GM']-old['statistics'][f][suite]['common31']['GM'])<1e-12
remaining=[x for x in e['all_cells']if not x['accepted']and x['cohort']!=c];assert len(remaining)==27
othernew=[x['cohort']for x in remaining if(R/'analysis'/(x['cohort']+'.RESULT.json')).exists()];assert not othernew,'Another new result requires its own delta review'
pid_checks=[]
for row in remaining:
 live=row.get('live_identity')
 if not live:continue
 try:s=(P('/proc')/str(live['pid'])/'stat').read_text().rsplit(')',1)[1].split();ok=int(s[19])==live['start_ticks']and s[0]not in['Z','X']
 except(FileNotFoundError,ProcessLookupError):ok=False
 pid_checks.append(dict(cohort=row['cohort'],pid=live['pid'],start_ticks=live['start_ticks'],same_birth_live=ok))
delta=dict(schema='INDEPENDENT_PRIMARY_RESULTS_ONE_POINT_DELTA_V2',status='VERIFIED_NEW_PRIMARY_ACCEPTANCE',review_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),previous_anchor= dict(primary_accepted=322,manifest_path=str(V1/'MANIFEST.json'),manifest_sha256=sha(V1/'MANIFEST.json'),E4_manifest_sha256=sha(E/'MANIFEST.json')),population=dict(primary_accepted=323,new_accepted=317,references=6,planned=350,inputs=35,DH_variant_pairs=256,fixed_common31_unchanged=True,remaining_primary=27,live_same_birth=sum(x['same_birth_live']for x in pid_checks),pending=sum(x['state']=='PENDING'for x in remaining),preserved_original_negative=1,CH_nonP0_accepted=0),new_point=dict(cohort=c,uuid=uuid,input_digest=inputid,program='hybridsort',profile='F256',cell='DH',P0_cycles=base['cycles'],cycles=v['cycles'],DH_P0_over_variant=speed,cycle_reduction_fraction=1-v['cycles']/base['cycles'],RESULT_path=str(resultpath),RESULT_sha256=sha(resultpath),spec_sha256=sha(out/'DOWNSTREAM_FROZEN_SPEC.json'),resolved_spec_sha256=db['resolved_spec_sha256'],dispatch_binding_sha256=sha(out/'DISPATCH_BINDING.json'),config_sources=spec['configs'],binary_sha256=p['binary_sha256'],core_commit=p['core_commit'],framework_commit=p['framework_commit'],expected=spec['expected'],raw_gzip_sha256=sha(rawpath),raw_uncompressed_sha256=hashlib.sha256(raw).hexdigest(),raw_uncompressed_bytes=len(raw),natural_exit=True,CPU2_and_IO_binding_3_documents_equal=True,archive_receipt=receipt,independent_source_restore_files_checked=restored_files,archive_chunks_bytes_verified=chunkbytes,elapsed_wall_seconds=done['elapsed_seconds'],full_application_numerical_values='UNPROVEN'),statistics=stats,previous_F256=old['statistics']['F256'],fixed_common31_program_exclusions=['SYRK','hybridsort','lavamd','scan'],liveness_checks=pid_checks,remaining_groups=dict(collections.Counter(x['program']for x in remaining)),no_new_CH_matching=True,R2_primary_included=False,engineering_canaries_primary_included=False,engineering_four_registered_or_started=False,limitations=['Only new hybridsort F256 raw/source/archive bytes checked; old322 strict/QA/raw reused from immutable E4/V1.','F256 available GM changes both population32→33 and the added measured speedup; fixed_common31 remains exactly unchanged.','No nonP0 CH accepted, so no claim of improved relative DTC advantage.','Host walltime is descriptive only and this run uses existing default observation, not BPF.','No test rerun, summary(), AUTO_SUMMARY write, production controller/registry/source/Git/READY action.'])
put('DELTA.json',delta);put('SOURCE_SHA_LIST.json',dict(schema='ONE_NEW_RESULT_SOURCE_SHA_LIST_V2',sources=source,analysis_source_sha256=sha(__file__),old322_receipts='Immutable E4/V1 source index reused, not rescanned'))
f=stats['F256']['ALL'];rd=stats['F256']['Rodinia']
report=f'''独立增量结果 V2（只读，旧V1不变）\n\n截至{delta['review_utc']}，新增且仅新增hybridsort DH-F256自然验收：UUID {uuid}，16,370,955cycles，对应同输入DH P0为18,563,916cycles，自对照{speed:.6f}x（周期减少{100*(1-v['cycles']/base['cycles']):.3f}%）。primary由322增至323/350；11同代live、15pending、原scan/M16负例1保留。R2和工程canary均未并入。\n\nF256可用人口32→33/35，GM由{old['statistics']['F256']['ALL']['available']['GM']:.6f}变为{f['available']['GM']:.6f}，符号数为{f['available']['positive']}正/{f['available']['neutral']}平/{f['available']['negative']}负，中位数仍1。Rodinia可用人口8→9/10，GM {rd['available']['GM']:.6f}。这加入了一个新测量输入，不能说旧32输入本身变快。\n\n八配置共同人口仍31（hybridsort其余7组变体尚缺，另外SYRK/lavamd及scan原M16也未齐）。因此F256共同31 GM仍{f['common31']['GM']:.6f}，F128仍{stats['F128']['ALL']['common31']['GM']:.6f}，所有共同人口结果不变。非P0 CH accepted仍0，不能据本DH自对照推断相对传统CH的DTC优势。\n\n本次仅检查新结果：严格RESULT与UUID/输入/270有效选项/4配置SHA，CPU2+IO三receipt绑定，DONE=NATIVE_EXIT=q执行回执，新增raw压缩/解压SHA及最终周期/指令/自然终结；164新archive的25,026,560bytes分块SHA、26项清单/恢复身份及21个regular source/native_restore字节SHA闭合（native dev2128）。FW02775/Core9eed/binary02a与旧P0相同。模拟应用数值正确性仍UNPROVEN；没有重跑QA/模拟或重新扫描旧322raw。\n'''
(D/'REPORT.txt').write_text(report)
entries=[]
for name in ['REPORT.txt','DELTA.json','SOURCE_SHA_LIST.json','analyze.py']:
 path=D/name;entries.append(dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path)))
put('MANIFEST.json',dict(schema='INDEPENDENT_RESULTS_DELTA_V2_MANIFEST',status='FROZEN',files=entries,production_changes=0,model_starts=0))
print(json.dumps(dict(path=str(D),manifest_sha256=sha(D/'MANIFEST.json'),delta_sha256=sha(D/'DELTA.json'),report_sha256=sha(D/'REPORT.txt'),speedup=speed,F256availableGM=f['available']['GM'],F256common31GM=f['common31']['GM'],new_result_sha256=sha(resultpath),newaccepted=323),ensure_ascii=False))
