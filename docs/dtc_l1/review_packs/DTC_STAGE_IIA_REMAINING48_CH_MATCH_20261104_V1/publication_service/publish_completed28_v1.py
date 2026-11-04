"""Publish completed28 consolidation and independent review; no science actions."""
from pathlib import Path
import importlib.util,json,fcntl,hashlib,subprocess
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
src=D/'report_only_publisher.py'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('existing_root_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
packs=[
 ('root_independent_cycle_statistics_v1/20261104T043415364666Z/MANIFEST.json','dd5076b738679dcd262689423bbef148fe1e7b20bb2bafb4cd8700e25df1a47d','root_independent_cycles_40accepted'),
 ('root_completed28_consolidation_v1/MANIFEST.json','f880b1388f0e8728fca8cfaf40de2ed3f39aa322c3b2c9c1353d3d5a8c323a8f','root_completed28_consolidation_v1'),
 ('agents/C_completed28_consolidation_review_v1/MANIFEST.json','807a7c2e7d6ea1d1153f512d1b8cc52406cfc6306655a68c3c2ea6c0edff734a','C_completed28_consolidation_review_v1')]
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()
 assert m.git('branch','--show-current')==m.BRANCH and not m.git('status','--porcelain')
 assert m.sha(m.R/'control/EXECUTION_PLAN.json')==m.PLAN_SHA
 for x in m.rd(m.R/'control/EXECUTION_PLAN.json')['source_pins']:m.verified(x['path'],x['sha256'])
 provider=m.checked_provider(m.rd(m.BP));assert provider['source_qualified']
 index=[]
 for path,want,name in packs:
  p=A/path;dest=m.O/'independent_reviews'/name;m.manifest_copy(p,dest,want)
  index.append(dict(source_manifest=path,sha256=want,public_directory=str(dest.relative_to(m.O))))
 note='''## Completed28 consolidated scientific review

Read [the completed28 report](independent_reviews/root_completed28_consolidation_v1/CURRENT_SCIENTIFIC_REPORT_40_OF_48.md), its [independent review](independent_reviews/C_completed28_consolidation_review_v1/README.md), and the current execution table below. The frozen report covers40 accepted new CH points and the same28/32 complete six-cell inputs for both F profiles; it is not the final CORE32 result. Independent review passed911 checks, including raw RESULT identities/cycles, legal P0 aliases, exact signs and independently recomputed geometric means. The machine-readable report member is `CONSOLIDATION.json.gz`; the frozen prose's uncompressed filename is a location shorthand only.

On this identical completed28 set, F128 has GM S_CH=1.015488, S_DH=1.013157, CH/DH=1.077227 and I=0.997705. F256 has GM S_CH=1.022801, S_DH=1.022166, CH/DH=1.079035 and I=0.999379. DH remains faster in this aggregate, while neither F setting improves the aggregate relative DH advantage over P0 on this partial set. Completion-order bias and all four pending programs remain explicit. No uniform F candidate is selected before final matched data.

The source Root audit rechecked184 accepted RESULT slots and40 new raw terminal-cycle endpoints. Existing per-program/per-kernel studies, zero responses, regressions, cost disclosures and independent companion reviews remain in this package. Longtail simulations, final full48 lifecycle/recovery audit, final32 narrative and final visual approval remain pending. This publication starts no model, changes no owner/registry/source and does not complete the Goal.

'''
 # Preserve this entry when the existing sole report publisher refreshes README.
 readme=(D/'REVIEW_PACK_README.md').read_text()
 assert '## Completed28 consolidated scientific review' not in readme
 first,rest=readme.split('\n',1);updated=first+'\n\n'+note+rest.lstrip('\n')
 m.write(D/'REVIEW_PACK_README.md',updated.encode());m.write(m.O/'README.md',updated.encode())
 m.put(m.O/'publication_service/COMPLETED28_CONSOLIDATION_PUBLICATION.json',dict(UTC=m.utc(),packs=index,source_sha256=m.sha(__file__),new_models=0,native_writes=0,final_scientific_closure=False))
 m.write(m.O/'publication_service/publish_completed28_v1.py',Path(__file__).read_bytes())
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json')
 m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=provider['all_registered48_terminal_verified'],final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()]
 m.git('add','-f','--',*paths)
 changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed)
 m.git('diff','--cached','--check')
 m.git('commit','-m','docs(dtc): consolidate independently reviewed completed28 results while eight tails run','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=provider['all_registered48_terminal_verified'],final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=provider['summary'],scope='Completed28 frozen report and911-check review; final48/core32 still pending')
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_COMPLETED28_COMMIT_RECEIPT.json',receipt);print(json.dumps(receipt))
