"""Private metadata only. No trace body, restore, simulator, GPU or public writes in generate()."""
from pathlib import Path
import json,hashlib,os,stat,time,math,types,ast,copy,collections
ROOT=Path("/root/share/mnt164/huangrulin/traces")
N=ROOT/"receipts/rtx4080_specialist_adaptation_20261026_v1"
HERE=Path(__file__).parent
BASE_SHA="239b8026fbc0e5620aee9f95933c8b833fd1e571bcb5f66afefc42e9ec23a4d0"
PLAN_SHA="7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6"
ORIGINAL=N/"unified_discovery_prepare_20261027_v1/trace_discovery_v1.py"
ORIGINAL_SHA="329ead13b907f9cb3535f484b9167e7f9c8c6d89bfa53e8b7f478da97fb6ba90"
CAT=ROOT/"rtx4080_sm89/bulk_20261024_v1/catalog"
TIMESTAMPS={"unix","utc_unix"}
def need(v,m):
 if not v:raise ValueError("UNIFIED_METADATA_REJECT:"+m)
def h(b):return hashlib.sha256(b).hexdigest()
def parse(b):
 def pairs(items):
  d={}
  for k,v in items:need(k not in d,"duplicate JSON key");d[k]=v
  return d
 return json.loads(b,object_pairs_hook=pairs)
def canonical(z):return (json.dumps(z,sort_keys=True,separators=(",",":"))+"\n").encode()
def no_links(p):
 p=Path(p);need(p.is_absolute()and ".."not in p.parts,"absolute canonical path")
 for q in[p,*p.parents]:need(not q.is_symlink(),"metadata parent/leaf symlink")
 return p
def raw(p,cap=32*2**20):
 p=no_links(p)
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode)and 0<s.st_size<=cap,"bounded regular metadata");blocks=[];left=s.st_size
  while left:
   b=os.read(fd,min(left,65536));need(b,"metadata short read");blocks.append(b);left-=len(b)
  need(not os.read(fd,1),"metadata grew");e=os.fstat(fd);sig=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  need(sig(s)==sig(e),"sameFD changed")
 finally:os.close(fd)
 return b"".join(blocks)
def ref(p):
 b=raw(p);return dict(path=str(p),bytes=len(b),sha256=h(b))
def readref(r):
 b=raw(r["path"]);need(len(b)==r["bytes"]and h(b)==r["sha256"],"reference rawSHA");return parse(b)
def readonly_module():
 b=raw(ORIGINAL,128*1024);need(h(b)==ORIGINAL_SHA,"original reviewed builder pin")
 m=types.ModuleType("original_reviewed_discovery");m.__file__=str(ORIGINAL);exec(compile(b,str(ORIGINAL),"exec"),m.__dict__)
 def bounded_read(p,cap=32*2**20):
  b=raw(p,cap);return m.parse(b),dict(path=str(p),bytes=len(b),sha256=h(b)),b
 m.read=bounded_read
 # Reuse exactly the original SM89 assembly AST block; SM70 is kept from the Root-accepted all125 snapshot.
 tree=ast.parse(b);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=="assemble")
 def assigned(n,name):return isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)
 start=next(i for i,n in enumerate(fn.body)if assigned(n,"sm89"));end=next(i for i,n in enumerate(fn.body)if assigned(n,"work"))
 body=copy.deepcopy(fn.body[start:end]);proof=h(ast.dump(ast.Module(body=body,type_ignores=[]),include_attributes=False).encode())
 small=ast.parse("def exact_original_SM89_assembly(ordinary,derived): pass").body[0];small.body=body+[ast.Return(value=ast.Name(id="sm89",ctx=ast.Load()))]
 module=ast.fix_missing_locations(ast.Module(body=[small],type_ignores=[]));exec(compile(module,"original_unchanged_SM89_AST_slice","exec"),m.__dict__)
 return m,proof
def pointer_semantic(v):
 need(type(v)is dict,"pointer dictionary")
 for k in TIMESTAMPS&set(v):need(type(v[k])in(int,float)and math.isfinite(v[k]),"typed finite known timestamp")
 return {k:x for k,x in v.items()if k not in TIMESTAMPS}
def exact_pointer_equal(before,after):
 need(set(before)==set(after),"complete pointer keyset");need(pointer_semantic(before)==pointer_semantic(after),"complete non-timestamp pointer semantics")
 return True
def safe_private_output(p):
 p=Path(p);need(p.is_absolute()and p.is_relative_to(HERE)and p!=HERE and ".."not in p.parts,"private output only")
 for q in[p,*p.parents]:need(not q.is_symlink(),"private output symlink")
 need(not p.exists(),"new output namespace");return p
def save_new(p,z):
 b=canonical(z);need(len(b)<=16*2**20,"public query compatible snapshot cap")
 with Path(p).open("xb")as f:f.write(b);f.flush();os.fsync(f.fileno())
 return dict(path=str(p),bytes=len(b),sha256=h(b))
def assert_no_secret_keys(v):
 if isinstance(v,dict):
  for k,x in v.items():
   need(not any(w in k.lower()for w in ["nonce","token","secret"]),"secret-bearing key cannot enter discovery")
   assert_no_secret_keys(x)
 elif isinstance(v,list):
  for x in v:assert_no_secret_keys(x)
def collect():
 m,ast_proof=readonly_module()
 baseline,baseref,_=m.read(ROOT/"catalog/versions"/("unified_"+BASE_SHA+".json"),16*2**20);need(baseref["sha256"]==BASE_SHA,"approved baseline snapshot")
 oldptr,oldptrref,_=m.read(ROOT/"catalog/CURRENT_UNIFIED_DISCOVERY.json",65536);need(oldptr["sha256"]==BASE_SHA,"no silent unified rebase")
 plan,planref,_=m.read(ROOT/"receipts/sm70_binding_parent_20261025_v1/content/sha256"/PLAN_SHA,8*2**20);need(planref["sha256"]==PLAN_SHA and len(plan)==125,"original exact125 plan")
 indexed={x["bundle_id"]:x for x in plan};need(len(indexed)==125,"unique original125 selectors")
 for row in baseline["SM70_exact_inputs"]:
  original=indexed[row["id"]]
  for key in ["suite","program","extent","members","ordered_kernel_members"]:need(row[key]==original[key],"unchanged exact SM70 selector "+key)
  need(row["qualification_inferred"]is False,"no SM70 qualification inference")
 need(len(baseline["SM70_exact_inputs"])==125,"all125 retained")
 access,accessref,accessraw=m.pointer(ROOT/"catalog","CURRENT_SM70_NAS_ACCESS.json")
 need(accessref["target"]["sha256"]=="90c498ca1fa83a85eeb07f79221a5580e40d6ce922aa6eb6e9beecc5cdfb9e62","accepted NAS access snapshot")
 accessptr=m.parse(accessraw);acceptance=readref(accessptr["Root_acceptance_ref"])
 need(accessptr["Root_acceptance_ref"]["sha256"]=="b2ac6f6dff997a5ee63e99832622802b798f8847d6bcecb8584371435e6fd190"and acceptance["bundles"]==125 and acceptance["members"]==25149,"Root all125 NAS acceptance unchanged")
 ordinary,oref,oraw=m.pointer(CAT,"CURRENT_RTX4080_CATALOG.json");derived,dref,draw=m.pointer(CAT,"CURRENT_RTX4080_DERIVED_CATALOG.json")
 overlay,qref,qraw=m.pointer(CAT,"CURRENT_RTX4080_QUALIFICATION_OVERLAY.json")
 need(len(ordinary["objects"])==len(derived["objects"])==63,"actual63/63 required")
 public_root_ref=dict(path=str(CAT.parent/"private_candidates/current11_light_post_consumer_prepare_20261029_v2/five_closed55_archive_pairs_prepare_v1/ROOT_INDEPENDENT_PUBLIC63_ALL126_AND_MAIN_DTC60_ACCEPTANCE_V1.json"),bytes=914,sha256="fb8c1067fb8b7ca2c98bf1069affd99dd6d12c26bf9e32b0c5259c5bc27cfdf6")
 public=readref(public_root_ref);need(public["ordinary"]==public["derived"]==63 and public["ordinary_version"]==oref["target"]["sha256"]and public["derived_version"]==dref["target"]["sha256"],"Root real63 acceptance and current immutable versions")
 enriched=m.enrich_ordinary(CAT.parent,ordinary);enriched_derived=m.enrich_ordinary(CAT.parent,derived)
 assets=m.exact_original_SM89_assembly(enriched,derived);need(len(assets)==126,"all126 actual objects")
 bindings=[]
 for kind,rows in [("regular",enriched["objects"]),("derived",enriched_derived["objects"])]:
  for row in rows:
   ident,ir,_=m.read(CAT.parent/"objects"/row["asset_id"]/"ASSET.json")
   need(ir==row["_identity_refs"]["asset"],"same manifest-bound own identity")
   bindings.append(dict(asset_id=row["asset_id"],variant=kind,source_queue_id=ident.get("source_queue_id"),parent_asset_id=ident.get("parent_asset_id"),own_manifest_bound_identity_refs=row["_identity_refs"],program_label=ident.get("program"),canonical_family_label=ident.get("canonical_family"),capture_or_consumer_qualification_inferred=False))
 result=copy.deepcopy(baseline);result["SM89_committed_trace_assets"]=assets
 result["source_refs"].update(SM89_ordinary=oref,SM89_derived=dref,SM89_qualification_overlay=qref,SM70_current_NAS_access=accessref)
 result["counts"].update(SM89_regular=63,SM89_derived=63)
 result["SM89_manifest_bound_capture_source_bindings"]=bindings
 result["label_units"]=dict(program_labels=sorted({x["program_label"]for x in bindings if x["program_label"]}),declared_family_labels=sorted({x["canonical_family_label"]for x in bindings if x["canonical_family_label"]}),programs_and_families_are_labels_not_workload_input_or_qualification_counts=True,objects_regular_and_derived_are_separate_not_126_workloads=True)
 typed_ref=dict(path=str(N/"auto161_pipeline_20261026_v1/exact_gaussian256_eighth_data_prepare_20261029_v1/ROOT_INDEPENDENT_TYPED_EIGHTH_FORMAL_CLOSEOUT_ACCEPTANCE_V1.json"),bytes=2026,sha256="ef3c3f37faf3dbe1e41c829e9c46a141a2ca3b324d8ef6216c8b520c03745e3a")
 typed=readref(typed_ref);need(typed["typed_scope_complete"]==8 and typed["formal_covered_rows"]==161 and typed["old160_ACK_inputfp_reused"],"actual typed8 formal close")
 deferred=readref(typed["remaining153_deferred_view_ref"])
 census_ref=dict(path=str(N/"ordinary33_asset_priority_stage_matrix_prepare_20261029_v1/ROOT_ORIGINAL33_ASSET_PRIORITY_STAGE_AUDIT_ENTRY_V3.json"),bytes=3578,sha256="ddc440e9670002b86baf4b79fdffb42c34c4618caca8e45ef4388a8d1c23c5c1")
 census=readref(census_ref)
 result["independent_stage_views"]=dict(typed161=dict(unit="frozen rows; not GPU jobs or generic consumer combinations",Root_formal_acceptance_ref=typed_ref,complete_exact_scopes=8,remaining_deferred=153,deferred_view_ref=typed["remaining153_deferred_view_ref"],all161_completion_delivery_gate=False,no_history_rewrite=True,no_generic_qualification_inferred=True),ordinary33=dict(unit="original33 exact capture jobs; independent from242 historical items",asof_census_ref=census_ref,capture_counts=census["capture_counts"],asof_source_document_not_current_process_status=True,no_old_QUEUE_status_rewrite=True))
 result["previous_snapshot_sha256"]=BASE_SHA;result["updated_unix"]=time.time()
 result["status"]="METADATA_ONLY_DISCOVERY_SNAPSHOT_NO_TOOL_OR_QUALIFICATION_ACTIVATION"
 result["consumer_or_scientific_qualification_granted"]=False;result["public_entry_changed"]=False
 need(result["SM70_exact_inputs"]==baseline["SM70_exact_inputs"]and result["SM89_historical_capture_work_items"]==baseline["SM89_historical_capture_work_items"]and len(result["SM89_historical_capture_work_items"])==242,"125 selectors and242 exact historical states preserved")
 m.validate_index(result);assert_no_secret_keys(result)
 source_docs={"SM89_ordinary":m.parse(oraw),"SM89_derived":m.parse(draw),"SM89_qualification_overlay":m.parse(qraw),"SM70_current_NAS_access":accessptr}
 source_catalogs={}
 for key,fn in [("SM89_ordinary","CURRENT_RTX4080_CATALOG.json"),("SM89_derived","CURRENT_RTX4080_DERIVED_CATALOG.json"),("SM89_qualification_overlay","CURRENT_RTX4080_QUALIFICATION_OVERLAY.json")]:
  exact_pointer_equal(source_docs[key],m.read(CAT/fn,1024*1024)[0])
 exact_pointer_equal(accessptr,m.read(ROOT/"catalog/CURRENT_SM70_NAS_ACCESS.json",65536)[0])
 exact_pointer_equal(oldptr,m.read(ROOT/"catalog/CURRENT_UNIFIED_DISCOVERY.json",65536)[0])
 for kind,fn,expected in [("ordinary","ASSETS.json",oref["target"]["sha256"]),("derived","DERIVED_ASSETS.json",dref["target"]["sha256"])]:
  rawdata=raw(CAT/fn);need(h(rawdata)==expected,"data catalog equals exact immutable version");source_catalogs[kind]=dict(path=str(CAT/fn),bytes=len(rawdata),sha256=h(rawdata))
 proof=dict(schema="PRIVATE_UNIFIED63_METADATA_SOURCE_FREEZE_V1",baseline_snapshot_ref=baseref,old_unified_pointer_ref=oldptrref,old_unified_pointer_preimage=oldptr,original_builder_ref=ref(ORIGINAL),original_SM89_assembly_AST_sha256=ast_proof,original125_plan_ref=planref,Root125_access_acceptance_ref=accessptr["Root_acceptance_ref"],Root_public63_acceptance_ref=public_root_ref,Root_typed8_acceptance_ref=typed_ref,source_refs=result["source_refs"],source_pointer_preimages=source_docs,current_data_catalog_refs=source_catalogs,all125_SM70_rows_exact_values_unchanged=True,all242_historical_rows_exact_values_unchanged=True,SM89_regular=63,SM89_derived=63,metadata_only=True,body_bytes_read=0,tool_switch_or_science_grant=False)
 return result,proof
