"""Windows orchestration helpers; never execute scientific applications."""
from pathlib import Path
import os, sys, subprocess, json, hashlib, gzip, time, base64
sys.dont_write_bytecode = True
W = Path(__file__).resolve().parents[5]
R = W / 'docs/ep_l2/operations/original174_verified_offload_reclaim_20261024_v1'
P = Path('D:/repo/tmp/original174_verified_offload_reclaim_20261024_v1')
P.mkdir(parents=True, exist_ok=True)
OLD = Path('D:/repo/original174-research-archive-exec-20261024-v1/docs/ep_l2/operations/original174_research_asset_archive_exec_20261024_v1')
TRACE = Path('D:/repo/ep-dtc-trace-migration-20261024-v1/docs/ep_l2/operations/174new_ep_dtc_trace_migration_20261024_v1')
FULL = Path('D:/repo/full-result-offload-20261023-v1/docs/ep_l2/operations/full_result_offload_20261023_v1/results')
NATIVE = '/root/data/research_asset_verified_offload_20261024_v1'
NAS = '/root/share/mnt164/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261024_verified_offload_reclaim_v1'

def load(p):
    p = Path(p)
    x = json.loads(p.read_bytes())
    if isinstance(x, dict) and x.get('schema') == 'LOSSLESS_AUDIT_METADATA_POINTER_V1':
        b = gzip.decompress((p.parent / x['compressed_file']).read_bytes())
        assert hashlib.sha256(b).hexdigest() == x['uncompressed_sha256']
        return json.loads(b)
    return x

def save(n, x):
    p = R / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((json.dumps(x, indent=2, ensure_ascii=False) + '\n').encode())

def remote(alias, code, timeout=90):
    r = subprocess.run(['ssh', '-o', 'BatchMode=yes', alias, 'nice -n 19 ionice -c 3 python3 -B -'],
                       input=code.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors='replace')[-4000:])
    return json.loads(r.stdout)

def install(name, blob, overwrite=False):
    dest = NATIVE + '/' + name
    code = 'from pathlib import Path;import base64,os,json\np=Path(' + repr(dest) + ');p.parent.mkdir(parents=True,exist_ok=True);b=base64.b64decode(' + repr(base64.b64encode(blob).decode()) + ')\n'
    code += ('p.write_bytes(b)\n' if overwrite else 'if p.exists():assert p.read_bytes()==b,"own immutable control collision"\nelse:p.write_bytes(b)\n')
    code += 'print(json.dumps({"path":str(p),"bytes":len(b)}))'
    return remote('hrl-174-new', code)

def git(*args):
    return subprocess.check_output(['git', '-c', 'http.version=HTTP/1.1', '-C', str(W), *args])
