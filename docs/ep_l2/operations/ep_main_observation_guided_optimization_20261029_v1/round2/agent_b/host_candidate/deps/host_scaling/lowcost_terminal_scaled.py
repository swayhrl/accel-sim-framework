"""Copyable, pure HostQ supplement. Never writes/accepts/registers/starts science.
Frozen C2 validation and numeric body are retained. Only its private dependency
namespace receives bounded structure storage; all added fields are provenance.
"""
import hashlib,importlib.util,pathlib
P=pathlib.Path;ROOT=P(__file__).resolve().parent
PINS={'dynamic_observation_scaled.py': '4db737bf5bdc09532480e401001e39bc0de414c0b692c666542e8665a011ab25', 'rolling_structure_core.py': 'b8f09af83cf2eb50933b46216f825593eb218c2a304a61ec7a624fc22f3f2066', 'frozen_math/parse_main_terminal.py': 'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e', 'frozen_math/lowcost_terminal_v2.py': 'cba193d8ec810219f58bbe55870814b70604082f4f6683a236a418e80b9da35c', 'frozen_math/ft_lane5/validate.py': '08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500', 'frozen_math/ft_lane5/parse_unified_terminal.py': '536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b'}
CANONICAL_LEGACY_COMMON='/root/data/ep_l2_dtc_l1_native_v2/EP/control/parse_main_terminal.py'

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def verify_pins():
 for rel,digest in PINS.items():need(sha(ROOT/rel)==digest,'package dependency drift '+rel)
 return {rel:{'path':str(ROOT/rel),'sha256':digest}for rel,digest in PINS.items()}
def load(rel,name):
 need(rel in PINS and sha(ROOT/rel)==PINS[rel],'unbound package module')
 s=importlib.util.spec_from_file_location(name,ROOT/rel);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def frozen_c():
 c=load('frozen_math/lowcost_terminal_v2.py','isolated_frozen_C2')
 # Only filesystem locators are rebound to identicalbyte frozen copies. Their
 # fullSHA and extracted numericbody checks remain exactly the original ones.
 c.COMMON=ROOT/'frozen_math/parse_main_terminal.py';c.FT=ROOT/'frozen_math/ft_lane5'
 c.PINS={str(c.COMMON):PINS['frozen_math/parse_main_terminal.py'],str(c.FT/'parse_unified_terminal.py'):PINS['frozen_math/ft_lane5/parse_unified_terminal.py'],str(c.FT/'validate.py'):PINS['frozen_math/ft_lane5/validate.py']}
 return c

def numeric_math():
 verify_pins();c=frozen_c();parse,receipt=c.numeric_math();receipt=dict(receipt)
 rolling=load('rolling_structure_core.py','private_bounded_structure')
 def structure(raw,spec,final):
  value,census=rolling.parse_structure_with_receipt(raw,spec,final);receipt['structure_stream_census']=census;return value
 parse.__globals__['parse_structure']=structure
 receipt.update(structure_adapter_sha256=PINS['rolling_structure_core.py'],frozen_final_suffix_sha256=rolling.FINAL_SUFFIX_SHA,structure_storage='CURRENT_CLOCK_ONLY_WITH_WHOLE_LOG_CENSUS',new_earlier_contract=True)
 return parse,receipt

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 dependencies=verify_pins();c=frozen_c()
 # c is a newly loaded pure module instance; no frozen file, running process,
 # imported controller or first7 namespace is changed.
 c.numeric_math=numeric_math
 result=c.validate_case(raw,spec,qualification,sourceq_path,sourceq_sha)
 result['model']['source_map']['mechanism']['legacy_numeric_source_reference_only']=CANONICAL_LEGACY_COMMON
 census=result['math_binding']['structure_stream_census']
 need(census['raw_logical_sha256']==result['raw_logical_sha256']and census['raw_logical_bytes']==result['raw_uncompressed_bytes'],'whole raw census disagrees with frozen validator')
 need(census['raw_lines']==result['application']['raw_lines'],'whole raw line census disagrees')
 result['host_scaling_provenance']={'schema':'EP_FULL_PERF_HOST_SCALING_PROVENANCE_V1','entry_sha256':sha(__file__),'dependencies':dependencies,'frozen_C2_sha256':PINS['frozen_math/lowcost_terminal_v2.py'],'only_numeric_dependency_replacement':'parse.__globals__[parse_structure] in private namespace','frozen_math_suffix_sha256':rolling_suffix_sha(),'original_validation_fields_unchanged_except_declared_provenance':True,'science_granted':False,'raw_modified_or_population_dropped':False}
 need(result['scientific_acceptance_granted']is False,'pure validation may not grant science')
 return result

def rolling_suffix_sha():return load('rolling_structure_core.py','suffix_source_only').FINAL_SUFFIX_SHA
