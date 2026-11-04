#!/usr/bin/env python3
"""Private inert Host/native metadata qualification. No launch, budget, route or executor API."""
import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=json.loads((ROOT/'SOURCE_BUILD_AND_DEPENDENCY_PINS.json').read_text())['source_identity']
def need(value,message):
    if not value: raise ValueError(message)
def exact(item):
    p=Path(item['path']); need(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'file pin drift '+str(p))
    return p
def validate(spec, profile, check_files=False):
    need(profile['schema']=='EP_PFV4_QUOTA_PRIVATE_FORMAL_HOST_NATIVE_METADATA_PROFILE_V1','profile schema')
    need(profile['source_identity']==SOURCE and profile['option_count']==283,'profile source/options')
    point=next((x for x in profile['points'] if x['cohort']==spec.get('cohort')),None)
    need(point is not None,'unscoped cohort')
    canonical=json.loads(exact(point['proposed_spec_ref']).read_text())
    need(spec==canonical,'metadata differs from exact private reviewed candidate')
    need(spec['source_identity']==SOURCE,'Source5')
    need(spec['mode']=='WV_ZERO_RO' and spec['T'] is False and spec['M'] is False and spec['RO_certificate'] is None,'RO/mode')
    need(spec['parameter_value'] in [0,64,128],'cap')
    e=spec['expected_effective_options'];need(len(e)==spec['effective_option_count']==spec['hardware_contract_option_count']==283,'exact283')
    need(e['-trace']==spec['trace_entry'] and e['-gpgpu_ep_l2_tvd_clean_limit']==str(spec['parameter_value']),'trace/quota')
    need(not spec['application_start_authorization'] and spec['application_budget_registered']==0 and not spec['retry'],'no authorization')
    old=json.loads(exact(spec['prior_candidate_ref']).read_text())
    for key in ['source_identity','expected_effective_options','ordered_configs','all_unique_kernel_members','expected_kernel_scopes','expected_kernel_launches','input_identity_sha256','command_count','expected_instructions','expected_CTA','hardware_fixed','geometry','observer_env']:
        need(spec[key]==old[key],'prior exact parser/input binding '+key)
    if check_files:
        for item in spec['ordered_configs']:exact(item)
        exact(spec['parser_cpu_evidence_ref']);exact(spec['source_build_dependency_ref'])
    return 'PASS_PRIVATE_HOST_NATIVE_METADATA_ONLY_NO_ENTRY_OR_APPLICATION_QUALIFICATION'
def qualify():
    p=json.loads((ROOT/'PRIVATE_FORMAL_HOST_NATIVE_PROFILE.json').read_text()); positives=[]
    for row in p['points']:
        s=json.loads(exact(row['proposed_spec_ref']).read_text()); positives.append(dict(cohort=s['cohort'],status=validate(s,p,True)))
    s=json.loads(exact(p['points'][0]['proposed_spec_ref']).read_text()); tests={}
    variants={
      'foreign_core':lambda t:t['source_identity'].update(core_source_commit='78f4b59e865b136eede74df74c44c210f5b4ca04'),
      'foreign_elf':lambda t:t['source_identity'].update(binary_sha256='0'*64),
      'force282':lambda t:t.update(effective_option_count=282),
      'missing_option':lambda t:t['expected_effective_options'].pop('-dram_latency'),
      'extra_option':lambda t:t['expected_effective_options'].update({'-unknown':'1'}),
      'quota_cap_conflict':lambda t:t.update(parameter_value=64 if t['parameter_value']==0 else 0),
      'cap129':lambda t:t.update(parameter_value=129),
      'RO_enabled':lambda t:t['expected_effective_options'].update({'-gpgpu_ep_l2_ro_tag_detach':'1'}),
      'wrong_WAD':lambda t:t['expected_effective_options'].update({'-gpgpu_ep_l2_wad_entries':'64'}),
      'wrong_D512':lambda t:t['expected_effective_options'].update({'-gpgpu_ep_l2_descriptor_pool_size':'256'}),
      'wrong_P1':lambda t:t['expected_effective_options'].update({'-gpgpu_ep_l2_bank_ops':'2'}),
      'alter_payload':lambda t:t['hardware_fixed'].update(payload_slots_per_slice=1296),
      'foreign_input':lambda t:t.update(input_identity_sha256='0'*64),
      'changed_config_order':lambda t:t['ordered_configs'].reverse(),
      'unauthorized_id':lambda t:t.update(cohort='EP_PERF_UNAUTHORIZED'),
      'authorization_smuggled':lambda t:t.update(application_start_authorization=True),
      'start_budget_smuggled':lambda t:t.update(application_budget_registered=1),
      'observer_change':lambda t:t['expected_effective_options'].update({'-gpgpu_ep_l2_ms_observer':'0'}),
      'foreign_anchor':lambda t:t.update(same_source_performance_anchor='Source78')}
    for name,mutate in variants.items():
        t=copy.deepcopy(s);mutate(t)
        try:validate(t,p)
        except ValueError as ex:tests[name]=dict(status='PASS_REJECTED',reason=str(ex))
        else:raise ValueError('negative accepted '+name)
    deps=json.loads((ROOT/'SOURCE_BUILD_AND_DEPENDENCY_PINS.json').read_text())
    exact(deps['binary_ref'])
    for item in deps['static_link_libraries']:exact(item)
    for item in deps['dynamic_library_files']:exact(item['resolved_ref'])
    exact(deps['interpreter_ref'])
    return dict(schema='EP_PFV4_QUOTA_PRIVATE_HOST_NATIVE_METADATA_CPU_RECEIPT_V1',status='PASS_PRIVATE_METADATA_ONLY',positives=positives,negative_count=len(tests),negatives=tests,production_CPU_tests_rerun=0,parser_probe_rerun=False,ELF_or_loader_executed=False,model_starts=0,budget_registered=0,native_entry_installed=False,official_shared_HostQ_executed=False,native_or_application_qualified=False)
if __name__=='__main__':
    print(json.dumps(qualify(),indent=2,sort_keys=True))
