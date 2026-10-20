"""Validate signed Source stage evidence; no I/O or Source authority creation.

The additive COPY5 policy belongs to Source and only covers the original
P9 remaining COPY-only windows. Target resource and release rules stay intact.
"""
import math

GIB = 1024**3
MIB = 1024**2
COPY5 = 'TLS_V10_P9_REMAINING_COPY_ONLY_5G_20261020_V1'
POLICY_SHA = '3b022a09f9c47f7dc5ebf3f0f98a64655b50043722d2d44cabf5eafe8815f4ec'


def verify_stage(window_id, stage, *, copy5_policy_sha=None):
    d = stage['decision']
    assert d['decision'] == 'POLICY_ELIGIBLE_NOT_READY' and d['reasons'] == []
    floor = d['effective_workspace_floor_bytes']
    if floor == 5 * GIB:
        assert copy5_policy_sha == POLICY_SHA, 'unreviewed Source COPY5 authority'
        prefix = 'TLS_V10_P9_PUBLIC_B'
        assert window_id.startswith(prefix) and len(window_id) == len(prefix) + 4
        number = int(window_id[len(prefix):])
        assert 29 <= number <= 33, 'COPY5 receive outside exact remaining P9'
        assert d['policy_id'] == COPY5 and d['source_unlink_authorized'] is False
        assert d['control_write_reserve_bytes'] == 32 * MIB
        assert d['projection_horizon_seconds'] == 120
        growth = d['predicted_external_growth_bytes']
        sample = stage['growth_sample']
        elapsed = sample['interval_seconds']
        assert 1 <= elapsed <= 30
        assert min(sample['first_available_bytes'], sample['last_available_bytes']) >= 0
        expected = max(256 * MIB, math.ceil(max(
            0, sample['first_available_bytes'] - sample['last_available_bytes']) / elapsed * 240))
        assert type(growth) is int and growth >= expected
        assert sample['last_available_bytes'] == stage['workspace_available_bytes']
        assert d['actual_workspace_available_bytes'] == stage['workspace_available_bytes']
        assert d['projected_workspace_available_bytes'] == (
            stage['workspace_available_bytes'] - 32 * MIB - growth)
    else:
        assert floor == 16 * GIB, 'unrecognized Source workspace policy'
    assert stage['workspace_available_bytes'] >= floor
    assert d['projected_workspace_available_bytes'] >= floor
    assert stage['share_available_bytes'] >= 40 * GIB
    assert 0 <= stage['snapshot_age_seconds'] <= 30
    assert 0 <= stage['staged_physical_bytes'] <= 256 * MIB
    return floor
