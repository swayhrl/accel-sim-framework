"""Read only, fail closed checks for the exact five EP-L2 points.

This program does not register science, consume budget, or launch a model.
"""
import hashlib
import json
import pathlib
import subprocess

P = pathlib.Path
J = P('/root/data/ep_l2_full_workload_performance_20261027_v1')
L = J / 'research/next_cost_aware_architecture_20261107_v1'
E = J / 'research/optional_clean128_exact5_execution_20261109_v1'
N = P('/root/data/ep_l2_dtc_l1_native_v2')
REG = N / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH = N / 'control/CURRENT_SCIENCE_EPOCH.json'
EXPECTED = {
    'NEXT_A_OPTIONAL128_GEMM_WV_EXT0_V1': ('A_GEMM_OPTIONAL128_CONTROL3_V1', 0),
    'NEXT_A_OPTIONAL128_GEMM_WV_EXT1_V1': ('A_GEMM_OPTIONAL128_CONTROL3_V1', 1),
    'NEXT_A_OPTIONAL128_GEMM_WV_EXT2_V1': ('A_GEMM_OPTIONAL128_CONTROL3_V1', 2),
    'NEXT_A_OPTIONAL128_STENCIL_WV_EXT0_V1': ('A_STENCIL_OPTIONAL128_NET2_V1', 0),
    'NEXT_A_OPTIONAL128_STENCIL_WV_EXT2_V1': ('A_STENCIL_OPTIONAL128_NET2_V1', 2),
}
AUTH_SHA = '900e9b6b1a31f1a9f3b8dd13c7e4580df415f27af3acc5727e59d930b7d7efc0'
REQUEST_SHA = '646e6b5c718f68de6c1f12fd5c3fc2f0f73b07761757d009d0c773ac790c7247'
SOURCE5 = {
    'core_source_commit': '3d3887bb2e8d5073d13b0792ff9116834e89fe2f',
    'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
    'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
    'binary_sha256': '9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86',
    'archive_sha256': '7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b',
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    digest = hashlib.sha256()
    with P(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(P(path).read_bytes())


def check_ref(item):
    need(sha(item['path']) == item['sha256'], 'reference drift: ' + item['path'])


def main():
    auth = E / 'control/USER_REQUEST.txt'
    request = L / 'agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json'
    need(sha(auth) == AUTH_SHA, 'authorization bytes changed')
    need(sha(request) == REQUEST_SHA, 'final request changed')
    req = read(request)
    need(req['Source5'] == SOURCE5, 'request Source5 changed')
    need({p['point_id'] for p in req['points']} == set(EXPECTED), 'point set changed')
    check_ref(req['source5_ref'])
    for point in req['points']:
        pid = point['point_id']
        need((point['family'], point['victim_extension']) == EXPECTED[pid], 'point family/mode changed: ' + pid)
        need(point['Source5'] == SOURCE5 and point['full_config_option_count'] == 283, 'point Source/config: ' + pid)
        need(point['mode'] == 'WV_ZERO_RO', 'mode changed: ' + pid)
        need(point['only_new_option'] == {'-gpgpu_ep_l2_victim_extension': str(point['victim_extension'])}, 'extension option: ' + pid)
        opts = point['full_effective_option_map']
        need(len(opts) == 283 and opts['-gpgpu_ep_l2_victim_extension'] == str(point['victim_extension']), 'actual283: ' + pid)
        canonical = hashlib.sha256(json.dumps(opts, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        need(canonical == point['full_config_canonical_sha256'], 'canonical283: ' + pid)
        for item in [point['full_config_ref'], point['constructor_receipt_ref'],
                     point['input_identity']['input_binding_ref'], point['input_identity']['historical_template_spec_ref']]:
            check_ref(item)
        inp = point['input_identity']
        need(len(inp['ordered_commands']) == inp['command_count'], 'command count: ' + pid)
        need(len(inp['expected_kernel_launches']) == len(inp['ordered_kernel_identity']), 'kernel population: ' + pid)
        need(point['resources']['bound_logical_CPUs'] == 1, 'CPU contract: ' + pid)
        need(point['resources']['hard_native_result_bytes'] == 64 * 1024 * 1024, 'result limit: ' + pid)
    epoch = read(EPOCH)
    registry = read(REG)
    need(epoch['state'] == 'NATIVE_SCIENCE_ACTIVE' and epoch['epoch'] == 2, 'Native epoch changed')
    need(epoch['native_registry_sha256'] == sha(REG), 'registry/epoch mismatch')
    rows = registry['registered_future_requests']
    matches = {k: v for k, v in rows.items() if any(pid in k for pid in EXPECTED)
               or any(pid in v.get('admitted_specs', {}) for pid in EXPECTED)
               or 'OPTIONAL128' in k or 'CLEAN128' in k}
    active = subprocess.run(['pgrep', '-af', 'accel-sim.out'], text=True, capture_output=True).stdout.splitlines()
    print(json.dumps({'status': 'READ_ONLY_PREACTIVATION_CHECK_PASS', 'point_count': 5,
                      'registry_sha256': sha(REG), 'epoch': epoch['epoch'],
                      'registered_request_count': len(rows), 'matching_requests': list(matches),
                      'observed_model_lines': active,
                      'budget_registration_performed': False, 'model_start_performed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
