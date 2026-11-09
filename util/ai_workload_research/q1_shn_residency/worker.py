"""Single owned GS-Scale worker. No framework import before proven parent flock."""
import os,sys,json,time,ast,hashlib,copy,random,traceback,shutil,gc,math,re
from pathlib import Path
from offline_asset_guard import verify_alexnet,install_external_network_guard
TOOL=Path(__file__).resolve().parent
ROOT=TOOL.parents[2]
sys.path.insert(0,str(TOOL.parent/"q1_3dgs_completion"))
OUT=Path(os.environ.get("Q1_EXECUTION_OUT",ROOT/"docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1"))
CFG=json.loads((OUT/"EXECUTION_BINDING.json").read_text())
class BlockDone(Exception):pass
LIVE=("is_densify","counter","valid_ids","valid_ids_cpu","valid_ids_cpu_prev","camtoworlds","Ks","pixels","image_ids","masks","height","width","opacities","colors0","colorsN")
def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp");tmp.write_text(json.dumps(value,indent=2,default=str)+"\n");tmp.replace(path)
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(4*1024**2),b""):h.update(b)
    return h.hexdigest()
def state_dir(name):
    assert isinstance(name,str) and re.fullmatch(r"[A-Za-z0-9_]+",name),"INVALID_OWN_STATE_NAME"
    return OUT/".private/STATES"/name
def restore_state_dir(name):
    own=state_dir(name)
    if own.exists():return own
    roots=CFG.get("external_readonly_state_roots",{})
    assert name in roots,"EXTERNAL_STATE_NAME_NOT_APPROVED"
    base=Path(roots[name])
    assert base.is_absolute() and base.is_dir() and not base.is_symlink(),"INVALID_EXTERNAL_STATE_ROOT"
    path=base/name
    assert path.is_dir() and not path.is_symlink() and path.resolve().parent==base.resolve()
    assert path.resolve()!=own.resolve()
    return path
def delete_own_state(name):
    p=state_dir(name);base=(OUT/".private/STATES").resolve()
    assert p.resolve().parent==base and not p.is_symlink()
    marker=p.with_suffix(".owner.json")
    if not p.exists():return
    v=json.loads(marker.read_text());assert v["goal_start_epoch"]==CFG["goal_start_epoch"] and v["name"]==name
    shutil.rmtree(p);marker.unlink()
    p.with_suffix(".sidecar.json").unlink(missing_ok=True)
    with (OUT/"raw/OWN_STATE_ROTATION.jsonl").open("a") as f:f.write(json.dumps({"name":name,"epoch":time.time(),"reason":"Verified later generation or completed early qualification; only own temporary state"})+"\n")
class Progress:
    def __init__(self,it,*args,**kwargs):self.it=it;self.last_description=""
    def __iter__(self):return iter(self.it)
    def set_description(self,text,*args,**kwargs):
        match=re.search(r"loss=([^|]+)",text)
        if match:assert math.isfinite(float(match.group(1))),"NONFINITE_REAL_TRAIN_LOSS"
        self.last_description=text
    def close(self):pass
class Controller:
    def __init__(self,job):
        self.job=job;self.resuming=False;self.resume_next_step=0;self.resume_live=None;self.bundle=None
        self.loader=None;self.current_ids=[];self.rows=[];self.regions=[];self.region_starts={};self.gpu_events=[]
        self.current_step=-1;self.window_start=None;self.window_end=None;self.preload=None
        self.stable_ids=None;self.next_id=0;self.lineage=[];self.saved=[];self.start=time.monotonic()
        self.last_checkpoint_wall=time.monotonic();self.recovery_name=job.get("restore")
        from transfer_observer import TransferObserver
        self.transfer=TransferObserver(lambda:self.current_step)
        self.diag=bool(job.get("diagnostic"));self.result={"status":"RUNNING","job":job,"started_epoch":time.time()}
    def loader_factory(self,dataset,**kwargs):
        assert kwargs.pop("shuffle",None) is True
        assert self.runner.cfg.patch_size is None and not self.runner.cfg.random_bkgd
        if self.loader is not None:return self.loader
        from loader_state import StatefulLoader,mapping_digest
        dg=mapping_digest(dataset.indices,self.runner.parser.image_names)
        state=self.sidecar["loader"] if self.resuming else None
        if state:
            state=copy.deepcopy(state)
            state["initial_base_seed_rng_state"]=torch.tensor(state["initial_base_seed_rng_state"],dtype=torch.uint8)
        self.loader=LoaderProxy(StatefulLoader(dataset,dataset_digest=dg,deterministic_dataset=True,restore_state=state,**kwargs),self)
        return self.loader
    def restore_schedule(self,schedulers,runner):
        for a,b in zip(schedulers,self.bundle["schedulers"]):a.load_state_dict(b)
        for kind in ["gpu","cpu"]:
            for name,opt in getattr(runner,"optimizers_"+kind).items():
                saved=self.bundle["optimizers"][kind][name]
                for dst,src in zip(opt.param_groups,saved["state_dict"]["param_groups"]):
                    for k,v in src.items():
                        if k!="params":dst[k]=v
                for k,v in saved["extra"].items():setattr(opt,k,v)
        self.set_rng(self.bundle["rng"])
    def assert_restored(self,runner,schedulers,loc):
        from state_store import fingerprint,semantic_fingerprint
        actual=self.capture(runner,self.resume_next_step-1,loc)
        legacy=fingerprint(actual);expected_legacy=self.sidecar["state_fingerprint"]
        fp=semantic_fingerprint(actual)
        expected=self.expected_restore_semantic
        dump(self.context/"RESTORE_INITIAL.json",{"status":"STATE_ROUNDTRIP_EXACT" if fp==expected else "RESTORE_INITIAL_NOT_EXACT",
            "actual_runner_fingerprint":legacy,"expected":expected_legacy,
            "legacy_fingerprint_equal":legacy==expected_legacy,
            "actual_semantic_fingerprint":fp,"expected_semantic_fingerprint":expected,
            "semantic_fingerprint_equal":fp==expected,"next_step":self.resume_next_step,
            "all_real_runner_optimizer_scheduler_live_loader_rng_frontiers_checked":True,
            "legacy_scope":"Includes incidental Python pickle memo identity; mismatch is retained, not relabeled numeric PASS"})
        assert fp==expected,("ACTUAL_RUNNER_RESTORE_NOT_EXACT",fp,expected)
        # The live frame owns the tensors; discard obsolete bundle containers.
        self.bundle=None;self.resume_live=None;gc.collect()
        if self.job["mode"]=="RESTORE_ONLY":
            self.result.update(status="COMPLETE",reached_next_step=self.resume_next_step,
                final_state_fingerprint=legacy,final_semantic_fingerprint=fp,
                continuation_numeric_class="NOT_EXECUTED",
                roundtrip_class="ACTUAL_RUNNER_STATE_EXACT",rows=[],
                new_training_steps=0,frontier=actual["frontier"],
                current_camera_ids=self.current_ids,
                saved_states=[],closure_extra_steps=0,
                scope="Exact reconstructed Runner state at original frontier; no resumed mathematical step")
            dump(self.context/"RESULT.json",self.result)
            raise BlockDone()
    def rng(self):
        return {"python":random.getstate(),"numpy":np.random.get_state(),"torch_cpu":torch.get_rng_state(),"torch_cuda":torch.cuda.get_rng_state_all()}
    def set_rng(self,s):
        random.setstate(s["python"]);np.random.set_state(s["numpy"]);torch.set_rng_state(s["torch_cpu"]);torch.cuda.set_rng_state_all(s["torch_cuda"])
    def capture(self,runner,step,loc):
        if loc.get("subthread") is not None:assert not loc["subthread"].is_alive()
        torch.cuda.synchronize()
        params={k:v for k,v in runner.splats.items()}
        opts={"gpu":{},"cpu":{}}
        for kind in opts:
            for name,opt in getattr(runner,"optimizers_"+kind).items():
                for k,v in opt.__dict__.items():
                    if "hook" in k and isinstance(v,dict):assert not v,("UNSERIALIZED_OPTIMIZER_HOOK",name,k)
                extra={}
                for k,v in opt.__dict__.items():
                    if k in {"state","param_groups","defaults","step"} or "hook" in k:continue
                    if isinstance(v,(str,int,float,bool,type(None),dict,list,tuple,torch.Tensor)):extra[k]=v
                    else:raise RuntimeError("UNSERIALIZED_OPTIMIZER_FIELD:"+name+":"+k+":"+type(v).__name__)
                opts[kind][name]={"state_dict":opt.state_dict(),"defaults":opt.defaults,"extra":extra,
                                 "runtime_keys":sorted(opt.__dict__)}
        current=self.current_ids
        assert list(map(int,loc["image_ids"].detach().cpu().reshape(-1).tolist()))==current
        return {
            "schema":"Q1_FULL_PIPELINE_STATE_V1","source_sha256":self.source_sha,"next_step":step+1,
            "parameters":params,"parameter_grads":{k:v.grad for k,v in params.items()},
            "optimizers":opts,"strategy_state":runner.strategy_state,
            "schedulers":[s.state_dict() for s in loc["schedulers"]],
            "live":{k:loc[k] for k in LIVE},"loader":self.loader.inner.snapshot(),
            "rng":self.rng(),"stable_ids":self.stable_ids,"next_id":self.next_id,
            "current_camera_ids":current,"execution":{"torch_intra_threads":torch.get_num_threads(),"torch_interop_threads":torch.get_num_interop_threads()},
            "frontier":{"processed_GPU_step":step,"CPU_applied_through_step":step if bool(loc["is_densify"]) else step-1,
                        "pending_CPU_gradient_step":None if bool(loc["is_densify"]) else step,
                        "prepared_camera_step":step+1,"deferred_zero_gradient_counters_preserved":True},
        }
    def save(self,name,runner,step,loc):
        from state_store import save_state,fingerprint,semantic_fingerprint
        b=self.capture(runner,step,loc);t=time.monotonic()
        # Diagnostic fingerprint and serialized raw storage are distinct read passes.
        fp=fingerprint(b)
        semantic=semantic_fingerprint(b)
        p=state_dir(name);p.parent.mkdir(parents=True,exist_ok=True)
        mf=save_state(b,p,chunk_bytes=64*1024**2,max_bytes=CFG.get("checkpoint_bytes_max",28*1024**3))
        assert sha(p/"bundle.pkl")==mf["metadata_sha256"]
        for storage in mf["storages"]:
            for item in storage["chunks"]:
                assert sha(p/item["name"])==item["sha256"]
        ld=copy.deepcopy(b["loader"]);ld["initial_base_seed_rng_state"]=ld["initial_base_seed_rng_state"].tolist()
        side={"loader":ld,"next_step":step+1,"current_camera_ids":b["current_camera_ids"],"source_sha256":self.source_sha,
              "state_fingerprint":fp,"semantic_state_fingerprint":semantic,"manifest_sha256":sha(p/"MANIFEST.json")}
        dump(p.with_suffix(".sidecar.json"),side);dump(p.with_suffix(".owner.json"),{"name":name,"goal_start_epoch":CFG["goal_start_epoch"]})
        rec={"name":name,"path":str(p),"next_step":step+1,"state_fingerprint":fp,"semantic_state_fingerprint":semantic,"manifest_sha256":side["manifest_sha256"],
             "sidecar_sha256":sha(p.with_suffix(".sidecar.json")),"wall_seconds":time.monotonic()-t,"frontier":b["frontier"],"current_camera_ids":b["current_camera_ids"],"manifest":mf}
        dump(OUT/"raw"/("STATE_"+name+"_MANIFEST.json"),rec);self.saved.append(rec)
        print("CHECKPOINT_COMPLETE",name,step+1,round(rec["wall_seconds"],3),flush=True)
        return fp
    def before(self,runner,step,loc):
        self.current_step=step
        if step==0:return
        self.before_wall=time.monotonic();self.row_ids=list(self.current_ids)
        self.row_visible=int(loc["valid_ids_cpu"].numel())
        if step==self.job.get("window_start"):self.window_start=self.before_wall
    def after(self,runner,step,loc):
        end=time.monotonic()
        row={"step":step,"camera_ids":self.row_ids,"N_total":int(runner.splats["means"].shape[0]),
             "N_visible":self.row_visible,"N_updated":int(loc["update_ids"].numel()) if "update_ids" in loc else None,
             "wall_seconds_body":end-self.before_wall,"diagnostic":self.diag}
        row["U_over_N"]=None if row["N_updated"] is None else row["N_updated"]/row["N_total"]
        if step>=self.job.get("window_start",10**9):self.rows.append(row)
        if step%500==0:print("REAL_STEP",self.job["id"],step,row["N_total"],round(row["wall_seconds_body"],4),flush=True)
        if self.job["mode"]=="EARLY" and step+1 in [5,8]:
            self.save("C_E" if step+1==5 else "C_R_E",runner,step,loc)
        if self.job["mode"]=="PRODUCE" and step+1 in [15140,15240]:
            self.save("C_D" if step+1==15140 else "C_V",runner,step,loc)
            if step+1==15140:
                if self.recovery_name and self.recovery_name not in ["C_D","C_V"]:delete_own_state(self.recovery_name)
                self.recovery_name="C_D"
            self.last_checkpoint_wall=time.monotonic()
        elif self.job["mode"]=="PRODUCE" and step+1<15140 and time.monotonic()-self.last_checkpoint_wall>=600:
            name="C_RECOVERY_"+str(step+1)
            self.save(name,runner,step,loc)
            if self.recovery_name and self.recovery_name not in ["C_D","C_V"]:delete_own_state(self.recovery_name)
            self.recovery_name=name;self.last_checkpoint_wall=time.monotonic()
        if step+1==self.job["stop_next"]:
            self.window_end=end
            if self.job.get("final_checkpoint_name"):
                self.save(self.job["final_checkpoint_name"],runner,step,loc)
            elif self.job.get("final_checkpoint"):
                # Canonical discovery state remains available to other formal blocks.
                self.save("C_FINAL",runner,step,loc)
            b=self.capture(runner,step,loc)
            from state_store import fingerprint,semantic_fingerprint
            fp=fingerprint(b)
            semantic=semantic_fingerprint(b)
            finite_checks={}
            value_samples={}
            for name,tensor in b["parameters"].items():
                flat=tensor.detach().reshape(-1)
                finite=True
                for offset in range(0,flat.numel(),1024**2):
                    if not bool(torch.isfinite(flat[offset:offset+1024**2]).all().item()):finite=False;break
                finite_checks["parameter:"+name]=finite
                count=min(128,flat.numel())
                value_samples["parameter:"+name]=flat[:count].to("cpu").tolist()
            for kind,optimizers in b["optimizers"].items():
                for name,opt in optimizers.items():
                    for index,entry in opt["state_dict"]["state"].items():
                        for key,tensor in entry.items():
                            if isinstance(tensor,torch.Tensor) and tensor.is_floating_point():
                                flat=tensor.detach().reshape(-1);finite=True
                                for offset in range(0,flat.numel(),1024**2):
                                    if not bool(torch.isfinite(flat[offset:offset+1024**2]).all().item()):finite=False;break
                                finite_checks[kind+":"+name+":"+str(index)+":"+key]=finite
                                value_samples[kind+":"+name+":"+str(index)+":"+key]=flat[:min(64,flat.numel())].to("cpu").tolist()
            assert all(finite_checks.values()),("NONFINITE_REAL_STATE",finite_checks)
            expected=self.job.get("expected_fingerprint")
            expected_semantic=self.job.get("expected_semantic_fingerprint")
            numeric=("EXACT" if expected_semantic==semantic else "NOT_ESTABLISHED") if expected_semantic else ("EXACT" if expected==fp else "NOT_ESTABLISHED" if expected else "NOT_COMPARED")
            self.result.update(status="COMPLETE",reached_next_step=step+1,final_state_fingerprint=fp,final_semantic_fingerprint=semantic,
                expected_fingerprint=expected,expected_semantic_fingerprint=expected_semantic,
                continuation_numeric_class=numeric,legacy_endpoint_equal=None if expected is None else expected==fp,rows=self.rows,
                closed_window_wall_seconds=None if self.window_start is None else end-self.window_start,
                body_window_steps=[self.job.get("window_start"),self.job.get("window_end")],
                closure_extra_steps=self.job.get("closure_extra_steps",0),
                saved_states=[{k:v for k,v in x.items() if k!="manifest"} for x in self.saved],
                actual_torch_intra_threads=torch.get_num_threads(),actual_torch_interop_threads=torch.get_num_interop_threads(),
                actual_OMP_cap=os.environ.get("OMP_THREAD_LIMIT"),train_affinity=sorted(os.sched_getaffinity(0)),
                current_camera_ids=self.current_ids,frontier=b["frontier"],
                finite_state_checks=finite_checks,numerical_samples=value_samples,
                sample_scope="Endpoint first128parameter/64moment elements only; full hash separate; no invented tolerance",
                pending_scope="Target-window credits closed; a later natural camera remains deferred, never claimed globally empty",
                numerical_equivalence_to_other_policies="NOT_ESTABLISHED; original tolerance not fabricated")
            dump(self.context/"RESULT.json",self.result)
            raise BlockDone()
    def region_begin(self,tag):
        if self.job.get("window_start",0)<=self.current_step<self.job["stop_next"]:
            self.region_starts[(threading.get_ident(),tag)]=(time.monotonic(),self.current_step)
    def region_end(self,tag):
        key=(threading.get_ident(),tag);x=self.region_starts.pop(key,None)
        if x:self.regions.append({"tag":tag,"TID":threading.get_native_id(),"thread_ident":key[0],"step":x[1],"begin_host_monotonic":x[0],"end_host_monotonic":time.monotonic()})
class LoaderProxy:
    def __init__(self,inner,ctl):self.inner=inner;self.ctl=ctl;self.prestarted=False
    def __iter__(self):
        if self.prestarted:self.prestarted=False;return self
        iter(self.inner);return self
    def __next__(self):
        x=next(self.inner);self.ctl.current_ids=list(map(int,x["image_id"].reshape(-1).tolist()));return x
    def __len__(self):return len(self.inner)
    def close(self):self.inner.close()
def stable_identity_hooks(ctl):
    import gsplat.strategy.default as mod
    for name in ["duplicate","split","remove"]:
        orig=getattr(mod,name)
        def wrapped(*args,_name=name,_orig=orig,**kw):
            mask=kw.get("mask",args[3] if len(args)>3 else None);assert mask is not None
            m=mask.detach().to("cpu");old=ctl.stable_ids
            if _name=="duplicate":
                count=int(m.sum());new=torch.cat([old,torch.arange(ctl.next_id,ctl.next_id+count,dtype=torch.int64)])
            elif _name=="split":
                count=2*int(m.sum());new=torch.cat([old[~m],torch.arange(ctl.next_id,ctl.next_id+count,dtype=torch.int64)])
            else:count=0;new=old[~m]
            result=_orig(*args,**kw)
            params=kw.get("params",args[0] if args else None);assert len(new)==len(params["means"])
            ctl.stable_ids=new;ctl.next_id+=count;ctl.lineage.append({"step":ctl.current_step,"operation":_name,"before_N":len(old),"after_N":len(new),"new_ID_count":count})
            return result
        setattr(mod,name,wrapped)
def restore_runner(ctl,runner,path):
    from state_store import load_state,fingerprint,semantic_fingerprint
    # Workers are forked from initial small state before loading late full state.
    public=json.loads((OUT/"raw"/("STATE_"+path.name+"_MANIFEST.json")).read_text())
    assert sha(path.with_suffix(".sidecar.json"))==public["sidecar_sha256"]
    ctl.sidecar=json.loads(path.with_suffix(".sidecar.json").read_text())
    assert ctl.sidecar["source_sha256"]==ctl.source_sha
    assert ctl.sidecar["manifest_sha256"]==sha(path/"MANIFEST.json")
    ctl.resuming=True;ctl.resume_next_step=ctl.sidecar["next_step"]
    ctl.current_ids=ctl.sidecar["current_camera_ids"]
    loader=ctl.loader_factory(runner.trainset,batch_size=runner.cfg.batch_size,shuffle=True,num_workers=4,persistent_workers=True,pin_memory=True)
    iter(loader.inner);loader.prestarted=True
    for opts in [runner.optimizers_gpu,runner.optimizers_cpu]:
        for opt in opts.values():
            opt.state.clear()
            for group in opt.param_groups:group["params"]=[]
    runner.splats=torch.nn.ParameterDict();gc.collect();torch.cuda.empty_cache()
    b,m=load_state(path,max_bytes=CFG.get("checkpoint_bytes_max",28*1024**3))
    # Derive expected semantic identity from hash-verified original bytes before
    # optimizer reconstruction can alter metadata containers.
    loaded_legacy=fingerprint(b)
    ctl.loaded_legacy_equal=loaded_legacy==ctl.sidecar["state_fingerprint"]
    ctl.expected_restore_semantic=semantic_fingerprint(b)
    if "semantic_state_fingerprint" in ctl.sidecar:
        assert ctl.expected_restore_semantic==ctl.sidecar["semantic_state_fingerprint"]
    assert b["schema"]=="Q1_FULL_PIPELINE_STATE_V1" and b["source_sha256"]==ctl.source_sha
    assert b["next_step"]==ctl.sidecar["next_step"]
    assert b["current_camera_ids"]==ctl.sidecar["current_camera_ids"]
    ld=copy.deepcopy(b["loader"]);ld["initial_base_seed_rng_state"]=ld["initial_base_seed_rng_state"].tolist()
    assert ld==ctl.sidecar["loader"],"SIDECAR_BUNDLE_LOADER_MISMATCH"
    for k,param in b["parameters"].items():param.grad=b["parameter_grads"][k]
    runner.splats=torch.nn.ParameterDict(b["parameters"])
    for kind in ["gpu","cpu"]:
        for name,opt in getattr(runner,"optimizers_"+kind).items():
            saved=b["optimizers"][kind][name]
            assert len(opt.param_groups)==1 and len(saved["state_dict"]["param_groups"])==1
            opt.param_groups[0]["params"]=[runner.splats[name]]
            opt.load_state_dict(saved["state_dict"]);opt.defaults=saved["defaults"]
            for k,v in saved["extra"].items():setattr(opt,k,v)
    runner.strategy_state=b["strategy_state"]
    ctl.stable_ids=b["stable_ids"];ctl.next_id=b["next_id"];ctl.bundle=b;ctl.resume_live=b["live"]
    torch.set_num_threads(b["execution"]["torch_intra_threads"])
    ctl.set_rng(b["rng"])
    fp=fingerprint(b)
    dump(ctl.context/"BUNDLE_ROUNDTRIP.json",{"status":"HASH_VERIFIED_BUNDLE_DECODED","fingerprint":fp,"legacy_equal":ctl.loaded_legacy_equal,"semantic_fingerprint":ctl.expected_restore_semantic,"next_step":b["next_step"],"loader_reconstructed_before_large_allocation":True,"worker_rng_scope":"DETERMINISTIC_DATASET_ONLY","frontier":b["frontier"]})
def main():
    global torch,np,threading
    os.sched_setaffinity(0,set(CFG["training_affinity"]))
    # AF_UNIX socket names use a short private alias while payloads remain under
    # this Goal's charged private directory. Never use another project's tmp.
    import tempfile
    short=Path("/tmp")/("aq1_"+str(CFG["goal_start_epoch"])+"_"+CFG.get("window_id","W1"))
    target=OUT/".private/tmp"
    if short.exists() or short.is_symlink():assert short.is_symlink() and short.resolve()==target.resolve()
    else:short.symlink_to(target,target_is_directory=True)
    os.environ["TMPDIR"]=str(short);tempfile.tempdir=None
    job=json.loads(Path(sys.argv[1]).read_text())
    context=OUT/".private/JOBS"/job["id"];context.mkdir(parents=True,exist_ok=True)
    from shared_gate import kernel_holders,identity
    owner=int(os.environ["Q1_LOCK_OWNER_PID"])
    assert kernel_holders(CFG["lock"])==[owner],"No live proven parent common flock"
    assert owner==os.getppid(),"Actual worker must be direct child of lock supervisor"
    # Recheck the exact LPIPS auxiliary weights before CUDA and block Python
    # external downloads while retaining loopback gate and AF_UNIX IPC.
    verify_alexnet(os.environ["TORCH_HOME"])
    install_external_network_guard()
    import torch,numpy as np,threading,dataclasses,importlib.util
    assert torch.__version__=="2.2.0+cu121"
    torch.set_num_threads(1);torch.set_num_interop_threads(1)
    torch.cuda.set_device(0);torch.cuda.set_per_process_memory_fraction(14/16,0)
    assert "RTX 4080" in torch.cuda.get_device_name(0),"CUDA device mismatch"
    asset=Path(CFG["author_assets"]);base=asset/"software_sources/gsscale"
    sys.path[:0]=[str(base/"examples"),str(base/"cpu_adam"),str(base)]
    source_path=base/"examples/simple_trainer_hybrid_optimized.py";source=source_path.read_text()
    source_sha=hashlib.sha256(source.encode()).hexdigest();assert source_sha=="17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a"
    spec=importlib.util.spec_from_file_location("q1_author",source_path);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    tree=ast.parse(source);preset=None
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="configs" for t in node.targets) and isinstance(node.value,ast.Dict):
            for key,val in zip(node.value.keys,node.value.values):
                if isinstance(key,ast.Constant) and key.value=="rubble":preset=val.elts[1]
    assert preset is not None
    cfg=eval(compile(ast.Expression(preset),str(source_path),"eval"),mod.__dict__)
    cfg.data_dir=str(asset/"scene");cfg.result_dir=str(context/"author_output");cfg.disable_viewer=True;cfg.adjust_steps(cfg.steps_scaler);mod.cfg=cfg
    assert cfg.max_steps==200000 and cfg.data_factor==4 and cfg.patch_size is None and cfg.test_every==83
    ctl=Controller(job);ctl.context=context;ctl.source_sha=source_sha
    from shn_candidate import attach_controller
    attach_controller(ctl)
    if job.get("numeric_audit"):
        original_after=ctl.after
        def audited_after(runner,step,loc):
            n=int(runner.splats["shN"].shape[0]);ids=sorted(set([0,n//2,n-1]+list(range(1,n,max(1,n//509)))[:509]))
            idx=torch.tensor(ids,dtype=torch.int64)
            opt=runner.optimizers_cpu["shN"]
            param=next(iter(opt.state))
            st=opt.state[param]
            def rows(t):return t.detach().index_select(0,idx.to(t.device)).cpu().reshape(len(ids),-1).tolist()
            row={"step":step,"sample_IDs":ids,"parameter":rows(runner.splats["shN"]),
                 "gradient":rows(runner.splats["shN"].grad),"moment1":rows(st["exp_avg"]),
                 "moment2":rows(st["exp_avg_sq"]),"counter":loc["counter"].index_select(0,idx).tolist(),
                 "optimizer_step":int(st["step"]),"camera_ids":list(ctl.current_ids),
                 "U_count":int(loc["update_ids"].numel()),
                 "U_first":loc["update_ids"][:128].tolist(),
                 "current_visible_count":int(loc["valid_ids_cpu_prev"].numel()),
                 "next_visible_count":int(loc["valid_ids_cpu"].numel()),
                 "next_visible_first":loc["valid_ids_cpu"][:128].tolist(),
                 "next_consumed_first":loc["colorsN"][:128].detach().cpu().reshape(min(128,loc["colorsN"].shape[0]),-1).tolist()}
            dump(context/("NUMERIC_STEP_"+str(step)+".json"),row)
            return original_after(runner,step,loc)
        ctl.after=audited_after
    mod.tqdm.tqdm=Progress
    from shn_candidate import install
    transform=install(mod,source,ctl,ctl.loader_factory,ctl.diag,enabled=bool(job.get("shn_resident",False)))
    if ctl.diag:
        observed_gpu=mod.Runner.gpu_forward_backward
        def event_gpu(self,*args,**kwargs):
            begin=torch.cuda.Event(enable_timing=True);end=torch.cuda.Event(enable_timing=True)
            h0=time.monotonic();begin.record()
            result=observed_gpu(self,*args,**kwargs)
            end.record();h1=time.monotonic()
            ctl.gpu_events.append({"step":args[0],"begin":begin,"end":end,"host_begin":h0,"host_end":h1})
            return result
        mod.Runner.gpu_forward_backward=event_gpu
    runner=mod.Runner(0,0,1,cfg);ctl.runner=runner
    ctl.stable_ids=torch.arange(len(runner.splats["means"]),dtype=torch.int64);ctl.next_id=len(ctl.stable_ids)
    stable_identity_hooks(ctl)
    dump(context/"WORKER_IDENTITY.json",{"identity":identity(os.getpid()),"supervisor_pid":owner,"job":job,"source_sha256":source_sha,"transform":transform,"dtype_by_parameter":{k:str(v.dtype) for k,v in runner.splats.items()},"nominal_max_steps":cfg.max_steps,"initial_N":len(runner.splats["means"])})
    if job.get("restore"):restore_runner(ctl,runner,restore_state_dir(job["restore"]))
    else:assert len(runner.splats["means"])==1694315
    try:runner.train()
    except BlockDone:pass
    finally:
        if ctl.loader:ctl.loader.close()
        torch.cuda.synchronize()
        dump(context/"REGIONS.json",ctl.regions);dump(context/"LINEAGE.json",ctl.lineage)
        dump(context/"TRANSFERS.json",ctl.transfer.rows)
        events=[{"step":x["step"],"gpu_span_ms":x["begin"].elapsed_time(x["end"]),"host_worker_begin":x["host_begin"],"host_worker_end":x["host_end"],"scope":"CUDA event span includes launch gaps; no uncalibrated host/device subtraction"} for x in ctl.gpu_events]
        dump(context/"GPU_EVENT_SPANS.json",events)
    assert ctl.result["status"]=="COMPLETE"
    ctl.result.update(worker_wall_seconds=time.monotonic()-ctl.start,torch_allocated_peak=torch.cuda.max_memory_allocated(),torch_reserved_peak=torch.cuda.max_memory_reserved())
    dump(context/"RESULT.json",ctl.result);print("Q1_JOB_COMPLETE",job["id"],ctl.result["reached_next_step"],ctl.result["continuation_numeric_class"],flush=True)
if __name__=="__main__":
    error=None
    try:main()
    except BaseException as e:
        error=e
        if len(sys.argv)>1:
            try:
                job=json.loads(Path(sys.argv[1]).read_text());dump(OUT/".private/JOBS"/job["id"]/"ERROR.json",{"type":type(e).__name__,"error":str(e),"traceback":traceback.format_exc()})
            except Exception:pass
        traceback.print_exc()
    if CFG.get("terminal_handoff"):
        from terminal_protocol import worker_terminal
        initialized=globals().get("torch") is not None and torch.cuda.is_initialized()
        quiescent=True
        if initialized:
            try:torch.cuda.synchronize()
            except Exception:quiescent=False
        job=json.loads(Path(sys.argv[1]).read_text())
        worker_terminal(OUT/".private/JOBS"/job["id"],int(os.environ["Q1_LOCK_OWNER_PID"]),CFG["lock"],error is None,quiescent)
    if error is not None:raise error
