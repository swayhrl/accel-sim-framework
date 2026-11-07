"""Small metadata-only identity and requestability checks; never grants science."""
import re,json,hashlib
def need(v,m):
 if not v:raise ValueError(m)
SOURCE_KEYS=('core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256','archive_sha256')
def valid_source(s):
 need(type(s)is dict and set(SOURCE_KEYS)<=set(s),'exact Source5 missing')
 for k in SOURCE_KEYS:need(type(s[k])is str and re.fullmatch('[0-9a-f]{'+str(64 if k.endswith('sha256')else 40)+'}',s[k]),'invalid exact Source5 '+k)
 return True
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def validate_pair(a,b,allowed_option_keys):
 valid_source(a['source_identity']);valid_source(b['source_identity'])
 need(a['source_identity']==b['source_identity'],'cross Source5/ELF comparison')
 for k in ['input_identity_sha256','literal_commandlist_sha256','ordered_commands_canonical_sha256','ordered_commands','ordered_kernel_identity','mode','geometry','clock_domains','observer_env','expected_kernel_launches','expected_instructions','expected_CTA']:
  need(a[k]==b[k],'unmatched '+k)
 for p in [a,b]:
  need(p['ordered_commands_canonical_sha256']==canonical(p['ordered_commands']),'canonical commandlist is not its ordered commands')
  need(type(p['expected_effective_options'])is dict and len(p['expected_effective_options'])==p['effective_option_count'],'incomplete fullconfig')
  need(p['fullconfig_sha256']==canonical(p['expected_effective_options']),'fullconfig SHA mismatch')
  need(p['expected_effective_options']['-gpgpu_clock_domains']==p['clock_domains'],'clock/config mismatch')
 need(a['effective_option_count']==b['effective_option_count'],'option population drift')
 delta={k:[a['expected_effective_options'].get(k),b['expected_effective_options'].get(k)]for k in a['expected_effective_options'].keys()|b['expected_effective_options'].keys()if a['expected_effective_options'].get(k)!=b['expected_effective_options'].get(k)}
 need(set(delta)<=set(allowed_option_keys),'undeclared fullconfig delta '+str(sorted(set(delta)-set(allowed_option_keys))))
 return dict(status='EXACT_SOURCE_INPUT_COMMAND_FULLCONFIG_MATCHED_WITH_DECLARED_DELTA',delta=delta,scientific_permission=False)
def validate_family(f):
 need(f['new_science_authorized']is False and f['registered_starts']==f['consumed_starts']==0,'engineering scope cannot grant starts')
 ready=f['engineering_readiness']
 closed=ready.get('production_correctness_closed')is True
 if f['owner']=='C'and not closed:
  need(f['status']=='NOT_REQUESTABLE'and f['formal_proposed_start_count']==0,'C partial must be NOT_REQUESTABLE formal0')
 if f['status']=='NOT_REQUESTABLE':
  need(f['formal_proposed_start_count']==0,'unready family cannot propose formal starts');return dict(status='VALID_EXPLICIT_GAP_FORMAL0',owner=f['owner'])
 need(closed and ready.get('source_frozen')is True and ready.get('actual_constructor_fullconfig_closed')is True and ready.get('input_mode_rebind_closed')is True,'newSource qualification incomplete')
 valid_source(f['source_identity'])
 need(f['points']and f['formal_proposed_start_count']==len(f['points'])and all(p['one_start_only']is True for p in f['points']),'finite exact point cardinality')
 need(f['reference_policy']=='SAME_NEW_SOURCE_NO_OLD_ELF_SUBSTITUTION','oldSource baseline not allowed')
 for p in f['points']:need(p['source_identity']==f['source_identity'],'point source mismatch')
 return dict(status='EXACT_REQUEST_METADATA_READY_FOR_MAIN_REVIEW_NOT_SCIENCE_AUTHORITY',owner=f['owner'])
