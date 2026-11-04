"""CPU-only exclusion tests using frozen real primary metadata; never launches."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from scope_bridge import CanaryScope, MARKER, ROLE, digest, make_dispatch_reader, wrap_primary_adaptive

A = Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
R = Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
read = lambda p: json.loads(Path(p).read_bytes())
plan = read(A/'coordinator/strace_bpf_engineering_canary_plan_v1/DRAFT_PLAN.json')
matrix, primary_scope = read(R/'control/MATRIX_CURRENT.json'), read(R/'control/SCOPE.json')
summary = read(R/'analysis/AUTO_SUMMARY.json')  # Do not call summary(): it writes production.
specs = {r['cohort']: read(r['draft_spec_path']) for r in plan['rows']}
q = dict(request=next(iter(specs.values()))['request'], admitted_specs={}, consumed={},
         authorized_engineering_observation_canaries=[])
for c, spec in specs.items():
    q['admitted_specs'][c] = digest(spec)
    lin = spec['engineering_observation_canary_lineage']
    q['authorized_engineering_observation_canaries'].append(dict(
        cohort=c, role=ROLE, mode=lin['mode'], science_projection_sha256=lin['science_projection_sha256'],
        primary_statistics_excluded=True, validated_union_authorized=False))
canonical = lambda c: (copy.deepcopy(specs[c]), digest(specs[c]))
scoped = CanaryScope(plan)
module_path = A/'agents/E/supplemental_scan_m16_v1/supplemental_trial.py'
sp = importlib.util.spec_from_file_location('actual_unmodified_R2_adapter_CPU', module_path)
r2 = importlib.util.module_from_spec(sp)
sp.loader.exec_module(r2)
base = copy.deepcopy(matrix)
r2spec = read(R/'control/specs'/(r2.NEW+'.json'))
base['points'].append({k: r2spec[k] for k in ('cohort','input_digest','program','suite','profile','cell','scientific_role')})
base['supplemental_dispatch_view'] = dict(schema='SUPPLEMENTAL_DISPATCH_ONLY_VIEW_V1')
originals = copy.deepcopy((plan, matrix, primary_scope, summary, specs, q, base))
checks = []

def ok(label, fn):
    assert fn() is not False
    checks.append(label)

def rejects(label, fn):
    try:
        fn()
    except (AssertionError, KeyError, TypeError, ValueError):
        checks.append(label)
    else:
        raise AssertionError('Accepted forbidden case: '+label)

view = scoped.dispatch_view(base, matrix, primary_scope, q, canonical)
ok('all four engineering rows added only to independent view', lambda: len(view['points']) == len(base['points'])+4)
ok('exact prior R2 dispatch view recovered', lambda: scoped.primary_view(view,matrix,primary_scope,q,canonical) == base)
ok('real existing primary summary passes unchanged', lambda: scoped.assert_primary_summary(summary,matrix,primary_scope))
sources = lambda: (matrix, primary_scope, q, canonical)
called = []
def original_recommend(s, actual_primary, history):
    assert actual_primary == matrix and s == summary
    called.append(True)
    return dict(proposals=[], scientific_stage_complete=False, adoption_ready=False)
prior = r2.make_primary_adaptive(original_recommend, SimpleNamespace(primary=lambda: matrix),
                               SimpleNamespace(guard_decision=lambda d: d))
wrapped = wrap_primary_adaptive(prior, scoped, sources)
ok('actual unchanged R2 wrapper still sees only its fixed original extra', lambda: wrapped(summary,view)['proposals'] == [] and len(called)==1)
ok('exact old view delegates when optional engineering view absent', lambda: wrapped(summary,base)['proposals'] == [] and len(called)==2)
for key, value in [('mode','BAD'),('primary_statistics_excluded',False),('validated_union_authorized',True)]:
    bad = copy.deepcopy(specs); c=next(iter(bad)); bad[c]['engineering_observation_canary_lineage'][key]=value
    qq=copy.deepcopy(q);qq['admitted_specs'][c]=digest(bad[c])
    rejects('reject lineage '+key, lambda bad=bad,qq=qq,c=c: scoped.validate(c,bad[c],digest(bad[c]),qq))
c = next(iter(specs))
bad=copy.deepcopy(specs[c]); bad['expected_options']['-gpgpu_clock_domains']=['1410:1410:1410:1000']
qq=copy.deepcopy(q);qq['admitted_specs'][c]=digest(bad)
rejects('reject architecture/clock change despite matching current admitted SHA',lambda: scoped.validate(c,bad,digest(bad),qq))
bad=copy.deepcopy(matrix);bad['points'].append(copy.deepcopy(view['points'][-1]))
rejects('engineering cohort forbidden in real primary matrix',lambda: scoped.check_primary(bad,primary_scope))
bad=copy.deepcopy(primary_scope);bad['points'][0]['scientific_role']=ROLE
rejects('unknown engineering role forbidden in real primary scope',lambda: scoped.check_primary(matrix,bad))
bad=copy.deepcopy(view);bad['points'][-1]['cohort']='UNKNOWN_ENGINEERING'
rejects('unknown engineering runtime row not silently promoted or dropped',lambda: scoped.primary_view(bad,matrix,primary_scope,q,canonical))
bad=copy.deepcopy(view);bad['points'].pop()
rejects('missing announced engineering row rejected',lambda: scoped.primary_view(bad,matrix,primary_scope,q,canonical))
bad=copy.deepcopy(summary)
input_id=plan['rows'][0]['input_digest'];bad['table'][input_id]['P0']['DH']=dict(cohort=c,accepted=True,cycles=1,scientific_role=ROLE)
rejects('malicious one-cycle engineering P0 cannot contaminate primary GM/parents',lambda: scoped.assert_primary_summary(bad,matrix,primary_scope))
held=wrapped(bad,view)
ok('contaminated summary yields explicit nonfinal HOLD without calling old inference',lambda: held['proposals']==[] and held['adoption_ready']is False and held['scientific_stage_complete']is False and len(called)==2)
qq=copy.deepcopy(q);qq['authorized_engineering_observation_canaries']=[]
reader=make_dispatch_reader(lambda path: base,scoped,lambda:(matrix,primary_scope,qq,canonical),'MATRIX')
ok('invalid optional authority leaves exact old primary/R2 queue available',lambda: reader('MATRIX') is base and reader.last_issue is not None)
qq=copy.deepcopy(q);qq['authorized_engineering_observation_canaries'].append(copy.deepcopy(qq['authorized_engineering_observation_canaries'][0]))
rejects('duplicate technical authority rejected',lambda: scoped.validate(c,specs[c],digest(specs[c]),qq))
amended=copy.deepcopy(specs);assert amended[c]['host_cpu'] is None;amended[c]['estimated_peak_model_RAM_bytes']+=4096
qq=copy.deepcopy(q);qq['admitted_specs'][c]=digest(amended[c])
ok('legal RAM refresh preserves unbound canonical CPU without freezing DRAFT SHA',lambda: scoped.validate(c,amended[c],digest(amended[c]),qq)['canonical_sha256']==digest(amended[c]))
rejects('stale current canonical SHA rejected',lambda: scoped.validate(c,amended[c],digest(specs[c]),qq))
bad=copy.deepcopy(amended[c]);bad['host_cpu']=131
bound_q=copy.deepcopy(qq);bound_q['admitted_specs'][c]=digest(bad)
rejects('bound CPU rejected in canonical even with matching current authority SHA',
        lambda: scoped.validate(c,bad,digest(bad),bound_q))
# Reproduce l2_native.spec_for canonical/resolved separation, not a CPU launch.
native_sha=lambda obj: hashlib.sha256((json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
unbound=copy.deepcopy(amended[c]);resolved=copy.deepcopy(unbound);resolved['host_cpu']=131
binding=dict(host_cpu=131,canonical_spec_sha256=native_sha(unbound),resolved_spec_sha256=native_sha(resolved))
ok('dispatch CPU changes only independently hashed resolved copy',
   lambda: unbound['host_cpu'] is None and resolved['host_cpu']==binding['host_cpu']
           and binding['canonical_spec_sha256']!=binding['resolved_spec_sha256'])

assert (plan,matrix,primary_scope,summary,specs,q,base) == originals
result=dict(schema='MAIN_ENGINEERING_SCOPE_BRIDGE_CPU_QUALIFICATION_V2',status='PASS_PURE_SCOPE_COMPONENTS_NOT_INSTALLED',
    checks=checks,count=len(checks),actual_primary_points=len(matrix['points']),actual_prior_R2_wrapper_source_sha256=hashlib.sha256(module_path.read_bytes()).hexdigest(),
    originals_unchanged=True,production_authority_writes=0,model_starts=0,signals=0,full_native_prefix_qualification=False)
out=Path(__file__).with_name('SCOPE_BRIDGE_CPU_QUALIFICATION.json')
with out.open('x') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
