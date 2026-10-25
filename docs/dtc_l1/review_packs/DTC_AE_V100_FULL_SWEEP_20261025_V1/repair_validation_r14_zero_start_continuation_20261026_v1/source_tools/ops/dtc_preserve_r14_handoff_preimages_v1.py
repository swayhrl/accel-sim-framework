"""Preserve exact metadata bytes; never mutates native authority or R13 assets."""
import pathlib,json,hashlib,datetime,fcntl
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=R/'ops/r14_handoff_preimages_v1';D.mkdir(exist_ok=False);BASE=T/'docs-worktree/docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/repair_validation_20261025_v1';items=[]
def keep(src,rel,body=None):
 body=src.read_bytes()if body is None else body;p=D/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(body)
 row={'source':str(src),'preserved_path':str(p),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'kind':'EXACT_FILE_BYTES'};items.append(row);return row
for name in ['REPAIR_BUILD_PROFILE_V1.json','EXECUTION_PLAN_V1.json','REGISTRY_REQUEST_CANDIDATE_V1.json','SCIENCE_AUTHORIZATION.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','ENGINE_OVERLAY_CPU_QUALIFICATION_V1.json','FINAL_REPAIR_CANDIDATE_POSTFREEZE_QUALIFICATION_V1.json']:
 published=BASE/'repair_metadata/control'/name
 if published.exists():keep(published,'published_R13_metadata/'+name)
 live=R/'validation/control'/name
 if live.exists():keep(live,'live_before_R14/'+name)
for rel in ['operations/R13_ZERO_MODEL_QUALIFICATION_V1.json','operations/R13_CPU_DRIVER_RESULT_V1.json','source_tools/ops/sweep_controller.py']:
 keep(BASE/rel,'published_R13_metadata/'+rel)
reg=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
with (N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as f:
 fcntl.flock(f,fcntl.LOCK_SH);body=reg.read_bytes();text=body.decode('utf-8');parsed=json.loads(body);regsha=hashlib.sha256(body).hexdigest();decoder=json.JSONDecoder();token='"registered_future_requests"';assert text.count(token)==1;start=text.index(':',text.index(token))+1
 while text[start].isspace():start+=1
 requestmap,map_end=decoder.raw_decode(text,start);spans=[]
 for req,label in [('DTC_AE_V100_FULL_SWEEP_20261025_V1','ORIGINAL_REQUEST_BEFORE_R14.EXACT_OBJECT.json'),('DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1','REPAIR_REQUEST_BEFORE_R14.EXACT_OBJECT.json')]:
  key=json.dumps(req)+':';a=text.index(key,start,map_end)+len(key)
  while text[a].isspace():a+=1
  obj,b=decoder.raw_decode(text,a);assert obj==parsed['registered_future_requests'][req];chunk=text[a:b].encode('utf-8');row=keep(reg,'live_before_R14/'+label,chunk);row['kind']='EXACT_JSON_OBJECT_SUBSPAN_BYTES';row['source_registry_sha256']=regsha;row['request']=req;spans.append({'request':req,'remaining':obj.get('remaining'),'consumed_count':len(obj.get('consumed',{})),'budget':obj.get('budget'),'exact_object_sha256':row['sha256'],'preserved_path':row['preserved_path']})
 epoch=N/'control/CURRENT_SCIENCE_EPOCH.json';keep(epoch,'live_before_R14/CURRENT_SCIENCE_EPOCH.json')
repair=parsed['registered_future_requests']['DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1'];assert repair['budget']==23 and not repair.get('consumed',{})and repair['remaining']==23
requestdir=N/'control/science_authority/requests/DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';intents=list(requestdir.glob('*.INTENT.json'))if requestdir.exists()else[];assert not intents
state=R/'validation/analysis/BATCH_STATE_R13.json'
if state.exists():keep(state,'live_before_R14/BATCH_STATE_R13.json')
report={'schema':'R14_ZERO_START_METADATA_PREIMAGES_V1','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'published_R13_commit':'7db6292af24c690553cdaaaffb3c9fe3496dca98','source_registry_sha256':regsha,'registry_snapshot_is_read_only':True,'requests':spans,'repair_before_R14':{'budget':23,'remaining':23,'consumed':0,'INTENT_files':0,'scientific_starts_proven_from_consumed_INTENT':0},'items':items,'old_files_rewritten':False,'live_authority_or_entry_writes':False,'new_scientific_start':False,'notes':'Q objects are exact byte subspans of the locked source registry; not reserialized approximations. Full registry is referenced by content SHA, avoiding unrelated peer authority duplication.'};out=D/'PREIMAGE_MANIFEST_V1.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':'EXACT_METADATA_PREIMAGES_PRESERVED','directory':str(D),'manifest_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(items),'bytes':sum(x['bytes']for x in items),'requests':spans},ensure_ascii=False))
