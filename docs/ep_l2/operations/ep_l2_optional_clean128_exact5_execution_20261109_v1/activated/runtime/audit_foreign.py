#!/usr/bin/env python3
"""Read-only audit of resource adapter's unmapped owner rows."""
import json
from pathlib import Path

p = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
reg = json.loads(p.read_bytes())
names = [
    'DTC_ORACLE_INITIAL8_20261106_V1',
    'DTC_ORACLE_REMAINING24_20261106_V1',
    'DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1',
    'DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1',
    'DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1',
    'DTC_PERF_FIRST_V2_PHYSICAL_PIB16_20261105_V1',
    'EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1',
    'EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1',
    'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1',
    'EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1',
    'EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1',
    'EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104',
]
for name in names:
    q = reg['registered_future_requests'][name]
    consumed = q.get('consumed', {})
    states = {}
    if isinstance(consumed, dict):
        for row in consumed.values():
            key = row.get('state', 'NO_STATE') if isinstance(row, dict) else 'NON_DICT'
            states[key] = states.get(key, 0) + 1
    sample = next(iter(consumed.values()), {}) if isinstance(consumed, dict) else {}
    print(json.dumps({'request': name, 'state': q.get('state'), 'budget': q.get('budget'),
                      'remaining': q.get('remaining'), 'consumed_count': len(consumed),
                      'consumed_states': states, 'reserved_write_bytes': q.get('reserved_write_bytes'),
                      'sample_row_keys': sorted(sample) if isinstance(sample, dict) else [],
                      'sample_row': sample if name.startswith('DTC_') else None},
                     separators=(',', ':')))
