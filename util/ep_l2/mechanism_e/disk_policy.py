"""Explicit user amendment, scoped to new leases of the existing original174 campaign.

Never mutates the legacy Registry host policy, existing leases, tokens or receipts.
The two GiB stop reserve covers sampled detection and owned-group termination;
all remaining own writes are additionally reserved at admission. External actors
cannot be stopped here. An abrupt external write beyond the reserve is not a
claimed hard OS quota guarantee.
"""
import copy
import time

GIB=2**30
CAMPAIGN='EPL2_MECHANISM_STUDY_20261019_V1'
FIELD='mechanism_study_20261019_v1'
POLICY_ID='E_USER_WORKSPACE_5G_20261020_V1'
FLOOR=5*GIB
MONITOR=2*GIB
POLL_SECONDS=.2
TERMINATION_GRACE_SECONDS=3


def amendment(host,boot_id):
    return dict(policy_id=POLICY_ID,campaign_id=CAMPAIGN,host=host,boot_id=boot_id,
        authority='EXPLICIT_USER_20261020_WORKSPACE_FLOOR_5G',
        disk_floor_bytes=FLOOR,monitor_reserve_bytes=MONITOR,
        monitor_interval_seconds=POLL_SECONDS,termination_grace_seconds=TERMINATION_GRACE_SECONDS,
        write_scope='PHYSICAL_WORKSPACE_ALL_TMP_BUILD_LOG_RESULT',
        existing_leases_unchanged=True,other_projects_unchanged=True)


def policy(item):
    row=item.get('workspace_disk_policy')
    if row is None:
        return dict(policy_id='HISTORICAL_48G',disk_floor_bytes=48*GIB,monitor_reserve_bytes=0,
                    monitor_interval_seconds=2,termination_grace_seconds=3)
    expected=amendment(item['host'],item['boot_id'])
    if item['campaign_id']!=CAMPAIGN or any(row.get(k)!=v for k,v in expected.items()):
        raise ValueError('invalid campaign-scoped workspace disk amendment')
    return copy.deepcopy(row)


def lease_policy(item):
    row=policy(item)
    return {k:row[k] for k in ('policy_id','disk_floor_bytes','monitor_reserve_bytes',
                              'monitor_interval_seconds','termination_grace_seconds')}


def stop_detail(resources,lease):
    floor=lease.get('disk_floor_bytes',48*GIB)
    margin=lease.get('monitor_reserve_bytes',0)
    if resources['disk_free_bytes']<=floor+margin:
        return dict(status='RESOURCE_LIMIT',reason='WORKSPACE_STOP_RESERVE',
            observed_free_bytes=resources['disk_free_bytes'],disk_floor_bytes=floor,
            monitor_reserve_bytes=margin,stop_at_bytes=floor+margin,
            policy_id=lease.get('policy_id','HISTORICAL_48G'),observed_unix=time.time())
    return None


def scoped_registry_view(data,host,floor):
    # Called only after Coordinator has validated campaign identity and policy.
    view=copy.deepcopy(data)
    view['hosts'][host]['min_disk_free_bytes']=floor
    return view
