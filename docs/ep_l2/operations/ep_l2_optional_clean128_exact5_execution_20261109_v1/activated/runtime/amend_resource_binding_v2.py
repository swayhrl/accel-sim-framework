#!/usr/bin/env python3
"""Version the unconsumed exact5 specs for the proven resource adapter fix."""
import hashlib
import importlib.util
import json
import pathlib

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FAMILIES = {
    'gemm': ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
             ['EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1', 'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1']),
    'stencil': ('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
                ['EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1', 'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1']),
}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


for family, (request, cases) in FAMILIES.items():
    module_path = ROOT / 'runtime' / ('host_' + family + '_bound_v2') / 'ep_perf_common_v2.py'
    modspec = importlib.util.spec_from_file_location('exact5_common_' + family, module_path)
    common = importlib.util.module_from_spec(modspec)
    modspec.loader.exec_module(common)
    adapter = module_path.with_name('resources_exact5_v2.py')
    adapter_ref = common.ref(adapter)
    specs = {}
    old = {}
    for case in cases:
        path = ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'
        prior = ROOT / 'cases' / case / 'control/FROZEN_SPEC.version1.json'
        if prior.exists():
            raise RuntimeError('version1 archive already exists; inspect before resume')
        old[case] = common.ref(path)
        value = common.read(path)
        assert value['resource_module_ref']['path'].endswith('resources_b1.py')
        value['resource_module_ref'] = adapter_ref
        specs[case] = value
    registry, _ = common.authority()
    row = registry['registered_future_requests'][request]
    assert not row['consumed'] and row['remaining'] == row['budget'] == len(cases)
    assert row['admitted_specs'] == {case: old[case]['sha256'] for case in cases}
    for case in cases:
        control = ROOT / 'cases' / case / 'control'
        (control / 'FROZEN_SPEC.version1.json').write_bytes((control / 'FROZEN_SPEC.json').read_bytes())
        assert sha(control / 'FROZEN_SPEC.version1.json') == old[case]['sha256']
        pre = control / 'NATIVE_PRELAUNCH_QUALIFICATION.json'
        if pre.exists():
            pre.rename(control / 'NATIVE_PRELAUNCH_QUALIFICATION.version1.json')

    def amend(reg):
        q = reg['registered_future_requests'][request]
        assert not q['consumed'] and q['admitted_specs'] == {c: old[c]['sha256'] for c in cases}
        new = {}
        for case in cases:
            path = ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'
            common.put(path, specs[case])
            new[case] = sha(path)
            q['admitted_specs'][case] = new[case]
        common.put(ROOT / 'control' / ('RESOURCE_BINDING_AMENDMENT_' + family.upper() + '_V2.json'),
                   {'schema': 'EP_L2_EXACT5_UNCONSUMED_RESOURCE_ADAPTER_AMENDMENT_V2',
                    'request': request, 'old_specs': old, 'new_spec_sha256': new,
                    'adapter_ref': adapter_ref, 'consumed_at_amendment': 0,
                    'native_epoch_unchanged': True, 'budget_unchanged': True,
                    'foreign_write_commitments_retained': True}, True)
        return new
    result = common.transaction('AMEND_UNCONSUMED_RESOURCE_ADAPTER_V2_KEEP_BUDGET', amend)
    print(json.dumps({'family': family, 'request': request, 'adapter_ref': adapter_ref,
                      'new_spec_sha256': result}, separators=(',', ':')))
