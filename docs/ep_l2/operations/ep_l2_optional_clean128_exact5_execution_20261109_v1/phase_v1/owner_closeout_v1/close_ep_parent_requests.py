"""EP Main: close three fully accepted parent requests through owner transactions.

Default is read-only preflight. --apply changes only each owned request's state.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = Path('/root/data/ep_l2_dtc_l1_native_v2')
REQUESTS = (
    ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1', 'host_gemm_bound_v2'),
    ('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1', 'host_stencil_bound_v2'),
    ('EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1', 'host_stencil_ext1_bound_v1'),
)


def load_owner_module(folder, name):
    path = ROOT / 'runtime' / folder / 'ep_perf_common_v2.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_request(module, registry, request):
    q = registry['registered_future_requests'][request]
    module.need(q['owner'] == 'EP-L2 Main', 'foreign owner: ' + request)
    module.need(q['state'] in ('RUNNING', 'CLOSED_COMPLETED'), 'unexpected parent state: ' + request)
    module.need(q['remaining'] == 0 and q['reserved_write_bytes'] == 0, 'remaining budget or write carrier: ' + request)
    rows = q['consumed']
    module.need(len(rows) == q['budget'], 'incomplete cohort count: ' + request)
    cohort_rows = []
    for cohort, row in sorted(rows.items()):
        module.need(row['state'] == 'CLOSED_ACCEPTED' and row['consumed'] == 1
                    and row['remaining'] == 0 and row['remaining_write_bytes'] == 0,
                    'child not accepted once: ' + cohort)
        receipt_ref = row['archive_receipt_ref']
        module.need(sha(receipt_ref['path']) == receipt_ref['sha256'], 'archive receipt drift: ' + cohort)
        receipt = module.read(receipt_ref['path'])
        module.need(receipt['status'] == 'TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS'
                    and receipt['cohort'] == cohort and receipt['uuid'] == row['uuid']
                    and receipt['source_keep'] is True, 'archive closure mismatch: ' + cohort)
        restores = receipt['native_restores']
        module.need(len(restores) == 2 and len({r['target'] for r in restores}) == 2
                    and all(r['status'] == 'INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS'
                            and r['source_keep'] is True for r in restores),
                    'two independent restores absent: ' + cohort)
        cohort_rows.append(dict(cohort=cohort, uuid=row['uuid'], state=row['state'],
                                receipt_sha256=receipt_ref['sha256']))
    return dict(request=request, before_state=q['state'], budget=q['budget'], remaining=q['remaining'],
                reserved_write_bytes=q['reserved_write_bytes'], cohorts=cohort_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    modules = {req: load_owner_module(folder, 'ep_parent_' + str(i))
               for i, (req, folder) in enumerate(REQUESTS)}
    first = modules[REQUESTS[0][0]]
    registry, epoch = first.authority()
    before = copy.deepcopy(registry)
    pre_sha = sha(first.REG)
    claims = first.read(ROOT / 'control/DISPATCH_CLAIMS.json')['claims']
    owned = [cohort for cohort, claim in claims.items() if claim.get('request') in modules]
    first.need(not owned, 'owned cohort still claimed')
    checks = [check_request(modules[req], registry, req) for req, _ in REQUESTS]
    first.need(sum(first.remaining(q) for q in registry['registered_future_requests'].values())
               == registry['new_scientific_budget_remaining'] == epoch['new_budget_remaining'],
               'global budget mismatch')
    if not args.apply:
        print(json.dumps(dict(status='PREFLIGHT_PASS', epoch=epoch['epoch'], registry_sha256=pre_sha,
                              owned_claims=owned, requests=checks), sort_keys=True))
        return
    for req, _ in REQUESTS:
        module = modules[req]

        def close(current, request=req, owner_module=module):
            checked = check_request(owner_module, current, request)
            owner_module.need(checked['before_state'] == 'RUNNING', 'parent changed before closure: ' + request)
            current['registered_future_requests'][request]['state'] = 'CLOSED_COMPLETED'

        if before['registered_future_requests'][req]['state'] == 'RUNNING':
            module.transaction('CLOSE_FULLY_ACCEPTED_PARENT_REQUEST_KEEP_CHARGE_AND_SOURCE', close)
    after, after_epoch = first.authority()
    expected = copy.deepcopy(before)
    for req, _ in REQUESTS:
        expected['registered_future_requests'][req]['state'] = 'CLOSED_COMPLETED'
    first.need(after == expected, 'postflight registry differs beyond three parent states')
    first.need(after_epoch['new_budget_remaining'] == epoch['new_budget_remaining'],
               'global budget changed')
    post_checks = [check_request(modules[req], after, req) for req, _ in REQUESTS]
    first.need(all(x['before_state'] == 'CLOSED_COMPLETED' for x in post_checks), 'postflight state')
    receipt = dict(schema='EP_L2_PARENT_REQUEST_CLOSEOUT_V1', status='CLOSED_COMPLETED_VERIFIED',
                   utc=first.now(), epoch=epoch['epoch'], pre_registry_sha256=pre_sha,
                   post_registry_sha256=sha(first.REG), global_budget_unchanged=True,
                   foreign_requests_unchanged=True, charged_starts_unchanged=True,
                   source_keep=True, owned_claims_empty=True, requests=post_checks)
    target = ROOT / 'control/EP_L2_PARENT_REQUEST_CLOSEOUT_20261111_V1.json'
    first.put(target, receipt, True)
    print(json.dumps(dict(receipt=str(target), **receipt), sort_keys=True))


if __name__ == '__main__':
    main()
