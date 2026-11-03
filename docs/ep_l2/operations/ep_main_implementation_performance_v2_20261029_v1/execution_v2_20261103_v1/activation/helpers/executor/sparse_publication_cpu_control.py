"""Actual bounded private Git sparse checkout publication control; no production Git/science."""
import contextlib,importlib.util,json,pathlib,subprocess,tempfile
P=pathlib.Path
sp=importlib.util.spec_from_file_location('executor',P(__file__).with_name('finite_main_executor.py'));x=importlib.util.module_from_spec(sp);sp.loader.exec_module(x)
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True,stderr=subprocess.STDOUT).strip()
with tempfile.TemporaryDirectory(prefix='ep_main_sparse_cpu_') as t:
 root=P(t);repo=root/'private_repo';remote=root/'private_remote.git';repo.mkdir()
 git(repo,'init','-b','test-stage2');git(repo,'config','user.name','EP CPU Fixture');git(repo,'config','user.email','ep-cpu-fixture@invalid')
 (repo/'visible').mkdir();(repo/'visible/keep.txt').write_text('bounded CPU fixture\n');git(repo,'add','.');git(repo,'commit','-m','private fixture baseline')
 subprocess.run(['git','init','--bare',str(remote)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 git(repo,'remote','add','origin',str(remote));git(repo,'push','origin','test-stage2')
 git(repo,'sparse-checkout','init','--cone');git(repo,'sparse-checkout','set','visible')
 c=root/'control';c.mkdir();x.put(c/'RESULTS_CURRENT.json',{'CPU_fixture':True});(c/'RESULTS_CURRENT.csv').write_text('fixture,status\nprivate,PASS\n')
 manifest=root/'manifest.json';x.put(manifest,{'CPU_fixture':True});authorization=root/'auth.json';x.put(authorization,{'CPU_fixture':True})
 e=object.__new__(x.Executor);e.C=c;e.session='private-cpu';e.manifest_path=manifest;e.m=dict(native_entry_ref={'CPU_fixture':True},authorization_ref=x.ref(authorization),publication=dict(repo=str(repo),branch='test-stage2',relative_directory='outside/execution_v2_20261103_v1'))
 before=git(repo,'rev-parse','HEAD')
 with contextlib.redirect_stdout(__import__('io').StringIO()):e.publish(final=True)
 after=git(repo,'rev-parse','HEAD');changed=git(repo,'diff-tree','--no-commit-id','--name-only','-r',after).splitlines()
 assert before!=after and changed and all(n.startswith('outside/execution_v2_20261103_v1/') for n in changed)
 assert git(repo,'ls-remote','origin','refs/heads/test-stage2').split()[0]==after
 assert not git(repo,'diff','--cached','--name-only')
 # An unrelated staged file must cause refusal before any owned publication commit.
 (repo/'visible/foreign.txt').write_text('must remain untouched\n');git(repo,'add','visible/foreign.txt')
 try:e.publish(final=False)
 except RuntimeError as exc:assert 'foreign staged' in str(exc)
 else:raise AssertionError('foreign staged work should block publication')
 assert git(repo,'rev-parse','HEAD')==after and git(repo,'diff','--cached','--name-only')=='visible/foreign.txt'
 receipt=dict(schema='EP_MAIN_SPARSE_GIT_PUBLICATION_CPU_CONTROL_V1',status='PASS',actual_sparse_checkout=True,new_directory_outside_sparse_cone=True,git_add_sparse_actual=True,exact_staged_scope_commit_actual=True,private_remote_push_and_HEAD_readback=True,foreign_staged_work_rejected_unchanged=True,committed_paths=changed,actual_models_started=0,production_git_writes=0,real_registry_writes=0)
 x.put(P(__file__).with_name('SPARSE_PUBLICATION_CPU_CONTROL.json'),receipt)
 print(json.dumps(receipt,indent=2))
