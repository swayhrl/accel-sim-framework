"""Private synthetic CPU fixture; never a production approval or simulator run."""
import copy,hashlib,importlib.util,json,pathlib,shutil
P=pathlib.Path;HERE=P(__file__).resolve().parent
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def loadmod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(js(v))
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def capture(pid,start,ppid,tracer=0,seccomp=0,filters=0):
 fields=['S',str(ppid)]+['0']*17+[str(start)]
 stat=f'{pid} (CPU-only-fixture) '+ ' '.join(fields)+'\n'
 return dict(pid=pid,start_ticks=start,stat_before_utf8=stat,stat_after_utf8=stat,status_utf8=f'Pid:\t{pid}\nPPid:\t{ppid}\nTracerPid:\t{tracer}\nSeccomp:\t{seccomp}\nSeccomp_filters:\t{filters}\n',mnt_namespace='mnt:[CPU_ONLY]',observed_UTC='CPU_QUALIFICATION_ONLY')
def fixture(root,mode='BPF_REQUIRED'):
 root=P(root);root.mkdir(parents=True,exist_ok=False)
 e=loadmod('fixture_real_extra',HERE/'bpf_extra_strict.py')
 b=loadmod('fixture_real_producer',A/'agents/B/strace_bpf_future_entry_v2/strace_entry.py')
 plan=json.loads((A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json').read_bytes())
 row=next(x for x in plan['rows']if x['program']=='heartwall'and x['mode']==mode)
 spec=json.loads(P(row['draft_spec_path']).read_bytes());c=spec['cohort'];uuid='CPU_ONLY_'+mode
 bindingfile=R/'control/input_bindings'/(spec['input_digest']+'.json');dest=root/'control/input_bindings'/bindingfile.name;dest.parent.mkdir(parents=True);dest.write_bytes(bindingfile.read_bytes())
 put(root/'control/specs'/(c+'.json'),spec)
 resolved=dict(spec,host_cpu=1);db=dict(cohort=c,host_cpu=1,canonical_spec_sha256=sha(root/'control/specs'/(c+'.json')),resolved_spec_sha256=e.objsha(resolved))
 put(root/'control/dispatch_bindings'/(c+'.json'),db)
 for name in ['SCOPE.json','MATRIX_CURRENT.json']:put(root/'control'/name,{'points':[],'fixture_only':True})
 out=root/'DTC/run/results'/uuid;out.mkdir(parents=True)
 roles={'entry':b.__file__,'frontend':b.__file__,'producer':b.__file__,'extra_strict':e.__file__,'consumer':str(HERE/'consumer_bridge.py')}
 sources={k:sha(v)for k,v in roles.items()}
 oldpins={str(R/'tools/l2_results.py'):sha(R/'tools/l2_results.py'),str(R/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py'):sha(R/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py')}
 qa=dict(status='PASS',native_prefix_qualified=True,extra_strict_qualified=True,consumer_archive_qualified=True,
  qualified_sources=sources,expected_pins=oldpins,qualification_only=True,proof_kind='CPU_SCHEMA_STANDIN_NOT_RELEASE_QUALIFICATION')
 put(root/'CPU_SCHEMA_QA.json',qa);back=dict(verified=True,QA_sha256=sha(root/'CPU_SCHEMA_QA.json'),qualified_sources=sources,expected_pins=oldpins,qualification_only=True)
 put(root/'CPU_SCHEMA_READBACK.json',back)
 cfg=dict(schema=e.ID,request=e.REQ,overlay_id=e.ID,status='ACTIVE_FUTURE_ONLY',root=str(root),qualification_only=True,modes={c:mode},future_primary_policy='NONE',
  source_paths=roles,qualified_sources=sources,expected_pins=oldpins,QA_path=str(root/'CPU_SCHEMA_QA.json'),QA_sha256=sha(root/'CPU_SCHEMA_QA.json'),
  readback_path=str(root/'CPU_SCHEMA_READBACK.json'),readback_sha256=sha(root/'CPU_SCHEMA_READBACK.json'),native_source_path=str(R/'tools/l2_native.py'),
  memory_frontend_path=str(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),memory_frontend_sha256=sha(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),default_native_entry='/root/data/ep_l2_dtc_l1_native_v2/bin/native')
 rec=dict(status='ACTIVE',**b.record(cfg));base=capture(4000,40,1);before=b.expected_argv(root,out,resolved);after=b.mode_argv(before,mode);science=b.scientific_identity(resolved)
 snap=dict(schema=e.ID,request=e.REQ,cohort=c,uuid=uuid,mode=mode,config=cfg,overlay_record=rec,
  source_snapshots={k:dict(path=v,sha256=sources[k],utf8=P(v).read_text())for k,v in roles.items()},QA_utf8=(root/'CPU_SCHEMA_QA.json').read_text(),readback_utf8=(root/'CPU_SCHEMA_READBACK.json').read_text(),
  canonical_spec_utf8=(root/'control/specs'/(c+'.json')).read_text(),canonical_spec_sha256=sha(root/'control/specs'/(c+'.json')),resolved_spec=resolved,resolved_spec_sha256=e.objsha(resolved),
  dispatch_binding_utf8=(root/'control/dispatch_bindings'/(c+'.json')).read_text(),dispatch_binding_sha256=sha(root/'control/dispatch_bindings'/(c+'.json')),
  scientific_identity=science,baseline_preINTENT=base,expected_argv_before=before,expected_argv_after=after,parent_lease={'CPU_ONLY':True})
 put(out/e.SNAP,snap)
 binding=dict(schema=e.ID,request=e.REQ,overlay_id=e.ID,cohort=c,uuid=uuid,mode=mode,snapshot_sha256=sha(out/e.SNAP),config_sha256=e.objsha(cfg),qualified_sources=sources,QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],
  canonical_spec_sha256=snap['canonical_spec_sha256'],resolved_spec_sha256=snap['resolved_spec_sha256'],dispatch_binding_sha256=snap['dispatch_binding_sha256'],expected_argv_before_sha256=e.objsha(before),expected_argv_after_sha256=e.objsha(after),scientific_identity=science)
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=dict(cohort=c,uuid=uuid,output=str(out),dispatch_binding_sha256=binding['dispatch_binding_sha256'],**{e.FIELD:binding})
 put(ip,intent)
 fork=dict(schema=e.ID,cohort=c,uuid=uuid,mode=mode,snapshot_sha256=binding['snapshot_sha256'],intent_sha256=sha(ip),baseline_prePopen=base,argv_before=before,argv_after=after,argv_list_mutated_in_place=True,scientific_identity=science)
 put(out/e.FORK,fork)
 model=capture(4002,42,4001,4001,2 if mode=='BPF_REQUIRED'else 0,1 if mode=='BPF_REQUIRED'else 0);tracer=capture(4001,41,4000)
 act=dict(schema=e.ID,cohort=c,uuid=uuid,mode=mode,snapshot_sha256=binding['snapshot_sha256'],fork_plan_sha256=sha(out/e.FORK),model=model,tracer=tracer,baseline_preINTENT=base,baseline_prePopen=base,verdict=b.activation_verdict(mode,model,tracer,base,base,4001,4002,42))
 put(out/e.ACT,act)
 launch=dict(cohort=c,uuid=uuid,launcher_pid=4001,argv=after,dispatch_binding_sha256=binding['dispatch_binding_sha256'],strace_fork_plan_sha256=sha(out/e.FORK),**{e.FIELD:binding})
 pid=dict(pid=4002,start_ticks=42,mnt_namespace='mnt:[CPU_ONLY]',dispatch_binding_sha256=binding['dispatch_binding_sha256'],strace_observation_activation_sha256=sha(out/e.ACT),**{e.FIELD:binding})
 put(out/'NATIVE_LAUNCH.json',launch);put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',pid)
 done=dict(uuid=uuid,cohort=c,stop_reason=None,launcher_wait_returncode=0)
 put(root/'control/qualification_ledger'/(c+'.DONE.json'),done);put(out/'NATIVE_EXIT.json',done)
 q=dict(qualification_only=True,admitted_specs={c:sha(root/'control/specs'/(c+'.json'))},consumed={c:dict(uuid=uuid,intent_sha256=sha(ip),execution_receipt=done)},additional_operational_overlays={e.ID:rec})
 rule=dict(row,primary_statistics_excluded=True,validated_union_authorized=False)
 contract=dict(root=str(root),qualification_only=True,cohorts={c:rule},science_keys=plan['science_keys'],primary_statistics_excluded=True,validated_union_authorized=False)
 reference=json.loads(P(spec['engineering_observation_canary_lineage']['reference_result_path']).read_bytes());dest=root/'analysis'/(row['reference_cohort']+'.RESULT.json');dest.parent.mkdir();dest.write_bytes(P(spec['engineering_observation_canary_lineage']['reference_result_path']).read_bytes())
 proof=copy.deepcopy(reference['proof']);proof.update(cohort=c,uuid=uuid)
 for name,key,status in [('CPU_SPARE_MEMORY_EXTRA_STRICT.json','additional_cpu_spare_memory_admission_strict','PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'),('SHARED_JSON_IO_EXTRA_STRICT.json','additional_shared_json_io_strict','PASS_SHARED_JSON_IO_AND_ORIGINAL_PERFORMANCE')]:
  put(out/name,dict(status=status,CPU_ONLY_STANDIN=True));proof[key]=dict(status=status,sidecar_path=str(out/name),sidecar_sha256=sha(out/name))
 return dict(root=root,c=c,q=q,contract=contract,cfg=cfg,out=out,proof=proof,extra=e,producer=b,reference=reference,CPU_ONLY=True)
def archive(f):
 out=f['out'];root=f['root'];bundle=root/'archive';restore=root/'DTC/run/recovery/CPU_FIXTURE';bundle.mkdir(exist_ok=True);restore.mkdir(parents=True,exist_ok=True)
 entries=[]
 for p in sorted(out.iterdir()):
  if p.is_file():entries.append(dict(path=p.name,type='file',size=p.stat().st_size,sha256=sha(p)));shutil.copyfile(p,restore/p.name)
 manifest=dict(cohort=f['c'],source_root=str(out),entries=entries)
 put(bundle/'SOURCE_MANIFEST.json',manifest);canonical=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 return dict(receipt=dict(cohort=f['c'],status='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET',source_disposition='SOURCE_KEEP',target_mount_path=str(bundle),native_restore=str(restore),manifest_sha256=hashlib.sha256(canonical).hexdigest(),archive_sha256='CPU_FIXTURE_NOT_A_REAL_ARCHIVE'),independently_verified_entries=len(entries))
