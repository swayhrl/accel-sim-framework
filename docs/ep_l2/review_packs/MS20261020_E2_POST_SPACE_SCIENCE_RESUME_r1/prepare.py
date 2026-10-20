"""Independent E resource/source admission after externally verified space release."""
from pathlib import Path
import sys,json,time,os,subprocess,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];ROLL=P.parent/'MS20261020_E2_MAIN_ROLLING_r1'
sys.path.insert(0,str(ROLL));import rolling_main as m
c=m.c;coord=c.Coordinator();s=coord.snapshot();data=m.read(c.SHARED/'RUN_REGISTRY.json')
assert os.uname().nodename=='huangrulin-174'
assert s['controller']['state']=='STOPPED' and s['actual_starts']==14 and s['t0_unix']==1792414193
assert s['uncertain_start_intents']==0
assert not any(r['status'] in c.ACTIVE for k in ['runs','resource_leases'] for r in data[k].values())
usage=c.output_usage();assert usage==dict(old_bytes=14309576384,new_bytes=3017637219,total_bytes=17327213603),'retained result accounting changed; reconcile historical generation before launch'
buckets={k:sum(c.policy_v2.charged_bucket(a,s['reservations'])==k and a.get('actual_start',False) for a in s['attempts']) for k in s['reservations']};assert buckets['contingency']==8
identity=m.read('/tmp/e2-resume-git-identity.json');inputs=m.read('/tmp/e2-cfd-full-independent-admission-inputs.json')
assert len(identity['readback'])==5 and all(x['shared_match'] for x in identity['readback'])
bridge=Path('/root/share/host174_storage_recovery_bridge/20261016_storageops_02')
for name in ['LANE_T_V3_BOTH_SOURCE_RELEASES_CONFIRMED_20261020.json','LANE_BA_V3_46BF3A69_SOURCE_RELEASE_RECEIPT_20261020.json','LANE_BA_TO_E2_SECOND_V3_SPACE_RECHECK_NOTICE_20261020.json','LANE_T_TO_E2_BOTH_V3_ACTUAL_SPACE_RETEST_20261020.json','V3_BOTH_BATCHES_RECOVERY_INDEX_20261020.json']:
 (P/name).write_bytes((bridge/name).read_bytes())
external=m.read(P/'LANE_T_V3_BOTH_SOURCE_RELEASES_CONFIRMED_20261020.json')
assert external['sum_of_two_measured_source_release_windows_bytes']==8968978432
assert all(not Path(a['source_root']).exists() for a in external['assets'])
assert all(a['full_archive_content_and_metadata_verified'] for a in external['assets'])
# V3 cold metadata says full archive member verification plus three native sample
# restores per batch; it does not claim whole-tree extraction. E does not upgrade it.
plan=m.read(ROLL/'PLAN.json');row=next(r for r in plan['conditions'] if r['workload']=='cfd_097k')
assert s['final_source_identity']==plan['source_identity']
admission=m.choose_slots(coord,row)
processes=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
  if any(x in args for x in ['accel-sim.out','rolling_main.py','mechanism_e/controller.py','durable_exit.py']) and 'python3 -' not in args:
   processes.append(dict(pid=int(proc.name),args=args[:500]))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
assert not processes,'existing native/controller process requires ownership review'
filesystem={}
for label,args in [('workspace_share_bytes',['df','-B1','/workspace','/root/share']),('workspace_share_inodes',['df','-i','/workspace','/root/share']),('workspace_mount',['findmnt','-T','/workspace','-o','TARGET,SOURCE,FSTYPE,MAJ:MIN','--json']),('share_mount',['findmnt','-T','/root/share','-o','TARGET,SOURCE,FSTYPE,MAJ:MIN','--json'])]:
 filesystem[label]=subprocess.check_output(args,text=True)
report=dict(schema='E2_POST_EXTERNAL_SPACE_INDEPENDENT_ADMISSION_V1',at_unix=time.time(),status='PASS',source_host=os.uname().nodename,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),mount_namespace=os.readlink('/proc/self/ns/mnt'),external_release=identity,external_measured_net_reclaim_bytes=8968978432,external_restore_scope='T full archive content/metadata member verification and3 native sample restores per batch; whole-tree extraction=false. External V3 release fact does not alter any E scientific identity.',independent_admission=admission,filesystem=filesystem,cpu=dict(count=os.cpu_count(),affinity_count=len(os.sched_getaffinity(0)),loadavg=os.getloadavg()),active_processes=processes,controller=s['controller'],active_runs={},active_leases={},original_T0=s['t0_unix'],actual_starts=14,remaining=26,maximum=40,budget_buckets=buckets,contingency_remaining=0,result_usage=usage,result_growth_since_pre_storage_checkpoint_bytes=0,new_result_ceiling_bytes=6*c.GIB,total_result_ceiling_bytes=20*c.GIB,cumulative_generated_results_not_reset=True,source_identity=s['final_source_identity'],input_audits=inputs,retained_NATIVE17_not_repeated=True,next=['cfd_097k S/F','dwt2d S/F','sad S/F'],max_simulators=2,selected_slots=admission['slots'],no_FWT_or_Vector_retry=True,source_production_modified=False,other_project_resource_policy_changed=False)
c.write_json(P/'INDEPENDENT_RESOURCE_ADMISSION.json',report)
c.write_json(P/'GITHUB_STORAGE_IDENTITY_READBACK.json',identity)
print(json.dumps(dict(status=report['status'],slots=report['selected_slots'],resources=admission['resources'],actual_starts=14,remaining=26,result_usage=usage)),flush=True)
