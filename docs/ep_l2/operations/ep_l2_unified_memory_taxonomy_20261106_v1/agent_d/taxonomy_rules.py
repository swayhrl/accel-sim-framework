"""CPU-only taxonomy rules. No model, raw, trace, registry or network operation."""
from math import isfinite
SOURCE5 = ('core_source_commit','framework_source_commit','vendor_pybind11_commit','binary_sha256','archive_sha256')
def number(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and isfinite(v) and v >= 0
def pressure(block_events=None, peak=None, capacity=None):
    if number(block_events):
        if block_events > 0: return 'OBSERVED_RESOURCE_BLOCKING'
        if number(peak) and number(capacity) and peak >= capacity:
            return 'BOUNDARY_REACHED_NO_BLOCK_OBSERVED'
        return 'NO_BLOCK_OBSERVED_IN_MEASURED_SCOPE'
    return 'UNKNOWN'
def activity(n):
    return 'OBSERVED_ACTIVITY' if number(n) and n > 0 else ('NONE_OBSERVED_IN_MEASURED_SCOPE' if n == 0 and number(n) else 'UNKNOWN')
def match_identity(a,b):
    """Missing identities never match; callers must supply exact full option maps."""
    keys=(*SOURCE5,'input_identity_sha256','literal_commandlist_sha256','ordered_kernel_identity_sha256','observer_identity_sha256')
    return all(a.get(k) is not None and a.get(k)==b.get(k) for k in keys)
def service_sensitivity(ref,candidate,identity_match=False,declared_service_only=False):
    if not identity_match or not declared_service_only or not number(ref) or not number(candidate) or ref == 0 or candidate == 0:
        return {'label':'UNKNOWN','cycle_change_fraction':None}
    delta=(ref-candidate)/ref
    return {'label':('MEASURED_SERVICE_RESPONSE_POSITIVE' if delta>0 else 'MEASURED_SERVICE_RESPONSE_NEGATIVE' if delta<0 else 'NO_CYCLE_RESPONSE_IN_THIS_PAIR'),
            'cycle_change_fraction':delta}
def classify_endpoint(m):
    """Labels require positive measurements, never the EP final speedup."""
    return {
      'ordinary_line_MSHR_pressure':pressure(m.get('line_full_events'),m.get('line_peak'),m.get('line_capacity')),
      'descriptor_pressure':pressure(m.get('descriptor_full_events'),m.get('descriptor_peak'),m.get('descriptor_capacity')),
      'per_address_pressure':pressure(m.get('per_address_block_events')),
      'Tag_reserved_pressure':pressure(m.get('tag_reserved_block_events')),
      'W_WB_activity':activity(m.get('wb_created')),
      'W_WB_data_pressure':pressure(m.get('wb_data_space_head_observations')),
      'V_realized_retained_sector_service':activity(m.get('victim_served_sectors')),
      'program_sector_temporal_reuse':m.get('exact_input_reuse_analysis_label') or 'UNKNOWN',
      'RO_admission_activity':activity(m.get('ro_accepted')),
      'RO_merge_activity':activity(m.get('ro_merges')),
      'RO_pressure_policy_activation':activity(m.get('pressure_epoch_activations')),
      'M_T_joint_pressure':m.get('exact_joint_pressure_label') or 'UNKNOWN'
    }
def allowed_policy_pair(a,b,option='-gpgpu_ep_l2_ro_pressure_epoch'):
    if len(a)!=283 or len(b)!=283 or set(a)!=set(b): return False
    return a.get(option)=='0' and b.get(option)=='1' and [k for k in a if a[k]!=b[k]]==[option]
