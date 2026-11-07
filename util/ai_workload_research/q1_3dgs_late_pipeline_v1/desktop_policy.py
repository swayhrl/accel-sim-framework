"""Evidence-constrained desktop co-residence. No process arguments or environment reads."""
import os
from pathlib import Path
from resource_monitor import MonitorStop
def read_identity(pid):
    p=Path("/proc")/str(pid)
    stat=(p/"stat").read_text().split(") ",1)[1].split()
    uid=next(line.split()[1:] for line in (p/"status").read_text().splitlines() if line.startswith("Uid:"))
    return dict(pid=pid,ppid=int(stat[1]),uids=[int(v) for v in uid],comm=(p/"comm").read_text().strip(),cgroup=(p/"cgroup").read_text().strip(),start_ticks=int(stat[19]))
def apply_desktop_policy(row,cfg,reader=read_identity):
    catalog=cfg.get("desktop_identity_catalog",{});qualified=[];rejected=[];evidence=[];total=0
    for item in row["gpu_processes"]:
        pid=item["pid"]
        if pid not in row["external_gpu_pids"]:continue
        mem=item["usedGpuMemory"]
        if mem is not None:total+=mem
        proof=catalog.get(str(pid));match=False;reason="No desktop-service identity evidence"
        actual=[]
        category=cfg.get("known_external_classifications",{}).get(str(pid),"IDENTITY_UNKNOWN")
        known=cfg.get("known_external_identity_fingerprints",{}).get(str(pid))
        if not proof and known:
            try:
                actual=[reader(pid)]
                if actual[0]!=known:category="IDENTITY_CHANGED_OR_REUSED";reason="Historical PID identity no longer matches"
            except Exception as e:category="IDENTITY_UNKNOWN";reason="Current identity gap:"+type(e).__name__
        if proof and proof.get("service_MainPID") and proof.get("ancestry_fingerprints") and proof.get("classification")=="VERIFIED_DESKTOP_SERVICE_IDENTITY_ACTIVITY_PENDING":
            try:
                expected=proof.get("ancestry_fingerprints",[proof["fingerprint"]])
                actual=[reader(v["pid"]) for v in expected]
                match=all(v==x for v,x in zip(actual,expected))
                reason="Verified GDM/service ancestry fingerprints unchanged" if match else "PID/start/UID/parent/service identity changed"
            except Exception as e:reason="Identity observation gap: "+type(e).__name__
        if match:qualified.append(pid)
        else:rejected.append(pid)
        evidence.append(dict(pid=pid,desktop_identity_match=match,reason=reason,category=category,current_fingerprints=actual))
    row.update(desktop_identity_matched_pids=sorted(qualified),unqualified_external_gpu_pids=sorted(rejected),external_NVML_bytes=total,external_identity_evidence=evidence)
    return row

def admit_low_activity(supervisor):
    cfg=supervisor.cfg;s=supervisor.s;began=s.mono()
    samples=[];supervisor.r["admission_activity_samples"]=samples
    for index in range(cfg.get("baseline_activity_samples_max",3)):
        if s.mono()-began>cfg.get("baseline_activity_window_seconds_max",5):
            raise MonitorStop("GPU_RESOURCE_DEFERRED","Bounded activity sampling window exceeded")
        row=supervisor.snapshot("BASELINE_ACTIVITY_"+str(index))
        try:
            util=s.nv.nvmlDeviceGetUtilizationRates(supervisor.handle)
            gpu=int(util.gpu)
            if gpu<0 or gpu>100:raise ValueError("invalidGPUutil")
            item=dict(index=index,wall=s.wall(),gpu_utilization_pct=gpu,memory_utilization_pct=getattr(util,"memory",None),elapsed=s.mono()-began,external_pids=row["external_gpu_pids"])
            samples.append(item);supervisor.save()
        except Exception as e:
            raise MonitorStop("GPU_RESOURCE_DEFERRED","GPU activity unavailable: "+type(e).__name__)
        if item["elapsed"]>cfg.get("baseline_activity_window_seconds_max",5):
            raise MonitorStop("GPU_RESOURCE_DEFERRED","Activity observation exceeded fixed window")
        if gpu>cfg.get("baseline_GPU_utilization_pct_max",5):
            raise MonitorStop("GPU_RESOURCE_DEFERRED","Baseline GPU activity above frozen5percent threshold")
        if index+1<cfg.get("baseline_activity_samples_max",3):s.sleep(0.25)
    coexist=any(x["external_pids"] for x in samples)
    supervisor.r["environment_classification"]="QUALIFIED_DESKTOP_CO_RESIDENT" if coexist else "NO_EXTERNAL_PROCESS_OBSERVED"
    supervisor.r["measurement_condition"]="DESKTOP_CO_RESIDENT_NATIVE_OBSERVATION" if coexist else "NO_EXTERNAL_PROCESS_OBSERVED_AT_ADMISSION"
    supervisor.r["baseline_activity_window_seconds"]=s.mono()-began
    supervisor.save()

def runtime_activity(supervisor,row):
    """Best-effort per-process activity attribution; overall own-load utilization is not external interference."""
    if row["phase"]!="WORKER" or not row.get("desktop_identity_matched_pids"):return
    nv=supervisor.s.nv
    try:
        infos=nv.nvmlDeviceGetProcessUtilization(supervisor.handle,supervisor.r.get("last_process_util_timestamp",0))
        vals=[]
        for info in infos:
            pid=int(info.pid)
            if pid in row["desktop_identity_matched_pids"]:
                vals.append(dict(pid=pid,sm_util_pct=int(info.smUtil),memory_util_pct=int(info.memUtil),timestamp=int(info.timeStamp)))
        row["desktop_process_activity"]=vals
        if infos:supervisor.r["last_process_util_timestamp"]=max(int(v.timeStamp) for v in infos)
        row["desktop_activity_attribution"]="AVAILABLE" if vals else "NO_FRESH_EXTERNAL_SAMPLES"
        supervisor.save()
        if any(v["sm_util_pct"]>supervisor.cfg.get("runtime_desktop_SM_utilization_pct_max",5) for v in vals):
            raise MonitorStop("GPU_RESOURCE_DEFERRED","Observed desktop GPU activity above frozen interference threshold")
    except MonitorStop:raise
    except Exception as e:
        row["desktop_activity_attribution"]="UNAVAILABLE:"+type(e).__name__
        supervisor.r["desktop_activity_attribution_gap"]=True
        supervisor.save()
        raise MonitorStop("GPU_RESOURCE_DEFERRED","Desktop activity attribution unavailable during own work")
