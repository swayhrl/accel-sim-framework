#!/usr/bin/env python3
import pathlib,hashlib,json,py_compile
R=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1')
C=R/'control'
src=(C/'capture_ordinary_worker.py').read_text()
old=""" for x in task.get('runtime_links',[]):
  rel=x.get('link',x.get('name'));src=pathlib.Path(x.get('target',x.get('source')));dest=runtime/rel
  assert runtime.resolve() in dest.resolve().parents
  if src.is_dir():shutil.copytree(src,dest)
  else:copy(src,dest)
"""
new=""" declared=task.get('input_files',task.get('input_identity',[]))
 declared=declared if isinstance(declared,list) else []
 staged=[]
 for x in task.get('runtime_links',[]):
  rel=x.get('link',x.get('name'));source=pathlib.Path(x.get('target',x.get('source')));dest=runtime/rel
  assert runtime.resolve() in dest.resolve().parents
  if source.is_dir():
   dest.mkdir(parents=True,exist_ok=False)
   relevant=[v for v in declared if source.resolve() in pathlib.Path(v['path']).resolve().parents]
   assert relevant,'runtime directory has no declared input files'
   for v in relevant:
    original=pathlib.Path(v['path']);assert sha(original)==v['sha256']
    target=dest/original.resolve().relative_to(source.resolve());copy(original,target)
    staged.append({'source':str(original),'member':str(target.relative_to(root)),'sha256':v['sha256']})
  else:
   expected=next(v['sha256'] for v in declared if pathlib.Path(v['path']).resolve()==source.resolve())
   assert sha(source)==expected;copy(source,dest)
   staged.append({'source':str(source),'member':str(dest.relative_to(root)),'sha256':expected})
 for v in declared:
  assert sha(pathlib.Path(v['path']))==v['sha256']
 save(root/'INPUT_STAGING.json',{'policy':'ONLY_MANIFEST_DECLARED_REGULAR_FILES;PRIVATE_COPIES','files':staged,'absolute_input_files_verified':len(declared)})
"""
assert src.count(old)==1
src=src.replace(old,new)
src=src.replace("for i,x in enumerate(task.get('sources',[])):","for i,x in enumerate(task.get('sources',task.get('source_files',[]))):")
src=src.replace("'source_version':task['version']","'source_version':task.get('version',task.get('source_version','UNKNOWN'))")
src=src.replace("'variant':task['variant']","'variant':task.get('variant','DECLARED_DEFAULT')")
src=src.replace("'input_identity':task.get('input_identity')","'input_identity':task.get('input_identity',task.get('input_files'))")
src=src.replace("'numerical_status':numerical,","'numerical_status':numerical,'input_byte_identity_qualification':job.get('input_byte_identity_qualification','DECLARED_FILE_SHA_OR_DETERMINISTIC_SOURCE;NO_UNRECORDED_SEED_CLAIM'),'native_state':job.get('native_state'),")
# Retain actual binary and helper identities; each executable source version is immutable.
digest=hashlib.sha256(src.encode()).hexdigest();dest=C/'pipeline_versions'/('capture_ordinary_'+digest+'.py')
dest.parent.mkdir(exist_ok=True)
if not dest.exists():dest.write_text(src)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
py_compile.compile(str(dest),doraise=True)
(C/'WORKER_V3_PREPARED.json').write_text(json.dumps({'path':str(dest),'sha256':digest,'changes':['declared input files only','source_files support','separate numerical/source identity']},indent=2)+'\n')
print(str(dest))
