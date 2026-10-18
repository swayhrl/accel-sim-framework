"""Same-binary RG1 OFF ready witnesses at both physical-clock offsets."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import argparse, datetime, hashlib, importlib.util, json, os, resource, subprocess

FW = Path('/workspace/worktrees/accel-sim-ep-l2-microopt20261018-lane1-v1')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1')
BUILD = Path('/workspace/build/ep-l2-microopt20261018-lane1-v1')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rg1-receipt', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    parent = json.loads(a.rg1_receipt.read_text())
    assert parent['status'] == 'PRODUCER_RG1_PASS_PENDING_LANE5'
    assert sha(BUILD/'accel-sim.out') == parent['binary_sha256']
    for path, key in [(CORE, 'core_source_commit'), (FW, 'framework_source_commit')]:
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip() == parent[key]
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=path)
    r = dict(status='DRY_RUN', authority='9a161b700ae2d17470fe7b08fc16725b3ef6317c',
             core_source_commit=parent['core_source_commit'], framework_source_commit=parent['framework_source_commit'],
             binary_sha256=parent['binary_sha256'], parent_receipt_sha256=sha(a.rg1_receipt),
             script_sha256=sha(__file__), commands=[], application_starts=0,
             disk_floor_bytes=48*2**30, memory_floor_bytes=64*2**30,
             test_executable_sha256=sha(BUILD/'gpgpu-sim/ep_l2_micro_rg1_partition'))
    def save(): (a.out/'RECEIPT.json').write_text(json.dumps(r, indent=2)+'\n')
    tests = []
    for mode, native, static in [('B16', 1, 0), ('S64', 1, 1), ('Unified', 2, 0)]:
        original = a.rg1_receipt.parent/f'{mode}_rg1.config'
        text = original.read_text()
        assert text.count('-gpgpu_ep_l2_rg1 1') == 1
        overlay = a.out/f'{mode}_OFF.config'
        overlay.write_text(text.replace('-gpgpu_ep_l2_rg1 1', '-gpgpu_ep_l2_rg1 0'))
        for offset in [0, 4096]:
            tests.append((mode+'_'+str(offset), [str(BUILD/'gpgpu-sim/ep_l2_micro_rg1_partition'),
                         str(CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'), str(overlay), str(native), '16', str(static), '0', '1', '0', str(offset)]))
    r['planned_tests'] = tests; save()
    if not a.execute: return
    cl = json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    assert sha(cl['registry_client']) == cl['registry_client_sha256']
    registry = module('mq2_off_registry', Path(cl['registry_client']))
    guard = module('mq2_off_guard', FW/'util/ep_l2/ft_lane1/build_r0_1.py')
    def resources():
        live = registry.local_resources()
        assert live['share_disk_free_bytes'] >= 40*2**30
        for k, v in live.items(): r['min_'+k] = min(r.get('min_'+k, v), v)
        return live
    lease = None
    try:
        resources(); lease = registry.Registry(cl['canonical_root']).build_lease('lane1', cpu=1, memory=4*2**30)
        r.update(status='TESTING', lease_id=lease)
        for mode, command in tests:
            guard.run_owned(['/usr/bin/time', '-v', *command], 'OFF_'+mode, a.out,
                            dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'),
                            r, save, resources, registry.process_identity, 180)
        r['status'] = 'PASS_SAME_BINARY_SIX_RG1_OFF_READY_WITNESSES'
    except BaseException as error:
        r.update(status='FAILED_NO_RELEASE', error=repr(error)); raise
    finally:
        if lease: registry.Registry(cl['canonical_root']).release_build(lease, 'lane1'); r['lease_released'] = True
        r['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat(); save()
    print(r['status'])

if __name__ == '__main__': main()
