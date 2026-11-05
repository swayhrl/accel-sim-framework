"""Readonly first actual births: native admission/activation only, not physics."""
import pathlib,json,hashlib,importlib.util,datetime,os,sys
P=pathlib.Path;D=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('No spawn/exec/signal')
sys.addaudithook(audit)
engine=load('firstbirth_actual_native_ro',R/'tools/l2_native.py');q=engine.registered()[2];rows=[]
for c,expected_uuid in [('E2-DTCL2MLP-ddb6806316876a85-CH-P0-V1','98d83595-84a4-43de-8e4b-472df204e8b5'),('E2-DTCL2MLP-09f94fcc7494a03b-DH-E384-IR1-V1','34bb91df-f5db-41a2-8727-a9e3eeff5ac7')]:
 ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);output=P(intent['output']);launch=read(output/'NATIVE_LAUNCH.json');pid=read(output/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 assert q['consumed'][c]['uuid']==intent['uuid']==expected_uuid and sha(ip)==q['consumed'][c]['intent_sha256']
 rb=intent['additional_cpu_shared_timeslice_binding'];ob=intent['additional_strace_bpf_observation_binding']
 for doc in [launch,pid]:assert doc['additional_cpu_shared_timeslice_binding']==rb and doc['additional_strace_bpf_observation_binding']==ob
 assert rb['schema']=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and rb['mode']=='CPU_SHARED_DYNAMIC_PER_COHORT'and ob['schema']=='DTC_STRACE_BROAD_SHARED_CPU_V1'and ob['mode']=='BPF_REQUIRED'
 rsp=output/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';osp=output/'STRACE_BPF_OBSERVATION_SNAPSHOT.json';assert sha(rsp)==rb['snapshot_sha256']and sha(osp)==ob['snapshot_sha256'];rs=read(rsp);osnap=read(osp);rcfg=rs['config'];ocfg=osnap['config']
 assert rcfg['qualification_only']is ocfg['qualification_only']is False
 for snap,b in [(rs,rb),(osnap,ob)]:
  cfg=snap['config'];assert cfg['qualified_sources']==b['qualified_sources']
  for role,path in cfg['source_paths'].items():assert sha(path)==cfg['qualified_sources'][role]==snap['source_snapshots'][role]['sha256']
 assert rcfg==json.loads(osnap['resource_configuration_utf8'])and osnap['memory_configuration_utf8']==osnap['resource_configuration_utf8']
 lib=load('firstbirth_captured_resource_'+c,rcfg['source_paths']['library']);assert lib.objsha(rcfg)==rb['config_sha256']
 assert all(p['config']==rcfg for p in rs['fresh_preflights']);preflights=[lib.verify_proof(p,require_native=True)for p in rs['fresh_preflights']]
 extra=load('firstbirth_captured_observation_'+c,ocfg['source_paths']['extra_strict']);assert extra.objsha(ocfg)==ob['config_sha256']
 prerequisite=extra.verify_release_prerequisite(ocfg,q,osnap['resource_configuration_utf8'],rs)
 assert prerequisite['production_release_eligible']is True
 fork=read(output/'STRACE_BPF_FORK_PLAN.json');act=read(output/'STRACE_BPF_ACTIVATION.json')
 assert sha(output/'STRACE_BPF_ACTIVATION.json')==pid['strace_observation_activation_sha256']and sha(output/'STRACE_BPF_FORK_PLAN.json')==launch['strace_fork_plan_sha256']==act['fork_plan_sha256']
 activation=extra.verify_activation(act,osnap,fork,launch,pid)
 assert activation['model_Seccomp']==2 and activation['model_filters']==1 and activation['fallback_accepted']is False
 assert launch['argv']==osnap['expected_argv_after']and launch['argv'].count('--seccomp-bpf')==1
 specpath=R/'control/specs'/(c+'.json');spec=read(specpath);dbp=R/'control/dispatch_bindings'/(c+'.json');db=read(dbp)
 assert spec['host_cpu']is None and q['admitted_specs'][c]==sha(specpath)==rb['canonical_spec_sha256']if 'canonical_spec_sha256'in rb else spec['host_cpu']is None and q['admitted_specs'][c]==sha(specpath)
 assert all(doc['dispatch_binding_sha256']==sha(dbp)for doc in [intent,launch,pid])and pid['host_cpu_affinity_actual']==[db['host_cpu']]==[rb['selected_cpu']]
 proc=P('/proc')/str(pid['pid']);fields=(proc/'stat').read_text().rsplit(')',1)[1].split();assert int(fields[19])==pid['start_ticks']and fields[0]not in ['Z','X','x']
 status={k:v.strip()for line in(proc/'status').read_text().splitlines()if ':'in line for k,v in[line.split(':',1)]}
 assert int(status['Seccomp'])==2 and int(status['Seccomp_filters'])==1 and int(status['TracerPid'])==activation['tracer_pid']
 assert os.readlink(proc/'ns/mnt')==pid['mnt_namespace']
 row=dict(cohort=c,uuid=expected_uuid,pid=pid['pid'],start_ticks=pid['start_ticks'],selected_cpu=db['host_cpu'],same_PID_generation_live=True,actual_proc_Seccomp=2,actual_proc_filters=1,actual_proc_tracer_pid=int(status['TracerPid']),resource_snapshot_sha256=sha(rsp),observation_snapshot_sha256=sha(osp),resource_sources=rcfg['qualified_sources'],observation_sources=ocfg['qualified_sources'],all_three_bindings_equal=True,native_resource_preflight_count=len(preflights),native_resource_preflights_verified=True,reserved_prospective_threads=[p['slot_evidence']['prospective_cpu_threads']for p in rs['fresh_preflights']],activation=activation,actual_Main_prerequisite=prerequisite,performance_completed=False)
 if spec.get('scientific_role')=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
  lineage=spec['incident_recovery_trial_lineage'];old=R/'analysis'/(lineage['original_cohort']+'.RESULT.json');assert sha(old)==lineage['original_negative_RESULT_sha256']and q['consumed'][lineage['original_cohort']]['uuid']==lineage['original_uuid'];row.update(role='INCIDENT_RECOVERY_PERFORMANCE_TRIAL',old_negative_sha256=sha(old),old_uuid=lineage['original_uuid'],old_negative_preserved=True,primary_statistics_excluded=True,validated_union_authorized=False)
 else:row.update(role='PRIMARY',primary_statistics_excluded=False,validated_union_authorized=False)
 rows.append(row)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=D/('BIRTH_BINDING_'+stamp);dest.mkdir()
report=dict(schema='E_ACTUAL_BROAD_FIRST_BIRTH_BINDING_VERIFICATION_V1',status='PASS_ACTUAL_BIRTH_BINDINGS_AND_NATIVE_ADMISSION_NOT_COMPLETION',observed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,models_started_by_observer=0,new_grants=0,production_changes=0,actual_performance_qualified=False,limitation='Native admission and BPF activation verified on real live generations. Natural full input physics/strict/archive/native completion is not yet established.')
put(dest/'REPORT.json',report);put(dest/'MANIFEST.json',dict(schema='E_ACTUAL_BIRTH_READONLY_MANIFEST_V1',source_sha256=sha(__file__),members=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(dest.iterdir())],production_changes=0))
print(json.dumps(dict(directory=str(dest),REPORT_sha256=sha(dest/'REPORT.json'),MANIFEST_sha256=sha(dest/'MANIFEST.json'),rows=[{k:r[k]for k in ['cohort','uuid','pid','start_ticks','selected_cpu','role','native_resource_preflight_count','reserved_prospective_threads','actual_proc_Seccomp','actual_proc_filters']}for r in rows])))
