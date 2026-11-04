"""Root-only publication enrichment; no native, registry or model mutations."""
from pathlib import Path
import importlib.util,json,gzip,fcntl,subprocess,re,hashlib,datetime
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
loader=importlib.util.spec_from_file_location('root_existing_report_publisher',src);m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
PACKS=[
 ('agents/B_closed_samples_analysis_v1/MANIFEST.json','8eb4e15853937db5d44ad3ead9a498079b51498f159849b263c6064b06862fd7','B_closed_samples_analysis_v1'),
 ('agents/C_interim_mechanism_review_v1/MANIFEST.json','4da996bb50dd15cc4fca36d69d684e03fb1df824cd657d962bd320c7a0430f41','C_interim_mechanism_review_v1'),
 ('agents/C_actual_sgemm_F256_lifecycle_v1/MANIFEST.json','acd8945c65e6482c3286cc5b340aad29bfac5bf3c27ca7219dd19361d4d4b3d7','C_actual_sgemm_F256_lifecycle_v1'),
 ('agents/A_historical_future_budget_readonly_v1/MANIFEST.json','98925e121508d42490725edd638ccc6c847a885c62c85ed532d1ef123d5464bc','A_historical_future_budget_readonly_v1'),
 ('root_independent_cycle_statistics_v1/20261104T022524025950Z/MANIFEST.json','d2adb4999b207be38fd1b05238e8abd34380bce8a509bce12d6def2ba0298841','root_independent_cycles_20261104T022524025950Z'),
 ('agents/A_longtail_kernel_mapping_v1/MANIFEST.json','144f4b6f7d7ac2a19cb18bee3a27ec3e9a749e259139d71d7a2cf448eae341ab','A_longtail_kernel_mapping_v1'),
 ('root_hardware_resource_cost_v1/MANIFEST.json','1ffc08f7ff786c11453d91dc67fbdc197f0370c617d2f91d32d43ad78220da49','root_hardware_resource_cost_v1'),
 ('agents/A_final_hardware_cost_review_v1/MANIFEST.json','a2fe5d44d42f307ea48afc4f0c100d2bd0380ab969bac38b1960bb41345a375e','A_final_hardware_cost_review_v1'),
 ('agents/C_final48_review_preparation_v1/MANIFEST.json','98363f73eb985a7089b236a91300e77b2cb170d99081555c703659ca7543fc59','C_final48_review_preparation_v1'),
 ('agents/B_final24_consumption_preparation_v1/MANIFEST.json','450cfdb615975f80da6dd4a48fd3de8853235efcf10052f158dc2d431e30d997','B_final24_consumption_preparation_v1'),
 ('agents/B_closed_samples_analysis_v1/updates/scalarProd_F256_v1/MANIFEST.json','854e5b81d7451c1a5b390de1eadf5e64e393211d2edd96a02d847afa0dd21ab4','B_scalarProd_F256_v1'),
 ('agents/C_scalarProd_F256_mechanism_review_v1/MANIFEST.json','ecc21f13da20b654e3b28a62c4735ec5df85e53a3e0ab37a3595ddc2f1a5489d','C_scalarProd_F256_mechanism_review_v1'),
 ('agents/B_completed_short_programs_v1/MANIFEST.json','f3905ebdd86f3d67da889bebb9dc0ac98360dc658388ba7f2e4d574521ee3b9d','B_completed_short_programs_v1'),
 ('agents/C_five_completed_programs_review_v1/MANIFEST.json','25123b488c1e1c43d150b61ccf05657b09bb75072e15f61968f4d16cf849e55b','C_five_completed_programs_review_v1')]
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for x in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(x['path'],x['sha256'])
 b=m.checked_provider(m.rd(m.BP));assert b['all_registered48_terminal_verified']is False
 frozen_dest={};pack_index=[]
 for path,expected,name in PACKS:
  p=A/path;dest=m.O/'independent_reviews'/name;m.manifest_copy(p,dest,expected)
  for x in m.rd(p)['files']:frozen_dest[str((dest/m.rel(x['path'])).relative_to(m.W))]=x['sha256']
  pack_index.append(dict(path=path,sha256=expected,public_directory=str(dest.relative_to(m.O))))
 # Reuse exactly the qualified report schema, with fresh independent source roles.
 for x in b['files']:m.write(m.O/'analysis'/m.rel(x['name']),m.verified(x['path'],x['sha256']))
 m.put(m.O/'analysis/PROVIDER.json',b);m.write(m.O/'analysis/SNAPSHOT_MANIFEST.json',Path(b['manifest']['path']).read_bytes())
 obsrow=next(x for x in b['files']if x['name']=='STAGEIIA_REMAINING48_OBSERVATIONS.json.gz');obs=json.loads(gzip.decompress(m.verified(obsrow['path'],obsrow['sha256'])))
 for row in obs['observations']:
  if row.get('RESULT_sha256'):
   name=m.rel(row['cohort']+'.RESULT.json');assert len(name.parts)==1
   m.write(m.O/'accepted_or_negative_receipts'/name,m.verified(m.R/'analysis'/name,row['RESULT_sha256']))
 batch=m.rd(m.R/'analysis/BATCH_STATE.json');m.put(m.O/'snapshots/BATCH_STATE.json',batch)
 req=m.rd(m.REG)['registered_future_requests'][m.REQ];assert req['budget']==48 and len(req['admitted_specs'])==48;m.put(m.O/'snapshots/NEW_REQUEST.json',req)
 f=m.export_figures()
 m.put(m.O/'LATEST_STATUS.json',dict(UTC=m.utc(),status='EXACT48_BACKGROUND_EXECUTION',summary=b['summary'],batch_asof=batch['UTC'],batch_running=batch.get('running'),canary_gate=batch.get('canary_runtime_gate_passed'),preclaim_resource_holds=batch.get('preclaim_resource_holds',[]),figure_snapshot=f['snapshot'],figure_n=f['common_both_F_n'],figure_accepted_new48=f['accepted_new48'],models_launched_by_publication_service=0,final_scientific_closure=False,additional_experiments_released=False))
 note='''# Reading the independent evidence

The current six-cell table has its own provider timestamp. Every analysis below is a separate immutable, dated snapshot; counts must not be mixed. All are interim until the exact48 legal terminal matrix and final CORE32 audit are complete.

- `B_closed_samples_analysis_v1`: qualified09:45:49 CST snapshot,13 newCH points/10 programs/53 closed sources. It establishes explicit zero/negative cases, write-miss versus DRAM-read distinctions and FWT per-kernel changes. It is not a full32 GM.
- **Forward scientific clarification:** its Facts wording `cold/read-active print interval` proves only that K6 is a **read-active print interval**. No compulsory/capacity/conflict or cold-start classification was established. With memcpy prefill enabled, `cold` must not be promoted to a cold-miss claim. The frozen B bytes remain unchanged; `C_interim_mechanism_review_v1` carries this limitation and223 independent checks.
- `C_actual_sgemm_F256_lifecycle_v1`: exact448633 cycles; full strict, all164 chunks and actual22 typed recovery entries. The extra pinned observer exit-race event is retained. Do not hardcode21 entries for every run.
- `root_independent_cycles_20261104T022524025950Z`: independently re-read170 accepted raw RESULT slots,26 accepted new48 raw terminal cycle endpoints and the common18/32 intersection. Exact Fraction/integer signs, available/common-set suite GMs, distributions and directF results match the source-qualified B table at that older snapshot. The six legal P0 wrappers are separately joined to their SHA-pinned underlying accepted results. Source options differ from each design's own P0 only by the authorized FR setting; the shared-credit coupling remains.
- `A_historical_future_budget_readonly_v1`: the StageI scan typed engineering-negative was already fully archived/restored, but the current frozen resource projection has not consumed that terminal certificate. Original-sweep departed failures lack complete forensic closure. This is a future-space accounting observation, not permission to edit old requests/results or release unproven reservations. Active122 source pins and all historical budgets remain unchanged.

Zero DRAM traffic does not prove compute-bound execution. All-L2 misses include writes; fixedWB/lazy-fetch-on-read and memcpy prefill can produce explicit write misses without DRAM reads. Falling retries do not prove lower critical-path latency. Missing late reason counters/means remain unavailable, not zero. Static source reuse is not a measured dynamic cache hit or MSHR merge.

Next-stage structure/combination choices remain pending complete matched data and a new separate authorization. This publication launches no experiment, changes no v0.23 manuscript and does not close the active Goal.
'''
 guide_path=m.O/'INDEPENDENT_EVIDENCE_READING_GUIDE.md';prior=guide_path.read_text()if guide_path.exists()else note
 addition='''
## Completed non-longtail evidence added in this submission

The completed initial10-program mechanism snapshot, scalarProd and five additional complete short programs cover the16 Remaining24 programs with complete six-cell data at this stage. First8 reviewed mechanisms retain their original source/profile limits; neither these snapshots nor the common24/32 table are the final fixed32 conclusion.

`B_scalarProd_F256_v1` and independent321-check `C_scalarProd_F256_mechanism_review_v1` preserve CH+1535 cycles and DH-1828, unchanged3563520 DRAM-read atoms, queue/MRQ histogram units, overlapping mean bounds and unconfirmed causation. Its F128-pending label is specific to that older frozen snapshot; the current main table independently includes the later accepted F128.

`B_completed_short_programs_v1` and independent695-check `C_five_completed_programs_review_v1` cover30 closed sources and408 kernel records: transpose, sad, sgemm and particlefilter_float are exact own-design zero responses to bothF settings. MRI-Q CH stays362244 and DH360174 becomes359855: K2-321, K3+4, K4-2. Preserve the particlefilter_float absolute DH negative; zero F sensitivity is not equal CH/DH performance. Transpose explicit0DRAM and nonzero ICNT admission/write misses do not establish a compute bottleneck. SGEMM has nonzero DRAM reads and exact zero F response; static source behavior is not a measured critical path.

`B_final24_consumption_preparation_v1` and `C_final48_review_preparation_v1` provide CPU-qualified final consumers and exact absolute commands. Their gates require actual legal natural completion and source-qualified evidence; preparation is not final full48 review. No driver or model is launched by this publication. Longtail12 execution and final fixed32 analysis remain active.
'''
 m.write(guide_path,(prior+addition).encode());m.put(m.O/'publication_service/REVIEWED_ANALYSIS_ENRICHMENT_V3.json',dict(UTC=m.utc(),pack_index=pack_index,source_sha256=m.sha(__file__),scientific_actions=0,active_science_sources_changed=0))
 m.write(m.O/'publication_service/publish_reviewed_analysis_v3.py',Path(__file__).read_bytes())
 # Frozen imported code keeps original EOF bytes. New Root prose/code is checked.
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 cmd=['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'];check=subprocess.run(cmd,capture_output=True,text=True,errors='replace')
 affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 exemptions=[]
 for path in affected:
  assert path in frozen_dest and m.sha(m.W/path)==frozen_dest[path],('NON_FROZEN_WHITESPACE',path)
  exemptions.append(dict(path=path,sha256=frozen_dest[path],reason='verbatim immutable reviewed member; retain SHA'))
 m.put(m.O/'publication_service/REVIEWED_PACK_VERBATIM_WHITESPACE.json',dict(UTC=m.utc(),exact_exemptions=exemptions,original_bytes_changed=0))
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json')
 m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=False,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths)
 changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(x.startswith(m.REL+'/')for x in changed)
 m.git('diff','--cached','--check','--',*[x for x in changed if x not in affected])
 m.git('commit','-m','docs(dtc): complete non-longtail CH evidence and independent reviews','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=False,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=b['summary'],reviewed_analysis_packs=pack_index)
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_ANALYSIS_COMMIT_RECEIPT.json',receipt);print(json.dumps(receipt))
