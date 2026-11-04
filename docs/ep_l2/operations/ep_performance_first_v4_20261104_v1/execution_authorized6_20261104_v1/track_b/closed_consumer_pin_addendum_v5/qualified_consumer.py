"""CPU-only exact one-pin compatibility supplement. No original files or authority writes."""
from pathlib import Path
import hashlib,importlib.util
ROOT=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_b/private_runtime')
PARSER_SHA='dc454107fd80ef2966abfed9d95c7bf0fc6ed23cad76ca26b79653ff0ee3fba1'
OLD_MC_SHA='9e43b1f218124e5b4a83f385482b7bef15754f0ef12539ac4f452a326b2d52d0'
QUALIFIED_MC_SHA='6a129f4c8682b4a5174ee29a9142979b506e18873491d0d6ff213bc7788a857f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def configured():
 p=ROOT/'mode_aware_terminal.py'
 if sha(p)!=PARSER_SHA or sha(ROOT/'mode_contract.py')!=QUALIFIED_MC_SHA:raise ValueError('exact qualified consumer dependency drift')
 sp=importlib.util.spec_from_file_location('unchanged_parser_under_exact_qualified_MC_pin',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 if m.PINS['mode_contract.py']!=OLD_MC_SHA:raise ValueError('unexpected parser base pin')
 m.PINS=dict(m.PINS,**{'mode_contract.py':QUALIFIED_MC_SHA})
 return m
def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 if spec['cohort']not in ['EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1','EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1']:raise ValueError('outside exact two-cohort consumer supplement')
 expected=dict(path=str(ROOT/'mode_contract.py'),sha256=QUALIFIED_MC_SHA)
 if spec['mode_contract_ref']!=expected or qualification['mode_contract_ref']!=expected:raise ValueError('consumer MC not exact Spec/NativeQ binding')
 result=configured().validate_case(raw,spec,qualification,sourceq_path,sourceq_sha)
 result['consumer_pin_compatibility_supplement']=dict(original_parser_sha256=PARSER_SHA,old_embedded_MC_pin=OLD_MC_SHA,Spec_and_NativeQ_bound_MC_pin=QUALIFIED_MC_SHA,module_object_only=True,numeric_math_or_raw_changes=False,scientific_acceptance_granted=False)
 return result
