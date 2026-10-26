#!/usr/bin/env python3
"""Prepare/check only. This tool never launches, registers, installs, or edits native state."""
import argparse, hashlib, json, os, pathlib, socket, datetime
P=pathlib.Path
N=P("/root/data/ep_l2_dtc_l1_native_v2")
OLD=P("/root/data/ep_l2_main_vector_r5_20261023_v1")
C="EP_NATIVE_VECTOR_DRAM935_SENSITIVITY_20261026_V1"
def sha(p): return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p): return json.loads(P(p).read_text())
def need(value,message):
    if not value: raise ValueError(message)
def resource_snapshot(spec):
    regp=N/"control/science_authority/NATIVE_SCIENCE_REGISTRY.json"
    ep=N/"control/CURRENT_SCIENCE_EPOCH.json"
    rb=regp.read_bytes();eb=ep.read_bytes();reg=json.loads(rb);epoch=json.loads(eb)
    consistent=hashlib.sha256(rb).hexdigest()==epoch["native_registry_sha256"]
    active=[];other=2**30
    for key,row in reg.get("registered_future_requests",{}).items():
        if key==C or row.get("state") in ["COMPLETE","CLOSED","STOP_UNACCEPTED"]: continue
        amount=row.get("reserved_write_bytes")
        need(type(amount) is int and amount>=0,"unknown foreign write reservation")
        other+=amount
        active.append({"request":key,"state":row.get("state"),"reserved_write_bytes":amount})
    v=os.statvfs(spec["hot_output_parent"])
    free=v.f_bavail*v.f_frsize
    available=int(next(l.split()[1] for l in P("/proc/meminfo").read_text().splitlines() if l.startswith("MemAvailable:")))*1024
    cur=int(P("/sys/fs/cgroup/memory.current").read_text());maximum=P("/sys/fs/cgroup/memory.max").read_text().strip()
    required=7*2**30+other+spec["reserved_write_bytes"]
    return {"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "registry_sha256":hashlib.sha256(rb).hexdigest(),"epoch_sha256":hashlib.sha256(eb).hexdigest(),
        "consistent_snapshot":consistent,"epoch":epoch["epoch"],"holder":epoch["holder"],
        "global_remaining_not_EP_authorization":reg["new_scientific_budget_remaining"],
        "EP_request_registered":C in reg.get("registered_future_requests",{}),
        "free_bytes":free,"required_free_bytes":required,"deficit_bytes":max(0,required-free),
        "floor_bytes":7*2**30,"unregistered_project_headroom_bytes":2**30,
        "own_reserved_write_bytes":spec["reserved_write_bytes"],"foreign_active_reservations":active,
        "free_inodes":v.f_favail,
        "host_MemAvailable_bytes":available,"cgroup_current_bytes":cur,"cgroup_max":maximum,
        "disk_pass":free>=required and v.f_favail>=100000,
        "RAM_pass":available>=64*2**30 and (maximum=="max" or int(maximum)-cur>=spec["memory_cap_bytes"]+512*2**20)}
def verify(package):
    s=read(package/"FROZEN_SPEC.json");auth=read(package/"USER_AUTHORIZATION.json")
    need(s["cohort"]==C and s["application_budget_request"]==1 and not s["automatic_retry"],"wrong bounded scope")
    need(auth["user_message"]=="同意，做吧" and auth["full_application_budget_request"]==1,"authorization record mismatch")
    need(sha(package/"USER_AUTHORIZATION.json")==s["authorization_sha256"],"authorization bytes changed")
    need(s["source_identity"]==read(OLD/"control/FROZEN_SPEC.json")["source_identity"],"source identity drift")
    need(sha(OLD/"bin/accel-sim.out")==s["source_identity"]["binary_sha256"],"binary changed")
    for path,h in s["pinned_files"].items(): need(sha(path)==h,"pinned source/library/metadata drift: "+path)
    for name,h in s["config_sha256"].items():need(sha(package/"env"/name)==h,"config changed: "+name)
    for i in range(4):
        need((package/"env"/f"config-{i}.config").read_bytes()==(OLD/"env"/f"config-{i}.config").read_bytes(),"baseline config mismatch")
    override=(package/"env/config-4.config").read_text()
    need(override=="-gpgpu_clock_domains 1132.0:1132.0:1132.0:935.0\n","unapproved override")
    baseline_clocks=[]
    for i in range(4):
        for line in (package/"env"/f"config-{i}.config").read_text().splitlines():
            tokens=line.split("#",1)[0].split()
            if tokens and tokens[0]=="-gpgpu_clock_domains":baseline_clocks.append(tokens[1])
    need(baseline_clocks[-1]=="1132.0:1132.0:1132.0:850.0","baseline clocks changed")
    point=read(P(s["baseline_result"])/"CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json")
    need(point["status"]=="EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED" and not point["pair"],"wrong accepted baseline")
    need(point["source_identity"]==s["source_identity"],"baseline source identity mismatch")
    need(sha(P(s["baseline_result"])/"raw.log")==point["raw_sha256"],"baseline raw drift")
    receipt=read(N/"control/EP_VECTORADD_S_TRACE_RECEIPT.json")
    members=[]
    for item in receipt["members"]:
        q=P(s["trace_entry"]).parent/item["relative_path"]
        st=q.stat();need(st.st_size==item["size"] and os.access(q,os.R_OK),"input member unavailable")
        members.append({"path":str(q),"resolved":str(q.resolve()),"bytes":st.st_size,
                        "prior_closed_SHA256":item["sha256"],"body_rehashed_this_check":False})
    need(socket.gethostname()=="huangrulin-sshfs-174","wrong host")
    # No lock creation, registry write, route install, subprocess, or ELF invocation.
    resources=resource_snapshot(s)
    holds=[]
    if not resources["consistent_snapshot"]:holds.append("EPOCH_REGISTRY_SNAPSHOT_MISMATCH")
    if not resources["disk_pass"]:holds.append("RESOURCE_DISK_HOLD")
    if not resources["RAM_pass"]:holds.append("RESOURCE_RAM_HOLD")
    if not resources["EP_request_registered"]:holds.append("EXACT_REQUEST_REGISTRATION_PENDING")
    holds+=["NEW_NATIVE_PRELAUNCH_QUALIFICATION_PENDING","EXACT_NATIVE_ENTRY_ROUTE_PENDING"]
    return {"schema":"EP_DRAM935_PREPARE_ONLY_RECEIPT_V1",
        "status":"STAGED_RESOURCE_HOLD" if not resources["disk_pass"] else "STAGED_NOT_LAUNCH_AUTHORITY",
        "cohort":C,"spec_sha256":sha(package/"FROZEN_SPEC.json"),
        "authorization_sha256":sha(package/"USER_AUTHORIZATION.json"),
        "static_identity_and_single_factor_check":"PASS",
        "changed_effective_options":{"-gpgpu_clock_domains":{"from":baseline_clocks[-1],"to":"1132.0:1132.0:1132.0:935.0"}},
        "baseline_reused_same_binary":True,"baseline_new_starts":0,
        "native_entry_current_sha256":sha(N/"bin/native"),
        "resources":resources,"input_member_metadata":members,
        "holds":holds,"simulator_invocations":0,"qualification_help_invocations":0,
        "native_registry_mutations":0,"budget_registered":0,"budget_consumed":0,
        "controller_or_shared_entry_modified":False,"automatic_retry":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("--package",type=P,default=P(__file__).resolve().parent);a=p.parse_args()
    print(json.dumps(verify(a.package),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
