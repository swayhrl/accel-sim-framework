#!/usr/bin/env python3
"""Single Main: stage one exact family and require fresh resource admission."""
import importlib.util
import json
import pathlib
import sys
import uuid

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FAMILIES = {
    'gemm': ['EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1'],
    'stencil': ['EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1', 'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'],
}
if len(sys.argv) != 2 or sys.argv[1] not in FAMILIES:
    raise SystemExit('usage: stage_dispatch_exact5.py gemm|stencil')
family = sys.argv[1]
cases = FAMILIES[family]
common_file = ROOT / 'runtime' / ('host_' + family + '_bound_v2') / 'ep_perf_common_v2.py'
loader = importlib.util.spec_from_file_location('exact5_common_stage_' + family, common_file)
common = importlib.util.module_from_spec(loader)
loader.loader.exec_module(common)
specs = {c: common.read(ROOT / 'cases' / c / 'control/FROZEN_SPEC.json') for c in cases}
request = specs[cases[0]]['science_request_id']
assert all(s['science_request_id'] == request for s in specs.values())
reg, _ = common.authority()
q = reg['registered_future_requests'][request]
assert not q['consumed'] and q['remaining'] == len(cases)
assert q['admitted_specs'] == {c: common.sha(ROOT / 'cases' / c / 'control/FROZEN_SPEC.json') for c in cases}
assert all((ROOT / 'cases' / c / 'control/NATIVE_PRELAUNCH_QUALIFICATION.json').exists() for c in cases)
resource = common.module(specs[cases[0]]['resource_module_ref'], 'exact5_resources_stage')
pre = resource.snapshot()
assert not pre.get('foreign_metadata_errors') and pre['current_scope_registered']
assert not pre['actual_loader_aware_models']
assert pre['true164_mount_verified']
occupied = set(pre['occupied_model_or_claim_cpus'])
allowed = [n for n in pre['cpu_allowed'] if n >= 128 and n not in occupied]
assert len(allowed) >= len(cases)
cpus = dict(zip(cases, allowed[:len(cases)]))
claims_path = ROOT / 'control/DISPATCH_CLAIMS.json'
binding_dir = ROOT / 'control/dispatch_bindings'
session = str(uuid.uuid4())
with common.locked(common.GLOBAL_MAIN_ADMISSION_LOCK):
    live_reg, _ = common.authority()
    live_q = live_reg['registered_future_requests'][request]
    assert not live_q['consumed'] and live_q['remaining'] == len(cases)
    assert live_q['admitted_specs'] == q['admitted_specs']
    assert not claims_path.exists() or common.read(claims_path) == {'claims': {}}
    assert not any((binding_dir / (c + '.json')).exists() for c in cases)
    current = resource.snapshot()
    assert not current.get('foreign_metadata_errors') and not current['actual_loader_aware_models']
    assert not (set(cpus.values()) & set(current['occupied_model_or_claim_cpus']))
    claims = {}
    for c, s in specs.items():
        binding = {'cohort': c, 'controller_session': session, 'host_cpu': cpus[c],
                   'spec_sha256': q['admitted_specs'][c]}
        common.put(binding_dir / (c + '.json'), binding, True)
        claims[c] = {'request': request, 'cohort': c, 'state': 'CLAIMED',
                     'host_cpu': cpus[c], 'spec_sha256': q['admitted_specs'][c],
                     'estimated_peak_RAM_bytes': s['estimated_peak_RAM_bytes'],
                     'remaining_write_bytes': s['limits']['result_bytes']}
    common.put(claims_path, {'claims': claims})
    s = resource.snapshot()
    writes = sum(x['remaining_write_bytes'] for x in claims.values()) + max(
        specs[c]['limits']['result_bytes'] for c in cases) + 2 * common.M
    ram = sum(x['estimated_peak_RAM_bytes'] for x in claims.values())
    decisions = {}
    for c in cases:
        policy = common.exact(specs[c]['resource_policy_ref'])
        policy = dict(policy, requested_request_id=request, requested_cohort=c,
                      requested_host_cpu=cpus[c], stage_ready=True, max_global_EP_models=10)
        decision = resource.admit(s, ram, writes, policy)
        decisions[c] = {'pass_admission': decision['pass_admission'],
                        'hold_reasons': decision['hold_reasons']}
    common.put(ROOT / 'control' / ('STAGED_ADMISSION_' + family.upper() + '_' + session + '.json'),
               {'family': family, 'request': request, 'controller_session': session,
                'registry_sha256': s['registry_sha256'], 'cpus': cpus,
                'own_pending_RAM_bytes': ram, 'own_remaining_writes_bytes': writes,
                'decisions': decisions, 'terminal_reconciliation': s.get('exact5_terminal_legacy_reconciliation'),
                'no_model_started': True}, True)
    if not all(d['pass_admission'] for d in decisions.values()):
        common.put(claims_path, {'claims': {}})
        for c in cases:
            (binding_dir / (c + '.json')).unlink()
        print(json.dumps({'status': 'RESOURCE_HOLD_NO_CLAIMS', 'decisions': decisions}))
        sys.exit(2)
    reserve = common.publish_own_write_carrier(claims)
print(json.dumps({'status': 'STAGED_AND_ADMITTED_NO_CONSUMPTION', 'family': family,
                  'session': session, 'cpus': cpus, 'reserve_bytes': reserve,
                  'decisions': decisions}, separators=(',', ':')))
