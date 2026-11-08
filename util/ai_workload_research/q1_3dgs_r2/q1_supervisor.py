"""One owner, one nonblocking common flock, serial interactive Q1 dispatcher."""
import os,sys,time,json,fcntl,subprocess,signal,traceback,hashlib,shutil
from pathlib import Path
from types import SimpleNamespace
from shared_lease import RenewingSharedClient
from shared_gate import identity,kernel_holders
from resource_monitor import collect_snapshot,enforce_snapshot,disk_bytes,MonitorStop
from rss_lifecycle import OwnLifecycle,SessionMemory,finalize_races
from desktop_policy import apply_desktop_policy,admit_low_activity,runtime_activity
from process_observation import observe_processes,enforce_observation
TOOL=Path(__file__).resolve().parent;ROOT=TOOL.parents[2]
OUT=ROOT/"docs/ai_workload_research/runs/AI_ARCH_Q1_R2_109_V1"
def dump(p,j):
    p=Path(p);t=p.with_name(p.name+".tmp");t.write_text(json.dumps(j,indent=2,default=str)+"\n");t.replace(p)
class Q1Supervisor:
    def __init__(self,cfg):
        import psutil,pynvml
        self.cfg=cfg;self.out=Path(cfg["out"]);self.owned={os.getpid()};self.child=None;self.lock=None;self.held=None;self.handle=None
        self.lifecycle=OwnLifecycle(psutil,os.getpid());self.session_memory=SessionMemory(os.getpid())
        self.s=SimpleNamespace(nv=pynvml,ps=psutil,pid=os.getpid(),wall=time.time,mono=time.monotonic,sleep=time.sleep)
        self.shared=RenewingSharedClient(cfg);self.disk_last=0;self.disk_value=0
        self.r={"status":"PRELOCK","lock_attempt_count":0,"lock_acquired":False,"lock_released":False,
                "reservation_created":False,"NVML_initialized":False,"jobs":[],"monitor_gaps":[],"samples_count":0,
                "peak_own_NVML_bytes":0,"peak_sampled_RSS_bytes":0,"peak_charged_bytes":0,"worker_launches":0}
    def save(self):
        self.r["lease_events"]=getattr(self.shared,"lease_events",[])
        dump(self.out/"RESOURCE_RECEIPT.json",self.r)
    def disk(self):
        if time.monotonic()-self.disk_last>5:
            self.disk_value=disk_bytes(self.cfg["root"]);self.disk_last=time.monotonic()
        return self.disk_value
    def snapshot(self,phase,enforce=True):
        self._sample_recorded=False;self.last_attempt=None
        try:return self._snapshot(phase,enforce)
        except BaseException as e:
            if not self._sample_recorded:
                row=self.last_attempt or {"phase":phase,"own_NVML_bytes":None,
                    "own_tree_RSS_bytes":None,"monitor_gaps":[]}
                row["field_collection_error"]=type(e).__name__+":"+str(e)
                row.setdefault("monitor_gaps",[]).append("FIELD_COLLECTION:"+type(e).__name__)
                self.record(row)
            raise
    def _snapshot(self,phase,enforce=True):
        row=collect_snapshot(self.s.nv,self.handle,self.s.ps,self.s.pid,self.owned,phase,time.time(),time.monotonic()-self.held,time.time()-self.cfg["goal_start_epoch"],self.disk(),lifecycle=self.lifecycle)
        self.last_attempt=row
        row=apply_desktop_policy(row,self.cfg)
        try:row=self.shared.check(row)
        except Exception as e:
            row["shared_gate_error"]=str(e);self.last_attempt=row;self.record(row)
            raise MonitorStop("GPU_RESOURCE_DEFERRED","Shared gate: "+str(e))
        try:row["session_memory"]=self.session_memory.read(self.child.pid if self.child is not None else None)
        except BaseException as e:
            row["session_memory_observation_error"]=type(e).__name__+":"+str(e)
            self.last_attempt=row;self.record(row)
            raise MonitorStop("RESOURCE_STOP","Own session charged-memory observation incomplete")
        row["filesystem_available_bytes"]=shutil.disk_usage(self.out).free
        row["MemAvailable_bytes"]=int(next(l.split()[1] for l in Path("/proc/meminfo").read_text().splitlines() if l.startswith("MemAvailable:")))*1024
        observed_worker=None if getattr(self,"inactive_child_verified",False) else self.child
        normal_exit=None
        if observed_worker is not None and observed_worker.poll()==0:
            normal_exit={"pid":self.child.pid,"creation_time":self.lifecycle.identities.get(self.child.pid),"returncode":0}
        observation=observe_processes(self.s.ps,row,self.lifecycle.identities,self.s.pid,
                    observed_worker.pid if observed_worker is not None else None,
                    self.cfg["training_affinity"],supervisor_affinity=self.cfg["supervisor_affinity"],
                    normal_worker_exit=normal_exit)
        row["own_process_observation"]=observation
        row["own_VmSwap_bytes"]=observation["observed_live_VmSwap_subtotal_bytes"]
        row["own_VmSwap_observation_complete"]=observation["swap_observation_complete"]
        row["own_VmSwap_censored"]=observation["censored"]
        row["VmSwap_scope"]="Observed live subtotal; terminated process missing fields are explicit censored None, never0; not a whole-tree peak claim."
        row["affinity_violations"]=observation["affinity_violations"]
        row["charged_scope_child_groups"]=[x.name for x in self.session_memory.path.iterdir() if x.is_dir()]
        self.last_attempt=row
        try:
            if enforce:
                enforce_observation(observation)
                enforce_snapshot(row,self.cfg)
                m=row["session_memory"]
                if m["current_bytes"]>self.cfg["charged_bytes_max"] or m["kernel_charged_peak_bytes"]>self.cfg["charged_bytes_max"]:
                    raise MonitorStop("RESOURCE_STOP","Trusted own session charged-memory exceeds48GiB")
                if row["charged_scope_child_groups"]:raise MonitorStop("RESOURCE_STOP","Unexpected delegated child cgroup needs explicit coverage proof")
                if row["filesystem_available_bytes"]<self.cfg["free_bytes_min"]:raise MonitorStop("RESOURCE_STOP","Filesystem reserve below32GiB")
                if row["MemAvailable_bytes"]<10*1024**3:raise MonitorStop("RESOURCE_STOP","Host MemAvailable below10GiB")
                if row["own_VmSwap_bytes"]>64*1024**2:raise MonitorStop("RESOURCE_STOP","Own VmSwap growth above64MiB")
                if row["affinity_violations"]:raise MonitorStop("RESOURCE_STOP","Owned thread left approved training CPU subset")
                try:runtime_activity(self,row)
                except MonitorStop as e:
                    if str(e)=="Desktop activity attribution unavailable during own work":
                        self.r["desktop_per_process_activity_gap"]="Inherited gap, shared native observation only; no exclusive claim."
                    else:raise
                finalize_races(row,gate_verified=bool(row.get("shared_gate")),runtime_policy_checked=True)
        finally:
            self.record(row)
        return row
    def record(self,row):
        self._sample_recorded=True
        self.r["samples_count"]+=1
        for dest,key in [("peak_own_NVML_bytes","own_NVML_bytes"),("peak_sampled_RSS_bytes","own_tree_RSS_bytes")]:
            if row.get(key) is not None:self.r[dest]=max(self.r[dest],row[key])
        if "session_memory" in row:
            self.r["peak_charged_bytes"]=max(self.r["peak_charged_bytes"],row["session_memory"]["kernel_charged_peak_bytes"])
        else:row["session_memory_observation"]="NOT_COLLECTED_AFTER_GATE_FAILURE"
        self.r["latest_snapshot"]=row;self.save()
        with (self.out/"raw/RESOURCE_SAMPLES.jsonl").open("a") as f:f.write(json.dumps(row)+"\n")
        self.last_attempt=row
    def stop_own(self):
        if self.child is None or self.child.poll() is not None:return
        try:os.killpg(self.child.pid,signal.SIGTERM)
        except ProcessLookupError:return
        try:self.child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:os.killpg(self.child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            self.child.wait(timeout=3)
    def retire_finished_worker(self):
        child=self.child
        code=child.poll()
        birth=self.lifecycle.identities.get(child.pid)
        proof={"pid":child.pid,"creation_time":birth,"returncode":code}
        self.r["completed_worker_retirement_attempt"]=proof
        if type(code) is not int or birth is None:
            raise MonitorStop("RESOURCE_STOP","Completed worker identity/exit is unproven")
        if self.s.ps.pid_exists(child.pid):
            raise MonitorStop("RESOURCE_STOP","Completed worker PID still exists; no identity bypass")
        try:self.s.ps.Process(child.pid).create_time()
        except self.s.ps.NoSuchProcess:proof["fresh_Process_NoSuchProcess"]=True
        else:raise MonitorStop("RESOURCE_STOP","Completed worker incarnation uncertain")
        for n in (1,2):
            try:Path("/proc",str(child.pid),"stat").read_text()
            except FileNotFoundError:proof["proc_stat_absent_"+str(n)]=True
            else:raise MonitorStop("RESOURCE_STOP","Completed worker /proc identity still present")
        for fn in (self.s.nv.nvmlDeviceGetComputeRunningProcesses,self.s.nv.nvmlDeviceGetGraphicsRunningProcesses):
            if any(getattr(x,"pid",None)==child.pid for x in fn(self.handle)):
                raise MonitorStop("GPU_RESOURCE_DEFERRED","Own completed worker context not cleared")
        proof["GPU_context_cleared"]=True
        self.inactive_child_verified=True;self.lifecycle.worker=None
        self.r["completed_worker_retirement"]=proof
        # Returncode remains unchanged, including engineering failures. Retirement
        # only says no active worker remains; full next snapshot enforces resources.
        return proof
    def run_job(self,job):
        if time.monotonic()-self.held>self.cfg["held_seconds_max"]-600:
            raise MonitorStop("RESOURCE_STOP","Insufficient GPU reserve for another full block")
        jid=job["id"];context=self.out/".private/JOBS"/jid;context.mkdir(parents=True,exist_ok=False)
        request=context/"REQUEST.json";dump(request,job)
        env=os.environ.copy()
        asset=Path(self.cfg["author_assets"]);private=self.out/".private"
        env.update(PYTHONDONTWRITEBYTECODE="1",Q1_LOCK_OWNER_PID=str(os.getpid()),CUDA_VISIBLE_DEVICES="0",
                   OMP_THREAD_LIMIT=str(job.get("OMP_cap",16)),OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",
                   NUMEXPR_NUM_THREADS="1",MAX_JOBS="2",OMP_PROC_BIND="false",KMP_AFFINITY="disabled",
                   TORCH_HOME=str(private/"cache/torch"),TORCH_EXTENSIONS_DIR=str(private/"cache/extensions"),
                   XDG_CACHE_HOME=str(private/"cache"),CUDA_CACHE_PATH=str(private/"cache/cuda"),
                   TMPDIR=str(private/"tmp"),HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",
                   LD_LIBRARY_PATH="/data/c16/env/cpython-3.10.12/lib"+(":"+os.environ["LD_LIBRARY_PATH"] if os.environ.get("LD_LIBRARY_PATH") else ""))
        command=["taskset","-c",",".join(map(str,self.cfg["training_affinity"])),str(asset/"venv/bin/python"),"-B",str(TOOL/"worker.py"),str(request)]
        log=(context/"worker.log").open("w")
        record={"job":job,"started_epoch":time.time(),"worker_sha256":hashlib.sha256((TOOL/"worker.py").read_bytes()).hexdigest(),"launch_status":"STARTING"}
        self.r["jobs"].append(record);self.save()
        self.child=None
        try:
            self.child=subprocess.Popen(command,cwd=self.cfg["root"],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            self.inactive_child_verified=False
            record.update(pid=self.child.pid,launch_status="SPAWNED")
            self.owned.add(self.child.pid);self.r["worker_launches"]+=1;self.save()
            self.lifecycle.bind_worker(self.child.pid)
            record["identity"]=identity(self.child.pid)
            self.r["status"]="WORKER";self.save()
            while self.child.poll() is None:
                try:self.snapshot("WORKER")
                except MonitorStop:
                    failed=getattr(self,"last_attempt",{})
                    gaps=set(failed.get("monitor_gaps",[]))
                    only_health=bool(gaps) and gaps.issubset({"WORKER_NOT_HEALTHY","OWNER_HEALTH:NoSuchProcess"})
                    process_gaps=set(failed.get("own_process_observation",{}).get("gaps",[]))
                    permitted={"WORKER_NOT_HEALTHY_OR_VERIFIED_NORMAL_EXIT",
                      "INDEPENDENT_MONITOR_GAP:WORKER_NOT_HEALTHY",
                      "INDEPENDENT_MONITOR_GAP:OWNER_HEALTH:NoSuchProcess",
                      "MISSING_VMSWAP_NOT_SAFELY_CENSORED:"+str(self.child.pid)}
                    process_health_only=process_gaps.issubset(permitted)
                    resource_safe=(failed.get("own_NVML_bytes",0)<=self.cfg["own_vram_bytes_max"]
                                   and failed.get("own_tree_RSS_bytes",0)<=self.cfg["rss_bytes_max"]
                                   and failed.get("own_new_disk_bytes",0)<=self.cfg["disk_bytes_max"]
                                   and failed.get("session_memory",{}).get("kernel_charged_peak_bytes",0)<=self.cfg["charged_bytes_max"]
                                   and failed.get("filesystem_available_bytes",0)>=self.cfg["free_bytes_min"]
                                   and failed.get("MemAvailable_bytes",0)>=10*1024**3
                                   and failed.get("own_VmSwap_bytes",0)<=64*1024**2)
                    if (self.child.poll()==0 and only_health and process_health_only and resource_safe
                            and not failed.get("field_collection_error") and not failed.get("session_memory_observation_error")
                            and not failed.get("shared_gate_error") and not failed.get("affinity_violations")
                            and not failed.get("unknown_gpu_pids") and not failed.get("invalid_pid_rows")
                            and not failed.get("unqualified_external_gpu_pids")
                            and not failed.get("rss_censored_observations")):
                        # Normal return0 raced only the live-worker phase label.
                        # Any RSS race, unknown GPU, extra gap or resource violation
                        # remains fatal; the recollection enforces all resource limits.
                        self.retire_finished_worker()
                        self.snapshot("WORKER_EXIT")
                        record["normal_exit_during_phase_sample"]=True
                        break
                    raise
                time.sleep(self.cfg["monitor_seconds"])
            if not getattr(self,"inactive_child_verified",False):self.retire_finished_worker()
            record.update(returncode=self.child.returncode,finished_epoch=time.time())
            self.snapshot("WORKER_EXIT")
            record["result"]=json.loads((context/"RESULT.json").read_text()) if (context/"RESULT.json").exists() else None
            record["error"]=json.loads((context/"ERROR.json").read_text()) if (context/"ERROR.json").exists() else None
            # Own CUDA context must clear before another serial job.
            row=self.r["latest_snapshot"]
            if any(v["pid"] in self.owned for v in row["gpu_processes"]):
                raise MonitorStop("GPU_RESOURCE_DEFERRED","Own completed worker context not cleared")
            self.r["status"]="DISPATCH_IDLE" if self.child.returncode==0 else "JOB_FAILED_ENGINEERING_DECISION_PENDING"
        except BaseException as exc:
            record["supervisor_job_error"]=type(exc).__name__+":"+str(exc)
            raise
        finally:
            # Preserve the actual OS status/error even when an independent monitor
            # gap forces STOP before normal completion bookkeeping.
            code=self.child.poll() if self.child is not None else None
            record["last_observed_returncode"]=code
            record["terminal_bookkeeping_epoch"]=time.time()
            if code is not None:
                record["returncode"]=code
            for label,filename in [("result","RESULT.json"),("error","ERROR.json")]:
                path=context/filename
                try:
                    if path.exists():record[label]=json.loads(path.read_text())
                except (OSError,ValueError) as exc:
                    record[label+"_read_error"]=type(exc).__name__+":"+str(exc)
            log.close();self.save()
        return record
    def drain_own_contexts(self,row):
        """Bounded driver cleanup observation under the existing lock only."""
        attempts=[]
        deadline=time.monotonic()+10
        for number in range(11):
            own=[x["pid"] for x in row["gpu_processes"] if x["pid"] in self.owned]
            attempts.append({"number":number,"epoch":time.time(),"own_context_PIDs":own})
            self.r["context_drain_attempts"]=attempts
            if not own:
                self.r["own_GPU_contexts_cleared"]=True
                return row
            self.r["own_GPU_contexts_cleared"]=False
            remaining=min(deadline-time.monotonic(),
                self.cfg["held_seconds_max"]-(time.monotonic()-self.held))
            if number==10 or remaining<=0:break
            time.sleep(min(1,remaining))
            row=self.snapshot("CONTEXT_DRAIN_UNDER_EXISTING_LOCK",enforce=False)
        self.r["cleanup_gap"]="Own CUDA contexts did not clear within bounded original-lock drain"
        return row
    def run(self):
        try:
            os.sched_setaffinity(0,set(self.cfg["supervisor_affinity"]))
            if shutil.disk_usage(self.out).free<96*1024**3:raise MonitorStop("RESOURCE_STOP","Admission filesystem free below96GiB")
            mem=int(next(l.split()[1] for l in Path("/proc/meminfo").read_text().splitlines() if l.startswith("MemAvailable:")))*1024
            if mem<50*1024**3:raise MonitorStop("RESOURCE_STOP","Admission MemAvailable below50GiB")
            self.r["reservation"]=self.shared.reserve();self.r["reservation_created"]=True;self.save()
            self.lock=open(self.cfg["lock"],"r")
            self.r["lock_attempt_count"]+=1
            try:fcntl.flock(self.lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise MonitorStop("GPU_RESOURCE_DEFERRED","Single nonblocking flock conflict; no retry")
            self.held=time.monotonic();self.r.update(lock_acquired=True,lock_acquired_epoch=time.time())
            self.s.nv.nvmlInit();self.r["NVML_initialized"]=True
            self.handle=self.s.nv.nvmlDeviceGetHandleByUUID(self.cfg["UUID"])
            name=self.s.nv.nvmlDeviceGetName(self.handle);uuid=self.s.nv.nvmlDeviceGetUUID(self.handle)
            if isinstance(name,bytes):name=name.decode()
            if isinstance(uuid,bytes):uuid=uuid.decode()
            assert "4080" in name and uuid==self.cfg["UUID"]
            self.r["device"]={"name":name,"UUID":uuid};self.snapshot("PRE_MODEL_ADMISSION");admit_low_activity(self)
            self.r.update(status="DISPATCH_IDLE",measurement_condition="VERIFIED_GATED_RESIDENT_SHARED_NATIVE_OBSERVATION");self.save()
            processed=0
            while True:
                commands=self.out/".private/DISPATCH.jsonl"
                lines=commands.read_text().splitlines() if commands.exists() else []
                if processed<len(lines):
                    command=json.loads(lines[processed]);processed+=1
                    if command.get("action")=="STOP":
                        self.r["status"]=command.get("status","COMPLETE");break
                    self.run_job(command)
                else:self.snapshot("DISPATCH_IDLE");time.sleep(1)
        except MonitorStop as e:
            self.r.update(status=e.status,reason=str(e));self.stop_own()
        except BaseException as e:
            self.r.update(status="INPUT_OR_RUNTIME_NO_GO",reason=str(e),traceback=traceback.format_exc());self.stop_own()
        finally:
            try:
                self.stop_own()
                if self.handle is not None:
                    row=self.snapshot("FINAL_OBSERVATION",enforce=False)
                    row=self.drain_own_contexts(row)
                    if not self.r["own_GPU_contexts_cleared"]:
                        self.r.update(status="RESOURCE_STOP")
            except BaseException as e:
                self.r["cleanup_observation_error"]=type(e).__name__+":"+str(e)
                self.r["status"]="RESOURCE_STOP"
                self.r.setdefault("own_GPU_contexts_cleared",False)
            finally:
                if self.held is not None:self.r["GPU_lock_held_seconds"]=time.monotonic()-self.held
                if self.lock is not None:
                    try:
                        if self.held is not None:fcntl.flock(self.lock.fileno(),fcntl.LOCK_UN);self.r["lock_released"]=True
                    except BaseException as e:
                        self.r["lock_unlock_error"]=str(e);self.r["status"]="RESOURCE_STOP"
                    finally:
                        try:self.lock.close();self.r["lock_closed"]=True
                        except BaseException as e:self.r["lock_close_error"]=str(e)
                if self.r["NVML_initialized"]:
                    try:self.s.nv.nvmlShutdown();self.r["NVML_shutdown"]=True
                    except Exception as e:self.r["NVML_shutdown_error"]=str(e)
                try:self.r["reservation_cleanup"]=self.shared.release()
                except Exception as e:self.r["reservation_cleanup_error"]=str(e)
                self.r["whole_Goal_elapsed_seconds"]=time.time()-self.cfg["goal_start_epoch"];self.save()
        return self.r
def main():
    cfg=json.loads((OUT/"EXECUTION_BINDING.json").read_text())
    result=Q1Supervisor(cfg).run()
    print(json.dumps({k:result.get(k) for k in ["status","reason","lock_attempt_count","lock_acquired","lock_released","worker_launches","GPU_lock_held_seconds"]}),flush=True)
if __name__=="__main__":main()
