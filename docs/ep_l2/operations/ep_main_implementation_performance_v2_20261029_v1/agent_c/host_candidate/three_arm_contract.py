"""Pure 16x8 three-arm preflight candidate. No launcher, registry writer or authority."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
CORRECTION='-gpgpu_ep_l2_ordinary_ro_tag_relief'
T='-gpgpu_ep_l2_ro_tag_detach'
SOURCE_KEYS={'core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256','archive_sha256'}
MODES={'F_MINUS_T':('0','0'),'LEGACY_F':('1','0'),'CORRECTED_F':('1','1')}
HEAVY={'EPL2_DETACH_DIAG':'0','EPL2_TAGPRESSURE_DIAG':'0','EPL2_TAG_LIFETIME':'0','EP_L2_EVENT_TIMELINE':'0','EPL2_LIFE_WIRE':'SUMMARY_STAGE'}
OLD_REQUEST='EP_L2_FULL_WORKLOAD_PERFORMANCE_POTENTIAL_EXPLORATION_V1'
INPUT='438eefd67b073f1ca0e2c08be6aa99b3b9b9619d7832cc6cad9cc4467e63654e'
def need(ok,message):
 if not ok:raise ValueError(message)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):
 def pairs(items):
  value={}
  for k,v in items:need(k not in value,'duplicate field');value[k]=v
  return value
 return json.loads(pathlib.Path(path).read_text(),object_pairs_hook=pairs,parse_constant=lambda v:need(False,'nonfinite'))
def parent():return read(ROOT/'LEGACY_PARENT_BACKGROUND.json')
def validate_source(s,seal):
 sid=s['source_identity'];need(set(sid)==SOURCE_KEYS,'Source5 fields')
 need(all(type(v)is str and len(v)==(40 if k.endswith('commit')else 64)and all(c in '0123456789abcdef'for c in v)for k,v in sid.items()),'unfrozen/non-SHA Source5')
 need(sid['core_source_commit']!=parent()['source_identity']['core_source_commit'] and sid['binary_sha256']!=parent()['source_identity']['binary_sha256'],'old Core/ELF not new correction Source')
 need(seal.get('status')=='MAIN_REVIEWED_EXACT_NEW_SOURCE_AND_MODES_CPU_ONLY'and seal.get('approved_by')=='EP-MAIN','Main newSource seal missing')
 need(seal.get('source_identity')==sid and seal.get('geometry')==s['geometry']and seal.get('modes_qualified')==sorted(MODES),'newSource mode/geometry mismatch')
 need(seal.get('application_acceptance_inherited')is False and seal.get('source_keep')is True,'no inherited app/source loss')
 need(seal.get('full_effective_option_keys')==sorted(s['expected_effective_options']),'newSource actual option echo keyset')
def validate_background(s):
 p=parent();mode=s['mode'];need(mode in MODES,'unknown three-arm mode');need(s['geometry']==p['geometry']==dict(slices=64,sets=16,ways=8,line_bytes=128),'exact16x8 only')
 need(s.get('M')is True and s.get('T')is (mode!='F_MINUS_T'),'typed M/T flags')
 need(s.get('ordinary_ro_tag_relief')is(mode=='CORRECTED_F'),'typed correction flag')
 need(s['input_identity_sha256']==INPUT and s['trace_entry']==p['trace_entry'],'exact input/trace identity')
 o=s['expected_effective_options'];base=p['expected_effective_options'];need(type(o)is dict and len(o)==283 and set(o)==set(base)|{CORRECTION},'old282 + one283 exact keys')
 need(all(type(k)is str and type(v)is str for k,v in o.items()),'effective strings')
 for k,v in base.items():
  if k!=T:need(o[k]==v,'undeclared hardware/background/input option:'+k)
 need((o[T],o[CORRECTION])==MODES[mode],'mode/correction option mismatch')
 need(s['observer_env']==HEAVY,'exact original FOUR_OFF + SUMMARY_STAGE; no inherited ON NI')
 need(s.get('old_application_acceptance_inherited')is False,'newELF must not inherit accepted app')
 need(s.get('source_keep')is True and s.get('automatic_retry')is False and s.get('refund')is False,'one-start Source KEEP')
 return dict(mode=mode,option_count=283,old_option_count=282,hardware_delta={},scientific_acceptance_granted=False,launch_permission=False)
def validate_ro(s,q):
 need(q.get('status')=='MAIN_REVIEWED_EXACT_NEW_SOURCE_RO_LOADER_INPUT_BINDING'and q.get('approved_by')=='EP-MAIN','newSource ROloader qualification missing')
 need(q.get('source_identity')==s['source_identity']and q.get('input_identity_sha256')==INPUT,'RO Source/input')
 need(q.get('epoch')=='whole_commandlist'and q.get('line_bytes')==128 and q.get('address_domain')=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','RO scope')
 for kind in ['manifest','ranges']:
  r=q[kind+'_ref'];path=pathlib.Path(r['path']);need(hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'],'RO bytes drift')
  need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind]==r['path']and s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind+'_sha256']==r['sha256'],'ROactual binding')
 need(s['expected_effective_options']['-gpgpu_ep_l2_ro_scope']=='TRACE_MODEL_CLOSED_WORLD','RO loader scope')
def validate_cpu_scope(s,q):
 need(q.get('status')=='MAIN_REVIEWED_NEW_SOURCE_16X8_THREE_ARM_PRODUCTION_CPU_PASS'and q.get('approved_by')=='EP-MAIN','actual newSource modeCPU qualification required')
 need(q.get('source_identity')==s['source_identity']and q.get('geometry')==s['geometry']and s['mode']in q.get('modes',[]),'modeCPU Source/geometry/mode')
 need(q.get('old_source78_cpu_inherited')is False and q.get('application_permission')is False,'oldCPU/application conflation')
 need(set(q.get('passed_controls',[]))>={'legacy_default_off','M1T0','legacy_M1T1','corrected_M1T1','sector_late_fill_generation','resources_negative','repeated_preview_and_drain'},'newCPU controls incomplete')
def preflight(s,source_seal,ro_seal,cpu_seal):
 b=validate_background(s);validate_source(s,source_seal);validate_ro(s,ro_seal);validate_cpu_scope(s,cpu_seal);return b

def validate_triplet(specs):
 need(len(specs)==3 and {s['mode']for s in specs}==set(MODES),'complete unique3 arms')
 for s in specs:validate_background(s)
 ref=specs[0]
 for s in specs[1:]:
  need(s['source_identity']==ref['source_identity'],'crossSource/ELF arms')
  for key in ['input_identity_sha256','trace_entry','geometry','observer_env','science_request_id']:
   need(s[key]==ref[key],'crossarm '+key)
  delta={k for k,v in s['expected_effective_options'].items()if v!=ref['expected_effective_options'][k]}
  need(delta<={T,CORRECTION},'crossarm undeclared effective delta')
 return dict(contrasts={'B/A':'speedup=cycles_A/cycles_B; Legacy T only','C/B':'correction policy plus charged lookup cost','C/A':'corrected full T'},old_F_reusable=False,launch_permission=False)

def validate_fresh_authority(s,request):
 """Read-only exact-request check; mock tests cannot grant real launcher rights."""
 rid=s.get('science_request_id');need(type(rid)is str and rid and rid!=OLD_REQUEST,'fresh separate T request id required')
 need(request.get('science_request_id')==rid and request.get('approved_by')=='USER_EXACT_START_AUTHORIZATION','no exact scoped authorization')
 need(request.get('source_identity')==s['source_identity']and request.get('automatic_retry')is False,'authorization Source/retry')
 need(type(request.get('budget'))is int and request['budget']==len(request['admitted_specs'])and request['remaining']==request['budget']-len(request['consumed']),'fresh arithmetic')
 need(s['cohort']in request['admitted_specs']and request['admitted_specs'][s['cohort']]==digest(s),'unregistered exact spec')
 need(s['cohort']not in request['consumed']and request['remaining']>0,'spent/no starts')
 return dict(read_only_check=True,launch_permission=False,consume_required_by_Main_sole_entry=True)
