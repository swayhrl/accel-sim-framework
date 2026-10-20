"""User-authorized P9 B0028 ACK / B0029-B0033 COPY-only exception.

No transfer, publication or unlink is performed by this pure evaluator.
The old 16/20/48 GiB policies and release controller remain unchanged.
"""
import math
from dataclasses import replace

import tls_v10_copy_only16g_gate as original
import tls_v10_copy_only20g_gate as frozen

POLICY_ID = 'TLS_V10_P9_REMAINING_COPY_ONLY_5G_20261020_V1'
FLOOR = 5 * frozen.GIB
CONTROL_RESERVE = 32 * frozen.MIB
TEMP_RESERVE = 256 * frozen.MIB
HORIZON_SECONDS = 120
MAX_BUFFER = frozen.MIB


def growth_reserve(first_free, last_free, elapsed):
    """Project twice measured consumption for 120s, plus a 256MiB minimum.

    Reclamation never offsets predicted writes. All source controls are
    reserved separately; source payloads are never staged on workspace.
    """
    if not 1 <= elapsed <= 30:
        raise ValueError('growth sample interval outside 1..30 seconds')
    if min(first_free, last_free) < 0:
        raise ValueError('negative available bytes')
    return max(TEMP_RESERVE,
               math.ceil(max(0, first_free-last_free) / elapsed *
                         HORIZON_SECONDS * 2))


def evaluate(item, *, window, action, predicted_growth_bytes,
             growth_sample_age_seconds, buffer_bytes=MAX_BUFFER):
    """Apply exact original non-workspace rules and the real 5GiB floor.

    Copy16's workspace check is reproduced explicitly, never fed invented
    available bytes. Only its workspace-floor reason can be replaced, after
    every immutable P9 identity has been checked by that original evaluator.
    """
    result = original.evaluate(item)
    reasons = [v for v in result['reasons']
               if v != 'WORKSPACE_F_BAVAIL_OR_PROJECTED_HEADROOM_BELOW_FLOOR']
    b = item.base
    allowed = ((window == 28 and action == 'ack-publish') or
               (29 <= window <= 33 and action in
                ('prepare', 'stage', 'publish', 'ack-prepare', 'ack-publish')))
    if not allowed or b.operation != 'TLS_V10_COPY_ONLY' or b.source_unlink_requested:
        reasons.append('OUTSIDE_EXACT_P9_REMAINING_COPY_SCOPE')
    if (type(predicted_growth_bytes) is not int or
            predicted_growth_bytes < TEMP_RESERVE or
            not 0 <= growth_sample_age_seconds <= 30):
        reasons.append('GROWTH_PROJECTION_MISSING_STALE_OR_UNDER_RESERVED')
    if not 0 < buffer_bytes <= MAX_BUFFER:
        reasons.append('BUFFER_LIMIT')
    projected = (b.workspace_available_bytes - CONTROL_RESERVE -
                 predicted_growth_bytes)
    if b.workspace_available_bytes < FLOOR or projected < FLOOR:
        reasons.append('ACTUAL_OR_CONSERVATIVE_PROJECTED_WORKSPACE_BELOW_5G')
    return dict(result, decision='POLICY_ELIGIBLE_NOT_READY' if not reasons else 'RESOURCE_HOLD',
                policy_id=POLICY_ID, effective_workspace_floor_bytes=FLOOR,
                actual_workspace_available_bytes=b.workspace_available_bytes,
                projected_workspace_available_bytes=projected,
                predicted_external_growth_bytes=predicted_growth_bytes,
                control_write_reserve_bytes=CONTROL_RESERVE,
                projection_horizon_seconds=HORIZON_SECONDS,
                source_unlink_authorized=False, reasons=reasons)
