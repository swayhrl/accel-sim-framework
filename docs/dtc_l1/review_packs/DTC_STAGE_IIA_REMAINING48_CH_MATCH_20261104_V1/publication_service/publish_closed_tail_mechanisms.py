"""Root publication of qualified closed-tail analysis; no model/native actions."""
from pathlib import Path
import importlib.util,json,fcntl,hashlib,argparse,re,subprocess,gzip
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
ap=argparse.ArgumentParser();ap.add_argument('--package-list',required=True);args=ap.parse_args();config_path=Path(args.package_list)
assert config_path.resolve().is_relative_to(A.resolve())
config=json.loads(config_path.read_bytes());packs=config['packages'];assert len(packs)==5
assert {p['name']for p in packs}=={'B_completed_3mm_v1','C_completed_3mm_review_v1','B_completed_myocyte_v1','C_completed_myocyte_review_v1','B_myocyte_cpu_capacity_observation_v1'}
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('existing_root_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for pin in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(pin['path'],pin['sha256'])
 frozen={};index=[]
 for row in packs:
  rel=m.rel(row['manifest']);assert rel.parts[0]=='agents'and rel.name=='MANIFEST.json';assert re.fullmatch('[0-9a-f]{64}',row['sha256'])
  p=A/rel;dest=m.O/'independent_reviews'/row['name'];m.manifest_copy(p,dest,row['sha256'])
  for item in m.rd(p)['files']:
   assert item['bytes']<8*1024**2
   frozen[str((dest/m.rel(item['path'])).relative_to(m.W))]=item['sha256']
  index.append(dict(source_manifest=str(rel),sha256=row['sha256'],public_directory=str(dest.relative_to(m.O))))
 note='''## Naturally closed myocyte and3MM: independent mechanism supplements

Read [myocyte](independent_reviews/B_completed_myocyte_v1/REPORT.md) and [3MM](independent_reviews/B_completed_3mm_v1/REPORT.md), with their companion [myocyte review](independent_reviews/C_completed_myocyte_review_v1/README.md) and [3MM review](independent_reviews/C_completed_3mm_review_v1/README.md). These are six-source matched, dated supplements; the current execution table retains its own timestamp. Neither supplement is the final CORE32 aggregate or the final48 lifecycle audit.

Both programs preserve exact own-design zero F responses. Current-contract CH/DH differences are architecture comparisons with the same Hash family, not newly isolated Hash gains. Selected additive counters use explicit cumulative endpoints; absent counters remain unavailable. Means, gauges and running maxima are not differenced. The3MM zero DRAM exposure is specific to the registered prefilled replay and does not prove compute-bound execution. Blocked ICNT admission events are not DRAM wait cycles or a critical-path fraction. CH common and DH OO counters do not describe equal structures.

myocyte issues one32B DRAM-read atom inK1. Its5993 registered kernel instances match the fixed single-RHS mapping;5993=13x461 is arithmetic compatibility with a candidate13-RHS solver, not a measured count of solver attempts or ODE steps. Accepted-step/retry IDs, native full-application completeness and live phase_epoch-to-kernel-ordinal bindings remain unproved. The repeated state/parameter HtoD uploads require an explicit cache-coherence and numeric-correctness boundary: measured simulator cache counters do not certify valid numerical reuse after CPU writes. The3MM candidate source S copies uninitialized E/F/G and uses +=, while its binding to historical capture source/ELF/macros and native numerical correctness remains unproved. Preserve that limitation without asserting historical captured numeric error, repairing or replacing the frozen input, or removing its accepted performance row. No new simulation, trace, controller, source-pin, final-waiter, budget or v0.23 manuscript action is performed here.

The independent myocyte review pins the specific kernel-idle invalidation and memcpy entrypoints, including the effective source-event OO-invalidation option0. These callsite facts define a pending coherence question; they do not exhaust all possible OO reset paths or prove stale-data behavior. Downstream F matching alone is not numerical-coherence certification.

The companion CPU-capacity observation records the successful V1 myocyte six-source parser subset under its6GiB AS limit. Its sampled RSS is not a peak; exact final wall/CPU time and start generation were not collected. This limited engineering observation does not qualify the final24 consumer's complete end-to-end capacity, and the original gated final chain remains unchanged.

'''
 readme=(D/'REVIEW_PACK_README.md').read_text();assert '## Naturally closed myocyte and3MM:'not in readme
 first,rest=readme.split('\n',1);updated=first+'\n\n'+note+rest.lstrip('\n');m.write(D/'REVIEW_PACK_README.md',updated.encode());m.write(m.O/'README.md',updated.encode())
 m.put(m.O/'publication_service/CLOSED_TAIL_MECHANISM_PUBLICATION.json',dict(UTC=m.utc(),packs=index,source_sha256=m.sha(__file__),package_list_sha256=m.sha(config_path),new_models=0,native_scientific_writes=0,final_scientific_closure=False))
 m.write(m.O/'publication_service/publish_closed_tail_mechanisms.py',Path(__file__).read_bytes())
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace')
 affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 for path in affected:assert path in frozen and m.sha(m.W/path)==frozen[path]
 m.put(m.O/'publication_service/CLOSED_TAIL_VERBATIM_SOURCE_CHECK.json',dict(UTC=m.utc(),exemptions=[dict(path=x,sha256=frozen[x],reason='Verbatim immutable reviewed member')for x in affected],scientific_bytes_changed=0))
 b=m.checked_provider(m.rd(m.BP));terminal=b['all_registered48_terminal_verified']
 for item in b['files']:m.write(m.O/'analysis'/m.rel(item['name']),m.verified(item['path'],item['sha256']))
 m.put(m.O/'analysis/PROVIDER.json',b);m.write(m.O/'analysis/SNAPSHOT_MANIFEST.json',Path(b['manifest']['path']).read_bytes())
 observed_row=next(x for x in b['files']if x['name']=='STAGEIIA_REMAINING48_OBSERVATIONS.json.gz');observed=json.loads(gzip.decompress(m.verified(observed_row['path'],observed_row['sha256'])))
 for row in observed['observations']:
  if row.get('RESULT_sha256'):
   name=m.rel(row['cohort']+'.RESULT.json');assert len(name.parts)==1;m.write(m.O/'accepted_or_negative_receipts'/name,m.verified(m.R/'analysis'/name,row['RESULT_sha256']))
 batch=m.rd(m.R/'analysis/BATCH_STATE.json');m.put(m.O/'snapshots/BATCH_STATE.json',batch)
 req=m.rd(m.REG)['registered_future_requests'][m.REQ];assert req['budget']==48 and len(req['admitted_specs'])==48;m.put(m.O/'snapshots/NEW_REQUEST.json',req)
 figure=m.export_figures();status=dict(UTC=m.utc(),status='ALL48_TERMINAL_FINAL_INDEPENDENT_REVIEW_PENDING'if terminal else'EXACT48_BACKGROUND_EXECUTION',summary=b['summary'],batch_asof=batch['UTC'],batch_running=batch.get('running'),canary_gate=batch.get('canary_runtime_gate_passed'),preclaim_resource_holds=batch.get('preclaim_resource_holds',[]),figure_snapshot=figure['snapshot'],figure_n=figure['common_both_F_n'],figure_accepted_new48=figure['accepted_new48'],models_launched_by_publication_service=0,final_scientific_closure=False,additional_experiments_released=False);m.put(m.O/'LATEST_STATUS.json',status)
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json');m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=terminal,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths)
 changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed)
 m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): add independently reviewed myocyte and3MM closed-tail mechanisms','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=terminal,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=status['summary'],new_mechanism_packages=index)
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_CLOSED_TAIL_MECHANISM_COMMIT_RECEIPT.json',receipt)
 continuation=m.rd(A/'GOAL_CONTINUATION.json');continuation['additional_readonly_mechanism_work']=dict(stage='FROZEN_B_C_PACKAGES_COMMITTED_PENDING_REMOTE_READBACK',programs=['myocyte','3MM'],packages=index,final24_consumer_still_original_waiter_once=True);m.put(A/'GOAL_CONTINUATION.json',continuation);print(json.dumps(receipt))
