"""Root-only publication of independently reviewed measured-resource evidence."""
from pathlib import Path
import importlib.util,json,fcntl,hashlib,argparse,re,subprocess
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
ap=argparse.ArgumentParser();ap.add_argument('--a-manifest-sha256',required=True);ap.add_argument('--c-manifest',required=True);ap.add_argument('--c-manifest-sha256',required=True);args=ap.parse_args()
for digest in [args.a_manifest_sha256,args.c_manifest_sha256]:assert re.fullmatch('[0-9a-f]{64}',digest)
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('existing_root_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
packs=[('agents/A_actual_resource_summary_v1/MANIFEST.json',args.a_manifest_sha256,'A_actual_resource_summary_v1'),(str(m.rel(args.c_manifest)),args.c_manifest_sha256,'C_actual_resource_summary_review_v1')]
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for x in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(x['path'],x['sha256'])
 frozen={};index=[]
 for path,want,name in packs:
  p=A/path;dest=m.O/'independent_reviews'/name;m.manifest_copy(p,dest,want)
  for x in m.rd(p)['files']:frozen[str((dest/m.rel(x['path'])).relative_to(m.W))]=x['sha256']
  index.append(dict(source_manifest=path,sha256=want,public_directory=str(dest.relative_to(m.O))))
 summary=m.rd(m.O/'independent_reviews/A_actual_resource_summary_v1/updates/current40_v1/SUMMARY.json')
 assert summary['closed_resource_complete']==40 and summary['pending_or_unverified']==8 and summary['closed_resource_evidence_HOLD']==0
 note='''## Measured host resources: closed40 snapshot

Read the [per-point resource report](independent_reviews/A_actual_resource_summary_v1/updates/current40_v1/REPORT.md), its manifest-pinned data and the [independent review](independent_reviews/C_actual_resource_summary_review_v1/README.md). This dated evidence covers40 closed identities, with all8 pending resource rows retained as null. It is distinct from resource admission estimates and simulated hardware capacity.

All40 receipt RSS maxima match their closed sample streams. These are approximately10-second observations of launcher plus observed simulator VmRSS, with possible shared-page double counting; they are not full-descendant or absolute physical peaks. Per-point CPU time/utilization is unknown. Elapsed receipt time includes wrapper activity; summing it would produce job-seconds, not round walltime. Per-point RSS maxima do not establish simultaneous memory usage.

The40 closed points contain15,941,022 bytes of compressed raw logs and122,040,320 bytes of archive containers. Source logical bytes, stored gzip files, archive containers and native allocated source/restore bytes are separately defined; these scopes must not be added into a current disk-usage claim. This excludes input libraries, binaries, other requests and the8 live points. Event records preserve their declared source coverage and are not a complete absence-of-fault proof. Larger raw/archive-content integrity is reused from qualified lifecycle evidence, pending final C full48 audit.

The resource consumer is CPU-only and starts no service or model. Its final-mode command is for a fresh output directory after actual legal48 terminal outcomes. Existing owner, dispatcher, source pins, budgets, original final-analysis waiter and SOURCE_KEEP remain unchanged. This evidence is not final scientific closure.

'''
 readme=(D/'REVIEW_PACK_README.md').read_text();assert '## Measured host resources: closed40 snapshot'not in readme
 first,rest=readme.split('\n',1);updated=first+'\n\n'+note+rest.lstrip('\n');m.write(D/'REVIEW_PACK_README.md',updated.encode());m.write(m.O/'README.md',updated.encode())
 m.put(m.O/'publication_service/ACTUAL_RESOURCE_PUBLICATION.json',dict(UTC=m.utc(),packs=index,source_sha256=m.sha(__file__),new_models=0,new_services=0,active_science_mutations=0,final_scientific_closure=False))
 m.write(m.O/'publication_service/publish_actual_resources.py',Path(__file__).read_bytes())
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace')
 affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 for path in affected:assert path in frozen and m.sha(m.W/path)==frozen[path]
 m.put(m.O/'publication_service/ACTUAL_RESOURCE_VERBATIM_SOURCE_CHECK.json',dict(UTC=m.utc(),exemptions=[dict(path=x,sha256=frozen[x],reason='Preserve immutable independently reviewed original bytes')for x in affected],scientific_bytes_changed=0))
 status=m.rd(m.O/'LATEST_STATUS.json');terminal=status['summary']['all_registered48_terminal_verified']
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json')
 m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=terminal,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths)
 changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed)
 m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): publish measured closed40 host-resource evidence and independent review','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=terminal,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=status['summary'],resource_closed_n=40,resource_pending_n=8)
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_ACTUAL_RESOURCE_COMMIT_RECEIPT.json',receipt)
 continuation=m.rd(A/'GOAL_CONTINUATION.json')
 continuation['actual_resource_summary_preparation']=dict(A_manifest=dict(path=str(A/packs[0][0]),sha256=packs[0][1]),C_manifest=dict(path=str(A/packs[1][0]),sha256=packs[1][1]),source_sha256='ea28e3cdb270f4edbc5fcade46d3317defc13b25262a0cea961699ba2398b81c',frozen_resource_n=40,pending_in_snapshot=8,final48_executed=False,not_part_of_original_waiter=True,final_action='After actual all48 legal terminal outcomes and frozen source-qualified provider, invoke A_actual_resource_summary_v1/summarize_actual_resources.py --mode final with fresh updates/final48_v1. Inspect resource evidence HOLD/unknowns and obtain narrow independent C review; publish final resource manifest. No model or CPU automatic retry.')
 if continuation.get('latest_root_cycle_audit_manifest',{}).get('sha256')=='d2adb4999b207be38fd1b05238e8abd34380bce8a509bce12d6def2ba0298841':
  continuation['latest_root_cycle_audit_manifest']=dict(path=str(A/'root_independent_cycle_statistics_v1/20261104T043415364666Z/MANIFEST.json'),sha256='dd5076b738679dcd262689423bbef148fe1e7b20bb2bafb4cd8700e25df1a47d')
 m.put(A/'GOAL_CONTINUATION.json',continuation);print(json.dumps(receipt))
