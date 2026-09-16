#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"; wh="$bundle/cache/wheelhouse"
python3 - "$wh" "$repo/offline/python-requirements.lock" <<'PY'
from pathlib import Path
from packaging.utils import canonicalize_name,parse_wheel_filename
import hashlib,sys
w,l=map(Path,sys.argv[1:]); rows=[]
for p in sorted(w.glob('*.whl')):
 n,v,_,_=parse_wheel_filename(p.name); rows.append((canonicalize_name(n),str(v),p.name,hashlib.sha256(p.read_bytes()).hexdigest()))
if not rows: raise SystemExit('wheelhouse empty')
l.write_text(''.join(f'{n}=={v}\n' for n,v,_,_ in rows))
(w/'WHEELHOUSE.SHA256').write_text(''.join(f'{s}  {f}\n' for _,_,f,s in rows))
PY
