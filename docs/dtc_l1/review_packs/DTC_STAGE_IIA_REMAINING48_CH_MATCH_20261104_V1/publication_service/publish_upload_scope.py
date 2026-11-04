"""Publish fixed32 event/configuration evidence, preserving all model identities."""
from pathlib import Path
import importlib.util,json,hashlib,fcntl,re,subprocess
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('existing_root_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
packs=[('agents/A_host_upload_scope_inventory_v1/MANIFEST.json','4a4b7d4a8497dda510efae7916cc7f69a38bf711d55cdaa143d135e315c1474d','A_host_upload_scope_inventory_v1'),('agents/C_host_upload_scope_review_v1/MANIFEST.json','f30453d22b1ad09913b87308b5eb7eef190c51682a6a870a574b071aa5291140','C_host_upload_scope_review_v1')]
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for pin in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(pin['path'],pin['sha256'])
 frozen={};index=[]
 for path,want,name in packs:
  p=A/path;dest=m.O/'independent_reviews'/name;m.manifest_copy(p,dest,want)
  for row in m.rd(p)['files']:
   assert row['bytes']<8*1024**2;frozen[str((dest/m.rel(row['path'])).relative_to(m.W))]=row['sha256']
  index.append(dict(source_manifest=path,sha256=want,public_directory=str(dest.relative_to(m.O))))
 note='''## Full fixed CORE32 upload/configuration scope

Read the [32-input host-upload inventory](independent_reviews/A_host_upload_scope_inventory_v1/REPORT.md) and its [356-check independent review](independent_reviews/C_host_upload_scope_review_v1/README.md). This is32-input event/configuration coverage, separate from the timestamped performance table and its accepted six-cell intersection. No missing performance cell is filled by this inventory.

All32 frozen commandlists and64 legal P0 option records are SHA/identity-bound, including the six inherited P0 wrapper/underlying joins. Five inputs declare HtoD between kernel commands:

| Program | Interkernel copies | Declared bytes |
|---|---:|---:|
|bfs|15|60|
|histo|19|152|
|mri-q|6|442368|
|myocyte|11984|2612512|
|particlefilter_naive|48|384000|

bfs also declares one4B post-last upload. All32 have pre-first uploads;27 have only that declared HtoD position category. Command format/binding UNKNOWN count is0. Positions are trace command order, not measured hook timestamps; declared addresses/bytes do not establish value changes or OO-read overlap. These groups are not safety labels or workload-selection rules. Absence of interkernel HtoD does not certify GPU-store,other-host-path or numerical coherence.

Every one of64 P0 records explicitly has prefill=1,flushL1=1,flushL2=0,source-event OO invalidation=0. Fixed-source defaults1/0/0/0 are recorded separately; actual values are not imputed from defaults, and matching values do not establish inheritance. Selected fixed Core/Framework entrypoints are pinned with their limited scope; OO global reset behavior,numerical freshness and source/capture ELF binding remain distinct questions. All accepted outcomes and32 identities remain unchanged.

The64 P0 records also explicitly report64 clusters x1 core and shader_core_pipeline2048:32. Report the executed profile as a fixed SM70/V100-derived64SM simulation with the frozen10MiB L2 and850MHz DRAM. The trace/profile label is not a stock/native V100 hardware measurement. This publication changes no geometry,clock,cache policy,input or scientific identity.

The remaining GES outcomes,final48 lifecycle/archive/recovery audit,full32 performance interpretation,final resource consumption,visual approval and final immutable closure remain separate requirements. The current performance snapshot retains its own timestamp. This packet starts no simulator,capture,GPU work,service or new experimental phase and leaves EnglishLaTeXv0.23 frozen.

'''
 readme=(D/'REVIEW_PACK_README.md').read_text();assert '## Full fixed CORE32 upload/configuration scope'not in readme
 first,rest=readme.split('\n',1);updated=first+'\n\n'+note+rest.lstrip('\n');m.write(D/'REVIEW_PACK_README.md',updated.encode());m.write(m.O/'README.md',updated.encode())
 m.put(m.O/'publication_service/HOST_UPLOAD_SCOPE_PUBLICATION.json',dict(UTC=m.utc(),packs=index,source_sha256=m.sha(__file__),new_models=0,native_writes=0,final_scientific_closure=False));m.write(m.O/'publication_service/publish_upload_scope.py',Path(__file__).read_bytes())
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace');affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 for path in affected:assert path in frozen and m.sha(m.W/path)==frozen[path]
 m.put(m.O/'publication_service/HOST_UPLOAD_VERBATIM_SOURCE_CHECK.json',dict(UTC=m.utc(),exemptions=[dict(path=x,sha256=frozen[x],reason='Verbatim immutable reviewed member')for x in affected],source_bytes_changed=0))
 status=m.rd(m.O/'LATEST_STATUS.json');terminal=status['summary']['all_registered48_terminal_verified']
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json');m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=terminal,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths);changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed);m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): bind full32 upload scope and actual fixed simulation geometry','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=terminal,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=status['summary'],upload_scope_inputs=32,reviewed_packages=index);m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_HOST_UPLOAD_SCOPE_COMMIT_RECEIPT.json',receipt)
 continuation=m.rd(A/'GOAL_CONTINUATION.json');continuation.setdefault('host_upload_scope_inventory',{}).update(stage='COMMITTED_PENDING_REMOTE_READBACK',packages=index,geometry=dict(n_clusters=64,cores_per_cluster=1,pipeline='2048:32'),coherence_not_certified=True,performance_population_not_filtered=True,commit=receipt['commit']);m.put(A/'GOAL_CONTINUATION.json',continuation);print(json.dumps(receipt))
