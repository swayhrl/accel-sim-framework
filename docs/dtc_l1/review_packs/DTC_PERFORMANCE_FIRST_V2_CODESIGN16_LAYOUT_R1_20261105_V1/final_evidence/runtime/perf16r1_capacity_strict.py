"""V2 CPU-qualified combo shape/legacy strict-capacity adapter. No execution authority."""
from pathlib import Path
import json,hashlib,types,shlex
P=Path
AUTH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/control/INPUT_AUTHORITY.fixed.json')
AUTH_SHA='0b9cd6dfe3c397e32ce286ef068717ac4dd563b65855dd245a4fceb08fdadfa1'
CORE='9eedb3131937748f0492fa83aad37d3691118d70';FRAMEWORK='02775fd795cde5aae1480d81cee6eb481d0a08f4'
BINARY='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d';CUDART='694f05ce97fe3e1552d94803c2202d8d037769c61624cde5f6a832622ed60c56'
LEGACY_PATH=P('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
LEGACY_SHA='9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
ANCHOR='0 <= value("oo_physical_allocated") <= 640 * 64, "physical_640_per_SM_capacity"'
COMMON=['546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa','e86d9ac278c389e5d641368624e4a7322263edad46f999d1bfeac45e2c08ac6a','19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e']
PROFILES={'PHYS768_OOPIB192_TAG64x8':dict(physical=768,config_sha=COMMON+['a8c1cbaf963d7f90b90583a0c55f2c8c6d00da4d77b8d8c19f909d7795143178']),'PHYS1024_OOPIB192_TAG64x8':dict(physical=1024,config_sha=COMMON+['a044187514252ec4220d45919aa9d5a18cca6de03faf2bf6cb681078b28d2841'])}
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def jsonsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def baseline(program,digest):
 assert sha(AUTH)==AUTH_SHA
 auth=json.loads(AUTH.read_bytes());found=[inp for inp in auth['inputs']if inp['population']['program']==program and inp['population']['input_digest']==digest];assert len(found)==1,'FIXED8_FULL_INPUT_IDENTITY_REQUIRED'
 ref=next(r for r in found[0]['P0_references']if r['source_cell']=='DH');assert ref['accepted']is True and sha(ref['source_RESULT_path'])==ref['source_RESULT_sha256']
 return ref

def supplied_options(paths):
 out={}
 for p in paths:
  tokens=[word for token in shlex.split(P(p).read_text(),comments=True)for word in token.split()];key=None
  for token in tokens:
   if token.startswith('-')and len(token)>1 and token[1].isalpha():key=token;out[key]=[]
   else:assert key is not None;out[key].append(token)
 return out

def validate_spec(spec,check_files=True):
 profile=spec['profile'];assert profile in PROFILES,'COMBO_PROFILE_ONLY_NOT_V1_SINGLE_OR_NEW_TAG_MECHANISM';assert spec.get('structure_variant',profile)==profile and spec['cell']=='DH'and spec['downstream_profile']=='P0'
 ref=baseline(spec['program'],spec['input_digest']);shape=PROFILES[profile];physical=shape['physical'];expect=dict(ref['effective_options']);expect['-gpgpu_dtc_l1_physical_lines']=[str(physical)];expect['-gpgpu_dtc_l1_oo_pib_entries']=['192']
 actual=spec['expected_options']if'expected_options'in spec else spec['expected_effective_options']
 if'expected_options'in spec and'expected_effective_options'in spec:assert spec['expected_options']==spec['expected_effective_options']
 assert len(actual)==270 and actual==expect,'EXACT_270_DH_P0_PLUS_TWO_FLAGS_ONLY'
 assert spec['expected']==ref['expected']and spec['core_commit']==CORE and spec['framework_commit']==FRAMEWORK and spec['binary_sha256']==BINARY
 assert any(x['sha256']==CUDART and x['actual_realpath'].endswith('/core-build/libcudart.so')for x in spec['runtime_files']),'FROZEN_CUDART_IDENTITY_REQUIRED'
 binding=spec['input_binding']if'input_binding'in spec else dict(path=spec['input_binding_path'],sha256=spec['input_binding_sha256']);assert binding['sha256']==ref['input_binding']['sha256']
 assert len(spec['configs'])==4 and [x['sha256']for x in spec['configs']]==shape['config_sha']
 if check_files:
  assert sha(binding['path'])==binding['sha256']
  for x in spec['configs']:assert sha(x['path'])==x['sha256']
  parsed=supplied_options([x['path']for x in spec['configs']]);assert all(expect.get(k)==v for k,v in parsed.items()),'ACTUAL_CONFIG_BYTES_NOT_EFFECTIVE_TWO_FLAG_VARIANT'
  for x in spec['runtime_files']:assert sha(x['actual_realpath'])==x['sha256']
 return dict(status='VALID_COMBO_CONFIGURATION_NO_EXECUTION_AUTHORITY',profile=profile,physical_lines_per_SM=physical,OO_PIB_entries=192,effective_lower_create_queue_bound=192,SMs=64,terminal_allocated_gauge_bound=physical*64,expected_270_options_sha256=jsonsha(actual),input_digest=spec['input_digest'],program=spec['program'],baseline_DH_RESULT_path=ref['source_RESULT_path'],baseline_DH_RESULT_sha256=ref['source_RESULT_sha256'],model_starts=0,scientific_registration_granted=False)

def transformed_source(spec):
 shape=validate_spec(spec);raw=LEGACY_PATH.read_bytes();assert hashlib.sha256(raw).hexdigest()==LEGACY_SHA;anchor=ANCHOR.encode();assert raw.count(anchor)==1
 replacement=('0 <= value("oo_physical_allocated") <= '+str(shape['physical_lines_per_SM'])+' * 64, "physical_'+str(shape['physical_lines_per_SM'])+'_per_SM_capacity"').encode();new=raw.replace(anchor,replacement,1);assert new.replace(replacement,anchor,1)==raw
 binding=dict(shape,legacy_source_path=str(LEGACY_PATH),legacy_source_sha256=LEGACY_SHA,transformed_source_sha256=hashlib.sha256(new).hexdigest(),replacement_count=1,all_other_legacy_parser_bytes_unchanged=True,only_terminal_allocation_gauge_changed=True,not_peak_occupancy_or_functional_value_proof=True,old_population_270_echo_and_lifecycle_conservation_must_be_called=True)
 return new,binding

def load_for(spec):
 text,binding=transformed_source(spec);m=types.ModuleType('DTC_V2_COMBO_PRIVATE_CONFIG_BOUND_LEGACY_STRICT');m.__file__=str(LEGACY_PATH);exec(compile(text,str(LEGACY_PATH)+':V2_COMBO_CAPACITY','exec'),m.__dict__);return m,binding


POPULATION_PATH=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_strict_cap1m.py')
POPULATION_SHA='87ee4025dce16a909a30c9e94a10dcaad14d3e71b3846371edd3be15a9b0bac5'
def population_from_verified_closed_text(raw_text,spec,input_domain):
 """Future wrapper must first verify actual grant/UUID/DONE/nonlive/raw identity.
 This pure reader never establishes native execution authority or closedness.
 Do not call the historical AG6 top-level AE/AD science entrypoint, whose
 fixed128/640 guard is intentionally preserved in the original source.
 """
 validate_spec(spec);assert sha(POPULATION_PATH)==POPULATION_SHA
 original=types.ModuleType('DTC_V2_COMBO_PRIVATE_EXISTING_POPULATION_COMPARATOR');original.__file__=str(POPULATION_PATH);exec(compile(POPULATION_PATH.read_bytes(),str(POPULATION_PATH),'exec'),original.__dict__)
 legacy,binding=load_for(spec);expected=spec['expected_options']if'expected_options'in spec else spec['expected_effective_options'];canonical=dict(spec,expected_options=expected);result=original.population(raw_text,canonical,input_domain,legacy)
 # The unchanged pure population reader verifies all270 actual echo values
 # before returning, but its result schema omits this field. Add the already
 # validated vector here; do not pretend the old reader returned it.
 result=dict(result,effective_options=expected)
 return result,binding
