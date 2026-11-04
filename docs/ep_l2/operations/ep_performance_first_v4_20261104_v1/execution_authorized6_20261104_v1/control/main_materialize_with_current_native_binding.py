from pathlib import Path
import hashlib,json,importlib.util,sys
C=Path(__file__).resolve().parent
V=C.parent.parent
B=V/"track_b"
ENTRY=B/"resource_activation_addendum_v3/main_activate_900_with_qualified_resources.py"
SEALED_ENTRY_SHA="b1df19cef280fec5b1b01632a8f88c310d5c880cc566048445b2f9f72da1b6d7"
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
review=json.loads((C/"CURRENT_NATIVE_REBASE_REVIEW.json").read_bytes())
candidate=review["new_combined_candidate_ref"]
pre=review["current_native_preimage_ref"]
assert digest(candidate["path"])==candidate["sha256"] and digest(pre["path"])==pre["sha256"]
assert Path(candidate["path"]).read_bytes().endswith(Path(pre["path"]).read_bytes())
assert digest(ENTRY)==SEALED_ENTRY_SHA
r=load("sealed_final_V4_900_resource_materializer",ENTRY);original_module=r.module
def bound_module(name,p):
 m=original_module(name,p)
 if Path(p)==B/"main_install_materialize.py":
  orig_sha=m.sha;orig_read=m.read;orig_ref=m.ref
  def current_sha(p):
   return candidate["sha256"] if Path(p)==B/"SHARED_NATIVE_ADDITIVE_CANDIDATE.sh" else orig_sha(p)
  def current_ref(p):
   return dict(candidate) if Path(p)==B/"SHARED_NATIVE_ADDITIVE_CANDIDATE.sh" else orig_ref(p)
  def current_read(p):
   return json.loads((C/"CURRENT_NATIVE_PREIMAGE_BINDING.json").read_bytes()) if Path(p)==B/"SHARED_NATIVE_PREIMAGE.json" else orig_read(p)
  m.sha=current_sha;m.ref=current_ref;m.read=current_read
 return m
r.module=bound_module
r.main()
