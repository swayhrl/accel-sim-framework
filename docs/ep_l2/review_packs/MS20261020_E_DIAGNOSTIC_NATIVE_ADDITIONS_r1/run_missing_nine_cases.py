"""Nine previously unexecuted E cases for pending diagnostic/static qualifications."""
from pathlib import Path
import importlib.util,sys
sys.path.insert(0,"/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e")
import coordinator as c
source=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261020_E_INDEPENDENT_NATIVE_EXECUTION_r2/independent_native.py')
c.require(c.digest(source)=='9af9ce756ac51b8d1d13fc1bd9bff2c6568b5ca4cb282fc7edd2b94c4afa7377',"frozen E replay driver changed")
spec=importlib.util.spec_from_file_location("native_driver",source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.GATE_CASES={"pending_affected_diagnostic_and_static_cases":['S_COPY_FREE_local', 'S_L2_DATA_FREE_local', 'U_L2_DATA_FREE_local', 'S_COPY_FREE_ROP7', 'S_L2_DATA_FREE_ROP7', 'WV_data_free', 'F_data_free', 'reject_TVD_copy', 'static_WB64']}
r=m.execute(source.with_name("E_NATIVE_ADMISSION.json"),c.OUTPUT/"E_INDEPENDENT_DIAGNOSTICS_STATIC_r1")
print(r["status"],len(r["tests"]))
