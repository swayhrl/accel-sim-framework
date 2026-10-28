"""Narrow Root-gated unified snapshot CAS only. Does not switch any public tool or grant qualifications."""
from pathlib import Path
import os,sys,json,hashlib,types,resource,time,fcntl,stat,shutil
HERE=Path(__file__).parent
C=Path("/root/data/shared_rtx4080_trace_library_20261024_v1/control")
def load(expected_manifest_sha):
 p=HERE/"unified_metadata_refresh_common_v1.py";b=p.read_bytes();mfraw=(HERE/"CODE_MANIFEST.json").read_bytes()
 assert hashlib.sha256(mfraw).hexdigest()==expected_manifest_sha
 mf=json.loads(mfraw);assert set(mf["files"])=={"unified_metadata_refresh_common_v1.py","generate_unified_private66_raw3_v1.py","publish_unified66_raw3_strict_CAS_candidate_v1.py"}
 for n,r in mf["files"].items():
  q=HERE/n;z=q.read_bytes();assert len(z)==r["bytes"]and hashlib.sha256(z).hexdigest()==r["sha256"]and not q.is_symlink()
 m=types.ModuleType("Root_exact_metadata_CAS_common");m.__file__=str(p);exec(compile(b,str(p),"exec"),m.__dict__);return m
def main():
 resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{494});os.nice(15)
 assert len(sys.argv)==3,"scope path rawSHA"
 sp=Path(sys.argv[1]);st=sp.stat()
 assert sp.parent==C and st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600 and not sp.is_symlink(),"Native Root0600 scope"
 with sp.open("rb")as f:sb=f.read(65537)
 assert len(sb)<=65536 and hashlib.sha256(sb).hexdigest()==sys.argv[2],"Root raw scope SHA"
 def unique_pairs(items):
  d={}
  for k,v in items:assert k not in d,"duplicate Root scope key";d[k]=v
  return d
 a=json.loads(sb,object_pairs_hook=unique_pairs)
 m=load(a["code_manifest_sha256"]) # Root raw authority is verified before any private module execution.
 m.need(a["schema"]=="ROOT_UNIFIED66_RAW3_METADATA_SNAPSHOT_CAS_V1"and a["status"]=="ROOT_APPROVED_EXACT_UNIFIED66_RAW3_METADATA_SNAPSHOT_CAS_ONCE","Root exact metadata CAS approval")
 m.need(a["code_manifest_sha256"]==m.h(m.raw(HERE/"CODE_MANIFEST.json",65536)),"Root code MF")
 m.need(a["runtime_root"]==str(HERE)and a["not_before_unix"]<=time.time()<a["absolute_deadline_unix"]<=a["not_before_unix"]+900,"finite Root exact source runtime")
 auth=a["authority"];m.need(set(auth)=={"old_pointer_ref","new_snapshot_ref","source_freeze_ref","write_policy"},"exact four authority groups")
 policy=auth["write_policy"];ptr=m.ROOT/"catalog/CURRENT_UNIFIED_DISCOVERY.json";snapref=auth["new_snapshot_ref"];freeze_ref=auth["source_freeze_ref"]
 m.need(auth["old_pointer_ref"]["path"]==str(ptr)and m.no_links(snapref["path"]).is_relative_to(HERE)and m.no_links(freeze_ref["path"]).parent==Path(snapref["path"]).parent,"exact source/target roots")
 m.need(policy["metadata_only"]is True and policy["no_tool_switch"]is True and policy["qualification_granted"]is False and policy["full_library_activation"]is False,"metadata-only policy")
 vp=m.ROOT/"catalog/versions"/("unified_"+snapref["sha256"]+".json")
 m.need(policy["pointer_path"]==str(ptr)and policy["immutable_version_path"]==str(vp),"literal publication paths")
 newraw=m.raw(snapref["path"],16*2**20);m.need(len(newraw)==snapref["bytes"]and m.h(newraw)==snapref["sha256"],"new snapshot exact raw")
 new=m.parse(newraw);freeze=m.readref(freeze_ref);baseline=m.parse(m.raw(m.ROOT/"catalog/versions"/("unified_"+m.BASE_SHA+".json"),16*2**20))
 legacy,_=m.readonly_module();legacy.validate_index(new)
 m.need(new["SM70_exact_inputs"]==baseline["SM70_exact_inputs"]and new["SM89_historical_capture_work_items"]==baseline["SM89_historical_capture_work_items"]and len(new["SM89_historical_capture_work_items"])==242,"exact125 and242 history")
 m.need(new["counts"]["SM89_regular"]==new["counts"]["SM89_derived"]==66 and freeze["SM89_regular"]==freeze["SM89_derived"]==66,"exact66 strict data")
 m.need(new["independent_stage_views"]["typed161"]==baseline["independent_stage_views"]["typed161"],"typed8/153 entire formal graph unchanged")
 m.need(len(new["RAW_capture_archives"])==freeze["RAW_capture_archives"]==3 and new["counts"]["SM89_RAW_capture_archives"]==3 and all(r["qualification_inferred"]is False and r["POST_complete"]is False and r["consumer_numeric_science_qualification"]=="NOT_GRANTED"for r in new["RAW_capture_archives"]),"distinct RAW3 gaps")
 m.need(new["source_refs"]==freeze["source_refs"]and freeze["old_unified_pointer_ref"]==auth["old_pointer_ref"],"frozen source graph")
 m.assert_no_secret_keys(new)
 out=HERE/"actual_publication_v1";m.need(not out.exists(),"one Root attempt only");out.mkdir()
 owner=[os.getpid(),Path("/proc/self/stat").read_text().rsplit(")",1)[1].split()[19]]
 m.save_new(out/"START.json",dict(owner=owner,scope_sha256=sys.argv[2],metadata_only=True))
 fds=[];locks=[(Path(policy["publication_lock_expected"]["path"]),fcntl.LOCK_EX),(C/"RTX4080_RAW_CAPTURE_ARCHIVE_PUBLICATION.lock",fcntl.LOCK_SH),(C/"RTX4080_SOURCE.lock",fcntl.LOCK_SH),(C/"RTX4080_TARGET.lock",fcntl.LOCK_SH),(m.CAT/"RTX4080_DERIVED_CATALOG.lock",fcntl.LOCK_SH)]
 m.need(str(locks[0][0])==str(C/"UNIFIED_METADATA_PUBLICATION.lock"),"one fixed existing serialization lock")
 def fresh():m.need(time.time()<a["absolute_deadline_unix"],"publication deadline")
 def sources_current():
  allowed={"SM89_RAW_capture_archives":m.CAT.parent/"raw_capture_archives/catalog/CURRENT_RAW_CAPTURE_ARCHIVES.json","SM89_ordinary":m.CAT/"CURRENT_RTX4080_CATALOG.json","SM89_derived":m.CAT/"CURRENT_RTX4080_DERIVED_CATALOG.json","SM89_qualification_overlay":m.CAT/"CURRENT_RTX4080_QUALIFICATION_OVERLAY.json","SM70_current_NAS_access":m.ROOT/"catalog/CURRENT_SM70_NAS_ACCESS.json"}
  for key,path in allowed.items():
   current=m.parse(m.raw(path,1024*1024));m.exact_pointer_equal(freeze["source_pointer_preimages"][key],current)
   target=freeze["source_refs"][key]["target"];m.need(Path(target["path"])==path.parent/current["relative_path"],"exact source immutable target")
   rel=Path(current["relative_path"]);m.need(not rel.is_absolute()and".."not in rel.parts and rel.parts[0]in["versions","qualification_overlays"],"source pointer traversal")
   m.readref(target)
  for r in freeze["current_data_catalog_refs"].values():m.readref(r)
  m.readref(freeze["Root_public66_acceptance_ref"]);m.readref(freeze["Root125_access_acceptance_ref"]);m.readref(freeze["Root_typed8_acceptance_ref"]);m.readref(freeze["Root_RAW3_acceptance_ref"]);m.readref(freeze["Root_capture_asof_projection_ref"])
 try:
  for i,(path,mode)in enumerate(locks):
   fresh();m.need(not path.is_symlink(),"lock symlink");fd=os.open(path,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);z=os.fstat(fd);m.need(stat.S_ISREG(z.st_mode)and z.st_size==0,"existing zero lock")
   if i==0:
    expected=policy["publication_lock_expected"];m.need((z.st_dev,z.st_ino,z.st_uid,stat.S_IMODE(z.st_mode))==(expected["dev"],expected["inode"],0,0o600),"Root exact serialization lock")
   if path==C/"RTX4080_RAW_CAPTURE_ARCHIVE_PUBLICATION.lock":
    expected=policy["raw_source_catalog_lock_expected"];m.need(expected["path"]==str(path)and(z.st_dev,z.st_ino,z.st_uid,stat.S_IMODE(z.st_mode))==(expected["dev"],expected["inode"],0,0o600),"Root exact RAW source catalog serialization lock")
   fds.append(fd)
   while True:
    fresh()
    try:fcntl.flock(fd,mode|fcntl.LOCK_NB);break
    except BlockingIOError:time.sleep(.05)
   current=path.stat();m.need((current.st_dev,current.st_ino)==(z.st_dev,z.st_ino),"same lock identity")
  oldraw=m.raw(ptr,65536);m.need(len(oldraw)==auth["old_pointer_ref"]["bytes"]and m.h(oldraw)==auth["old_pointer_ref"]["sha256"],"strict old unified pointer raw CAS")
  old=m.parse(oldraw);m.need(old["sha256"]==m.BASE_SHA and old["tool_code_version_id"]==policy["unchanged_tool_code_version_id"],"no silent baseline or tool rebase")
  sources_current()
  m.need(shutil.disk_usage("/root/data").free>=5*2**30+64*2**20 and shutil.disk_usage(m.ROOT).free>=5*2**30+64*2**20+len(newraw),"actual Native/NAS floor and this metadata pending bytes")
  m.no_links(vp);m.no_links(ptr)
  if vp.exists():m.need(m.raw(vp,16*2**20)==newraw,"existing immutable version exact")
  else:
   with vp.open("xb")as f:f.write(newraw);f.flush();os.fsync(f.fileno())
  m.need(m.raw(vp,16*2**20)==newraw,"closed immutable snapshot")
  sources_current();m.need(m.raw(ptr,65536)==oldraw,"immediate strict unified raw CAS")
  pointer=dict(old);pointer.update(relative_path=str(vp.relative_to(ptr.parent)),sha256=snapref["sha256"],bytes=snapref["bytes"],published_unix=time.time(),previous_snapshot_sha256=old["sha256"],Root_approval_path=str(sp))
  m.need(pointer["tool_code_version_id"]==old["tool_code_version_id"]and pointer["qualification_granted"]is False and pointer["full_library_activation"]is False,"tool and permissions unchanged")
  m.no_links(vp);m.no_links(ptr)
  tmp=ptr.parent/(".own_unified_"+str(os.getpid())+"_"+str(time.time_ns())+".tmp")
  with tmp.open("xb")as f:f.write(m.canonical(pointer));f.flush();os.fsync(f.fileno())
  os.replace(tmp,ptr);m.need(m.parse(m.raw(ptr,65536))==pointer,"closed pointer readback")
  m.save_new(out/"PUBLISHED_COMPLETE.json",dict(status="PUBLIC_UNIFIED66_RAW3_METADATA_ONLY_STRICT_CAS_COMPLETE",old_pointer_ref=auth["old_pointer_ref"],new_snapshot_ref=snapref,public_version_ref=m.ref(vp),public_pointer_ref=m.ref(ptr),scope_sha256=sys.argv[2],no_tool_switch=True,qualification_granted=False,full_library_activation=False,body_bytes_read=0,Source_KEEP=True,release_bytes=0))
 except BaseException as e:
  m.save_new(out/"HOLD_FAILED_RETAINED.json",dict(error=str(e),no_auto_retry_or_rebase=True));raise
 finally:
  for fd in reversed(fds):os.close(fd)
 m.save_new(out/"PROCESS_CLOSED.json",dict(owner=owner,owned_children=[],locks_released=True))
 print("PUBLIC_UNIFIED66_RAW3_METADATA_ONLY_COMPLETE")
if __name__=="__main__":main()
