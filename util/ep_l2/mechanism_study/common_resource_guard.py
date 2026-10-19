"""A's runtime limit evidence. Policy values come from E's published lease.

This module neither grants resources nor changes the central registry. The
frozen run_owned supervisor catches ResourceLimit and retires only its owned
process group; this helper seals the resource incident before that happens.
"""
import json
import time
from pathlib import Path


class ResourceLimit(RuntimeError):
    pass


def finalize_limit(report, out):
    if not report.get('resource_limit'):
        return
    incident = report['resource_limit']
    incident.update(final_commands=report['commands'],
                    lease_released=report.get('lease_released',False),
                    finished_UTC=report.get('finished_UTC'))
    out = Path(out)
    temporary = out/'RESOURCE_LIMIT.json.tmp'
    temporary.write_text(json.dumps(incident,indent=2)+'\n')
    temporary.replace(out/'RESOURCE_LIMIT.json')


def check_runtime(report, out, live, share_free, written, built, memory_rss,
                  result_growth, build_growth, build_total, baseline_build=0,
                  baseline_results=0, prior_results=None, share_floor=40*2**30,
                  memory_floor=64*2**30, memory_limit=8*2**30):
    if prior_results is not None and prior_results != baseline_results:
        raise RuntimeError('retained result identity/bytes changed; stop affected owned task')
    reasons = []
    if live['disk_free_bytes'] <= report['disk_floor_bytes']:
        reasons.append('WORKSPACE_MONITORED_STOP_MARGIN')
    if share_free < share_floor:
        reasons.append('SHARE_FLOOR')
    if live['available_memory_bytes'] < memory_floor:
        reasons.append('MEMAVAILABLE_FLOOR')
    if memory_rss > memory_limit:
        reasons.append('OWN_PROCESS_TREE_RAM')
    if written >= result_growth:
        reasons.append('OWN_RESULT_GROWTH')
    if built is not None and (built >= build_total or max(0, built-baseline_build) >= build_growth):
        reasons.append('OWN_BUILD_GROWTH')
    if not reasons:
        return
    incident = dict(schema='EP_L2_A_RESOURCE_LIMIT_V1', status='RESOURCE_LIMIT',
        observed_unix=time.time(), campaign_id=report['campaign_id'],
        lease_id=report.get('lease_id'), disk_policy=report.get('E_workspace_disk_policy'),
        E_source_publication=report.get('E_source_publication'),
        E_api_sha256=report.get('E_resource_api_sha256'), reasons=reasons,
        actual_resources=dict(live), share_free_bytes=share_free,
        physical_workspace_floor_bytes=report['authorized_task_floor_bytes'],
        monitored_stop_bytes=report['disk_floor_bytes'],
        monitor_reserve_bytes=report.get('monitor_reserve_bytes',0),
        own_result_bytes=written, result_growth_bytes=result_growth,
        own_build_bytes=built, inherited_build_bytes=baseline_build,
        build_growth_bytes=build_growth, build_total_cap_bytes=build_total,
        own_process_tree_rss_bytes=memory_rss, memory_limit_bytes=memory_limit,
        retained_result_bytes=prior_results, retained_result_expected_bytes=baseline_results,
        commands=[dict(command=c['command'], process=c.get('process'), log=c['log'])
                  for c in report.get('commands',[])],
        scope='STOP_ONLY_OWNED_PROCESS_GROUP; preserve all logs/receipts; no new task',
        native_or_application_qualification=False)
    report['resource_limit'] = incident
    out = Path(out)
    tmp = out/'RESOURCE_LIMIT.json.tmp'
    tmp.write_text(json.dumps(incident,indent=2)+'\n')
    tmp.replace(out/'RESOURCE_LIMIT.json')
    raise ResourceLimit(','.join(reasons))
