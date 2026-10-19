"""Only two missing observer-ON production cases; no repeat of E40 or app starts."""
from pathlib import Path
import importlib.util
import sys
sys.path.insert(0,"/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e")
from coordinator import digest,require
SOURCE=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261020_E_INDEPENDENT_NATIVE_EXECUTION_r2/independent_native.py')
require(digest(SOURCE)=='9af9ce756ac51b8d1d13fc1bd9bff2c6568b5ca4cb282fc7edd2b94c4afa7377',"frozen native driver changed")
spec=importlib.util.spec_from_file_location("frozen_e_native",SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.GATE_CASES={"observer_on_equivalence":["S_observer1","U_observer1"]}
r=m.execute(Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261020_E_INDEPENDENT_NATIVE_EXECUTION_r2/E_NATIVE_ADMISSION.json'),Path('/workspace/ep_l2_ms20261019_e_results/E_INDEPENDENT_OBSERVER_ON_SCOPE_r1'))
print(r["status"],len(r["tests"]))
