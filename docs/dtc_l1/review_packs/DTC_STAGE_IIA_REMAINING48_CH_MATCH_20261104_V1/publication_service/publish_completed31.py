"""Publish independently reviewed completed31 evidence; exact48 science unchanged."""
from pathlib import Path
import argparse,importlib.util,json,hashlib,fcntl,re,subprocess,gzip
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
ap=argparse.ArgumentParser();ap.add_argument('--package-list',required=True);arg=ap.parse_args();config_path=Path(arg.package_list);assert config_path.resolve().is_relative_to(A.resolve())
config=json.loads(config_path.read_bytes());packs=config['packages'];assert len(packs)==5
assert {r['name']for r in packs}=={'B_completed_srad_v1','C_completed_srad_review_v1','root_independent_cycles_46accepted','root_completed31_consolidation_v1','C_completed31_consolidation_review_v1'}
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('root_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for pin in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(pin['path'],pin['sha256'])
 frozen={};index=[]
 for row in packs:
  p=A/m.rel(row['manifest']);assert p.name=='MANIFEST.json'and re.fullmatch('[0-9a-f]{64}',row['sha256'])
  dest=m.O/'independent_reviews'/row['name'];m.manifest_copy(p,dest,row['sha256'])
  for member in m.rd(p)['files']:
   assert member['bytes']<8*1024**2;frozen[str((dest/m.rel(member['path'])).relative_to(m.W))]=member['sha256']
  index.append(dict(source_manifest=row['manifest'],sha256=row['sha256'],public_directory=str(dest.relative_to(m.O))))
 note='''## Completed31 review: final GES pair pending

Start with the [completed31 scientific report](independent_reviews/root_completed31_consolidation_v1/REPORT.md) and its [independent review](independent_reviews/C_completed31_consolidation_review_v1/README.md). This frozen source has46 accepted new CH identities and the same31 complete six-cell inputs for both F profiles. GESUMMV-F128/F256 remain absent. The current execution table has an independent timestamp; no31-program result is promoted to final32 coverage.

On this matched31 set, F128 has GM S_CH=1.013978406,S_DH=1.011876444,CH/DH=1.092348845,I=0.997927015. F256 has GM S_CH=1.020571838,S_DH=1.019999506,CH/DH=1.094004114,I=0.999439204. Common P0 CH/DH GM is1.094617971. Both designs gain from downstream expansion in this subset; the aggregate incremental relative DH advantage is slightly below its P0 value. Absolute DH advantage and incremental I are different statements. No bestF or equal-area conclusion is selected here.

Two forward wording clarifications preserve the original report SHA: R always means CH_cycles/DH_cycles, equivalently the DH/CH performance ratio; it is not the inverse cycle ratio. The requirement for new approval concerns validation that starts new scientific execution,capture,GPU work,instrumentation or simulation. Already authorized CPU-only read-only/source/static numeric checks remain authorized without another approval.

The [srad supplement](independent_reviews/B_completed_srad_v1/REPORT.md) and [independent review](independent_reviews/C_completed_srad_review_v1/README.md) complete the naturally closed cases. Six sources cover3012 records and seven actual phase selectors, including450CTA and1CTA reduce phases with the same symbol. BothF settings are exact own-design zero responses; the22cycle absolute DH extract regression and13 DRAM-read atoms remain explicit. Write misses,small bank populations,unavailable counters and full-application/numeric limits remain distinct.

The Root cycle audit independently checks190 RESULT source slots and46 accepted new raw terminal-cycle endpoints, with exact signs,suites,distributions and directF values. Original128 plusfirst16 source roles and six legal P0 aliases are retained. This audit does not replace final48 lifecycle/archive/native recovery review. New myocyte source-event invalidation/coherence and3MM candidate-source correctness limits remain explicit in their companion reviews and the31 report. Accepted model outcomes are retained under the frozen contract; numerical-correctness certification remains separate.

Final GES outcomes,the original one-shot final analysis chain,final48 measured-resource consumption,full32 narrative,independent end review,final visual approval and final immutable Git/SHA closure are pending. No additional experiment or manuscript change is released.

'''
 readme=(D/'REVIEW_PACK_README.md').read_text();assert '## Completed31 review:'not in readme
 first,rest=readme.split('\n',1);updated=first+'\n\n'+note+rest.lstrip('\n');m.write(D/'REVIEW_PACK_README.md',updated.encode());m.write(m.O/'README.md',updated.encode())
 m.put(m.O/'publication_service/COMPLETED31_PUBLICATION.json',dict(UTC=m.utc(),packs=index,source_sha256=m.sha(__file__),new_models=0,native_writes=0,final_scientific_closure=False));m.write(m.O/'publication_service/publish_completed31.py',Path(__file__).read_bytes())
 # Preserve a resolved report-transport incident separately from model outcomes.
 incident=D/'LAST_ERROR.json';resolved=D/'receipts/91d288465801124d681650ab7ba04ec3530ba289.json'
 if incident.exists()and resolved.exists():
  err=m.rd(incident);receipt=m.rd(resolved)
  if err.get('UTC')=='2026-11-04T07:05:24.926285+00:00'and receipt.get('status')=='PUSH_LSREMOTE_HTTPS_VERIFIED':
   m.put(m.O/'publication_service/RESOLVED_TRANSPORT_TIMEOUT_91d2884.json',dict(error=err,resolution=receipt,models_retried=0,scientific_identities_changed=0,interpretation='Same Git commit transport retried after90s timeout and subsequently verified; not a model failure.'))
 b=m.checked_provider(m.rd(m.BP));terminal=b['all_registered48_terminal_verified']
 for item in b['files']:m.write(m.O/'analysis'/m.rel(item['name']),m.verified(item['path'],item['sha256']))
 m.put(m.O/'analysis/PROVIDER.json',b);m.write(m.O/'analysis/SNAPSHOT_MANIFEST.json',Path(b['manifest']['path']).read_bytes())
 item=next(x for x in b['files']if x['name']=='STAGEIIA_REMAINING48_OBSERVATIONS.json.gz');observed=json.loads(gzip.decompress(m.verified(item['path'],item['sha256'])))
 for row in observed['observations']:
  if row.get('RESULT_sha256'):
   name=m.rel(row['cohort']+'.RESULT.json');assert len(name.parts)==1;m.write(m.O/'accepted_or_negative_receipts'/name,m.verified(m.R/'analysis'/name,row['RESULT_sha256']))
 batch=m.rd(m.R/'analysis/BATCH_STATE.json');m.put(m.O/'snapshots/BATCH_STATE.json',batch);req=m.rd(m.REG)['registered_future_requests'][m.REQ];assert req['budget']==48 and len(req['admitted_specs'])==48;m.put(m.O/'snapshots/NEW_REQUEST.json',req)
 f=m.export_figures();m.put(m.O/'LATEST_STATUS.json',dict(UTC=m.utc(),status='ALL48_TERMINAL_FINAL_INDEPENDENT_REVIEW_PENDING'if terminal else'EXACT48_BACKGROUND_EXECUTION',summary=b['summary'],batch_asof=batch['UTC'],batch_running=batch.get('running'),canary_gate=batch.get('canary_runtime_gate_passed'),preclaim_resource_holds=batch.get('preclaim_resource_holds',[]),figure_snapshot=f['snapshot'],figure_n=f['common_both_F_n'],figure_accepted_new48=f['accepted_new48'],models_launched_by_publication_service=0,final_scientific_closure=False,additional_experiments_released=False))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace');affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 for path in affected:assert path in frozen and m.sha(m.W/path)==frozen[path]
 m.put(m.O/'publication_service/COMPLETED31_VERBATIM_SOURCE_CHECK.json',dict(UTC=m.utc(),exemptions=[dict(path=x,sha256=frozen[x],reason='Verbatim immutable reviewed member')for x in affected],source_bytes_changed=0))
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json');m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=terminal,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths);changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed);m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): consolidate independently reviewed completed31 evidence pending GES pair','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=terminal,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=b['summary'],new_review_packages=index);m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_COMPLETED31_COMMIT_RECEIPT.json',receipt)
 continuation=m.rd(A/'GOAL_CONTINUATION.json');continuation['latest_root_cycle_audit_manifest']=dict(path=str(A/'root_independent_cycle_statistics_v1/20261104T071015468833Z/MANIFEST.json'),sha256='60f89782895950134e3946333dbf78dd9fed3d102c131cb5db64435ae80c71bd');continuation['completed31_consolidation']=dict(manifest=str(A/'root_completed31_consolidation_v1/MANIFEST.json'),sha256='23fd901794b23c37b185aa29de3fb6db40a0e50a3b4cc58eca340aa1303a8c2f',packages=index,stage='COMMITTED_PENDING_REMOTE_READBACK');continuation['additional_readonly_srad_work']['stage']='COMMITTED_PENDING_REMOTE_READBACK';m.put(A/'GOAL_CONTINUATION.json',continuation);print(json.dumps(receipt))
