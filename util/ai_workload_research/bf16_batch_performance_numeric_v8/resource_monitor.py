"""NVML snapshot collection and policy shared by real supervision and CPU mocks."""
import os
from pathlib import Path
class MonitorStop(RuntimeError):
    def __init__(self,status,reason):
        super().__init__(reason); self.status=status
def normalize_memory(value):
    if value is None: return None
    try: value=int(getattr(value,"value",value))
    except (TypeError,ValueError,OverflowError): return None
    return None if value<0 or value>=(1<<64)-1 else value
def normalize_pid(value):
    if value is None or isinstance(value,bool): return None
    try: value=int(getattr(value,"value",value))
    except (TypeError,ValueError,OverflowError): return None
    return value if value>0 else None
def disk_bytes(root):
    total=0
    for parent,dirs,files in os.walk(root):
        for name in files:
            p=Path(parent)/name
            try: total+=p.stat().st_size
            except FileNotFoundError: pass
    return total
def collect_snapshot(nv,handle,ps,root_pid,owned,phase,wall,held_seconds,goal_elapsed,disk,lifecycle=None):
    censored=[];observed=[]
    if lifecycle is None:
        live={root_pid}; gaps=[]
        try: live.update(p.pid for p in ps.Process(root_pid).children(recursive=True))
        except Exception as e: gaps.append("OWN_TREE:"+type(e).__name__)
        owned.update(live);rss=0
        for pid in live:
            try:rss+=ps.Process(pid).memory_info().rss
            except Exception as e:gaps.append("RSS_PID_"+str(pid)+":"+type(e).__name__)
    else:
        live,rss,gaps,censored,observed=lifecycle.rss(phase)
        owned.update(live)
        owned.update(x['pid'] for x in censored)
    merged={};unknown_rows=[]
    for kind,fn in [("compute",nv.nvmlDeviceGetComputeRunningProcesses),("graphics",nv.nvmlDeviceGetGraphicsRunningProcesses)]:
        for info in fn(handle):
            pid=normalize_pid(getattr(info,"pid",None));mem=normalize_memory(getattr(info,"usedGpuMemory",None))
            if pid is None:
                unknown_rows.append(dict(pid=None,kinds=[kind],usedGpuMemory=mem,reason="INVALID_PID"));continue
            if pid not in merged:merged[pid]=dict(pid=pid,kinds=[],usedGpuMemory=mem,memory_observation_consistent=True)
            item=merged[pid];item["kinds"].append(kind)
            if item["usedGpuMemory"]!=mem:item["memory_observation_consistent"]=False
    external=[];unknown=[];ownmem=0
    for pid,item in merged.items():
        if pid not in owned:external.append(pid)
        try:alive=bool(ps.pid_exists(pid))
        except Exception:alive=False
        if not alive or item["usedGpuMemory"] is None or not item["memory_observation_consistent"]:
            unknown.append(pid)
        elif pid in owned:ownmem+=item["usedGpuMemory"]
    state="UNKNOWN" if unknown or unknown_rows or gaps else "EXTERNAL_GPU_PID" if external else "OWN_LIVE_PID" if merged else "EMPTY"
    row=dict(wall_time=wall,held_seconds=held_seconds,goal_elapsed_seconds=goal_elapsed,phase=phase,state=state,live_own_pids=sorted(live),known_own_pids=sorted(owned),gpu_processes=list(merged.values())+unknown_rows,external_gpu_pids=sorted(external),unknown_gpu_pids=sorted(unknown),invalid_pid_rows=unknown_rows,monitor_gaps=gaps,own_NVML_bytes=ownmem,own_NVML_MiB=ownmem/1024**2,own_tree_RSS_bytes=rss,own_new_disk_bytes=disk)
    if lifecycle is not None:
        row.update(rss_censored_observations=censored,rss_observed_processes=observed,
          rss_sample_complete=not bool(censored),rss_lifecycle_rule='V7_NARROW_EXITED_CHILD')
        lifecycle.gpu_identity_checks(row)
        if row['monitor_gaps']:row['state']='UNKNOWN'
    return row
def enforce_snapshot(row,cfg):
    if row["unknown_gpu_pids"] or row["invalid_pid_rows"] or row["monitor_gaps"]:
        raise MonitorStop("GPU_RESOURCE_DEFERRED","Unknown GPU PID/memory or incomplete resource observation")
    if row.get("unqualified_external_gpu_pids",row["external_gpu_pids"]):
        raise MonitorStop("GPU_RESOURCE_DEFERRED","External GPU process lacks desktop qualification: "+str(row.get("unqualified_external_gpu_pids",row["external_gpu_pids"])))
    if row.get("external_NVML_bytes",0)>cfg.get("desktop_external_vram_bytes_max",512*1024**2):
        raise MonitorStop("GPU_RESOURCE_DEFERRED","External desktop VRAM exceeds512MiB")
    for key,limit in [("own_NVML_bytes","own_vram_bytes_max"),("own_tree_RSS_bytes","rss_bytes_max"),("own_new_disk_bytes","disk_bytes_max")]:
        if row[key]>cfg[limit]:raise MonitorStop("INCONCLUSIVE","Resource limit: "+key)
    if row["held_seconds"]>cfg["held_seconds_max"]-cfg["shutdown_reserve_seconds"]:
        raise MonitorStop("INCONCLUSIVE","GPU deadline shutdown reserve")
    if row["goal_elapsed_seconds"]>cfg["goal_seconds_max"]-25:
        raise MonitorStop("INCONCLUSIVE","Goal deadline archival reserve")
