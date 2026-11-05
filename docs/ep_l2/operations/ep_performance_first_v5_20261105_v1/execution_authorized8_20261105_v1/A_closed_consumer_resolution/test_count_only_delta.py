from pathlib import Path
import json,hashlib,importlib.util,copy
O=Path(__file__).parent
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load(O/'closed_consumer_283.py','A_count_test');c=m.load_ref(m.PLAN['old_frozen_source_ref'],'A_original_C');fixed=m.compile_exact_scan(m.load_ref(m.PLAN['old_frozen_source_ref'],'A_fixed_C'))
G=Path(m.PLAN['old_adapter_ref']['path']).parent.parent
sp=next((G/'execution/cases').glob('*/control/FROZEN_SPEC.json'));s=json.load(open(sp));binding=json.load(open(s['input_binding_ref']['path']))
lines=['gpgpu-sim_git-commit-'+s['source_identity']['core_source_commit'][:7]+'\n','accelsim-commit-'+s['source_identity']['framework_source_commit'][:7]+'\n']
lines+=['%s %s # CPU synthetic metadata fixture\n'%(k,v)for k,v in s['expected_effective_options'].items()]
for x in binding.get('expectedcommands',binding.get('all_commands')):
 lines.append(('Processing kernel /synthetic/'+x if x.endswith('.traceg')else'launching memcpy command : '+x)+'\n')
for x in s['expected_kernel_launches']:lines.append('launching kernel name: %s uid: %s cuda_stream_id: 0\n'%(x['name'],x['uid']))
lines+=['gpu_tot_sim_cycle = 12345\n','gpu_tot_sim_insn = %s\n'%s['expected_instructions'],'gpu_tot_issued_cta = %s\n'%s['expected_CTA']]
for prefix,field,n in [('EPL2B0V1','slice',64),('EPL2M0AV1','slice',64),('EPL2DRAMV1','channel',32)]:
 for i in range(n):lines.append('%s|scope=application|%s=%s|completion_cycle=12345\n'%(prefix,field,i))
lines+=['EPL2L1V1|scope=application|completion_cycle=12345\n','GPGPU-Sim: *** exit detected ***\n']
F=O/'bounded_count_fixtures';F.mkdir(exist_ok=True);raw=F/'synthetic_scan_fixture.txt';raw.write_text(''.join(lines))
try:c.scan(raw,s)
except Exception as ex:assert 'all282 actual options mismatch'in str(ex)
else:raise AssertionError('old count guard should fail283')
assert len(fixed.scan(raw,s)['actual_options'])==283
cases=[]
mutations=[
 ('drop_feature',lambda xs:[l for l in xs if not l.startswith('-gpgpu_ep_l2_tvd_cold_filter ')]),
 ('extra_port',lambda xs:xs+['-hidden_free_port 1 # forbidden\n']),
 ('bad_feature',lambda xs:[l.replace('-gpgpu_ep_l2_tvd_cold_filter 0 ','-gpgpu_ep_l2_tvd_cold_filter 2 ')if l.startswith('-gpgpu_ep_l2_tvd_cold_filter ')else l for l in xs]),
 ('conflicting_option',lambda xs:xs+['-gpgpu_ep_l2_tvd_cold_filter 2 # conflict\n']),
 ('wrongSource_banner',lambda xs:[l.replace('gpgpu-sim_git-commit-'+s['source_identity']['core_source_commit'][:7],'gpgpu-sim_git-commit-78f4b59')for l in xs]),
 ('wrongCTA',lambda xs:[l.replace('gpu_tot_issued_cta = '+str(s['expected_CTA']),'gpu_tot_issued_cta = 1')for l in xs]),
 ('missingCommand',lambda xs:[l for l in xs if not l.startswith('Processing kernel /synthetic/kernel-1.traceg')]),
 ('noNaturalEnd',lambda xs:[l for l in xs if 'exit detected'not in l]),
 ('missingScope',lambda xs:[l for l in xs if not l.startswith('EPL2DRAMV1|scope=application|channel=31|')]),
]
for name,change in mutations:
 p=F/(name+'.txt');p.write_text(''.join(change(lines)))
 try:fixed.scan(p,s)
 except Exception as ex:cases.append(dict(case=name,pass_reject=True,reason=str(ex)))
 else:raise AssertionError(name)
(O/'BOUNDED_COUNT_DELTA_TEST_RESULT.json').write_text(json.dumps(dict(synthetic_fixture_not_application=True,positive_exact283=True,old282_rejects283=True,negative_cases=cases,Source_banner_guard_unchanged=True,scientific_starts=0),indent=2)+'\n')
print('positive1 negative',len(cases),'actual Source banner still fail-closed')
