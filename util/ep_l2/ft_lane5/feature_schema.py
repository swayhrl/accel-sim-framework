"""Explicit RO detach/bypass vectors; legacy R0 identities stay immutable."""
from copy import deepcopy
from registry import run_key

COMMON = {'finite_wbuf', 'unified_wb', 'tvd', 'adaptive_policy', 'wbuf_entries',
          'payload_capacity_per_slice', 'bank_count', 'ops_per_bank_cycle'}
V1 = COMMON | {'ro'}
V2 = COMMON | {'ro_tag_detach', 'ro_line_mshr_bypass'}


def ro_bits(vector):
    """Return explicit bits without guessing an old ambiguous enabled-RO mode."""
    if set(vector) == V1:
        if vector['ro'] is not False:
            raise ValueError('legacy enabled RO has no certified detach/bypass mapping')
        return False, False
    if set(vector) != V2:
        raise ValueError('feature vector must be complete V1 or complete V2')
    if type(vector['ro_tag_detach']) is not bool or type(vector['ro_line_mshr_bypass']) is not bool:
        raise ValueError('RO detach/bypass flags must be explicit booleans')
    return vector['ro_tag_detach'], vector['ro_line_mshr_bypass']


def legacy_view(identity):
    """Read-only display projection, not a new run identity or qualification."""
    key = run_key(identity)
    vector = identity['feature_vector']
    if set(vector) != V1:
        raise ValueError('only a legacy V1 record needs this projection')
    detach, bypass = ro_bits(vector)
    display = {k: deepcopy(v) for k, v in vector.items() if k != 'ro'}
    display.update(ro_tag_detach=detach, ro_line_mshr_bypass=bypass)
    return {'schema_version': 'EPL2_FEATURE_VIEW_V2', 'original_run_key': key,
            'original_identity': deepcopy(identity), 'feature_vector_display': display,
            'projection_only': True, 'new_run_key_issued': False,
            'qualification': 'unchanged; projection confers no new feature qualification'}
