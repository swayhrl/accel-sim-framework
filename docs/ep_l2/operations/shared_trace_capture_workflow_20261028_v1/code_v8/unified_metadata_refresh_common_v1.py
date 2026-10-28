"""Private metadata only. No trace body, restore, simulator, GPU or public writes in generate()."""
from pathlib import Path
import json,hashlib,os,stat,time,math,types,ast,copy,collections
ROOT=Path("/root/share/mnt164/huangrulin/traces")
N=ROOT/"receipts/rtx4080_specialist_adaptation_20261026_v1"
HERE=Path(__file__).parent
BASE_SHA="4cf3f4203731a5488164f6f862cb45149fb4df7f19107db55497deacf1c97ce3"
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
def raw_archive_view(m):
 rawbase=CAT.parent/"raw_capture_archives";table,rref,rraw=m.pointer(rawbase/"catalog","CURRENT_RAW_CAPTURE_ARCHIVES.json");ptr=m.parse(rraw)
 need(table["schema"]=="RTX4080_RAW_CAPTURE_ARCHIVE_CATALOG_V1"and table["object_count"]==len(table["objects"])==3 and table["post_qualified_object_count"]==0 and table["consumer_qualification_granted"]is False and table["science_qualification_granted"]is False,"distinct RAW3 catalog without POST grant")
 rootref=dict(path=str(N/"large_multistream_raw3_public_directory_prepare_20261029_v2/ROOT_INDEPENDENT_PUBLIC_RAW3_ALL675_MAIN_DTC_AND13LOCK_ACCEPTANCE_V1.json"),bytes=1773,sha256="9a8a78b1a3e769d37c42c63dad08656bb053bc20048436f5c7883ce9b28f05fe")
 accepted=readref(rootref);need(accepted["objects"]==3 and accepted["manifest_members"]==675 and accepted["logical_bytes"]==34475098987 and accepted["immutable_catalog"]==rref["target"]and accepted["pointer"]==rref["pointer"]and accepted["POST_group_crop_consumer_numeric_science_granted"]is False,"Root actual RAW3 public acceptance")
 ids={"ORD_EXT_simpleStreams_cd83980a2646_A001_RAW_CAPTURE_ARCHIVE_V1","ORD_EXT_simpleMultiCopy_1eeba4a17d69_A001_RAW_CAPTURE_ARCHIVE_V1","ORD_EXT_simpleMultiCopy_db274fb1a2d8_A001_RAW_CAPTURE_ARCHIVE_V1"}
 need({r["asset_id"]for r in table["objects"]}==ids,"exact3 RAW IDs")
 rows=[]
 for r in table["objects"]:
  aid=r["asset_id"];need(r["kind"]=="RAW_CAPTURE_ARCHIVE"and r["state"]=="RAW_CAPTURE_ARCHIVE_POST_PENDING"and r["object_relative_path"]=="objects/"+aid,"typed RAW object path and state")
  directory=no_links(rawbase/r["object_relative_path"]);manifest,mr,_=m.read(directory/"MANIFEST.json");commit,cr,_=m.read(directory/"COMMIT.json");asset,ar,_=m.read(directory/"ASSET.json")
  need(mr["sha256"]==r["manifest_sha256"]and cr["sha256"]==r["commit_sha256"]and ar["sha256"]==r["asset_sha256"]and commit["manifest_sha256"]==mr["sha256"],"RAW catalog exact COMMIT MANIFEST ASSET refs")
  need(manifest["asset_id"]==commit["asset_id"]==asset["asset_id"]==aid and manifest["kind"]==commit["kind"]==asset["kind"]=="RAW_CAPTURE_ARCHIVE"and commit["status"]==asset["state"]=="RAW_CAPTURE_ARCHIVE_POST_PENDING","RAW actual identity")
  members={x["path"]:x for x in manifest["files"]};need(len(members)==r["member_count"]==commit["files"]and sum(x["bytes"]for x in members.values())==r["logical_bytes"]==commit["logical_bytes"],"RAW metadata member and byte totals")
  need(members["ASSET.json"]["sha256"]==ar["sha256"]and members["ASSET.json"]["bytes"]==ar["bytes"],"manifest-bound RAW ASSET")
  need(commit["POST_complete"]is False and commit["full_record_validation_complete"]is False and commit["consumer_qualification"]=="NOT_GRANTED"and commit["science_or_performance_qualification"]is False and asset["numeric_qualification"]=="NOT_GRANTED"and asset["derived_crop_available"]is False,"RAW gaps not converted to POST or consumer qualification")
  job,jr,_=m.read(directory/"FROZEN_JOB_RAW.json");need(jr["sha256"]==members["FROZEN_JOB_RAW.json"]["sha256"]and jr["bytes"]==members["FROZEN_JOB_RAW.json"]["bytes"]and job["id"]==r["source_queue_id"]and job["task"]["binary_sha256"]==r["task_identity"]["binary_sha256"],"RAW exact manifest-bound original job")
  rows.append(dict(asset_id=aid,source_queue_id=r["source_queue_id"],program_label=job["task"]["program"],task_identity=r["task_identity"],producer_sha256=r["producer_sha256"],state="RAW_CAPTURE_ARCHIVE_POST_PENDING",kind="RAW_CAPTURE_ARCHIVE",public_object_path=str(directory),member_count=r["member_count"],logical_bytes=r["logical_bytes"],declared_kernel_launches=r["declared_kernel_launches"],declared_records=r["declared_records"],counts_declared_not_POST_verified=True,identity_refs=dict(manifest=mr,commit=cr,asset=ar,frozen_job=jr),original_receiver_proof_ref=r["original_receiver_proof_ref"],POST_complete=False,grouped_trace_available=False,derived_crop_available=False,consumer_numeric_science_qualification="NOT_GRANTED",body_read_for_discovery=False,qualification_inferred=False))
 return rows,rref,ptr,rootref

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
 need(len(ordinary["objects"])==len(derived["objects"])==66,"actual66/66 required")
 public_root_ref=dict(path=str(CAT.parent/"private_candidates/current11_light_post_consumer_prepare_20261029_v2/tiny_concurrent2_closed55_archive_pairs_prepare_v1/ROOT_INDEPENDENT_PUBLIC66_ALL132_AND_MAIN_DTC24_TYPED_UNKNOWN_ACCEPTANCE_V1.json"),bytes=1187,sha256="989cd4bc6fb9737638c59596958c764a8e4c8288ff3ccb5787d344978f57e552")
 public=readref(public_root_ref);need(public["ordinary"]==public["derived"]==66 and public["ordinary_version"]==oref["target"]["sha256"]and public["derived_version"]==dref["target"]["sha256"],"Root real66 acceptance and current immutable versions")
 enriched=m.enrich_ordinary(CAT.parent,ordinary);enriched_derived=m.enrich_ordinary(CAT.parent,derived)
 assets=m.exact_original_SM89_assembly(enriched,derived);need(len(assets)==132,"all132 strict actual objects")
 bindings=[]
 for kind,rows in [("regular",enriched["objects"]),("derived",enriched_derived["objects"])]:
  for row in rows:
   ident,ir,_=m.read(CAT.parent/"objects"/row["asset_id"]/"ASSET.json")
   need(ir==row["_identity_refs"]["asset"],"same manifest-bound own identity")
   bindings.append(dict(asset_id=row["asset_id"],variant=kind,source_queue_id=ident.get("source_queue_id"),parent_asset_id=ident.get("parent_asset_id"),own_manifest_bound_identity_refs=row["_identity_refs"],program_label=ident.get("program"),canonical_family_label=ident.get("canonical_family"),capture_or_consumer_qualification_inferred=False))
 result=copy.deepcopy(baseline);result["SM89_committed_trace_assets"]=assets
 result["source_refs"].update(SM89_ordinary=oref,SM89_derived=dref,SM89_qualification_overlay=qref,SM70_current_NAS_access=accessref)
 result["counts"].update(SM89_regular=66,SM89_derived=66)
 result["SM89_manifest_bound_capture_source_bindings"]=bindings
 result["label_units"]=dict(program_labels=sorted({x["program_label"]for x in bindings if x["program_label"]}),declared_family_labels=sorted({x["canonical_family_label"]for x in bindings if x["canonical_family_label"]}),programs_and_families_are_labels_not_workload_input_or_qualification_counts=True,objects_regular_and_derived_are_separate_not_132_workloads=True)
 typed_ref=dict(path=str(N/"auto161_pipeline_20261026_v1/exact_gaussian256_eighth_data_prepare_20261029_v1/ROOT_INDEPENDENT_TYPED_EIGHTH_FORMAL_CLOSEOUT_ACCEPTANCE_V1.json"),bytes=2026,sha256="ef3c3f37faf3dbe1e41c829e9c46a141a2ca3b324d8ef6216c8b520c03745e3a")
 typed=readref(typed_ref);need(typed["typed_scope_complete"]==8 and typed["formal_covered_rows"]==161 and typed["old160_ACK_inputfp_reused"],"actual typed8 formal close")
 deferred=readref(typed["remaining153_deferred_view_ref"])
 need(baseline["independent_stage_views"]["typed161"]["Root_formal_acceptance_ref"]==typed_ref and baseline["independent_stage_views"]["typed161"]["complete_exact_scopes"]==8 and baseline["independent_stage_views"]["typed161"]["remaining_deferred"]==153,"typed8/153 entire formal view remains frozen")
 result["independent_stage_views"]=copy.deepcopy(baseline["independent_stage_views"])
 capture_projection_ref=dict(path=str(N/"ordinary33_asset_priority_stage_matrix_prepare_20261029_v1/ORDINARY33_PUBLIC_ASOF31_CAPTURE_ONLY_PROJECTION_V6.json"),bytes=16466,sha256="1ca1aa3e3dd6793778b1f03c55c843fdb3e9f0428ecba3fea561187d802a0da4")
 cp=readref(capture_projection_ref);readref(cp["source_census_ref"])
 need(cp["schema"]=="ORDINARY33_CAPTURE_ASOF_PUBLIC_METADATA_PROJECTION_V6"and cp["total_original33"]==33 and cp["capture_positive_closed"]==31 and cp["capture_not_closed"]==len(cp["remaining_qids"])==2 and len(cp["this12_positive_closed"])==10,"exactpositive capture31 asof only")
 positive=[];closed_qids=set()
 for row in cp["this12_positive_closed"]:
  need(row["qid"]not in closed_qids and row["status"]=="CAPTURED_POST_PENDING","unique positiveclosed capture only");closed_qids.add(row["qid"])
  projected=dict(qid=row["qid"],status=row["status"])
  for key,value in row.items():
   if key.endswith("_ref"):
    need(set(value)=={"path","bytes","sha256"},"public closedproof reference fields");readref(value);projected[key]=value
  positive.append(projected)
 need(not closed_qids.intersection(cp["remaining_qids"]),"open capture must not be counted closed")
 result["independent_stage_views"]["ordinary33"]=dict(unit="original33 exact capture jobs; not POST/consumer or242historical rewrite",asof_census_ref=capture_projection_ref,full_census_ref=cp["source_census_ref"],asof_unix=cp["asof_epoch"],asof_source_document_not_current_process_status=True,capture_counts=dict(baseline_captured21=21,baseline_remaining12=12,fresh_capture_closed=31,fresh_not_capture_closed=2,new_positive_capture_closed_since_census=10),positive_capture_closed_this12=positive,remaining_qids=cp["remaining_qids"],POST_qualification_not_inferred=True,no_old_QUEUE_status_rewrite=True)
 rawrows,rawref,rawptr,rawaccept=raw_archive_view(m)
 result["RAW_capture_archives"]=rawrows;result["source_refs"]["SM89_RAW_capture_archives"]=rawref
 result["counts"]["SM89_RAW_capture_archives"]=3
 result["label_units"]["raw_program_labels"]=sorted({r["program_label"]for r in rawrows})
 result["label_units"]["RAW3_not_strict_POST_assets_or_three_new_workloads"]=True
 result["independent_stage_views"]["RAW_archive_delivery"]=dict(unit="raw immutable archives; separate from strict ordinary/derived objects and workload coverage",objects=3,Root_public_acceptance_ref=rawaccept,public_catalog_ref=rawref,POST_qualified_objects=0,consumer_or_scientific_qualification_granted=False,remaining_gates=["FULL_RECORD_POST","MULTISTREAM_GROUPING","DERIVED_CROP","EXACT_CONSUMER","NUMERIC_SCIENCE"])
 result["previous_snapshot_sha256"]=BASE_SHA;result["updated_unix"]=time.time()
 result["status"]="METADATA_ONLY_DISCOVERY_SNAPSHOT_NO_TOOL_OR_QUALIFICATION_ACTIVATION"
 result["consumer_or_scientific_qualification_granted"]=False;result["public_entry_changed"]=False
 need(result["SM70_exact_inputs"]==baseline["SM70_exact_inputs"]and result["SM89_historical_capture_work_items"]==baseline["SM89_historical_capture_work_items"]and len(result["SM89_historical_capture_work_items"])==242,"125 selectors and242 exact historical states preserved")
 need(result["independent_stage_views"]["typed161"]==baseline["independent_stage_views"]["typed161"],"typed8/153 exact graph unchanged")
 m.validate_index(result);assert_no_secret_keys(result)
 source_docs={"SM89_RAW_capture_archives":rawptr,"SM89_ordinary":m.parse(oraw),"SM89_derived":m.parse(draw),"SM89_qualification_overlay":m.parse(qraw),"SM70_current_NAS_access":accessptr}
 source_catalogs={}
 for key,fn in [("SM89_ordinary","CURRENT_RTX4080_CATALOG.json"),("SM89_derived","CURRENT_RTX4080_DERIVED_CATALOG.json"),("SM89_qualification_overlay","CURRENT_RTX4080_QUALIFICATION_OVERLAY.json")]:
  exact_pointer_equal(source_docs[key],m.read(CAT/fn,1024*1024)[0])
 exact_pointer_equal(rawptr,m.read(CAT.parent/"raw_capture_archives/catalog/CURRENT_RAW_CAPTURE_ARCHIVES.json",65536)[0])
 exact_pointer_equal(accessptr,m.read(ROOT/"catalog/CURRENT_SM70_NAS_ACCESS.json",65536)[0])
 exact_pointer_equal(oldptr,m.read(ROOT/"catalog/CURRENT_UNIFIED_DISCOVERY.json",65536)[0])
 for kind,fn,expected in [("ordinary","ASSETS.json",oref["target"]["sha256"]),("derived","DERIVED_ASSETS.json",dref["target"]["sha256"])]:
  rawdata=raw(CAT/fn);need(h(rawdata)==expected,"data catalog equals exact immutable version");source_catalogs[kind]=dict(path=str(CAT/fn),bytes=len(rawdata),sha256=h(rawdata))
 proof=dict(schema="PRIVATE_UNIFIED66_RAW3_METADATA_SOURCE_FREEZE_V1",baseline_snapshot_ref=baseref,old_unified_pointer_ref=oldptrref,old_unified_pointer_preimage=oldptr,original_builder_ref=ref(ORIGINAL),original_SM89_assembly_AST_sha256=ast_proof,original125_plan_ref=planref,Root125_access_acceptance_ref=accessptr["Root_acceptance_ref"],Root_public66_acceptance_ref=public_root_ref,Root_RAW3_acceptance_ref=rawaccept,Root_capture_asof_projection_ref=capture_projection_ref,Root_typed8_acceptance_ref=typed_ref,source_refs=result["source_refs"],source_pointer_preimages=source_docs,current_data_catalog_refs=source_catalogs,all125_SM70_rows_exact_values_unchanged=True,all242_historical_rows_exact_values_unchanged=True,SM89_regular=66,SM89_derived=66,RAW_capture_archives=3,metadata_only=True,body_bytes_read=0,tool_switch_or_science_grant=False)
 return result,proof
