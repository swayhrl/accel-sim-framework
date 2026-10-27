"""Preserve the failed pure v1 preparation; resume only equal unspent files.
The v1 negative was fail-closed TypeError for absent NI. No models started.
"""
import importlib.util,json,sys
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0,str(J/'tools'))
from ep_perf_common import *
p=J/'tools/main_prepare_source92_ni_v1.py'
t=p.read_text().replace('ValueError,RuntimeError,KeyError,FileNotFoundError','ValueError,RuntimeError,TypeError,KeyError,FileNotFoundError')
t=t.replace("with p.open('xb') as f:f.write(Path(r['path']).read_bytes())", "if p.exists():need(p.read_bytes()==Path(r['path']).read_bytes(),'prior unspent config bytes differ')\n            else:\n                with p.open('xb') as f:f.write(Path(r['path']).read_bytes())")
original_put=put
def equal_unspent_put(path,value,exclusive=False):
    if exclusive and Path(path).exists():
        need(read(path)==value,'existing unspent engineering file differs '+str(path))
        return dict(path=str(path),sha256=sha(path),bytes=Path(path).stat().st_size)
    return original_put(path,value,exclusive)
ns=dict(__name__='main_source92_NI_preparation_v2',__file__=str(p))
exec(compile(t,'MAIN_PURE_PREPARATION_V2_RESUME_EQUAL_FILES','exec'),ns)
ns['put']=equal_unspent_put
correction=original_put(J/'control/SOURCE92_P1_NI_PREPARATION_V1_FAILURE_BOUNDARY.json',dict(status='PURE_ENGINEERING_NEGATIVE_CONTROL_EXCEPTION_CLASS_FIXED_NO_MODEL_OR_REGISTRY_START',
    failed_v1_ref=ref(p),wrapper_v2_ref=ref(__file__),failure='P2 missing application NI correctly failed closed with TypeError; test harness did not catch TypeError. Resume only identical existing unspent metadata/config, no simulator retry, no frozen Source or native engine mutation.',
    source_and_native_engine_unchanged=True,model_starts_in_failed_preparation=0,registry_writes_in_failed_preparation=0),True)
ns['main']()
