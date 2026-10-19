"""One missing full-combination observer-ON actual native equivalence case."""
from pathlib import Path
import importlib.util,sys
sys.path.insert(0,"/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e")
import coordinator as c
source=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261020_E_INDEPENDENT_NATIVE_EXECUTION_r2/independent_native.py')
c.require(c.digest(source)=='9af9ce756ac51b8d1d13fc1bd9bff2c6568b5ca4cb282fc7edd2b94c4afa7377',"frozen E replay driver changed")
spec=importlib.util.spec_from_file_location("native_driver",source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.GATE_CASES={"full_combination_observer_equivalence":["combined_same_address_observer"]}
r=m.execute(source.with_name("E_NATIVE_ADMISSION.json"),c.OUTPUT/"E_INDEPENDENT_FULL_OBSERVER_ON_r1")
print(r["status"],len(r["tests"]))
