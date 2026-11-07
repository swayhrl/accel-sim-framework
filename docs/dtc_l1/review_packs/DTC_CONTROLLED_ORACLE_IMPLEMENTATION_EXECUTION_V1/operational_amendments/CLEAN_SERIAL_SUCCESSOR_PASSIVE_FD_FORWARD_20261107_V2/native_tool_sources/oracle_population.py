"""New 271-option Oracle population supplement, old pure checks preserved."""
from pathlib import Path
import hashlib,json,re,shlex,types
P=Path;R=P(__file__).resolve().parents[1]
POP=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_strict_cap1m.py')
POP_SHA='87ee4025dce16a909a30c9e94a10dcaad14d3e71b3846371edd3be15a9b0bac5'
LEGACY=P('/root/data/ep_l2_dtc_l1_native_v2/DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6/ag6_strict.py')
LEGACY_SHA='9039c1d0df66210ad9c8fba325bc5e6d9ae10bd67981d7668c18a4576b81b3e4'
MODES={'OFF_MATCHED':0,'M_DATAREAD':1,'L2_DATAREAD':2,'L1_DATAREADY':3}
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def validate_spec(s,check_files=True):
 plan=read(R/'control/EXECUTION_PLAN.json');build=read(R/'control/BUILD_PROFILE.json')
 assert s['cell']=='DH' and s['oracle_mode']in MODES and s['oracle_mode_enum']==MODES[s['oracle_mode']]
 assert s['oracle_mode']=='OFF_MATCHED' or s['oracle_mode']in plan['qualified_modes']
 assert s['core_commit']==build['core_commit'] and s['framework_commit']==build['framework_commit']=='02775fd795cde5aae1480d81cee6eb481d0a08f4'
 assert s['binary_sha256']==build['binary_sha256'] and s['downstream_profile']=='P0'
 historical=read(s['historical_DH_P0_spec_path']);assert sha(s['historical_DH_P0_spec_path'])==s['historical_DH_P0_spec_sha256']
 old=historical['expected_options'];expected=dict(old,**{'-gpgpu_dtc_oracle_mode':[str(s['oracle_mode_enum'])]})
 assert len(old)==270 and len(expected)==271 and s['expected_options']==expected
 assert s['expected']==historical['expected'] and s['input_digest']==historical['input_digest']
 assert s['input_binding_sha256']==historical['input_binding_sha256'] and s['original_environment']==historical['original_environment']
 assert expected['-gpgpu_perfect_mem']==expected['-l2_ideal']==['0']
 assert expected['-gpgpu_dtc_l1_logical_sets']==['64'] and expected['-gpgpu_dtc_l1_logical_ways']==['8']
 assert expected['-gpgpu_dtc_l1_physical_lines']==['640'] and expected['-gpgpu_dtc_l1_oo_pib_entries']==['128']
 assert expected['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']
 if check_files:
  assert sha(s['input_binding_path'])==s['input_binding_sha256']
  assert [x['sha256']for x in s['configs'][:4]]==[x['sha256']for x in historical['configs']]
  assert len(s['configs'])==5,'EXACT_FROZEN_FOUR_PLUS_MODE_CONFIG_REQUIRED'
  for x in s['configs']:assert sha(x['path'])==x['sha256']
  tokens=shlex.split(P(s['configs'][-1]['path']).read_text(),comments=True)
  assert tokens==['-gpgpu_dtc_oracle_mode',str(s['oracle_mode_enum'])]
  for x in s['runtime_files']:assert sha(x['actual_realpath'])==x['sha256']
 return dict(status='VALID_CONTROLLED_ORACLE_SPEC_NO_EXECUTION_AUTHORITY',mode=s['oracle_mode'],input_digest=s['input_digest'],effective_options_count=271)

def population_from_verified_closed_text(raw,s,input_domain):
 validate_spec(s)
 assert sha(POP)==POP_SHA and sha(LEGACY)==LEGACY_SHA
 original=POP.read_text();anchor="len(s['expected_options'])==270";assert original.count(anchor)==1
 transformed=original.replace(anchor,"len(s['expected_options'])==271",1)
 assert transformed.replace("len(s['expected_options'])==271",anchor,1)==original
 population=types.ModuleType('ORACLE_POPULATION_271_PRIVATE');population.__file__=str(POP)
 exec(compile(transformed,str(POP)+':CONTROLLED_ORACLE_271','exec'),population.__dict__)
 legacy=load('ORACLE_UNCHANGED_PURE_LIFECYCLE_CHECKS',LEGACY)
 result=population.population(raw,s,input_domain,legacy)
 helper=load('ORACLE_COUNTER_SUPPLEMENT',R/'tools/oracle_runtime_contract.py')
 historical=read(s['historical_DH_P0_spec_path'])['expected_options']
 helper.verify_option_echo(raw,s['expected_options'],historical,s['oracle_mode'])
 blocks=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',raw,re.M));oracle=[]
 for i,match in enumerate(blocks):
  block=raw[match.start():blocks[i+1].start()if i+1<len(blocks)else len(raw)]
  counters=helper.oracle_counter_terminal(block,s['oracle_mode'],False);flat=legacy.numeric(block)
  enq=counters['L1']['events_enqueued']
  assert flat['DTC_L1_oo_new_misses']==flat['DTC_L1_oo_lower_created']+enq,'ORACLE_NEW_MISS_REAL_OR_VIRTUAL_CONSERVATION'
  oracle.append(dict(ordinal=i+1,kernel=match[1],**counters))
 result=dict(result,effective_options=s['expected_options'],oracle_mode=s['oracle_mode'],oracle_kernel_counters=oracle,
             actual_mechanism_exposure=oracle[-1]['exposure'])
 return result,dict(original_population_source_path=str(POP),original_population_source_sha256=POP_SHA,
                    unchanged_legacy_source_path=str(LEGACY),unchanged_legacy_source_sha256=LEGACY_SHA,
                    transformed_population_source_sha256=hashlib.sha256(transformed.encode()).hexdigest(),
                    exact_edit='270 full option count ->271; all original ordered-input/lifecycle/ref/PIB/physical/finite/credit/traffic checks retained',
                    supplemental_Oracle_counter_source_sha256=sha(R/'tools/oracle_runtime_contract.py'))
