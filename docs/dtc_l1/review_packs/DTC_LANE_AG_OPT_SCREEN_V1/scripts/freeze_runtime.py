#!/usr/bin/env python3
"""Freeze CPU-built ELFs/loader/libs and source identities; never calls sim main."""
from common import *
import re
import shutil
import sys

def main():
 core=git(CORE,'rev-parse','HEAD');assert core=='965dffe04366e665626de4afeb7ffebca8622b5f'
 assert not git(CORE,'status','--porcelain')
 assert not git(FW,'diff',FRAMEWORK_BUILD,'--','gpu-simulator','util/tracer_nvbit/tracer_tool')
 dest=BUILD/'runtime-frozen'
 assert not list((RAW/'attempts').glob('*/RUN_START.json')),'NO_METADATA_REFREEZE_AFTER_ANY_SCIENTIFIC_START'
 dest.mkdir(exist_ok=True)
 for name,source in [('accel-sim.out',BUILD/'combined-trace-preview/accel-sim.out'),('libcudart.so',BUILD/'combined-preview/libcudart.so')]:
  if (dest/name).exists():assert sha(source)==sha(dest/name),'CPU_METADATA_REENTRY_CANNOT_REPLACE_FROZEN_ELF'
  else:shutil.copyfile(source,dest/name);(dest/name).chmod(0o555 if name.endswith('.out') else 0o444)
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',LD_LIBRARY_PATH=str(dest),CUDA_VISIBLE_DEVICES='')
 interp=subprocess.check_output(['readelf','-lW',str(dest/'accel-sim.out')],text=True)
 loader=Path(re.search(r'Requesting program interpreter: (.*?)\]',interp)[1]).resolve()
 files={str((dest/n).resolve()) for n in ['accel-sim.out','libcudart.so']}
 listings=[]
 # --list resolves libraries but does not execute the application entrypoint.
 # Source .traceg PipeReader uses /bin/sh + cat; freeze both helpers too.
 helpers=[Path('/bin/sh').resolve(),Path('/usr/bin/cat').resolve()]
 for exe in [dest/'accel-sim.out',*helpers]:
  r=subprocess.run([str(loader),'--list',str(exe)],env=env,capture_output=True,text=True,timeout=30)
  assert r.returncode==0,r.stderr
  listings.append(dict(executable=str(exe),argv=[str(loader),'--list',str(exe)],stdout=r.stdout,stderr=r.stderr))
  for line in r.stdout.splitlines():
   m=re.search(r'=> (/\S+)\s+\(',line) or re.search(r'^\s*(/\S+)\s+\(',line)
   if m:files.add(str(Path(m[1]).resolve()))
  files.add(str(exe.resolve()))
 assert str(dest/'libcudart.so') in files
 assert any('libcudart.so => '+str(dest/'libcudart.so') in r['stdout'] for r in listings)
 files.add(str(loader))
 runtime_files=[dict(path=p,sha256=sha(p),bytes=Path(p).stat().st_size) for p in sorted(files)]
 detailed=(BUILD/'combined-preview/detailed_version').read_text()
 assert '965dffe0_modified_0.0.' in detailed
 wrapper=(BUILD/'combined-trace-preview/accelsim_version.h').read_text()
 assert core in wrapper and FRAMEWORK_BUILD in wrapper
 sources=[]
 for repo,prefix in [(CORE,''),(FW,'gpu-simulator')]:
  paths=git(repo,'ls-files',prefix).splitlines() if prefix else git(repo,'ls-files').splitlines()
  for name in paths:
   path=repo/name
   if path.is_file():sources.append(dict(repository='Core' if repo==CORE else 'Framework',path=name,blob=git(repo,'rev-parse','HEAD:'+name),sha256=sha(path)))
 table(PACK/'SOURCE_FILES_SHA256.tsv',sources)
 write(PACK/'LOADER_RESOLUTION_CPU.json',dict(status='PASS_PRIVATE_CORE_LIBRARY_RESOLVED_NO_MAIN_CALL',listings=listings,
     no_trace_open=True,kernels=0,full_simulations_started=0))
 cache=(BUILD/'combined-preview/CMakeCache.txt').read_text();compilers=[]
 for language in ['CXX']:  # This Core CMake project enables CXX only.
  compiler=Path(re.search(r'^CMAKE_'+language+r'_COMPILER:FILEPATH=(.*)$',cache,re.M)[1]).resolve()
  compilers.append(dict(language=language,path=str(compiler),sha256=sha(compiler),
      version=subprocess.check_output([str(compiler),'--version'],text=True)))
 write(PACK/'RUNTIME_BINDINGS.json',dict(status='FROZEN_CPU_BUILD_IDENTITY_NOT_YET_PERFORMANCE_REGISTRATION',compilers=compilers,
     combined_core_commit=core,combined_core_tree=git(CORE,'rev-parse','HEAD^{tree}'),
     framework_compilation_source=FRAMEWORK_BUILD,framework_gpu_simulator_tree=git(FW,'rev-parse',FRAMEWORK_BUILD+':gpu-simulator'),
     runtime_path=str(dest/'accel-sim.out'),runtime_sha256=sha(dest/'accel-sim.out'),
     runtime_library_path=str(dest/'libcudart.so'),runtime_library_sha256=sha(dest/'libcudart.so'),
     loader=dict(path=str(loader),sha256=sha(loader)),runtime_files=runtime_files,
     trace_helpers=[dict(path=str(p),sha256=sha(p),availability='STATIC_BINDING_ACTUAL_DESCENDANTS_RECORDED_IF_OBSERVED') for p in helpers],
     expected_embedded_core_version=re.search(r'="(.*?)"',detailed)[1],
     expected_embedded_framework_version=re.search(r'="(.*?)"',wrapper)[1],runtime_environment=env,
     CPU_option_probe_sha256=sha(BUILD/'combined-trace-preview/ag-options-cpu-probe'),
     assert_enabled=True,compile_flags='O3 without NDEBUG, exact compile_commands and passed hard-assert CPU cases',
     Core_compile_commands_sha256=sha(BUILD/'combined-preview/compile_commands.json'),
     Framework_compile_commands_sha256=sha(BUILD/'combined-trace-preview/compile_commands.json'),
     Core_build_log_sha256=sha(BUILD/'final-core-relink.log'),Framework_build_log_sha256=sha(BUILD/'final-trace-build.log'),
     coordinator_python=dict(path=str(Path(sys.executable).resolve()),sha256=sha(Path(sys.executable).resolve()),version=sys.version),
     source_files_sha256=sha(PACK/'SOURCE_FILES_SHA256.tsv'),new_performance_starts=0))
 print(json.dumps(dict(status='FROZEN_PRIVATE_RUNTIME_NO_MAIN_CALL',core=core,runtime_files=len(runtime_files),source_files=len(sources))))

if __name__=='__main__':main()
