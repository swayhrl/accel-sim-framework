"""CPU-only dynamic calls of the ALREADY BUILT production OO constructor.
No compilation, simulator executable, GPU cycle, kernel, C++ state edit, or
assertion suppression. Scope is constructor mode/finite fail-closed only.
The ctypes ABI is explicit for this x86-64, LP64, 56-byte config build.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys

SYMBOL = '_ZN6dtc_l111oo_frontendC1ENS_6configE'
class Config(ctypes.Structure):
    _fields_ = [('finite_service', ctypes.c_bool),
                ('progressive_wakeup', ctypes.c_bool),
                ('selected_mode', ctypes.c_int)] + [
        (name, ctypes.c_uint) for name in (
            'pib_entries', 'tag_banks', 'tag_requests_per_bank_per_cycle',
            'tag_requests_per_cycle', 'coalescer_threads_per_cycle',
            'logical_sets', 'logical_ways', 'physical_lines',
            'allocation_width', 'io_pib_entries', 'oo_pib_entries',
            'ref_count_bits')]
class Storage(ctypes.Union):
    _fields_ = [('alignment', ctypes.c_longdouble),
                ('bytes', ctypes.c_ubyte * 4096)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def child(library, enabled, mode, finite):
    assert platform.machine() == 'x86_64' and ctypes.sizeof(ctypes.c_void_p) == 8
    assert ctypes.sizeof(Config) == 56
    assert (Config.finite_service.offset, Config.progressive_wakeup.offset,
            Config.selected_mode.offset, Config.ref_count_bits.offset) == (0,1,4,52)
    resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    lib = ctypes.CDLL(str(library), mode=os.RTLD_NOW | os.RTLD_LOCAL)
    # Expected-abort children report the real assertion signal, not the
    # library crash-report handler's exit1. Production assertions stay intact.
    signal.signal(signal.SIGABRT, signal.SIG_DFL)
    mappings = [row for row in Path('/proc/self/maps').read_text().splitlines()
                if str(library) in row]
    assert mappings
    print('AD_EXISTING_LIBRARY_BINDING ' + json.dumps(dict(
        path=str(library), sha256=sha(library), symbol=SYMBOL,
        config_bytes=ctypes.sizeof(Config), config_align=ctypes.alignment(Config),
        mapped_rows=len(mappings))), flush=True)
    cfg = Config(bool(finite), bool(enabled), mode,
                 8,4,1,4,32,1,1,2,4,256,16,13)
    # Construct in aligned opaque storage. No internal C++ field is inspected
    # or changed; process exit reclaims this tiny CPU fixture's allocations.
    storage = Storage()
    ctor = getattr(lib, SYMBOL)
    ctor.argtypes = [ctypes.c_void_p, Config]
    ctor.restype = None
    ctor(ctypes.byref(storage), cfg)
    print('AD_EXISTING_LIBRARY_CONSTRUCTOR_RETURNED', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--library', required=True, type=Path)
    ap.add_argument('--raw', type=Path)
    ap.add_argument('--child', nargs=3, type=int, metavar=('ENABLED','MODE','FINITE'))
    a = ap.parse_args()
    library = a.library.resolve()
    if a.child is not None:
        child(library, *a.child)
        return
    assert a.raw is not None
    raw = a.raw.resolve(); raw.mkdir(parents=True, exist_ok=False)
    initial_sha = sha(library)
    env = dict(os.environ)
    env.pop('LD_PRELOAD',None)
    env['LD_LIBRARY_PATH'] = str(library.parent)
    env['CUDA_VISIBLE_DEVICES'] = ''
    cases = []
    for enabled in (0,1):
        for mode in range(5):
            for finite in (0,1):
                label = f'on{enabled}_mode{mode}_finite{finite}'
                argv = [sys.executable, str(Path(__file__).resolve()),
                        '--library',str(library),'--child',str(enabled),str(mode),str(finite)]
                with (raw/(label+'.stdout')).open('w') as out, (raw/(label+'.stderr')).open('w') as err:
                    proc = subprocess.run(argv,cwd=raw,env=env,stdout=out,stderr=err,timeout=20)
                stdout = (raw/(label+'.stdout')).read_text()
                stderr = (raw/(label+'.stderr')).read_text()
                bindings = [json.loads(line.split(' ',1)[1]) for line in stdout.splitlines()
                            if line.startswith('AD_EXISTING_LIBRARY_BINDING ')]
                assert len(bindings)==1 and bindings[0]['sha256']==initial_sha
                reject = bool(enabled and not (mode==3 and finite))
                if reject:
                    assert proc.returncode == -signal.SIGABRT, (label,proc.returncode,stderr)
                    assert stderr == 'DTC_PROGRESSIVE_WAKE_UNSUPPORTED_MODE_STOP\n', (label,stderr)
                    assert 'AD_EXISTING_LIBRARY_CONSTRUCTOR_RETURNED' not in stdout
                else:
                    assert proc.returncode == 0, (label,proc.returncode,stderr)
                    assert 'AD_EXISTING_LIBRARY_CONSTRUCTOR_RETURNED' in stdout
                    assert not stderr
                cases.append(dict(case=label,enabled=enabled,mode=mode,finite=finite,
                    status='REJECTED_AS_REQUIRED' if reject else 'CONSTRUCTOR_RETURNED_AS_REQUIRED',
                    returncode=proc.returncode,stdout_sha256=sha(raw/(label+'.stdout')),
                    stderr_sha256=sha(raw/(label+'.stderr')),actual_binding=bindings[0]))
    assert sha(library)==initial_sha
    result=dict(status='PASS_EXISTING_PRODUCTION_OO_CONSTRUCTOR_MODE_GUARD_ONLY',
        library=str(library),library_sha256=initial_sha,symbol=SYMBOL,cases=cases,
        invalid_ON_cases_rejected=9,supported_ON_cases=1,OFF_cases_returned=10,
        compiler_invocations=0,full_simulators_started=0,GPU_cycle_calls=0,kernels=0,
        scope='Direct exported production OO constructor via verified x86-64 config ABI. Does not execute full LDST constructor/routing or corrected C++ fixtures, validate data values, or close ON acceptance STOP.')
    (raw/'EXISTING_LIBRARY_MODE_GUARD.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('status','invalid_ON_cases_rejected','supported_ON_cases','OFF_cases_returned','compiler_invocations')}))

if __name__ == '__main__': main()
