"""CPU-only validation candidate. Never starts a simulator or mutates authority."""
import hashlib, json, os, re, stat
from pathlib import Path
HEADER=b"#!/bin/sh\nset -eu\n"
TOKEN=re.compile(r"E2-DTC2A48-[0-9a-f]{16}-CH-F(?:128|256)-V1")
class Hold(ValueError): pass
def need(ok, reason):
    if not ok: raise Hold(reason)
def digest(b): return hashlib.sha256(b).hexdigest()
def stable_read(path, limit=16<<20):
    """Read once using O_NOFOLLOW, record inode generation-ish metadata and bytes."""
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        a=os.fstat(fd)
        need(stat.S_ISREG(a.st_mode) and a.st_size<=limit,"nonregular/oversize artifact")
        chunks=[]; count=0
        while True:
            b=os.read(fd,65536)
            if not b: break
            count+=len(b); need(count<=limit,"artifact grew beyond bound"); chunks.append(b)
        z=os.fstat(fd)
        need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==
             (z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),"artifact changed while read")
        return b"".join(chunks),dict(dev=a.st_dev,ino=a.st_ino,size=a.st_size,
                mtime_ns=a.st_mtime_ns,ctime_ns=a.st_ctime_ns)
    finally: os.close(fd)
def pin(ref):
    b,t=stable_read(ref["path"])
    need(digest(b)==ref["sha256"],"immutable artifact SHA drift: "+ref["path"])
    return b,t
def render_foreign(grant):
    """One narrowly reviewed grammar, no general shell parser or wildcard grant."""
    cohorts=grant["cohorts"]
    need(cohorts and len(cohorts)==len(set(cohorts))<=48,"nonfinite/duplicate foreign cohorts")
    need(all(TOKEN.fullmatch(x) for x in cohorts),"foreign namespace or metacharacter")
    need(grant["frontend_ref"]["path"]==
         "/root/data/dtc_stage_iia_remaining48_20261104_v1/tools/stage2_frontend.py",
         "foreign handler replacement")
    patterns="|".join(v+":"+x for x in cohorts for v in ("experiment","result"))
    return ('# User-authorized Stage II-A remaining48 only. All prior entry bytes remain unchanged.\n'
      'if [ "$#" -ge 3 ]; then\n case "$1:$3" in\n  '+patterns+')\n'
      '   export DTC_STAGEII_REMAINING48_NATIVE_ENTRY=1\n'
      '   exec /usr/bin/python3 -B '+grant["frontend_ref"]["path"]+' "$@"\n'
      '   ;;\n esac\nfi\n').encode()
def validate_global(current, baseline, grant=None):
    need(baseline.startswith(HEADER),"baseline malformed")
    if current==baseline: return "EXACT_BASE"
    need(grant is not None,"unreviewed sharedNative modification")
    expected=HEADER+render_foreign(grant)+baseline[len(HEADER):]
    need(current==expected,"not exact authorized finite insertion; mutation/shadow/injection")
    return "EXACT_REVIEWED_FOREIGN_INSERT"
def validate_grant(grant):
    auth,_=pin(grant["authorization_ref"])
    authority=json.loads(pin(grant["science_authorization_ref"])[0])
    need(authority.get("explicit_user_approval") is True,"no foreign authorization")
    need(authority.get("approved_contract_commit")==grant["approved_commit"],"authority commit mismatch")
    need(authority.get("fresh_user_authorization_sha256")==digest(auth),"foreign user transcript identity")
    need(set(authority["budgets"])==set(grant["cohorts"]) and
         all(x==1 for x in authority["budgets"].values()),"foreign exact cohort scope")
    pin(grant["frontend_ref"])
    return True
def validate_scoped(entry, expected_sha, binding, spec_bytes, runtime_bytes):
    need(digest(entry)==expected_sha,"scoped entry mutation")
    s=json.loads(spec_bytes)
    need(digest(spec_bytes)==binding["spec_sha256"],"frozen spec drift")
    need(s["cohort"]==binding["cohort"],"cohort identity")
    need(s["source_identity"]==binding["source_identity"],"Source5 identity")
    need(s["input_identity_sha256"]==binding["input_identity_sha256"],"input identity")
    need(digest(runtime_bytes)==binding["frontend_sha256"],"scoped frontend identity")
    # Exact SHA approval covers the entire entry, all EP routes and unreachable suffix.
    # Independent executable-prefix audit is also required before adding an entry hash.
    return True
def recheck(snapshot):
    for item in snapshot:
        b,token=stable_read(item["path"])
        need(digest(b)==item["sha256"] and token==item["token"],"TOCTOU artifact replacement")
    return True
def admission_math(*,active_ep,available_ram,cgroup_remaining,new_ram,
                   pending_growth,ssd_free,new_writes,committed_writes,
                   restore_increment,foreign_floor=0,emergency=1<<30,
                   unknown_owner=False,scope_authorized=False):
    """All increments are deduplicated upstream. Current RSS/on-disk bytes excluded."""
    need(all(type(v) is int and v>=0 for v in [active_ep,available_ram,cgroup_remaining,
      new_ram,pending_growth,ssd_free,new_writes,committed_writes,restore_increment,
      foreign_floor,emergency]),"negative/noninteger resource inputs")
    if unknown_owner: return False,"LOCAL_HOLD_UNKNOWN_OWNER"
    if not scope_authorized: return False,"LOCAL_HOLD_UNAUTHORIZED"
    if active_ep>=2:return False,"LOCAL_HOLD_V3_EP_CAP2"
    if new_ram+pending_growth>min(available_ram,cgroup_remaining):return False,"LOCAL_HOLD_RAM"
    if new_writes+committed_writes+restore_increment+max(emergency,foreign_floor)>ssd_free:
        return False,"LOCAL_HOLD_SSD"
    return True,"PASS_NUMERIC_ONLY_NOT_SCIENCE_PERMISSION"

def classify_simulator_argv(argv):
    """Model ELF may be executed by ld-linux. Wrapper argv is not another model."""
    indices=[i for i,x in enumerate(argv) if Path(x).name=="accel-sim.out"]
    if not indices:return "NOT_MODEL"
    i=indices[0]
    if any(Path(x).name=="strace" for x in argv[:i]):return "WRAPPER_NOT_MODEL"
    if i==0 or "ld-linux" in Path(argv[0]).name:return "MODEL_CANDIDATE"
    return "UNRESOLVED_MODEL_TOKEN"
