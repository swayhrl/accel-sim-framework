"""Readonly small-metadata request checker; never starts any application or writes authority."""
import hashlib,json
from pathlib import Path
from taxonomy_rules import allowed_policy_pair
D=Path(__file__).resolve().parent
def load(p):
 p=Path(p)
 if p.stat().st_size>2*2**20: raise AssertionError('Not a small metadata file: '+str(p))
 return json.loads(p.read_text())
def checked_ref(r):
 p=Path(r['path']);b=p.read_bytes()
 assert len(b)==r.get('bytes',len(b)) and hashlib.sha256(b).hexdigest()==r['sha256'],str(p)
 return load(p)
def run():
 r=load(D/'NEXT_EXACT_PERFORMANCE_EXPERIMENT_REQUEST.json');checks=[]
 def c(n,v):
  assert v,n
  checks.append(n)
 c('request_only_zero_science',r['approved_starts']==r['consumed_starts']==r['new_science_starts_this_task']==r['new_science_budget_consumption_this_task']==0)
 c('two_families_four_requested_starts',len(r['groups'])==2 and r['requested_new_starts']==sum(g['requested_new_starts'] for g in r['groups'])==4)
 ids=[]
 for g in r['groups']:
  pre=g['program']+':'
  source=checked_ref(g['source_ref']);c(pre+'Source5_exact',g['source_identity']==source['source_identity'])
  qualification=checked_ref(g['new_input_CPU_qualification_ref'])
  qc=next(q for q in qualification['input_checks'] if q['input_identity_sha256']==g['input_identity_sha256'])
  c(pre+'RO_loader_policy_cases_PASS',len(qc['RO_loader_runs'])==2 and all(x['returncode']==0 for x in qc['RO_loader_runs']))
  inputmeta=checked_ref(g['exact_ordered_input_ref']);original=checked_ref(inputmeta['original_binding_ref'])
  c(pre+'ordered_commands_verbatim',inputmeta['ordered_commands']==original['expectedcommands'])
  c(pre+'ordered_kernel_hashes_verbatim',inputmeta['ordered_kernel_identity']==original['ordered_kernel_identity'])
  c(pre+'exact_input_binding',inputmeta['input_identity_sha256']==original['input_identity_sha256']==g['input_identity_sha256'])
  c(pre+'CTA_complete_scope_sum',sum(x['CTA'] for x in inputmeta['expected_kernel_scopes'])==inputmeta['expected_CTA'])
  c(pre+'instruction_complete_scope_sum',sum(x['instructions'] for x in inputmeta['expected_kernel_scopes'])==inputmeta['expected_instructions'])
  old=checked_ref(g['historical_source78_spec_ref']);maps=[]
  for p in g['points']:
   ids.append(p['prospective_cohort'])
   opts=checked_ref(p['effective_options_ref']);maps.append(opts)
   c(pre+p['mode']+':283',len(opts)==p['effective_options_count']==283)
   c(pre+p['mode']+':same_source_input',p['source_identity']==g['source_identity'] and p['input_identity_sha256']==g['input_identity_sha256'])
   c(pre+p['mode']+':old282_unchanged',all(opts[k]==v for k,v in old['expected_effective_options'].items()))
   parsed=next(x for x in qc['parser_runs'] if x['effective_options']['-gpgpu_ep_l2_ro_pressure_epoch']==opts['-gpgpu_ep_l2_ro_pressure_epoch'])
   c(pre+p['mode']+':actual_production_parser_exact',parsed['returncode']==0 and parsed['effective_options']==opts)
   c(pre+p['mode']+':not_launch_eligible',p['launch_eligible_now'] is False and p['host_spec_frozen_now'] is False)
  c(pre+'pair_only_policy_diff',allowed_policy_pair(*maps))
 c('four_distinct_new_cohort_names',len(ids)==len(set(ids))==4)
 c('future_resource_four_CPU',r['aggregate_planning']['physical_CPU_cores_if_all_admitted']==4)
 return {'status':'PASS','checks':checks,'count':len(checks),'science_starts':0,'budget_consumption':0}
if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
