"""Main-only exact12-point small-G preparation; zero starts and no registry writes."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys

J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0, str(J / 'tools'))
from ep_perf_common import *


def main():
    # The same exact128MiB CPU-only admission math is conservative for the tiny
    # package/spec joins too. It grants no application/native admission.
    import main_p64_ni_and_stage_v2 as bounded
    gate_ref = bounded.gate()
    delivery_path = J / 'agent_b/small_geometry_host_v2/DELIVERY_MANIFEST.json'
    need(sha(delivery_path) == 'd723b020c3ac97255d0c0b053d5d923046c842997b30c9ae45567eb631b89c04', 'reviewed final V2 delivery')
    delivery = read(delivery_path)
    cpu = exact(delivery['CPU_result_ref'])
    need(cpu['test_count'] == 41 and all(t['PASS'] for t in cpu['tests']), '41 actual CPU controls')
    need(cpu['DAG_outer_root_verified_after_all_tests'] and cpu['full_application_positive_examples'] == 0, 'CPU scope/final package verification')
    source = Path(delivery['entry_ref']['path']).parent
    manifest = exact(delivery['package_manifest_ref'])
    need('PACKAGE_MANIFEST.json' not in manifest['files'], 'no manifest self reference')
    dest = J / 'tools/qualified_small_geometry_v2'
    need(not dest.exists(), 'new immutable qualified package directory only')
    dest.mkdir()
    for rel, r in manifest['files'].items():
        p = source / rel
        need(sha(p) == r['sha256'] and p.stat().st_size == r['bytes'], 'all final package member integrity')
        t = dest / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, t)
    shutil.copyfile(source/'PACKAGE_MANIFEST.json', dest/'PACKAGE_MANIFEST.json')
    entry_ref = ref(dest/'small_geometry_terminal.py')
    need(entry_ref['sha256'] == '2600e7a8da4104eb77eedbf6d7bb3aacb8fc9467fe246b026f49a75128f61b7c', 'V2 entry')
    adapter = module(entry_ref, 'Main_small_G_exact_V2')
    adapter.verify_pins()
    _, math = adapter.numeric_math()
    need(math['numeric_body_sha256'] == '7cc347a6c62974eedf9e1e39b007c2716fa886d26057f005c938c820b48e1817' and math['frozen_final_suffix_sha256'] == 'bf91f534869a1ec59aea92ee2de961d50e16e68a28eed636448ca83122339432', 'original correctness math unchanged')
    hq = read(J/'control/HOST_QUALIFICATION_GEOMETRY_QUEUE_V1.json')
    bypath = {r['path']: r for r in hq['modules']}
    for rel in [*manifest['files'], 'PACKAGE_MANIFEST.json']:
        r = ref(dest/rel)
        bypath[r['path']] = r
    hq.update(utc=now(), scope='EXACT_SOURCE78_S_F_TWO_SMALL_GEOMETRIES_FOUR_HEAVY_OFF_MS_B0_M0A1',
        qualified_by='Main', qualified_parameter_validation_module_ref=entry_ref,
        modules=list(bypath.values()), package_delivery_ref=ref(delivery_path),
        package_CPU_control_ref=delivery['CPU_result_ref'], package_manifest_ref=ref(dest/'PACKAGE_MANIFEST.json'),
        geometry_scope=[dict(slices=64, sets=16, ways=8, line_bytes=128), dict(slices=64, sets=32, ways=4, line_bytes=128)],
        CPU_resource_gate_reuse_ref=gate_ref,
        CPU_resource_gate_purpose='Same conservative128MiB bounded engineering admission; spec/package joins, no raw/Trace scans. Gate origin name is historical and not an application or registration permission.',
        Main_review='Read complete V1 entry/actual Source78 ctor and FT1/FT2 behavior population joins and numeric/STRUCT boundaries. Found stale self-pinned outer manifest after old controls; V1 rejected. Read V2 DAG-only correction, final41 controls, exact source/282/policy guards; pin V2 root and all dependencies externally. Main installed byte exact, independently verifies runtime pins and original math. No old raw renamed; new app acceptance pending.',
        V1_final_package_accepted=False, heavy_observer_ON_qualified=False,
        Source92_or_P2_or_queue_interventions_qualified=False, Core_ELF_unchanged=True,
        actual_new_optional_OFF_application_validation='PENDING_FIRST_NEW_COMPLETE_MODEL')
    hqr = put(J/'control/HOST_QUALIFICATION_SMALL_GEOMETRY_V2.json', hq, True)
    samples = read(J/'control/SEARCH_PLAN_U_D_N_V1.json')['exploration_inputs']
    need(len(samples) == 3, 'same predeclared diverse fixed3')
    profiles = [('G16_W8', 16, 8), ('G32_W4', 32, 4)]
    plan_name = 'SEARCH_PLAN_SMALL_GEOMETRY_FIXED3_V2'
    plan = dict(schema='EP_MAIN_FINITE_SOURCE78_SMALL_G_PLAN_V2', goal=GOAL,
        status='MAIN_REVIEWED_PREDECLARED_FINITE_EXPLORATION', profiles=[dict(profile=p, sets=n, ways=w) for p,n,w in profiles],
        exploration_inputs=samples, host_qualification_ref=hqr, maximum_new_starts=12,
        physical_payload_slots_per_slice=1168, nominal_tag_address_coverage_GPU_bytes=1048576,
        kept_resources='64 slices/32 channels/D512/line128/WAD128/bank1/all queues/DRAM100/clocks/physical payload1168',
        mechanisms='Exact formal S/F unchanged; no new protocol policy or certificate',
        contrast='Both small geometries have128 Tags/slice; associativity and actual IPOLY indexing differ.',
        outcome_policy='All negatives retained; no acceptance condition requires detach or speedup.',
        optional_lifetime_pressure='FOUR_HEAVY_OFF_NOT_OBSERVED_NOT_ZERO', model_starts=0,
        scope='Fixed3 exploration only; no global optimum/common-set GM or area claim')
    planref = put(J/'control'/(plan_name+'.json'), plan, True)
    registry, unused = authority()
    q = registry['registered_future_requests'][GOAL]
    refs, rows = [], []
    for profile, sets, ways in profiles:
        delta = {'-gpgpu_cache:dl2': f'S:{sets}:128:{ways},L:B:m:L:P,A:128:1,128:0,32'}
        for sample in samples:
            for mode in ('S', 'F'):
                basecase = sample['reference_cohorts'][mode]
                r = q['consumed'][basecase]
                need(r['state'] == 'CLOSED_ACCEPTED', 'closed exact reference')
                oldpath = J/'cases'/basecase/'control/FROZEN_SPEC.json'
                base = read(oldpath)
                point = exact(r['accepted_point_ref'])
                need(point['input_identity_sha256'] == sample['input_identity_sha256'] and base['profile'] == 'REF32x8_L100', 'actual unchanged input/reference')
                case = 'EP_PERF_'+sample['case_short']+'_'+mode+'_'+profile+'_V1'
                need(case not in q['admitted_specs'], 'fresh exact cohort')
                folder = J/'cases'/case
                s = copy.deepcopy(base)
                s.update(cohort=case, profile=profile, host_qualification_ref=hqr,
                    validation_module_ref=entry_ref, geometry=dict(slices=64, sets=sets, ways=ways, line_bytes=128))
                s['expected_effective_options'].update(delta)
                configs=[]
                for i,c in enumerate(base['ordered_configs']):
                    text=Path(c['path']).read_text()
                    if i==len(base['ordered_configs'])-1:
                        text+='\n# Exact small Tag geometry; declared physical payload and all services unchanged.\n-gpgpu_cache:dl2 '+delta['-gpgpu_cache:dl2']+'\n'
                    path=folder/'env'/('config-'+str(i)+'.config')
                    path.parent.mkdir(parents=True,exist_ok=True)
                    with path.open('x')as f:f.write(text)
                    configs.append(ref(path))
                s['ordered_configs']=configs
                s['limits']['wall_seconds']=max(s['limits']['wall_seconds'], 48*3600 if sample['case_short']=='CONV' else 24*3600)
                s['limits']['result_bytes']=max(s['limits']['result_bytes'],128*M)
                s['pinned_files'].update({r['path']:r['sha256']for r in hq['modules']})
                s['pinned_files'][planref['path']]=planref['sha256']
                s['scientific_option_contract']=dict(mode=mode,complete_282=True,reference_spec_ref=ref(oldpath),reference_accepted_point_ref=r['accepted_point_ref'],
                    exact_common_hardware_delta=delta,only_geometry_changes=True,mode_policy_unchanged=True,observer_profile_unchanged=True,
                    search_plan_ref=planref,physical_payload_slots_per_slice=1168,area_or_payload_SRAM_shrink_claim=False)
                binding=adapter.qualify_history_spec(s)
                adapter.history_for(s)
                need(binding['logical_tags_per_slice']==128, 'actual small Tag count')
                refs.append(put(folder/'control/FROZEN_SPEC.json',s,True))
                rows.append(dict(case=case,mode=mode,program=s['program'],all282_delta={k:[base['expected_effective_options'][k],v]for k,v in delta.items()}))
    need(len(refs)==12,'exact finite stage12')
    name='STAGE_SMALL_GEOMETRY_FIXED3_12POINTS_V2'
    stage=dict(schema='EP_FULL_PERF_FINITE_STAGE_V1',goal=GOAL,status='MAIN_REVIEWED_EXACT_FINITE_STAGE',stage=name,scientific_owner='Main',maximum_new_starts=12,
        automatic_retry=False,refund=False,source_keep=True,authorization_ref=ref(J/'control/USER_AUTHORIZATION.json'),engine_ref=ref(J/'tools/ep_perf_native.py'),common_ref=ref(J/'tools/ep_perf_common.py'),
        specs=refs,resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME',host_qualification_ref=hqr,predeclared_search_plan_ref=planref)
    sr=put(J/'control'/(name+'.json'),stage,True)
    put(J/'control'/(name+'_PREPARATION_RECEIPT.json'),dict(status='ALL12_EXACT_282_AND_ACTUAL_HISTORY_MATH_PREJOINS_PASS_ZERO_STARTS',utc=now(),CPU_resource_gate_ref=gate_ref,rows=rows,stage_ref=sr),True)
    print(json.dumps(dict(stage_ref=sr,host_qualification_ref=hqr,model_starts=0)))


if __name__=='__main__':main()
