"""Exact5 resource adapter for terminal legacy rows unknown to V3.

Keep the V3 accounting and every advertised write commitment. Clear only
its stale unmapped-RAM diagnostics after a fresh, bounded terminal audit.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REG = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH = Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
FAMILY = 'gemm' if 'host_gemm_bound_v2' in __file__ else 'stencil'
ORIGINAL = Path(__file__).with_name('resources_b1.py')
PIN = {'gemm': 'a7bd990569f2f2ea025a1e7063b18a3f6b0fa0f5aa611d56d838d0e1838dfd81',
       'stencil': '589d2d8944de8737d9eaa7d1b33624d8b8fdbaf4d06e9db0d92cd835aa24ba26'}[FAMILY]
EP_CLOSED = {
    'EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1',
    'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1',
    'EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1',
    'EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104',
}
DTC_TERMINAL = {
    'DTC_ORACLE_INITIAL8_20261106_V1',
    'DTC_ORACLE_REMAINING24_20261106_V1',
    'DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1',
    'DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1',
    'DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1',
    'DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1',
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def original():
    if sha(ORIGINAL) != PIN:
        raise ValueError('pinned original resource adapter drift')
    spec = importlib.util.spec_from_file_location('exact5_original_resources_' + FAMILY, ORIGINAL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot():
    s = original().snapshot()
    before = s.get('foreign_metadata_errors', [])
    if not before:
        return s
    raw = REG.read_bytes()
    epoch = json.loads(EPOCH.read_bytes())
    if hashlib.sha256(raw).hexdigest() != s.get('registry_sha256') or epoch['native_registry_sha256'] != s['registry_sha256']:
        return s
    reg = json.loads(raw)['registered_future_requests']
    if s.get('actual_loader_aware_models'):
        return s
    cleared = []
    for name in EP_CLOSED | DTC_TERMINAL:
        q = reg[name]
        rows = q.get('consumed')
        if not isinstance(rows, dict) or q.get('remaining') != 0 or len(rows) != q.get('budget'):
            return s
        if name in EP_CLOSED:
            if q.get('state') != 'CLOSED_COMPLETED' or q.get('reserved_write_bytes') != 0 or any(
                    row.get('state') not in ('CLOSED_ACCEPTED', 'CLOSED_UNACCEPTED') for row in rows.values()):
                return s
        else:
            if q.get('state') != 'RUNNING' or any(not isinstance(row.get('execution_receipt'), dict)
                    or row.get('charged') != 1 for row in rows.values()):
                return s
        cleared.append('unmapped active foreign RAM owner ' + name)
    if not set(cleared).issubset(before):
        return s
    s['foreign_metadata_errors'] = [e for e in before if e not in cleared]
    s['exact5_terminal_legacy_reconciliation'] = {
        'cleared_errors': sorted(cleared), 'registry_sha256': s['registry_sha256'],
        'DTC_advertised_write_commitments_retained': True,
        'no_live_models_at_snapshot': True,
    }
    return s


def admit(s, additional, writes, policy):
    return original().admit(s, additional, writes, policy)
