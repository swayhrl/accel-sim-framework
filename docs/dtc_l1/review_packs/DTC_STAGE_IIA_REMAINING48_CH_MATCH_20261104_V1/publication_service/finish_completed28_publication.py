"""Finish prepared report preserving immutable reviewed source bytes."""
from pathlib import Path
import importlib.util,json,fcntl,ast,subprocess,re,hashlib
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1');D=A/'publication_service_v1'
src=D/'report_only_publisher.py';assert hashlib.sha256(src.read_bytes()).hexdigest()=='acbb284231abf5c0d3dfe53a588e2101bdf778d7729d9fe38736b82a3f4c9f1f'
s=importlib.util.spec_from_file_location('existing_publisher',src);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with(A/'PUBLICATION.lock').open('a+b')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(D/'PENDING_PUSH.json').exists()and m.git('branch','--show-current')==m.BRANCH
 tree=ast.parse((D/'publish_completed28_v1.py').read_text())
 packs=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='packs'for t in n.targets))
 frozen={}
 for path,want,name in packs:
  p=A/path;m.verified(p,want);dest=m.O/'independent_reviews'/name
  for x in m.rd(p)['files']:
   target=dest/m.rel(x['path']);m.verified(target,x['sha256']);frozen[str(target.relative_to(m.W))]=x['sha256']
 assert '## Completed28 consolidated scientific review' in(m.O/'README.md').read_text()
 assert(m.O/'README.md').read_bytes()==(D/'REVIEW_PACK_README.md').read_bytes()
 check=subprocess.run(['git','-c','safe.directory='+str(m.W),'-C',str(m.W),'diff','--cached','--check'],capture_output=True,text=True,errors='replace')
 affected=sorted(set(z.group(1)for line in check.stdout.splitlines()if(z:=re.match(r'^(docs/.*?):[0-9]+: ',line))))
 assert affected
 for path in affected:assert path in frozen and m.sha(m.W/path)==frozen[path]
 m.put(m.O/'publication_service/COMPLETED28_VERBATIM_SOURCE_CHECK.json',dict(UTC=m.utc(),frozen_original_bytes_unchanged=True,exemptions=[dict(path=x,sha256=frozen[x],reason='Verbatim independently reviewed source; retain manifest identity')for x in affected],scientific_mutations=0))
 m.write(m.O/'publication_service/finish_completed28_publication.py',Path(__file__).read_bytes())
 provider=m.checked_provider(m.rd(m.BP))
 members=sorted(p for p in m.O.rglob('*')if p.is_file()and p!=m.O/'MANIFEST.json')
 m.put(m.O/'MANIFEST.json',dict(schema='DTC_STAGEII_REMAINING48_EXECUTION_PROGRESS_MANIFEST_V1',UTC=m.utc(),base_authority=m.BASE,request=m.REQ,all48_terminal_verified=provider['all_registered48_terminal_verified'],final_scientific_closure=False,files=[dict(path=str(p.relative_to(m.O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in members]))
 paths=[str(p.relative_to(m.W))for p in sorted(m.O.rglob('*'))if p.is_file()];m.git('add','-f','--',*paths)
 changed=m.git('diff','--cached','--name-only').splitlines();assert changed and all(p.startswith(m.REL+'/')for p in changed)
 m.git('diff','--cached','--check','--',*[p for p in changed if p not in affected])
 m.git('commit','-m','docs(dtc): consolidate independently reviewed completed28 results while eight tails run','--',*paths)
 receipt=dict(commit=m.git('rev-parse','HEAD'),branch=m.BRANCH,UTC=m.utc(),all48_terminal_verified=provider['all_registered48_terminal_verified'],final_scientific_closure=False,manifest_sha256=m.sha(m.O/'MANIFEST.json'),summary=provider['summary'],scope='Completed28 report and independent911-check review; final48/core32 pending')
 m.put(D/'PENDING_PUSH.json',receipt);m.put(D/'ROOT_COMPLETED28_COMMIT_RECEIPT.json',receipt);print(json.dumps(receipt))
