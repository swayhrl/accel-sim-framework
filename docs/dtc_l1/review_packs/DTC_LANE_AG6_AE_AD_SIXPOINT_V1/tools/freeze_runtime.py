"""Read-only static runtime freeze; no target/loader execution, no launch API."""
from common import *
from freeze_static import freeze_executable,metadata
from mapping_roles import require,validate_manifest

def main():
 gate=json.loads((PACK/'CURRENT_SITE_AUDIT.json').read_text())
 require(gate['all_resource_checks_pass'] and gate['authority']['status']=='PASS_CURRENT_NO_OTHER_DTC_DISPATCH_AUTHORITY','RESOURCE_AUTHORITY_HOLD_NO_RUNTIME_SCAN')
 expected=json.loads((PACK.parent/'DTC_LANE_AG3_AE_AD_SCREEN_V1/specs/BASE_GEMM.json').read_text())
 require(git(CORE,'rev-parse','HEAD')==expected['core_commit']=='c8090115bd57512b1b23fca7d925301fa620c751','FIXED_CORE_ONLY')
 require(not git(CORE,'status','--porcelain'),'CORE_NOT_CLEAN')
 require(git(CORE,'rev-parse','refs/ag6-source/core-final')==expected['core_commit'],'FIXED_CORE_FETCH_BACK_REQUIRED')
 sources=json.loads((PACK/'HISTORICAL_AG3_SOURCE_FILES_SHA256.json').read_text())
 for row in sources:
  repo=CORE if row['repository']=='Core' else FW_REPO
  current=CORE if row['repository']=='Core' else FW
  commit=expected['core_commit'] if row['repository']=='Core' else FRAMEWORK_BUILD
  require(git(repo,'rev-parse',commit+':'+row['path'])==row['blob'],'SOURCE_GIT_BLOB_CHANGED:'+row['path'])
  require(hashlib.sha256(blob(repo,commit,row['path'])).hexdigest()==row['sha256'],'SOURCE_BLOB_SHA_CHANGED:'+row['path'])
  require(sha(current/row['path'])==row['sha256'],'SOURCE_WORKTREE_SHA_CHANGED:'+row['path'])
 require(len(sources)==702,'FULL_SOURCE_IDENTITY_POPULATION')
 target=Path(expected['runtime_path']);library=Path(expected['runtime_library_path'])
 require(sha(target)==expected['runtime_sha256'],'ACTUAL_EXECUTABLE_SHA_CHANGED')
 require(sha(library)==expected['runtime_library_sha256'],'ACTUAL_LIBRARY_SHA_CHANGED')
 all_manifests={};closure={}
 for exe in [target,Path('/usr/bin/dash'),Path('/usr/bin/cat')]:
  m,objects=freeze_executable(exe,library.parent);validate_manifest(m)
  all_manifests[m['target']]=m;closure[m['target']]=objects
 actual=all_manifests[str(target)]
 require(any(r['path']==str(library) and r['sha256']==expected['runtime_library_sha256'] for r in actual['files']),'FROZEN_ACTUAL_LIBRARY_MISSING')
 roles={r['path']:r for m in all_manifests.values() for r in m['files']}
 require('/etc/ld.so.cache' in roles and roles['/etc/ld.so.cache']['role']=='LOADER_DATA_CACHE','EXPLICIT_CURRENT_CACHE_REQUIRED')
 buildids={str(p):subprocess.check_output(['/usr/bin/readelf','-nW',str(p)],text=True) for p in [target,library]}
 require('6a0ceed9abbe0e26c66e375687dcb2439085969d' in buildids[str(target)],'EXECUTABLE_BUILD_ID_CHANGED')
 require('ab1ca2782871068e7fe333974561fcf75f2fe28c' in buildids[str(library)],'LIBRARY_BUILD_ID_CHANGED')
 write(PACK/'RUNTIME_MAPPING_MANIFESTS.json',all_manifests)
 write(PACK/'RUNTIME_STATIC_ELF_CLOSURE.json',closure)
 write(PACK/'RUNTIME_FREEZE_QUALIFICATION.json',dict(status='PASS_CURRENT_RUNTIME_IDENTITY',utc=now(),core=expected['core_commit'],framework_compilation_source=FRAMEWORK_BUILD,source_files_verified=len(sources),source_binding_sha256=sha(PACK/'HISTORICAL_AG3_SOURCE_FILES_SHA256.json'),actual_executable=str(target),executable_sha256=sha(target),actual_library=str(library),library_sha256=sha(library),buildid_readelf=buildids,role_union=list(roles.values()),registry_sha256=sha(PACK/'RUNTIME_MAPPING_MANIFESTS.json'),target_executions=0,loader_executions=0,new_simulator_starts=0,pre_fork_current_cache_identity=True))
 print('PASS_CURRENT_RUNTIME_IDENTITY',len(roles))
if __name__=='__main__':main()
