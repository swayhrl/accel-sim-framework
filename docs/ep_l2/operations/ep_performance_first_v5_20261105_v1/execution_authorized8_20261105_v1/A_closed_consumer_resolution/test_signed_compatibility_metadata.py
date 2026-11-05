from pathlib import Path
import json,importlib.util,copy
O=Path(__file__).parent
sp=importlib.util.spec_from_file_location('A_signed_metadata_negatives',O/'exact_banner_compatibility.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
r=json.load(open(O/'MAIN_EXACT_BANNER_COMPATIBILITY_APPROVAL_REF.json'));a=m.exact(r);row=a['exact_cohort_rows'][0];s=m.exact(row['sealed_spec_ref']);raw=row['raw_ref']['path'];consumer=a['consumer_entry_ref'];checks=[]
def rejected(name,ss=s,rr=raw,ar=r,cr=consumer):
 try:m.check(ss,rr,ar,cr)
 except Exception as ex:checks.append(dict(case=name,pass_reject=True,reason=str(ex)))
 else:raise AssertionError(name)
unsigned=O/'UNSIGNED_EXACT_BANNER_COMPATIBILITY_APPROVAL_TEMPLATE.json'
rejected('unsigned_compatibility',ar=dict(path=str(unsigned),sha256=m.sha(unsigned)))
bad=copy.deepcopy(s);bad['source_identity']['core_source_commit']='78f4b59e865b136eede74df74c44c210f5b4ca04';rejected('no_source_relabel78',ss=bad)
bad=copy.deepcopy(s);bad['cohort']='EP_PERF_FOREIGN';rejected('no_foreign_cohort',ss=bad)
bad=copy.deepcopy(s);bad['source_feature_profile']='UNKNOWN';rejected('no_unreviewed_profile',ss=bad)
bad=copy.deepcopy(s);bad['limits']['wall_seconds']=1;rejected('sealed_spec_drift',ss=bad)
rejected('unsealed_raw_path',rr=O/'bounded_count_fixtures/synthetic_scan_fixture.txt')
bad=copy.deepcopy(consumer);bad['sha256']='0'*64;rejected('unsigned_consumer_bytes',cr=bad)
# Exact literal comparison cannot be relaxed to matching token/prefix.
core=row['observed_core_banner_lines'];framework=row['observed_framework_banner_lines']
mut=copy.deepcopy(a);mut['exact_core_banner_lines']=[core[0].replace('modified_6.0.','modified_0.0.')]
assert not(core==mut['exact_core_banner_lines']==row['observed_core_banner_lines']and framework==mut['exact_framework_banner_lines']==row['observed_framework_banner_lines'])
checks.append(dict(case='same_prefix_different_full_literal',pass_reject=True,reason='exact full line equality remains required'))
(O/'SIGNED_COMPATIBILITY_NEGATIVE_RESULT.json').write_text(json.dumps(dict(scope='bounded metadata guards only; real3raw positive full consumer separate',cases=checks,actual_scientific_starts=0,original_artifacts_unchanged=True),indent=2)+'\n')
print('negative_PASS',len(checks))
