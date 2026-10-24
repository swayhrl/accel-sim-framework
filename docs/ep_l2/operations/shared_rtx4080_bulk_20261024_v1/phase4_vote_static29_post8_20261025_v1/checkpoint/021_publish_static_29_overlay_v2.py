import pathlib,json,hashlib,time,fcntl,os,copy,shutil
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');T=B/'objects/stage_evidence_cubin_collision_cpu_109_20261024_v1';STATUS='ALL_LISTED_IMAGES_PRESERVED_PRECEDING_EMPTY_CODE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o,exclusive=True):
 with p.open('x'if exclusive else'w')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
parent=T/'supplement_v1/PARENT_29_COLLISION_READBACK.json';assert sha(parent)=='766e56f449af1b0a8c414b172d56fa7dfc1277edc2cf25042fdc9b118e43476e';review=json.loads(parent.read_text());assert review['status']=='PARENT_29_COLLISION_BINARIES_FULL_ARCHIVES_NATIVE_SHA_AND_EMPTY_CODE_ANALYSIS_PASS'
main=json.loads((T/'COMMIT.json').read_text());supp=json.loads((T/'supplement_v1/COMMIT.json').read_text());assert main['manifest_sha256']=='da028a60adb9f7d19685888dde770f7c4d5ff43d2a277836412e6e2bac8f6555'
assert sha(T/'MANIFEST.json')==main['manifest_sha256']
for obj,commit in [(T,main),(T/'supplement_v1',supp)]:
 for row in commit['files']:
  p=obj/row['path'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256']
classes={r['binary_sha256']:r for r in review['binary_classifications']};assert len(classes)==29 and all(r['all_overwritten_preceding_images_empty_code']for r in classes.values())
locks=[];deadline=time.time()+120
try:
 for n in ['RTX4080_SOURCE.lock','RTX4080_TARGET.lock']:
  f=open(C/n,'a');locks.append(f)
  while True:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);break
   except BlockingIOError:assert time.time()<deadline;time.sleep(1)
 pointer=B/'catalog/CURRENT_RTX4080_QUALIFICATION_OVERLAY.json';before=pointer.read_bytes();old=json.loads(before);p=B/'catalog'/old['relative_path'];assert sha(p)==old['sha256'];q=json.loads(p.read_text())
 def annotate(row,h):
  r=dict(row);r.update(status=STATUS,previous_census_status=row.get('status'),duplicate_basename_remains_true=True,static_all_listed_images_preserved=True,overwritten_preceding_images_empty_code=True,static_image_classification=classes[h],static_image_parent_evidence={'engineering_object':str(T.relative_to(B)),'engineering_manifest_sha256':main['manifest_sha256'],'main_archive_sha256':'3048adf8536d93f86787321c66774d73c55bd785b34b369aaceb6648a74c380d','supplement_archive_sha256':'bdd671e550a8baa19d4b95f99e10fb2cc906c572ad4b4ded766b4c00aa03309b','parent29_receipt_member':str(parent.relative_to(B)),'parent29_receipt_sha256':sha(parent)},qualification_scope='Static exact29 listed image retention and preceding empty-code classification only; no actual-loaded/JIT/runtime completeness/input/consumer/timing/science upgrade')
  return r
 for h in classes:q['by_binary'][h]=annotate(q['by_binary'].get(h,{'binary_sha256':h}),h)
 asset_count=0
 for ident,row in list(q['by_asset'].items()):
  h=row.get('binary_sha256')
  if h in classes:q['by_asset'][ident]=annotate(row,h);asset_count+=1
 assert asset_count==5
 q.update(schema='RTX4080_STATIC_IMAGE_QUALIFICATION_OVERLAY_V2',kind='EXACT29_STATIC_IMAGE_RETENTION_AND_EMPTY_PREDECESSOR_CLASSIFICATION_NOT_RUNTIME_REVALIDATION',previous_overlay_sha256=old['sha256'],resolved_duplicate_binary_count=29,resolved_formal_asset_count=5,immutable_assets_unchanged=True,executed_domain_evidence_retained=True,scope='Prior duplicate census preserved;29 exact binaries now all listed images retained. All overwritten preceding images were empty code. No change to loaded-code/input/producer/consumer/timing/numerical/science axes.')
 payload=(json.dumps(q,indent=2)+'\n').encode();h=hashlib.sha256(payload).hexdigest();dst=B/'catalog/qualification_overlays'/('static_enum_'+h+'.json');assert not dst.exists()
 with dst.open('xb')as f:f.write(payload);f.flush();os.fsync(f.fileno())
 assert sha(dst)==h and pointer.read_bytes()==before
 new={'schema':'RTX4080_QUALIFICATION_OVERLAY_POINTER_V1','relative_path':str(dst.relative_to(B/'catalog')),'sha256':h,'previous':old,'unix':time.time()};tmp=pointer.with_suffix('.tmp');save(tmp,new,False);os.replace(tmp,pointer)
 save(C/'STATIC_29_PUBLIC_OVERLAY_V2_PUBLICATION.json',{'status':'EXACT29_STATIC_AXIS_ONLY_PUBLISHED','new_overlay':new,'resolved_formal_assets':5,'resolved_unique_formal_binaries':3,'immutable_payloads_unchanged':True,'parent29_receipt_sha256':sha(parent),'no_new_GPU_or_SIM':True})
 print(json.dumps({'overlay_sha256':h,'resolved_formal_assets':5,'resolved_binaries':29}))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
