#!/usr/bin/env python3
"""Capture actual compiler/tool binaries and assertion-bearing build flags."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path

def capture(build,out):
 result={}
 for name,path in [('cxx',Path(shutil.which('g++')).resolve()),('cmake',Path(shutil.which('cmake')).resolve()),('cuda_nvcc',Path('/usr/local/cuda-11.8/bin/nvcc').resolve())]:
  result[name]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),version=subprocess.check_output([str(path),'--version'],text=True).strip())
 commands=json.loads((build/'compile_commands.json').read_text())
 assert all('-DNDEBUG' not in c.get('command','') for c in commands)
 result.update(cmake_build_type='Release',production_flags_assertions_enabled=True,production_translation_units=len(commands),directed_probe_flags=['-std=c++17','-UNDEBUG','-DCUDART_VERSION=11080'],production_compile_commands_sha256=hashlib.sha256((build/'compile_commands.json').read_bytes()).hexdigest(),python_interpreter=str(Path(sys.executable).resolve()))
 out.write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':capture(Path(sys.argv[1]),Path(sys.argv[2]))
