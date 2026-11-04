"""V5 read-only runtime attestation plus authenticated claimant reservation. Never logs credentials."""
import os,json,time,secrets,urllib.request,hashlib
from pathlib import Path
from resource_monitor import MonitorStop
FIELDS=["pid","uid","start_ticks","boot_id","executable"]
def identity(pid):
    p=Path("/proc")/str(pid);v=(p/"stat").read_text().split(") ",1)[1].split()
    return dict(pid=pid,uid=int(next(l.split()[1] for l in (p/"status").read_text().splitlines() if l.startswith("Uid:"))),start_ticks=v[19],boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip(),executable=os.readlink(p/"exe"))
def same(a,b):return all(str(a.get(k))==str(b.get(k)) for k in FIELDS)
def kernel_holders(path):
    st=Path(path).stat();key=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino);out=[]
    for line in Path("/proc/locks").read_text().splitlines():
        f=line.split()
        if len(f)<6 or f[1]!="FLOCK" or f[3]!="WRITE":continue
        try:
            d=f[5].split(":");value=(int(d[0],16),int(d[1],16),int(d[2]))
            if value==key:out.append(int(f[4]))
        except (ValueError,IndexError):continue
    return out
class SharedClient:
    def __init__(self,cfg):
        self.cfg=cfg;self.s=cfg["shared_resident"];self.claimant=identity(os.getpid());self.request_id=None;self.baseline=None;self.latest=None
    def api(self,method,path,body=None,admin=False):
        headers={"Content-Type":"application/json"}
        if admin:
            p=Path(self.s["admin_config_path"]);st=p.stat()
            if st.st_uid!=self.claimant["uid"] or st.st_mode&0o777!=0o600 or hashlib.sha256(p.read_bytes()).hexdigest()!=self.s["admin_config_sha256"]:raise RuntimeError("Admin profile identity changed")
            # Credential exists only in request memory; never persisted or returned.
            token=json.loads(p.read_text())["admin_token"];headers["X-Image-Lab-GPU-Admin"]=token
        data=None if body is None else json.dumps(body).encode()
        req=urllib.request.Request(self.s["status_url"].split("/gpu-sharing/status")[0]+path,data=data,headers=headers,method=method)
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=self.s["request_timeout_seconds"]) as response:
            return json.load(response),dict(response.headers)
    def get(self):
        challenge=secrets.token_hex(24);started=time.time()
        value,headers=self.api("GET","/gpu-sharing/status?challenge="+challenge)
        if value.get("challenge")!=challenge or headers.get("Cache-Control",headers.get("cache-control"))!="no-store":raise RuntimeError("Runtime challenge/cache evidence invalid")
        if time.time()-value["updated_unix"]>self.s["status_max_age_seconds"]:raise RuntimeError("Stale runtime status")
        if not same(value["owner"],self.s["owner"]) or not same(identity(self.s["owner"]["pid"]),self.s["owner"]):raise RuntimeError("Resident process incarnation changed")
        if value.get("run_nonce")!=self.s["run_nonce"] or value.get("build_commit")!=self.s["source_commit"]:raise RuntimeError("Runtime build/nonce changed")
        if value["loaded_function_hashes"]!=self.s["loaded_function_hashes"] or value["loaded_modules"]!=self.s["loaded_module_hashes"]:raise RuntimeError("Loaded code differs from approved audit")
        if value.get("recovery") or value.get("quarantined") or value.get("maintenance_mode"):raise RuntimeError("ImageLab recovery/quarantine/maintenance")
        for k in ["live_ready","worker_alive","worker_initialized","profile_monitor_alive"]:
            if value.get(k) is not True:raise RuntimeError("ImageLab live guard unavailable:"+k)
        if time.time()-value["last_profile_checked_unix"]>self.s["profile_check_max_age_seconds"]:raise RuntimeError("Profile monitor stale")
        if value.get("coverage")!="integrated_restricted_profile" or value.get("in_flight_scopes")!=0:raise RuntimeError("Incomplete coverage or active ImageLab scope")
        q=value["last_quiescence"];proof=q["proof"]
        if not all(proof.get(k) is True for k in ["all_models_unloaded","cuda_synchronized","children_drained"]):raise RuntimeError("Unconfirmed GPU quiescence")
        if value["queue_counts"][0]!=0:raise RuntimeError("ImageLab running queue not empty")
        for ch in value.get("children",[]):
            if not ch.get("drained") or ch.get("returncode") is None:raise RuntimeError("ImageLab child not drained")
            live=ch.get("live_identity")
            if live and same(live,ch["identity"]):raise RuntimeError("ImageLab original child still alive")
        st=Path(self.cfg["lock"]).stat()
        if (st.st_dev,st.st_ino)!=(self.s["lock_device"],self.s["lock_inode"]) or (value["lock_device"],value["lock_inode"])!=(st.st_dev,st.st_ino):raise RuntimeError("Common lock inode changed")
        self.latest=value;return value
    def reserve(self):
        value=self.get()
        if value["state"]!="IMAGE_LAB_IDLE" or kernel_holders(self.cfg["lock"]):raise RuntimeError("ImageLab not currently quiescent/unlocked")
        if value.get("reservation"):raise RuntimeError("Existing reservation must not be overwritten")
        result,_=self.api("POST","/gpu-sharing/reservation",dict(owner_pid=os.getpid(),ttl_seconds=self.s["reservation_ttl_seconds"],pause_new_work=True),admin=True)
        r=result["reservation"]
        if result.get("ownership_granted") is not False or not same(r["owner"],self.claimant):raise RuntimeError("Reservation does not identify supervisor")
        self.request_id=r["request_id"]
        return dict(request_id=self.request_id,owner=self.claimant,expires_unix=r["expires_unix"],ownership_granted=False,pause_new_work=True)
    def check(self,row):
        value=self.get();r=value.get("reservation",{})
        if r.get("request_id")!=self.request_id or not same(r.get("owner",{}),self.claimant) or not r.get("pause_new_work"):raise RuntimeError("Claimant reservation changed")
        own=kernel_holders(self.cfg["lock"])
        if own!=[os.getpid()] or value["state"]!="GPU_RESERVED_FOR_AI_ARCH":raise RuntimeError("Actual flock owner/reservation state mismatch")
        holders=value.get("kernel_holders",[])
        if not holders or any(not same(h.get("identity") or {},self.claimant) for h in holders):raise RuntimeError("Server kernel-holder attestation mismatch")
        fingerprint=(value["completed_scopes"],value["last_quiescence"]["finished_unix"])
        if self.baseline is None:self.baseline=fingerprint
        if self.baseline!=fingerprint:raise RuntimeError("ImageLab execution occurred during AIArch lock")
        resident=self.s["owner"]["pid"]
        unknown=[x["pid"] for x in value.get("observed_compute_processes",[]) if x["pid"]!=resident and x["pid"] not in row["known_own_pids"]]
        if unknown:raise RuntimeError("Unknown compute task reported by ImageLab")
        if resident in row["external_gpu_pids"]:
            row["unqualified_external_gpu_pids"]=[p for p in row["unqualified_external_gpu_pids"] if p!=resident]
        row["verified_gated_resident_pids"]=[resident]
        row["shared_gate"]=dict(state=value["state"],run_nonce=value["run_nonce"],owner=value["owner"],claimant=self.claimant,reservation_id=self.request_id,in_flight_scopes=0,completed_scopes=value["completed_scopes"],last_quiescence=value["last_quiescence"],queue_counts=value["queue_counts"],profile_monitor_alive=True,last_profile_checked_unix=value["last_profile_checked_unix"],challenge_verified=True,loaded_function_count=len(value["loaded_function_hashes"]),loaded_module_count=len(value["loaded_modules"]),kernel_holder_pids=own)
        return row
    def release(self):
        if self.request_id is None:return dict(reservation_created=False)
        value,_=self.api("GET","/gpu-sharing/status?challenge="+secrets.token_hex(16))
        r=value.get("reservation",{})
        if r.get("request_id")!=self.request_id or not same(r.get("owner",{}),self.claimant):return dict(released=False,reason="Reservation changed;do not delete another claimant")
        result,_=self.api("DELETE","/gpu-sharing/reservation",admin=True)
        return dict(released=not bool(result.get("reservation")),ownership_granted=result.get("ownership_granted"))
