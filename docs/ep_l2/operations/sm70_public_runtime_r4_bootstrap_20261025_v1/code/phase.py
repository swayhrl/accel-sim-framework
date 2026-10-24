#!/usr/bin/python3
from pathlib import Path
import sys,json,hashlib,importlib.util
if sys.flags.optimize:raise RuntimeError('optimized Python is unsupported')
package=Path(__file__).resolve().parent
def bounded_code(path,limit):
 with path.open('rb')as f:
  raw=f.read(limit+1)
 if len(raw)>limit:raise RuntimeError('RESOURCE_HOLD_PUBLIC_CODE_METADATA_LIMIT')
 return raw
manifest=json.loads(bounded_code(package/'CODE_MANIFEST.json',4*2**20))
canonical=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
expected=hashlib.sha256(canonical({k:v for k,v in manifest.items()if k!='code_version_id'})).hexdigest()
if package.name!=expected or manifest['code_version_id']!=expected:raise RuntimeError('immutable code version mismatch')
for name,row in manifest['files'].items():
 p=package/name
 if not p.resolve().is_relative_to(package)or p.is_symlink():raise RuntimeError('code member escape')
 raw=bounded_code(p,8*2**20)
 if len(raw)!=row['bytes']or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('public package hash mismatch')
spec=importlib.util.spec_from_file_location('public_trace_runtime',package/'runtime.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
stage_spec=importlib.util.spec_from_file_location('public_trace_stages',package/'stages.py')
stages=importlib.util.module_from_spec(stage_spec);stage_spec.loader.exec_module(stages)
stages.main()
