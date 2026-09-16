#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"; wh="$bundle/cache/wheelhouse"
test -d "$wh"; (cd "$wh" && sha256sum -- *.whl | sort > WHEELHOUSE.SHA256)
python3 - "$wh" "$repo/offline/python-requirements.lock" <<'PY'
import pathlib, re, sys
w=pathlib.Path(sys.argv[1]); out=[]
for p in sorted(w.glob('*.whl')):
 m=re.match(r'([A-Za-z0-9_.-]+)-([A-Za-z0-9_.!+]+)-',p.name)
 if m: out.append(f'{m.group(1).replace("_","-")}=={m.group(2)}')
pathlib.Path(sys.argv[2]).write_text('\n'.join(sorted(set(out)))+'\n')
PY
