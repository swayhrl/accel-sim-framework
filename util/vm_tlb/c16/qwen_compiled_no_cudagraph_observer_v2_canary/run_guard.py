#!/usr/bin/env python3
"""Shared GPU lock and conservative process-wall caps; no CUDA import."""
import fcntl
import os
import signal
import subprocess
import time
from pathlib import Path

LOCK=Path("/data/c16/locks/c16_gpu_campaign.lock")
EXPECTED_UUID="GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59"
MAX_TOTAL=180.0
MAX_POINT={"MP02":75.0,"MP03":105.0}

def gpu_query():
    text=subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,memory.used","--format=csv,noheader,nounits"],text=True).strip()
    apps=subprocess.check_output(["nvidia-smi","--query-compute-apps=pid,process_name,used_gpu_memory","--format=csv,noheader,nounits"],text=True).strip()
    parts=[x.strip() for x in text.split(",")]
    return {"uuid":parts[0],"name":parts[1],"memory_used_mib":int(parts[2]),
            "compute_processes":apps.splitlines() if apps else []}

class GpuGuard:
    def __init__(self,prior_total=0.0,prior_by_point=None):
        self.total=float(prior_total)
        self.by_point={p:float((prior_by_point or {}).get(p,0)) for p in MAX_POINT}
        if self.total<0 or self.total>=MAX_TOTAL or any(self.by_point[p]<0 or self.by_point[p]>=MAX_POINT[p] for p in MAX_POINT):
            raise ValueError("invalid prior GPU budget")
        self.lock_file=None
        self.baseline=None
        self.history=[]

    def __enter__(self):
        self.lock_file=LOCK.open("a+")
        fcntl.flock(self.lock_file,fcntl.LOCK_EX)
        self.baseline=gpu_query()
        if self.baseline["uuid"]!=EXPECTED_UUID or self.baseline["compute_processes"] or self.baseline["memory_used_mib"]>256:
            self.__exit__(None,None,None)
            raise RuntimeError("GPU_BUSY_OR_AUTHORITY_FAIL_CLOSED")
        return self

    def run(self,point,label,cmd,stdout_path,stderr_path,env=None):
        if point not in MAX_POINT:
            raise ValueError("point not allowlisted")
        remaining=min(MAX_TOTAL-self.total,MAX_POINT[point]-self.by_point[point])
        if remaining<=4:
            raise RuntimeError(f"GPU_BUDGET_EXHAUSTED_BEFORE_{point}_{label}")
        start=time.monotonic()
        with Path(stdout_path).open("wb") as out,Path(stderr_path).open("wb") as err:
            process=subprocess.Popen(cmd,stdout=out,stderr=err,env=env,start_new_session=True)
            try:
                code=process.wait(timeout=remaining-3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try: process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL)
                    process.wait()
                code=-1
        elapsed=time.monotonic()-start
        self.total+=elapsed
        self.by_point[point]+=elapsed
        self.history.append({"point":point,"label":label,"command":cmd,"exit_code":code,
                             "gpu_active_seconds_conservative_wall":elapsed,
                             "point_cumulative_seconds":self.by_point[point],"goal_cumulative_seconds":self.total})
        if self.total>MAX_TOTAL or self.by_point[point]>MAX_POINT[point]:
            raise RuntimeError(f"GPU_BUDGET_EXCEEDED_{point}_{label}")
        if code!=0:
            raise RuntimeError(f"GPU_PROCESS_FAILED_{point}_{label}_{code}")
        return elapsed

    def __exit__(self,exc_type,exc,tb):
        if self.lock_file is not None:
            fcntl.flock(self.lock_file,fcntl.LOCK_UN)
            self.lock_file.close()
            self.lock_file=None
