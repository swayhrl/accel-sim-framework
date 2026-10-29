"""DRAFT pure five-mode adapter. No actors or application-acceptance writes."""
import pathlib,hashlib,importlib.util,json
P=pathlib.Path;ROOT=P(__file__).resolve().parent
PINS={'deps/host_scaling/dynamic_observation_scaled.py': '4db737bf5bdc09532480e401001e39bc0de414c0b692c666542e8665a011ab25', 'deps/host_scaling/lowcost_terminal_scaled.py': 'fdcaab0aef93363148a81257e548dd1cc58cc1369986cbfc809366ff83cd1df1', 'deps/host_scaling/rolling_structure_core.py': 'b8f09af83cf2eb50933b46216f825593eb218c2a304a61ec7a624fc22f3f2066', 'deps/host_scaling/PACKAGE_MANIFEST.json': '83a0ac96f6f26f0788a46cde210277e22222476157e74352d9ed41f0ae1be2c1', 'deps/host_scaling/frozen_math/parse_main_terminal.py': 'f518aed003f2f70a4d84afc95c215773da2c14761315349b7600655a1e549c8e', 'deps/host_scaling/frozen_math/lowcost_terminal_v2.py': 'cba193d8ec810219f58bbe55870814b70604082f4f6683a236a418e80b9da35c', 'deps/host_scaling/frozen_math/ft_lane5/validate.py': '08a7396a6e11893dbbcb982725765a6c9b12194b1e01e3f0dc70d337f85dd500', 'deps/host_scaling/frozen_math/ft_lane5/parse_unified_terminal.py': '536d1a8d55452b7aee5b84168648b228eb35cc5e82b523e81b59634c51db352b', 'mode_contract.py': 'd832ad1a898c58eb381d4034d7f7c022a7133af55c8436ce1bf562b1b77097dc', 'REF_282_S.json': '65474df0a47f5e16ce0314004b160cbd0a8da4d83473a1f3351e4bf5cc574062'}
BODY_SHA='7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817'
SUFFIX_SHA='bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432'
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def verify():
 for n,h in PINS.items():need(sha(ROOT/n)==h,'pure package dependency drift:'+n)
 return {n:{'path':str(ROOT/n),'sha256':h}for n,h in PINS.items()}
def load(n,label):
 need(n in PINS and sha(ROOT/n)==PINS[n],'unpinned pure module');sp=importlib.util.spec_from_file_location(label,ROOT/n);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def configured_base():
 mc=load('mode_contract.py','pure_five_mode_contract');b=load('deps/host_scaling/lowcost_terminal_scaled.py','private_unchanged_scaled');factory=b.frozen_c
 def isolated_c():
  c=factory();c.history_for=mc.history_for;return c
 b.frozen_c=isolated_c
 return b,mc

def history_for(s):
 verify();mc=load('mode_contract.py','history_only');return mc.history_for(s)
def numeric_math():
 verify();b,_=configured_base();parse,receipt=b.numeric_math();need(receipt['numeric_body_sha256']==BODY_SHA and receipt['frozen_final_suffix_sha256']==SUFFIX_SHA,'frozen7cc/bf91 bytes changed');return parse,receipt

def validate_case(raw,spec,qualification,sourceq_path,sourceq_sha):
 dependencies=verify();b,mc=configured_base();s=mc.read(spec)if isinstance(spec,(str,P))else dict(spec);q=mc.read(qualification)if isinstance(qualification,(str,P))else dict(qualification);binding=mc.validate_static(s)
 need(s['validation_module_ref']['sha256']==sha(__file__),'new parser self identity');need(q.get('formal_mode')==s['mode']and q.get('mode_contract_ref')==s['mode_contract_ref']and q.get('validation_module_ref')==s['validation_module_ref']and q.get('mode_cpu_qualification_ref')==s.get('mode_cpu_qualification_ref'),'new NativeQ mode/parser bindings absent; oldQ not inherited')
 result=b.validate_case(raw,s,q,sourceq_path,sourceq_sha);receipt=result['math_binding'];need(receipt['numeric_body_sha256']==BODY_SHA and receipt['frozen_final_suffix_sha256']==SUFFIX_SHA,'frozen math changed')
 # Native disabled RO/TVD does not emit these rows. Their absence is N/A,
 # never synthetic zero rows. Keep the full raw and original numeric checks.
 ro_lines=tvd_lines=0;c=b.frozen_c()
 with c.RawPath(raw).open(errors='strict')as f:
  for line in f:
   ro_lines+=line.startswith('EPL2ROV1|SUMMARY|');tvd_lines+=line.startswith(('EPL2TVDV2|','EPL2TVDV3|'))
 ro=mc.ro_enabled(s['mode']);victim=bool(mc.MODES[s['mode']][1]);need(ro_lines>=64 if ro else ro_lines==0,'RO emitted population contradicts formal mode');need(tvd_lines>=64 if victim else tvd_lines==0,'TVD emitted population contradicts formal mode')
 result['RO_applicability']=binding['RO']['applicability'];result['outer_join_required']=[x.replace('exact RO certificate iff F','exact RO certificate iff T or M')for x in result['outer_join_required']]
 result['formal_mode_binding']=binding;result['formal_history_profile']=mc.MODES[s['mode']][5];result['mode_adapter_provenance']={'entry_sha256':sha(__file__),'dependencies':dependencies,'numeric_body_sha256':BODY_SHA,'frozen_final_suffix_sha256':SUFFIX_SHA,'private_history_mapper_only':True,'W_was_not_relabelled_F':True,'actual_mode_rows':{'RO_summary_lines':ro_lines,'TVD_lines':tvd_lines},'newHostQ_and_modeCPU_required':True,'scientific_acceptance_granted':False}
 need(result['scientific_acceptance_granted']is False,'pure validator must not accept');return result
