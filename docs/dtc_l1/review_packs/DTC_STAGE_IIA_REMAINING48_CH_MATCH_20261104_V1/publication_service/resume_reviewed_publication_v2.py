"""Finish only Root's already prepared report transaction; no science changes."""
from pathlib import Path
import json,ast,importlib.util,subprocess,fcntl,re
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
s=importlib.util.spec_from_file_location('root_report',D/'report_only_publisher.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH
 assert(A/'root_figure_promotion_v2/previous_FIGURE_VISUAL_APPROVAL.json').exists()
 assert m.git('rev-parse','HEAD')=='91c48a3371ee77e41fe732572f18385d3480b3ba'
 tree=ast.parse((D/'publish_reviewed_analysis_v2.py').read_text());packs=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PACKS'for t in n.targets))
 packs+= [('agents/C_final48_review_preparation_v1/MANIFEST.json','98363f73eb985a7089b236a91300e77b2cb170d99081555c703659ca7543fc59','C_final48_review_preparation_v1'),('agents/A_final_hardware_cost_review_v1/MANIFEST.json','a2fe5d44d42f307ea48afc4f0c100d2bd0380ab969bac38b1960bb41345a375e','A_final_hardware_cost_review_v1')]
 frozen={}
 for rel,want,name in packs:
  p=A/rel;dest=m.O/'independent_reviews'/name;m.manifest_copy(p,dest,want)
  for x in m.rd(p)['files']:frozen[str((dest/m.rel(x['path'])).relative_to(m.W))]=x['sha256']
 b=m.checked_provider(m.rd(m.O/'analysis/PROVIDER.json'));assert b['source_qualified']and not b['all_registered48_terminal_verified']
 for x in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(x['path'],x['sha256'])
 f=m.export_figures();assert f['manifest']['sha256']=='373dd17b17c3d3d431e01f1479588a52700324f6347804d251a70f8be77d6af1'
 assert(m.O/'.gitattributes').read_bytes()==b'figures/*.svg -whitespace\n'
 # Keep exact upstream bytes, including legacy encodings. Decode diagnostics
 # only with replacement; source files are neither decoded nor normalized.
 guide=(m.O/'INDEPENDENT_EVIDENCE_READING_GUIDE.md').read_text()
 guide+='\n## Completed preparation for the remaining long tail\n\n`A_longtail_kernel_mapping_v1` freezes7 programs/6844 registered kernel instances and source/trace phase selectors without reading live results. `C_final48_review_preparation_v1` is a CPU-qualified verifier and actual closed-subset qualification, not a final48 PASS. Call its final mode only after the exact48 legal terminal matrix is ready. `A_final_hardware_cost_review_v1` independently checks the fixed FR/credit cost and effective L1/Tag/pool/PIB/completion paths.\n\nThe DH16KiB compatibility cache is not used by the selected loads taken over by OO, but eligible fallback routes (such as some stores/atomics) remain. Do not treat it as universally inactive, remove it from area cost, or call80KiB pool plus16KiB compatibility a unified96KiB effective cache. Actual dynamic routing/hits and physical area/timing remain unproven by geometry alone. The old source/result bytes and v0.23 remain unchanged.\n'
 m.write(m.O/'INDEPENDENT_EVIDENCE_READING_GUIDE.md',guide.encode())
 m.write(m.O/'publication_service/resume_reviewed_publication_v2.py',Path(__file__).read_bytes())
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()and p!=m.O/'MANIFEST.json'];m.git('add','-f','--',*paths)
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace')
 affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 exemptions=[]
 for path in affected:
  assert path in frozen and m.sha(m.W/path)==frozen[path],('UNREVIEWED_STYLE_EXCEPTION',path)
  exemptions.append(dict(path=path,sha256=frozen[path],reason='Immutable reviewed upstream member; preserve bytes and original encoding'))
 m.put(m.O/'publication_service/REVIEWED_PACK_VERBATIM_WHITESPACE_V2.json',dict(UTC=m.utc(),exact_exemptions=exemptions,source_bytes_normalized=0,diagnostic_decode_only='UTF8 errors=replace',generated_SVG_scope='figures/*.svg only; actual3-case Git qualification retained'))
 m.put(m.O/'publication_service/ROOT_NON_LONGTAIL_PUBLICATION_SCOPE.json',dict(UTC=m.utc(),request=m.REQ,complete_scientific_stage=False,all48_started=True,longtail_execution_unchanged=True,source_qualified_table_asof=b['observed_utc'],summary=b['summary'],new_frozen_review_packages=[dict(path=x,sha256=y,public_name=z)for x,y,z in packs],final48_independent_review_pending=True,all32_final_analysis_pending=True,ordinary_engineering_resolved='Preserve original source encodings; Git diagnostics decoded tolerantly; generatedSVG whitespace attribute qualified; no scientific/source/native changes.'))
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json');m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=False,final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths);changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed)
 m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): publish completed analysis and final-review preparation while long tails run','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=False,final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=b['summary'],scope='Completed non-longtail evidence and preparation; longtail simulation and final full32 review still active')
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_NON_LONGTAIL_COMMIT_RECEIPT.json',receipt);print(json.dumps(receipt))
