"""Pure draft option plans. No config/spec/registry writes and no model starts."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P(__file__).resolve().parent;MC_SHA='d832ad1a898c58eb381d4034d7f7c022a7133af55c8436ce1bf562b1b77097dc'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def candidate_from_existing_S(S_spec_ref,mode,ro_qualification_ref=None):
 p=ROOT/'mode_contract.py'
 if sha(p)!=MC_SHA:raise ValueError('mode contract drift')
 sp=importlib.util.spec_from_file_location('draft_only_mode_contract',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);s=m.exact(S_spec_ref);m.need(s['mode']=='S','muststartfromactualS');m.check_background(s);m.need(mode in m.MODES,'unknown formal mode')
 if mode=='S':return dict(status='DRAFT_EXISTING_S_REUSE_REVIEW_ONLY',actual_S_spec_ref=S_spec_ref,launch_candidate=False,new_S_requested=False,required='New Main exactexistinghardware/input/observer reference qualification; no duplicatedS start')
 o=dict(s['expected_effective_options']);o.update(m.flags(mode));T,M=m.MODES[mode][3:5];final=True
 if T or M:
  if ro_qualification_ref is None:
   final=False
   for k in m.VARIABLE-{'-trace'}:o[k]='__UNBOUND_EXACT_RO_QUALIFICATION_REQUIRED__'
  else:
   q=m.exact(ro_qualification_ref);m.need(q['input_identity_sha256']==s['input_identity_sha256']and q['source_identity']==s['source_identity'],'ROqualdifferentinput/Source')
   for k in ['manifest','ranges']:o['-gpgpu_ep_l2_ro_'+k]=q[k+'_ref']['path'];o['-gpgpu_ep_l2_ro_'+k+'_sha256']=q[k+'_ref']['sha256']
   o['-gpgpu_ep_l2_ro_scope']=q['scope']
 return dict(schema='EP_C_WV_MODES_DRAFT_OPTION_PLAN_NOT_A_FROZEN_SPEC',status='DRAFT_MODE_CPU_HOSTQ_NATIVE_AND_CONFIG_MATERIALIZATION_REQUIRED',program=s['program'],mode=mode,T=bool(T),M=bool(M),source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],actual_S_spec_ref=S_spec_ref,baseline_ordered_configs_reference_only=s['ordered_configs'],expected_effective_options_draft=o,RO_binding_complete=final,ro_qualification_ref=ro_qualification_ref,delta_vs_S={k:dict(before=s['expected_effective_options'][k],after=v)for k,v in o.items()if s['expected_effective_options'][k]!=v},new_mode_CPU_qualification_ref=None,newHostQ_ref=None,matched_S_anchor_qualification_ref=None,ordered_configs_are_not_new_mode_configs=True,launch_permission=False,scientific_acceptance_granted=False,new_S_requested=False)
