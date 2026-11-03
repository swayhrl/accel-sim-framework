"""Pure, fail-closed six-cell DRAM family engineering contract.
No process, ledger, native-entry, environment, acceptance or source mutations.
The explicit engineering_enabled flag is NOT scientific launch authorization.
"""
import copy,hashlib,json
from pathlib import Path
class FamilyContractError(ValueError):pass
def need(ok,message):
 if not ok: raise FamilyContractError(message)
def load_exact(ref):
 need(type(ref)is dict and type(ref.get('path'))is str and type(ref.get('sha256'))is str,'invalid immutable reference')
 p=Path(ref['path'])
 try:data=p.read_bytes()
 except OSError as e:raise FamilyContractError('immutable reference unavailable') from e
 need(hashlib.sha256(data).hexdigest()==ref['sha256'],'immutable reference SHA mismatch')
 def unique(items):
  out={}
  for k,v in items:
   need(k not in out,'duplicate JSON key');out[k]=v
  return out
 try:return json.loads(data,object_pairs_hook=unique,parse_constant=lambda _:need(False,'nonfinite JSON'))
 except (UnicodeError,json.JSONDecodeError) as e:raise FamilyContractError('invalid immutable JSON') from e
SOURCE78 = {'archive_sha256': 'e5a743a2bb796d82f58109251f43d5c1997d5c1f7fdeac61213416da3835b697', 'binary_sha256': '78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a', 'core_source_commit': '78f4b59e865b136eede74df74c44c210f5b4ca04', 'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7', 'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'}
ALLOWLIST = {'PF_FWT_S_DRAM1020.0': {'reference_spec': {'bytes': 32685, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_FASTWALSHTRANSFORM_FC3A9062_S_REF_V1/control/FROZEN_SPEC.json', 'sha256': '893ede5568187939839478cc38f7a191bfd483b9289b1ee092e9bc2bbd8f14b6'}, 'mode': 'S', 'profile': 'PF_DCLK_FWT_1020', 'workload': 'FWT', 'clock': '1132.0:1132.0:1132.0:1020.0', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e'}, 'PF_FWT_WV_ZERO_RO_DRAM1020.0': {'reference_spec': {'bytes': 32757, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1/control/FROZEN_SPEC.json', 'sha256': 'bc9b320dd93dada542d5a4d9c2f4daae7a1b4e50899eb83ee124e855a5fc4c1b'}, 'mode': 'WV_ZERO_RO', 'profile': 'PF_DCLK_FWT_1020', 'workload': 'FWT', 'clock': '1132.0:1132.0:1132.0:1020.0', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e'}, 'PF_GEMM_S_DRAM1020.0': {'reference_spec': {'bytes': 25250, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GEMM_140F6ED3_S_REF_V1/control/FROZEN_SPEC.json', 'sha256': '506342de800727af72a367cece1ffdadcf1ac8b5725d6cbbd33ffa94e7a5c227'}, 'mode': 'S', 'profile': 'PF_DCLK_GEMM_1020', 'workload': 'GEMM', 'clock': '1132.0:1132.0:1132.0:1020.0', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b'}, 'PF_GEMM_WV_ZERO_RO_DRAM1020.0': {'reference_spec': {'bytes': 25322, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1/control/FROZEN_SPEC.json', 'sha256': '647b026041961f216d1f7d1581d6b654b5495ad0fdd941d1b03f46e7d3c47b24'}, 'mode': 'WV_ZERO_RO', 'profile': 'PF_DCLK_GEMM_1020', 'workload': 'GEMM', 'clock': '1132.0:1132.0:1132.0:1020.0', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b'}, 'PF_VECTOR4M_S_DRAM1275.0': {'reference_spec': {'bytes': 20830, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR4M_S_REF_V1/control/FROZEN_SPEC.json', 'sha256': '8a2ed7f554adc2f771c807d2e66cb26a8424e1fc21a672640b7a54af12097689'}, 'mode': 'S', 'profile': 'PF_DCLK_VECTOR4M_1275', 'workload': 'VECTOR4M', 'clock': '1132.0:1132.0:1132.0:1275.0', 'input_identity_sha256': 'ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc'}, 'PF_VECTOR4M_F_DRAM1275.0': {'reference_spec': {'bytes': 21133, 'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/cases/EP_PERF_VECTOR4M_F_REF_V1/control/FROZEN_SPEC.json', 'sha256': 'fd8d7f1478b1591cbd6c1436e18e9c47d3a304e6c97c9881adf166dacb8bb6c3'}, 'mode': 'F', 'profile': 'PF_DCLK_VECTOR4M_1275', 'workload': 'VECTOR4M', 'clock': '1132.0:1132.0:1132.0:1275.0', 'input_identity_sha256': 'ddf26d4f6b4b672de3c5f6d1ab633cc44d3d9ef8023b87ae9a10760f3f4057dc'}}
FIVE_FLAGS={'-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass'}
RO_OPTIONS={'-gpgpu_ep_l2_ro_manifest','-gpgpu_ep_l2_ro_manifest_sha256','-gpgpu_ep_l2_ro_ranges','-gpgpu_ep_l2_ro_ranges_sha256','-gpgpu_ep_l2_ro_scope'}
MODE_FLAGS={'S':('1','0','0','0','0'),'WV_ZERO_RO':('2','1','1','0','0'),'F':('2','1','1','1','1')}
FLAG_ORDER=['-gpgpu_ep_l2_ft_mode','-gpgpu_ep_l2_tvd_clean','-gpgpu_ep_l2_tvd_dirty','-gpgpu_ep_l2_ro_tag_detach','-gpgpu_ep_l2_ro_line_mshr_bypass']
def validate_candidate(candidate,*,engineering_enabled=False):
 need(engineering_enabled is True,'family engineering gate default OFF')
 need(type(candidate)is dict,'candidate must be object')
 key=candidate.get('performance_first_family_contract_id');need(key in ALLOWLIST,'candidate not in exact six-cell family')
 rule=ALLOWLIST[key];need(candidate.get('performance_first_reference_spec')==rule['reference_spec'],'reference binding mismatch')
 need(candidate.get('cohort')==key.replace('.','_'),'candidate cohort mismatch')
 base=load_exact(rule['reference_spec'])
 need(base['source_identity']==SOURCE78,'reference Source78 drift')
 need(candidate.get('source_identity')==SOURCE78,'candidate Source5 mismatch')
 for f in ['binary_path','static_library_path','source_worktrees','input_identity_sha256','input_binding_ref','all_unique_kernel_members','ordered_configs','trace_entry','geometry','observer_env','ro_qualification_ref','M','T','program','command_count','expected_CTA','expected_instructions','expected_kernel_launches','expected_kernel_scopes','source_keep','limits']:
  need(candidate.get(f)==base.get(f),'reference field mismatch: '+f)
 need(type(candidate.get('M'))is bool and type(candidate.get('T'))is bool,'M/T typed bool required')
 need(candidate['input_identity_sha256']==rule['input_identity_sha256'],'input allowlist mismatch')
 need(candidate.get('mode')==rule['mode'],'mode allowlist mismatch')
 need(candidate.get('profile')==rule['profile'],'profile allowlist mismatch')
 need(candidate.get('engineering_candidate_only')is True and candidate.get('science_launch_permission')is False,'candidate may not claim launch permission')
 need(candidate['geometry']==dict(slices=64,sets=32,ways=8,line_bytes=128),'Tag geometry mismatch')
 o=candidate.get('expected_effective_options');need(type(o)is dict and len(o)==282,'exact282 required')
 need(all(type(k)is str and type(v)is str for k,v in o.items()),'option keys/values must be strings')
 expected=copy.deepcopy(base['expected_effective_options']);expected['-gpgpu_clock_domains']=rule['clock']
 need(o==expected,'non-clock effective option delta or wrong clock')
 need([o[k] for k in FLAG_ORDER]==list(MODE_FLAGS[candidate['mode']]),'formal mechanism flags mismatch')
 load_exact(candidate['input_binding_ref'])
 ro=candidate['mode']=='F'
 if ro:
  q=load_exact(candidate['ro_qualification_ref'])
  need(q.get('status')=='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED' and q.get('qualified_by')=='Main','RO qualification status')
  need(q.get('source_identity')==SOURCE78 and q.get('input_identity_sha256')==candidate['input_identity_sha256'],'RO source/input mismatch')
  need(q.get('epoch')=='whole_commandlist' and q.get('line_bytes')==128 and q.get('address_domain')=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS','RO scope mismatch')
  for name in ['manifest','ranges']:
   r=q[name+'_ref'];load_exact(r) if name=='manifest' else need(hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'],'RO range SHA mismatch')
   need(o['-gpgpu_ep_l2_ro_'+name]==r['path'] and o['-gpgpu_ep_l2_ro_'+name+'_sha256']==r['sha256'],'RO effective option mismatch')
 else:need(candidate.get('ro_qualification_ref')is None,'ROdisabled candidate cannot inherit certificate')
 return dict(status='PURE_HOST_FAMILY_ENGINEERING_CHECK_PASS_NOT_APPLICATION_QUALIFICATION',id=key,workload=rule['workload'],mode=rule['mode'],profile=rule['profile'],clock=rule['clock'],source_identity=SOURCE78,input_identity_sha256=rule['input_identity_sha256'],scientific_launch_permission=False,application_acceptance=False)
def validate_pair(candidates,*,engineering_enabled=False):
 need(type(candidates)is list and len(candidates)==2,'exact S/EP pair required')
 receipts=[validate_candidate(c,engineering_enabled=engineering_enabled) for c in candidates]
 need(len({r['workload'] for r in receipts})==1,'pair different input workload')
 need(len({r['input_identity_sha256'] for r in receipts})==1,'pair different input identity')
 need(len({r['clock'] for r in receipts})==1,'pair different hardware clock')
 need(len({r['profile'] for r in receipts})==1,'pair different family profile')
 modes={r['mode'] for r in receipts};need(modes==({'S','F'}if receipts[0]['workload']=='VECTOR4M'else{'S','WV_ZERO_RO'}),'pair must contain exact S and EP modes')
 # Only historical formal five switches and closed-world RO binding may differ.
 a,b=[c['expected_effective_options'] for c in candidates]
 need({k:v for k,v in a.items() if k not in FIVE_FLAGS|RO_OPTIONS}=={k:v for k,v in b.items() if k not in FIVE_FLAGS|RO_OPTIONS},'pair hardware or input option mismatch')
 return dict(status='PURE_HOST_FAIR_PAIR_PASS_NOT_SCIENTIFIC_ACCEPTANCE',receipts=receipts,scientific_launch_permission=False)
def validate_packet(candidates,*,engineering_enabled=False):
 need(type(candidates)is list and len(candidates)==6,'exact six-cell packet required')
 need({c.get('performance_first_family_contract_id') for c in candidates}==set(ALLOWLIST),'six-cell packet membership mismatch')
 receipts=[]
 for workload in ['FWT','GEMM','VECTOR4M']:
  pair=[c for c in candidates if ALLOWLIST[c['performance_first_family_contract_id']]['workload']==workload]
  receipts.append(validate_pair(pair,engineering_enabled=engineering_enabled))
 return dict(status='PURE_HOST_SIX_CELL_PACKET_PASS_NOT_NATIVE_QUALIFICATION',pairs=receipts,scientific_launch_permission=False)
