"""CPU-only command planner; only the existing locked supervisor launches GPU work."""
import os
os.sched_setaffinity(0,{22,23})
import json,time,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]
OUT=R/"docs/ai_workload_research/runs/AI_ARCH_Q1_R2_109_V1"
def read(p):
    try:return json.loads(p.read_text())
    except (OSError,ValueError):return None
def write(name,x):
    p=OUT/name;q=p.with_suffix(p.suffix+".tmp");q.write_text(json.dumps(x,indent=2)+"\n");q.replace(p)
def enqueue(job):
    p=OUT/".private/DISPATCH.jsonl"
    existing=[json.loads(x) for x in p.read_text().splitlines()]
    if any(x.get("id")==job.get("id") for x in existing):return
    with p.open("a") as f:f.write(json.dumps(job)+"\n")
    with (OUT/"raw/PLANNER_EVENTS.jsonl").open("a") as f:f.write(json.dumps(dict(epoch=time.time(),action="ENQUEUE",job=job))+"\n")
def stop(reason):
    write("PLANNER_STATUS.json",dict(status="HALTED_NO_NEW_JOB",reason=reason,epoch=time.time()))
def main():
    stages=[]
    for i in [1,2]:stages.append(dict(id="RELOAD_C_R2_A"+str(i),mode="RESTORE_ONLY",restore="C_R2_A"+str(i),stop_next=8,OMP_cap=16,diagnostic=False))
    stages.append(dict(id="PRODUCE_LATE",mode="PRODUCE",restore="C_R_E",stop_next=15240,OMP_cap=16,diagnostic=False,sample_pool="NATURAL_STATE_PRODUCTION_NOT_FORMAL"))
    orders=[[16,8],[8,16],[16,8],[8,16],[16,8],[8,16],[16,8]]
    for phase,restore,start,end in [("DISCOVERY","C_D",15150,15200),("VALIDATION","C_V",15250,15300)]:
        for roundno,order in enumerate(orders):
            for cap in order:
                pool="WARMUP" if roundno<2 else "FORMAL"
                stages.append(dict(id=phase+"_"+pool+"_R"+str(roundno+1)+"_T"+str(cap),
                    mode="MEASURE",restore=restore,window_start=start,window_end=end,stop_next=end+1,
                    closure_extra_steps=1,OMP_cap=cap,diagnostic=False,sample_pool=pool,phase=phase,round=roundno+1))
    for cap in [16,8]:stages.append(dict(id="DISCOVERY_DIAGNOSTIC_T"+str(cap),mode="MEASURE",restore="C_D",
        window_start=15150,window_end=15200,stop_next=15201,closure_extra_steps=1,OMP_cap=cap,
        diagnostic=True,sample_pool="DIAGNOSTIC_NOT_FORMAL",phase="DISCOVERY"))
    write("FROZEN_DISPATCH_PLAN.json",dict(epoch=time.time(),planner_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),jobs=stages,scope="CPU only; no lock/NVML/Torch/service API or GPU subprocess. Actual job resources are enforced by existing owner. Halts on any failed job or terminal supervisor."))
    while True:
        r=read(OUT/"RESOURCE_RECEIPT.json")
        if r is None:time.sleep(1);continue
        if r["status"] not in ["WORKER","DISPATCH_IDLE","JOB_FAILED_ENGINEERING_DECISION_PENDING"]:
            stop("Supervisor terminal: "+r["status"]);return
        jobs={j["job"]["id"]:j for j in r["jobs"]}
        failure=[k for k,j in jobs.items() if j.get("returncode") not in (None,0) or j.get("error")]
        if failure:stop("Observed failed job: "+",".join(failure));return
        if r["status"]!="DISPATCH_IDLE":time.sleep(1);continue
        early=["RESTORE_C_E","RESTORE_C_R_E","EARLY_CONTINUE_A1","EARLY_CONTINUE_A2"]
        if not all(k in jobs and jobs[k].get("returncode")==0 and (jobs[k].get("result") or {}).get("status")=="COMPLETE" for k in early):
            stop("Early qualification missing; root review required");return
        for n in ["RESTORE_C_E","RESTORE_C_R_E"]:
            if jobs[n]["result"].get("roundtrip_class")!="ACTUAL_RUNNER_STATE_EXACT":
                stop("Early restore not exact");return
        for i in [1,2]:
            d=OUT/".private/STATES"/("C_R2_A"+str(i))
            if not d.is_dir() or not d.with_suffix(".sidecar.json").exists():
                stop("Early saved state/sidecar missing");return
        pending=None
        for job in stages:
            j=jobs.get(job["id"])
            if j is None:pending=job;break
            if j.get("returncode")!=0 or (j.get("result") or {}).get("status")!="COMPLETE":
                stop("Incomplete finished-stage identity: "+job["id"]);return
            if job["mode"]=="RESTORE_ONLY" and j["result"].get("roundtrip_class")!="ACTUAL_RUNNER_STATE_EXACT":
                stop("New early saved state restore not exact");return
        if pending:
            enqueue(pending);write("PLANNER_STATUS.json",dict(status="RUNNING",next_job=pending["id"],epoch=time.time()))
        else:
            enqueue(dict(id="PLANNER_TERMINAL_STOP",action="STOP",status="NATIVE_Q1_MATRIX_COMPLETE"))
            write("PLANNER_STATUS.json",dict(status="COMPLETE_STOP_QUEUED",epoch=time.time()));return
        time.sleep(1)
if __name__=="__main__":main()
