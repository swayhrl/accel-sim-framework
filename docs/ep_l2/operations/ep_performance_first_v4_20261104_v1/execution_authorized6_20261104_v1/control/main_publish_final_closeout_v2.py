"""Sole Main bounded metadata publisher. No scientific starts or changes to model inputs."""
from pathlib import Path
import json,hashlib,subprocess,sys,fcntl,datetime,os
C=Path(__file__).resolve().parent;V=C.parent.parent;P=V.parent.parent
BRANCH="hrl/ep-l2-performance-first-v4-20261104-v1";BASE="457511c3561029ddd40c2af207f65f14c6934e54"
REPO="repos/swayhrl/accel-sim-framework";PREFIX="docs/ep_l2/operations/ep_performance_first_v4_20261104_v1/execution_authorized6_20261104_v1"
final="--final"in sys.argv
def digest(b):return hashlib.sha256(b).hexdigest()
def ref(p):b=p.read_bytes();return dict(path=str(p),sha256=digest(b),bytes=len(b))
def read(p):return json.loads(p.read_bytes())
def write(p,o):p.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
def api(method,path,body=None):
 args=["/usr/local/bin/gh","api","-X",method,path]
 if body is not None:
  q=C/"PUBLICATION_API_REQUEST.json";write(q,body);args+=["--input",str(q)]
 z=subprocess.run(args,capture_output=True,timeout=180)
 if z.returncode:raise ValueError("GitHub API "+method+" failed "+z.stderr.decode(errors="replace")[-1000:])
 return json.loads(z.stdout)
def clean(o):
 if isinstance(o,dict):return{k:clean(v)for k,v in o.items()if not any(w in k.lower()for w in["token","nonce","secret"])}
 if isinstance(o,list):return[clean(x)for x in o]
 return o
def main():
 lockpath=P/"execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock"
 with lockpath.open("a+b")as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  ep=C/"PUBLICATION_EXPECTED_HEAD.json";base=read(ep)["head"]if ep.exists()else BASE
  assert api("GET",REPO+"/git/ref/heads/"+BRANCH)["object"]["sha"]==base,"branch changed; no force"
  z=subprocess.run(["/usr/bin/python3","-B",str(V/"activation_20261104_v1/closed_result_report_candidate_v2/closed_result_report.py"),"--once"],capture_output=True,text=True,timeout=120);assert z.returncode==0,z.stderr
  report=json.loads(z.stdout);write(C/"PERFORMANCE_CURRENT.json",report);(C/"PERFORMANCE_CURRENT.md").write_text(report["markdown_candidate"])
  files={}
  allowed=["USER_REQUEST.txt","USER_AUTHORIZATION.json","EXACT_EXECUTION_MANIFEST.json","MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json","MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json","ROOT_LAUNCH_ACK.json","MAIN_DISPATCHER_STARTUP_REVIEW.json","MAIN_APPROVED_VECTOR_CONSUMER_AMENDMENT.json","VECTOR_W_CONSUMER_APPLY_STDOUT.json","VECTOR_W_OFFICIAL_ARCHIVE_TWO_RESTORES_STDOUT.json","AUTHORIZED_EXECUTION_TRUE164_ARCHIVE_RECEIPT.json","PERFORMANCE_CURRENT.json","PERFORMANCE_CURRENT.md","main_activate_exact6.py","main_materialize_with_current_native_binding.py","bind_current_resources.py","main_closed_result_finalizer.py","main_publish_execution_metadata.py","main_publish_final_closeout_v2.py","CURRENT_NATIVE_REBASE_REVIEW.json","SHARED_ROUTE_CONTRACT_V4_EXACT6.json","resources_current_A1.py","resources_current_B.py","resources_current_A3.py","EXECUTOR_STARTED.json","EXECUTOR_FINISHED.json","FINAL_SCOPE_CLOSURE.json","METADATA_FINALIZER_STARTED.json","METADATA_FINALIZER_FINISHED.json","METADATA_FINALIZER_ATTENTION.json"]
  for name in allowed:
   p=C/name
   if p.exists():files["control/"+name]=p
  roots=[V/"activation_20261104_v1/engineering_dispatcher_candidate_v1",V/"activation_20261104_v1/closed_result_report_candidate_v2",V/"activation_20261104_v1/exact_wv_native_worker",C/"a2_cpu_review",C/"closeout_20261105_v1",V/"track_b/foreign_phys4_mapping_addendum_v4",V/"track_b/closed_consumer_pin_addendum_v5",V/"track_c/hardware_delta_v1"]
  for root in roots:
   for p in root.rglob("*"):
    if not p.is_file()or"__pycache__"in p.parts or p.suffix not in[".py",".json",".md",".txt",".sh"]:continue
    if p.name in["PURE_VALIDATED_W_ONLY_BUNDLE.json"]or"review"in p.parts:continue
    files[str(root.relative_to(V))+"/"+str(p.relative_to(root))]=p
  for p in (C/"closeout_20261105_v1").rglob("*"):
   if p.is_file()and p.suffix in[".py",".json",".md",".txt",".sh"]:files["control/closeout_20261105_v1/"+str(p.relative_to(C/"closeout_20261105_v1"))]=p
  m=read(C/"EXACT_EXECUTION_MANIFEST.json")
  for g,x in m["groups"].items():
   root=Path(x["data_root"])
   for name in ["USER_AUTHORIZATION.json","HOST_QUALIFICATION_MAIN_V4.json",x["route_file"]]:
    p=root/"control"/name;files["formal/"+g+"/"+name]=p
   for p in root.glob("cases/*/control/FROZEN_SPEC.json"):files["formal/"+g+"/"+p.parts[-3]+"/FROZEN_SPEC.json"]=p
  entries=[];rows=[]
  for rel,p in sorted(files.items()):
   raw=p.read_bytes();assert len(raw)<4*(1<<20)
   if p.suffix==".json":
    obj=json.loads(raw);filtered=clean(obj)
    if filtered!=obj:out=(json.dumps(filtered,sort_keys=True,indent=2)+"\n").encode()
    else:out=raw
   else:out=raw
   text=out.decode("utf-8");entries.append(dict(path=PREFIX+"/"+rel,mode="100644",type="blob",content=text))
   rows.append(dict(path=rel,original_ref=ref(p),export_sha256=digest(out),export_bytes=len(out),raw_preserved=raw==out))
  assert sum(x["export_bytes"]for x in rows)<12*(1<<20)
  note="# EP-L2 V4 authorized exact6 execution\n\nThree independent requests A1/B/A3 have two starts each. All original V3 eight accepts and two technical failures remain closed and charged. No A2/C model, new Trace, 109 GPU task, NI model or paper work is authorized.\n\nThis is a review-only metadata snapshot, not relocated Native execution authority. Formal Specs, Host graph, exact resource mapping and scoped entries are pinned separately. Initial current-Native preimage changed because an authorized foreign PHYS768 first4 route was added; Main preserved all its bytes and mapped its exact CPU/RAM/write commitments without weakening math/cap10/5GiB floor.\n\nVector's original natural W run hit a stale consumer mode-contract pin, before numeric parsing. Main retained the original immutable Spec/raw/HOLD, qualified a one-pin loaded-module consumer binding to the contract already pinned in Spec/NativeQ, reused every original outer check and frozen numeric algorithm, then archived and restored twice. This was post-close review, with no new model or refund. The remaining authorized WV point was delegated once to a Main Native worker only after the full W stage gate; the original sole coordinator continues A1/A3. There is no second general model queue or controller hot replacement.\n\nAll6 points are accepted and all3 scopes CLOSED_COMPLETED. See [final closeout](control/closeout_20261105_v1/FINAL_RESULT_SUMMARY.md). Main resolved the reviewed finite foreign-route HOLD after the original supervisor expired, without rerunning models. See [current performance](control/PERFORMANCE_CURRENT.md), [exact execution manifest](control/EXACT_EXECUTION_MANIFEST.json), and the original [V4 engineering request](../README.md). Missing/unaccepted cycles remain UNKNOWN, not zero. Source KEEP.\n"
  entries.append(dict(path=PREFIX+"/README.md",mode="100644",type="blob",content=note))
  manifest=dict(schema="EP_MAIN_V4_AUTHORIZED_EXECUTION_REVIEW_EXPORT_V1",files=rows,final=final,review_only=True,redaction="JSON token/nonce/secret field names omitted; original SHA distinct where transformed",scientific_scope_new_starts=6,Source_KEEP=True)
  entries.append(dict(path=PREFIX+"/REVIEW_EXPORT_MANIFEST.json",mode="100644",type="blob",content=json.dumps(manifest,sort_keys=True,indent=2)+"\n"))
  basecommit=api("GET",REPO+"/git/commits/"+base)
  tree=api("POST",REPO+"/git/trees",dict(base_tree=basecommit["tree"]["sha"],tree=entries))
  commit=api("POST",REPO+"/git/commits",dict(message="EP V4 exact6 "+("closed results"if final else"authorized execution progress"),tree=tree["sha"],parents=[base]))
  assert api("GET",REPO+"/git/ref/heads/"+BRANCH)["object"]["sha"]==base,"branch changed; no force"
  api("PATCH",REPO+"/git/refs/heads/"+BRANCH,dict(sha=commit["sha"],force=False))
  assert api("GET",REPO+"/git/ref/heads/"+BRANCH)["object"]["sha"]==commit["sha"]
  # The remote recursive tree at the exact commit binds every exported byte.
  remote=api("GET",REPO+"/git/trees/"+tree["sha"]+"?recursive=1")
  if not remote.get("truncated"):
   bypath={x["path"]:x for x in remote["tree"]if x["type"]=="blob"}
   for e in entries:
    b=e["content"].encode();assert bypath[e["path"]]["sha"]==hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
  else:
   for rel in ["README.md","control/PERFORMANCE_CURRENT.json","control/EXACT_EXECUTION_MANIFEST.json"]:
    x=api("GET",REPO+"/contents/"+PREFIX+"/"+rel+"?ref="+commit["sha"]);assert x["sha"]
  receipt=dict(status="EXACT_REMOTE_HEAD_PARENT_TREE_AND_EXPORTED_BLOBS_READBACK_PASS",head=commit["sha"],parent=base,tree=tree["sha"],files=len(entries),final=final,prefix=PREFIX,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  write(C/("REMOTE_FINAL_PUBLICATION_RECEIPT.json"if final else"REMOTE_EXECUTION_PUBLICATION_RECEIPT.json"),receipt);write(ep,dict(head=commit["sha"]))
  print(json.dumps(receipt))
if __name__=="__main__":main()
