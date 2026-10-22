#!/bin/sh
set -eu
[ "$#" -eq 1 ] || { echo "usage: RESTORE.sh NEW_ABSENT_NATIVE_DESTINATION" >&2; exit 2; }
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 -B - "$HERE" "$1" <<'PY'
import pathlib,sys,json,hashlib
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]);dst=pathlib.Path(sys.argv[2]).absolute()
lib=root/'v9_transaction.py'
assert hashlib.sha256(lib.read_bytes()).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe'
sys.path.insert(0,str(root));import v9_transaction as v
receipt=json.loads((root/'FINAL_SYNTHETIC_RESULT.json').read_bytes());arc=root/'archive'/receipt['txid'];raw=(arc/'manifest.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()==receipt['manifest_sha256'];m=json.loads(raw)
assert not dst.is_relative_to(pathlib.Path(m['source_root'])) and not dst.is_relative_to(root)
assert not dst.exists() and not dst.is_symlink()
print(json.dumps(v.native_restore(arc/'tree',m,dst),indent=2))
PY
