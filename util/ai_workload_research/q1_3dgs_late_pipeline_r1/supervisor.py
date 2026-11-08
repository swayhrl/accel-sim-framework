"""Single-attempt locked execution; all driver observation is dependency-injected for CPU tests."""
import os,sys,json,time,fcntl,subprocess,signal,traceback
from pathlib import Path
from types import SimpleNamespace
from persistence import save_json
from shared_gate import SharedClient
from rss_lifecycle import OwnLifecycle,SessionMemory,finalize_races
from resource_monitor import collect_snapshot,enforce_snapshot,disk_bytes,MonitorStop
from desktop_policy import apply_desktop_policy,admit_low_activity,runtime_activity,read_identity
TOOL=Path(__file__).resolve().parent
ROOT=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-dense-memory-mechanism-convergence-109-v11')
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_DENSE_MEMORY_MECHANISM_CONVERGENCE_109_V11"

class Supervisor:
    def __init__(self,cfg,services):
        self.cfg=cfg;self.s=services;self.out=Path(cfg["out"]);self.owned={services.pid}
        self.lifecycle=getattr(services,"lifecycle",None);self.session_memory=getattr(services,"session_memory",None)
        self.child=None;self.lock=None;self.held=None;self.handle=None;self.log=None
        self.shared=SharedClient(cfg) if cfg.get("shared_resident") else None
        self.r=dict(status="PRELOCK",lock_attempt_count=0,lock_acquired=False,lock_released=False,NVML_initialized=False,worker_launches=0,samples=[],children=[],monitor_gaps=[],GPU_model_initializations=0,EXCLUSIVITY_EVIDENCE_COMPLETE=False)
    def save(self):
        save_json(self.out/"RESOURCE_RECEIPT.json",self.r)
    def snapshot(self,phase,enforce=True):
        row=collect_snapshot(self.s.nv,self.handle,self.s.ps,self.s.pid,self.owned,phase,self.s.wall(),self.s.mono()-self.held,self.s.wall()-self.cfg["goal_start_epoch"],self.s.disk(),**({"lifecycle":self.lifecycle} if getattr(self,"lifecycle",None) is not None else {}))
        row=apply_desktop_policy(row,self.cfg,getattr(self.s,"read_identity",read_identity))
        if self.shared:
            try:row=self.shared.check(row)
            except Exception as e:raise MonitorStop("GPU_RESOURCE_DEFERRED","Shared gate qualification: "+str(e))
        if getattr(self,"session_memory",None) is not None:
            row["session_memory"]=self.session_memory.read(self.child.pid if self.child is not None else None)
        self.r["samples"].append(row);self.save()
        if enforce:
            enforce_snapshot(row,self.cfg)
            if "session_memory" in row and row["session_memory"]["kernel_charged_peak_bytes"]>self.cfg["rss_bytes_max"]:
                raise MonitorStop("INCONCLUSIVE","Session charged-memory peak exceeds16GiB")
            try:runtime_activity(self,row)
            except MonitorStop as activity_error:
                if self.shared and str(activity_error)=="Desktop activity attribution unavailable during own work":
                    self.r["performance_comparability_gap"]="Desktop per-process NVML activity unavailable;retain INCONCLUSIVE"
                    self.save()
                else:raise
            if getattr(self,"lifecycle",None) is not None:
                finalize_races(row,gate_verified=bool(self.shared and row.get("shared_gate")),runtime_policy_checked=True)
                self.save()
        return row
    def execute_v8_tasks(self):
        if self.cfg.get("v9_dispatch"):
            from v9_runtime import execute_tasks
            return execute_tasks(self)
        for task in self.cfg["worker_tasks"]:
            if self.s.mono()-self.held>self.cfg["held_seconds_max"]-150:
                self.r.setdefault("optional_skips",[]).append(dict(task=task,reason="Insufficient bounded initialization reserve"));break
            self.child=self.s.spawn();self.owned.add(self.child.pid)
            if self.lifecycle is not None:self.lifecycle.bind_worker(self.child.pid)
            self.r["worker_launches"]+=1
            self.r["children"].append(dict(task=task,pid=self.child.pid,start_epoch=self.s.wall()))
            while self.child.poll() is None:
                self.snapshot("WORKER");self.s.sleep(self.cfg["monitor_seconds"])
            self.r["children"][-1].update(exit_code=self.child.returncode,finish_epoch=self.s.wall())
            self.snapshot("WORKER_EXIT")
            result=self.s.worker_result()
            self.r["children"][-1]["model_initializations"]=result.get("model_initializations",0)
            self.r["children"][-1]["result_status"]=result.get("status")
            self.r["children"][-1]["config_completion"]=result.get("config_completion",{})
            self.save()
            if task=="PREFIX" and result.get("status")=="V8_WORKER_OPTIONAL_UNAVAILABLE" and self.child.returncode==0:
                self.r.setdefault("optional_skips",[]).append(dict(task=task,reason=result.get("optional_error")))
            elif self.child.returncode!=0 or result.get("status")!="V8_WORKER_COMPLETE":
                raise MonitorStop("NUMERIC_OR_RUNTIME_NO_GO","V8 worker runtime STOP; preserve every completed configuration")
            if result.get("status")=="V8_WORKER_COMPLETE":
                expected=["MAIN","LP20_CONTROL","LP_NONE"] if task=="BASE" else ["APC_COLD","APC_WARM"]
                if not all(all(result.get("config_completion",{}).get(config,{}).get("P"+str(i),0)>=5 for i in range(1,7)) for config in expected):
                    raise MonitorStop("NUMERIC_OR_RUNTIME_NO_GO","V8 expected formal configuration matrix incomplete")
            own=[g["pid"] for g in self.r["samples"][-1]["gpu_processes"] if g["pid"] in self.owned]
            if own:raise MonitorStop("GPU_RESOURCE_DEFERRED","Worker CUDA context not drained before next serial engine")
        self.r["GPU_model_initializations"]=sum(c.get("model_initializations",0) for c in self.r["children"])
        self.r["status"]="V8_STUDY_COMPLETE"
    def stop_own(self):
        if self.child is not None:
            self.s.terminate(self.child)
            self.r["controlled_shutdown"]=True
    def run(self):
        try:
            if self.s.wall()-self.cfg["goal_start_epoch"]>self.cfg["goal_seconds_max"]-300:
                raise MonitorStop("INCONCLUSIVE","CPU preparation consumed execution/archival reserve")
            if self.shared:
                try:self.r["shared_reservation"]=self.shared.reserve()
                except Exception as e:raise MonitorStop("GPU_RESOURCE_DEFERRED","Prelock shared reservation: "+str(e))
            self.lock=self.s.open_lock(self.cfg["lock"])
            self.r["lock_attempt_count"]+=1
            try:self.s.flock(self.lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                raise MonitorStop("GPU_RESOURCE_DEFERRED","Single nonblocking lock conflict; no retry")
            self.held=self.s.mono();self.r.update(lock_acquired=True,lock_acquired_epoch=self.s.wall())
            self.save()
            self.s.nv.nvmlInit();self.r["NVML_initialized"]=True
            self.handle=self.s.nv.nvmlDeviceGetHandleByUUID(self.cfg["UUID"])
            name=self.s.nv.nvmlDeviceGetName(self.handle);uuid=self.s.nv.nvmlDeviceGetUUID(self.handle)
            if isinstance(name,bytes):name=name.decode()
            if isinstance(uuid,bytes):uuid=uuid.decode()
            self.r["device"]=dict(name=name,UUID=uuid,total_MiB=self.s.nv.nvmlDeviceGetMemoryInfo(self.handle).total/1024**2)
            if uuid!=self.cfg["UUID"] or "4080" not in name:
                raise MonitorStop("NUMERIC_OR_RUNTIME_NO_GO","Device identity mismatch")
            self.snapshot("PRE_MODEL_ADMISSION")
            admit_low_activity(self)
            if self.shared:
                self.r["environment_classification"]="VERIFIED_GATED_RESIDENT_CONTEXT"
                self.r["measurement_condition"]="VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION"
                self.save()
            if self.cfg.get("v8_dispatch"):
                self.execute_v8_tasks()
            else:
                self.child=self.s.spawn();self.owned.add(self.child.pid)
                if self.lifecycle is not None:self.lifecycle.bind_worker(self.child.pid)
                self.r["worker_launches"]=1
                self.r["children"].append(dict(pid=self.child.pid,start_epoch=self.s.wall()))
                while self.child.poll() is None:
                    self.snapshot("WORKER");self.s.sleep(self.cfg["monitor_seconds"])
                self.r["children"][-1].update(exit_code=self.child.returncode,finish_epoch=self.s.wall())
                self.snapshot("WORKER_EXIT")
                if self.child.returncode!=0:
                    raise MonitorStop("NUMERIC_OR_RUNTIME_NO_GO","Worker stopped; retain raw error and log")
                raw=self.s.worker_result()
                self.r["GPU_model_initializations"]=raw.get("model_initializations",0)
                if raw.get("status")!="NATIVE_BATCH_SENSITIVITY_COMPLETE" or sum(s.get("role")=="FORMAL" and s.get("status")=="PASS" for s in raw.get("samples",[]))!=30:
                    raise MonitorStop("NUMERIC_OR_RUNTIME_NO_GO","Incomplete six-point worker result")
                self.r["status"]="NATIVE_BATCH_SENSITIVITY_COMPLETE"
        except MonitorStop as e:
            self.r.update(status=e.status,reason=str(e));self.stop_own()
        except BaseException as e:
            self.r.update(status="NUMERIC_OR_RUNTIME_NO_GO",reason=str(e),traceback=traceback.format_exc());self.stop_own()
        finally:
            # Errors in final observation must never skip unlock, close or error persistence.
            try:
                if self.child is not None:
                    self.r["children"][-1]["exit_code"]=self.child.poll()
                    if self.cfg.get("v9_dispatch"):
                        try:self.r["children"][-1]["model_initializations"]=max(self.r["children"][-1].get("model_initializations",0),self.s.worker_result().get("model_initializations",0))
                        except Exception:pass
                    try:self.r["GPU_model_initializations"]=sum(c.get("model_initializations",0) for c in self.r["children"]) if self.cfg.get("v8_dispatch") else self.s.worker_result().get("model_initializations",0)
                    except Exception:pass
                if self.handle is not None:
                    deadline=min(self.held+self.cfg["held_seconds_max"]-2,self.s.mono()+6)
                    while True:
                        row=self.snapshot("FINAL_OBSERVATION",enforce=False)
                        own_gpu={x["pid"] for x in row["gpu_processes"] if x["pid"] in self.owned}
                        if not own_gpu or self.s.mono()>=deadline:break
                        self.stop_own();self.s.sleep(0.5)
                    self.r["own_GPU_contexts_cleared"]=not bool(own_gpu)
                    self.r["final_GPU_pids"]=[x["pid"] for x in row["gpu_processes"]]
                    self.r["final_observation_state"]=row["state"]
                    if own_gpu:
                        self.r.update(status="NUMERIC_OR_RUNTIME_NO_GO",cleanup_gap="Own context unresolved")
                    elif row["state"]=="UNKNOWN":
                        self.r["cleanup_gap"]="Final observation incomplete; admission STOP preserved"
                        if self.r["status"] in ["NATIVE_BATCH_SENSITIVITY_COMPLETE","V8_STUDY_COMPLETE","V9_STUDY_COMPLETE","V10_STUDY_COMPLETE","V11_STUDY_COMPLETE"]:self.r["status"]="NUMERIC_OR_RUNTIME_NO_GO"
            except BaseException as e:
                self.r.update(status="NUMERIC_OR_RUNTIME_NO_GO",final_observation_error=str(e))
            finally:
                try:
                    if self.held is not None:
                        self.r["GPU_lock_held_seconds"]=self.s.mono()-self.held
                        self.s.flock(self.lock.fileno(),fcntl.LOCK_UN)
                        self.r["lock_released"]=True
                except BaseException as e:self.r.update(status="NUMERIC_OR_RUNTIME_NO_GO",unlock_error=str(e))
                finally:
                    if self.lock is not None:
                        try:self.lock.close();self.r["lock_closed"]=True
                        except BaseException as e:self.r["lock_close_error"]=str(e)
                    if self.r["NVML_initialized"]:
                        try:self.s.nv.nvmlShutdown();self.r["NVML_shutdown"]=True
                        except BaseException as e:self.r.update(status="NUMERIC_OR_RUNTIME_NO_GO",NVML_shutdown_error=str(e))
                    self.r["DESKTOP_CO_RESIDENCE_EVIDENCE_COMPLETE"]=bool(self.r.get("environment_classification")=="QUALIFIED_DESKTOP_CO_RESIDENT" and self.r["worker_launches"] and self.r.get("own_GPU_contexts_cleared") and not any(x.get("unqualified_external_gpu_pids") for x in self.r["samples"]))
                    if self.shared:
                        try:self.r["shared_reservation_cleanup"]=self.shared.release()
                        except Exception as e:self.r["shared_reservation_cleanup_error"]=str(e)
                    self.r["whole_Goal_elapsed_seconds"]=self.s.wall()-self.cfg["goal_start_epoch"]
                    self.r["EXCLUSIVITY_EVIDENCE_COMPLETE"]=bool(self.r["worker_launches"] and self.r["lock_released"] and self.r.get("own_GPU_contexts_cleared") and all(s["state"] in ["EMPTY","OWN_LIVE_PID"] for s in self.r["samples"]) and all(c.get("exit_code") is not None for c in self.r["children"]))
                    self.save()
        return self.r

def real_services(cfg):
    if cfg.get("v9_dispatch"):
        from v9_runtime import real_services as v9_services
        return v9_services(cfg,TOOL)
    import psutil,pynvml
    state={"task_index":0}
    context=Path(cfg["out"])/".private/PROBE"
    lifecycle=OwnLifecycle(psutil,os.getpid()) if cfg.get("rss_lifecycle_rule") else None
    session_memory=SessionMemory(os.getpid()) if cfg.get("rss_lifecycle_rule") else None
    def spawn():
        nonlocal context
        if cfg.get("v8_dispatch"):
            task=cfg["worker_tasks"][state["task_index"]];state["task_index"]+=1;state["task"]=task
            context=Path(cfg["out"])/".private"/task
            if state.get("log"):state["log"].close()
        else:task="PROBE"
        context.mkdir(parents=True,exist_ok=False);(context/"tmp").mkdir()
        env=os.environ.copy();env.update(WEIGHT_PROBE_LOCK_OWNER=str(os.getpid()),HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",VLLM_ENABLE_V1_MULTIPROCESSING="0",PYTHONDONTWRITEBYTECODE="1",TOKENIZERS_PARALLELISM="false",CUDA_VISIBLE_DEVICES="0",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",NUMEXPR_NUM_THREADS="1",TORCHINDUCTOR_COMPILE_THREADS="1",VLLM_NO_USAGE_STATS="1",DO_NOT_TRACK="1")
        for key,sub in [("VLLM_CACHE_ROOT","vllm"),("VLLM_CONFIG_ROOT","vllm_config"),("TORCHINDUCTOR_CACHE_DIR","inductor"),("TRITON_CACHE_DIR","triton"),("CUDA_CACHE_PATH","cuda"),("XDG_CACHE_HOME","xdg"),("HF_HOME","hf"),("TORCH_HOME","torch"),("TORCH_EXTENSIONS_DIR","extensions"),("HOME","home"),("TMPDIR","tmp"),("NUMBA_CACHE_DIR","numba")]:
            env[key]=str(context/sub)
        state["log"]=(context/"worker.log").open("w")
        child=subprocess.Popen([sys.executable,str(TOOL/"worker.py"),task],cwd=cfg["root"],env=env,stdout=state["log"],stderr=subprocess.STDOUT,start_new_session=True)
        return child
    def terminate(child):
        try:os.killpg(child.pid,signal.SIGTERM)
        except ProcessLookupError:return
        try:child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            child.wait(timeout=2)
    return SimpleNamespace(pid=os.getpid(),lifecycle=lifecycle,session_memory=session_memory,nv=pynvml,ps=psutil,wall=time.time,mono=time.monotonic,sleep=time.sleep,disk=lambda:disk_bytes(cfg["root"]),open_lock=lambda p:open(p,"r"),flock=fcntl.flock,spawn=spawn,terminate=terminate,worker_result=lambda:json.loads((Path(cfg["out"])/("raw/"+state["task"]+".json" if cfg.get("v8_dispatch") else "raw/PROBE.json")).read_text()))
def main():
    cfg=json.loads((OUT/"EXECUTION_BINDING.json").read_text())
    r=Supervisor(cfg,real_services(cfg)).run()
    print(json.dumps({k:r.get(k) for k in ["status","reason","lock_attempt_count","lock_acquired","lock_released","worker_launches","GPU_model_initializations","GPU_lock_held_seconds"]}),flush=True)
if __name__=="__main__":main()
