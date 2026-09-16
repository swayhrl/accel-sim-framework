#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; out="${1:-$root/docs-local/reports/ENVIRONMENT.json}"
mkdir -p "$(dirname "$out")"
python3 - "$root" "$out" <<'PY'
import json, os, platform, shutil, subprocess, sys
root,out=sys.argv[1:]
def cmd(x):
 try:return subprocess.check_output(x,text=True,stderr=subprocess.STDOUT).splitlines()[0]
 except Exception as e:return f"MISSING: {e}"
cuda=[x for x in ['/usr/local/cuda','/usr/local/cuda-11.5','/usr/local/cuda-12.4','/usr/local/cuda-12.8'] if os.path.exists(x)]
d={'os':platform.platform(),'machine':platform.machine(),'tools':{x:cmd([x,'--version']) for x in ['gcc','g++','cmake','make','python3','git','bison','flex']},'cuda_toolkits':cuda,'system_libraries':cmd(['ldconfig','-p']),'root':root}
open(out,'w').write(json.dumps(d,indent=2,sort_keys=True)+'\n')
PY
echo "Wrote $out"
