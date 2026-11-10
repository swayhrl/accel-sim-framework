#!/usr/bin/env python3
"""Version the resource adapter binding for four unconsumed exact5 points."""
import importlib.util
import json
import pathlib
import shutil

root = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
targets = {
    'gemm': ('EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1',
             'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1'),
    'stencil': ('EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
                'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'),
}
for family, cases in targets.items():
    host = root / 'runtime' / ('host_' + family + '_bound_v2')
    mod = importlib.util.spec_from_file_location('exact5_rebind_common_' + family,
                                                  host / 'ep_perf_common_v2.py')
    c = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(c)
    adapter = host / 'resources_exact5_v3.py'
    assert adapter.is_file()
    new_ref = c.ref(adapter)
    with c.locked(c.GLOBAL_MAIN_ADMISSION_LOCK):
        reg, epoch = c.authority()
        q = reg['registered_future_requests'][c.GOAL]
        claims = c.read(root / 'control/DISPATCH_CLAIMS.json')['claims']
        changes = {}
        for case in cases:
            path = root / 'cases' / case / 'control/FROZEN_SPEC.json'
            old_sha = c.sha(path)
            old = c.read(path)
            assert old['science_request_id'] == c.GOAL
            assert q['admitted_specs'][case] == old_sha
            assert case not in q['consumed'] and case not in claims
            assert old['resource_module_ref']['path'].endswith('resources_exact5_v2.py')
            prior = path.with_name('FROZEN_SPEC.resource_v2.json')
            assert not prior.exists()
            shutil.copy2(path, prior)
            assert c.sha(prior) == old_sha
            updated = dict(old, resource_module_ref=new_ref)
            c.put(path, updated)
            changes[case] = {'prior_spec_ref': c.ref(prior),
                             'current_spec_ref': c.ref(path),
                             'prior_resource_ref': old['resource_module_ref'],
                             'current_resource_ref': new_ref}
        def publish(registry):
            request = registry['registered_future_requests'][c.GOAL]
            for case, refs in changes.items():
                assert request['admitted_specs'][case] == refs['prior_spec_ref']['sha256']
                request['admitted_specs'][case] = refs['current_spec_ref']['sha256']
        c.transaction('REBIND_UNCONSUMED_EXACT5_RESOURCE_ADAPTER_V3', publish)
        for case in cases:
            receipt = root / 'cases' / case / 'control/NATIVE_PRELAUNCH_QUALIFICATION.json'
            prior = receipt.with_name('NATIVE_PRELAUNCH_QUALIFICATION.resource_v2.json')
            assert receipt.exists() and not prior.exists()
            shutil.copy2(receipt, prior)
            receipt.unlink()
            changes[case]['prior_prepare_ref'] = c.ref(prior)
        c.put(root / 'control' / ('RESOURCE_V3_REBIND_' + family.upper() + '.json'),
              {'schema': 'EP_EXACT5_UNCONSUMED_RESOURCE_ADAPTER_REBIND_V1',
               'request': c.GOAL, 'utc': c.now(), 'adapter_reason':
               'map verified live exact5 peer while retaining terminal legacy owner writes',
               'consumed_points_untouched': True, 'changes': changes}, True)
    print(json.dumps({'request': c.GOAL, 'updated': list(cases),
                      'resource_module_sha256': new_ref['sha256']}))
