#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; out="${1:-$root/docs-local/reports/ENVIRONMENT.json}"
mkdir -p "$(dirname "$out")"
python3 - "$root" "$bundle" "$out" <<'PY'
import json, os, platform, shutil, subprocess, sys
root,bundle,out=sys.argv[1:]
def cmd(x):
 try:return subprocess.check_output(x,text=True,stderr=subprocess.STDOUT).splitlines()[0]
 except Exception as e:return f"MISSING: {e}"
cuda=[x for x in [os.environ.get('CUDA_INSTALL_PATH',''),os.path.join(bundle,'toolchain/cuda-12.4'),'/usr/local/cuda','/usr/local/cuda-11.5','/usr/local/cuda-12.4','/usr/local/cuda-12.8'] if x and os.path.exists(x)]
d={'os':platform.platform(),'machine':platform.machine(),'tools':{x:cmd([x,'--version']) for x in ['gcc','g++','cmake','make','python3','git','bison','flex']},'cuda_toolkits':cuda,'status':{'cuda':'PASS' if any(os.path.exists(os.path.join(x,'bin/nvcc')) for x in cuda) else 'FAIL','bison':'PASS' if shutil.which('bison') else 'FAIL','flex':'PASS' if shutil.which('flex') else 'FAIL'},'system_libraries':cmd(['ldconfig','-p']),'repo_root':root,'bundle_root':bundle}
open(out,'w').write(json.dumps(d,indent=2,sort_keys=True)+'\n')
PY
echo "Wrote $out"
