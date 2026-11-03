"""Fail-closed pure retention candidate checks; no actor/import/native/ledger writes."""
import copy,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
PINS_SHA='019c67387518b327536506713a514561526ed461cd23895a95c89d82a64af08f'
MODES={'WV_CLEAN_ONLY':('1','0','RETENTION_CLEAN_ONLY'),'WV_DIRTY_ONLY':('0','1','RETENTION_DIRTY_ONLY')}
KEYS={'schema','program','mode','source_identity','input_identity_sha256','geometry','profile','expected_effective_options','observer_env','matched_S_anchor_qualification_ref','ro_qualification_ref','M','T','numeric_profile','option_pack_ref'}
def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(p):
 def unique(pairs):
  obj={}
  for k,v in pairs:need(k not in obj,'duplicate JSON field');obj[k]=v
  return obj
 return json.loads(pathlib.Path(p).read_bytes(),object_pairs_hook=unique,parse_constant=lambda _:need(False,'nonfinite JSON'))
def exact(ref):
 need(type(ref) is dict and set(ref)>={'path','sha256'} and sha(ref['path'])==ref['sha256'],'immutable reference changed');return read(ref['path'])
def pins():
 need(sha(ROOT/'OPTION_PACK_PINS.json')==PINS_SHA,'pin manifest drift');return read(ROOT/'OPTION_PACK_PINS.json')
def build_candidate(key):
 ps=pins();need(key in ps,'unknown exact input/class');r=ps[key];p=exact(r);b=exact(p['ordered_kernel_and_input_base_ref'])
 return dict(schema='EP_PURE_HOST_RETENTION_CANDIDATE_V1',program=p['program'],mode=p['mode_candidate'],source_identity=p['source_identity'],input_identity_sha256=p['input_identity_sha256'],geometry=p['geometry'],profile=b['profile'],expected_effective_options=p['expected_effective_options'],observer_env=b['observer_env'],matched_S_anchor_qualification_ref=b['matched_S_anchor_qualification_ref'],ro_qualification_ref=None,M=False,T=False,numeric_profile=MODES[p['mode_candidate']][2],option_pack_ref=r)
def check_candidate(s,*,candidate_enabled=False):
 need(candidate_enabled is True,'candidate checks are disabled by default; no native authority')
 need(type(s) is dict and set(s)==KEYS,'candidate schema fields differ');need(s['schema']=='EP_PURE_HOST_RETENTION_CANDIDATE_V1','candidate schema')
 need(s['mode'] in MODES,'unknown retention mode; no fallback');key=s['program']+'_'+s['mode'].replace('WV_','');ps=pins();need(key in ps and s['option_pack_ref']==ps[key],'unapproved exact program/input/pack')
 p=exact(ps[key]);b=exact(p['ordered_kernel_and_input_base_ref']);expected=build_candidate(key)
 for k in KEYS-{'expected_effective_options'}:need(s[k]==expected[k],'changed binding:'+k)
 need(type(s['M']) is bool and type(s['T']) is bool and not s['M'] and not s['T'],'typed M/T disabled')
 o=s['expected_effective_options'];need(type(o) is dict and len(o)==282 and all(type(k) is str and type(v) is str for k,v in o.items()),'exact282 typed strings');need(o==p['expected_effective_options'],'undeclared effective option delta')
 need(s['ro_qualification_ref'] is None,'RO certificate authority forbidden')
 c,d,prof=MODES[s['mode']];need((o['-gpgpu_ep_l2_ft_mode'],o['-gpgpu_ep_l2_tvd_clean'],o['-gpgpu_ep_l2_tvd_dirty'],o['-gpgpu_ep_l2_ro_line_mshr_bypass'],o['-gpgpu_ep_l2_ro_tag_detach'])==('2',c,d,'0','0'),'wrong five flags')
 q=exact(s['matched_S_anchor_qualification_ref']);a=exact(q['spec_ref']);point=exact(q['point_ref'])
 need(q['status']=='EXACT_EXISTING_S_HARDWARE_INPUT_OBSERVERS_QUALIFIED_FOR_MATCHED_REFERENCE' and q.get('approved_by')=='EP-MAIN','missing exact Main S review')
 need(q.get('current_closed_state')=='CLOSED_ACCEPTED' and q.get('currently_accepted_population') is True,'frozen S review not accepted')
 need(a['mode']==point['mode']=='S' and point['hardware_drained'] is True and point['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED','S anchor type/drain')
 need(a['source_identity']==point['source_identity']==s['source_identity'] and a['input_identity_sha256']==point['input_identity_sha256']==s['input_identity_sha256'],'S identity mismatch')
 need(a['geometry']==s['geometry'] and a['observer_env']==s['observer_env'],'S hardware/observer mismatch')
 permitted=dict(a['expected_effective_options']);permitted.update({'-gpgpu_ep_l2_ft_mode':'2','-gpgpu_ep_l2_tvd_clean':c,'-gpgpu_ep_l2_tvd_dirty':d})
 need(permitted==o,'not same S background plus exact mode switches')
 return dict(status='PURE_HOST_RETENTION_CANDIDATE_PASS_NOT_NATIVE_OR_APPLICATION',mode=s['mode'],numeric_profile=prof,numeric_parser_status='NOT_IMPLEMENTED_RETENTION_PROFILE',RO_applicability='NOT_APPLICABLE_RO_RUNTIME_DISABLED',TVD_summary_required=True,RO_summary_required=False,scientific_acceptance_granted=False,launch_permission=False,native_qualified=False)
