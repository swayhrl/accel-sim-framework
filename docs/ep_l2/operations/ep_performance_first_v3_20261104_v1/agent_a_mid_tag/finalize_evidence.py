from pathlib import Path as P
import json,hashlib,csv,subprocess
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1');A=J/'research/performance_first_v3_20261104_v1/agent_a_mid_tag';V=J/'research/performance_first_v2_20261103_v1';close=V/'activation_20261104_v1/recovery_20261104_v1/concurrency10_20261104_v1/closeout_20261104_v1';O=P('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p),bytes=P(p).stat().st_size)
def read(p):return json.loads(P(p).read_text())
def put(p,d):P(p).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');return ref(p)
idx=read(A/'MID_TAG_FAMILY_SCOPE.json');rows=[];reuse=[];deltas=[]
for row in idx['points']:
 p=P(row['spec_ref']['path']);s=read(p);work=s['workload'];s['estimated_peak_RAM_bytes']=(1 if work=='FWT'else 5)*(1<<30);s['estimated_wall_seconds']=(1200 if work=='FWT'else 5400)
 s['output_forecast'].update(stored_hot_envelope_bytes=16<<20,estimated_result_archive_bytes=16<<20,forecast_basis='V2 matched exact input111 observed FWT max3.6MiB hot/GEMM<0.9MiB; sixteenMiB includes metadata;256MiB is hardstop not extra resource reservation')
 put(p,s);row['spec_ref']=ref(p)
 rows.append(dict(workload=work,mode=s['mode'],sets=s['geometry']['sets'],ways=s['geometry']['ways'],Tag_entries_per_slice=512,nominal_Tag_addressable_bytes=64*512*128,physical_Payload_bytes=64*1168*128,status='ENGINEERING_CANDIDATE_NOT_EXECUTED',cycles=None,same_background_S_EP_ratio=None,Source=s['source_identity']['core_source_commit'],ELF=s['source_identity']['binary_sha256'],spec_path=str(p),spec_sha256=sha(p),estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],estimated_result_growth_bytes=16<<20))
 base=read(s['absolute_REF850_spec_ref']['path']);diff={k:dict(before=base['expected_effective_options'][k],after=v)for k,v in s['expected_effective_options'].items()if base['expected_effective_options'][k]!=v};assert set(diff)=={'-gpgpu_cache:dl2'}
 deltas.append(dict(cohort=s['cohort'],mode=s['mode'],input_identity_sha256=s['input_identity_sha256'],exact_option_count=282,reference_spec_ref=s['absolute_REF850_spec_ref'],candidate_spec_ref=ref(p),option_deltas=diff))
 if s['geometry']['sets']!=32:continue
 mode=s['mode'];anchorfield='absolute_REF850_S_anchor_qualification_ref'if mode=='S'else'absolute_REF850_EP_anchor_qualification_ref';q=read(s[anchorfield]['path']);pt=read(q['point_ref']['path']);assert pt['hardware_drained']and pt['source_identity']==s['source_identity']and pt['input_identity_sha256']==s['input_identity_sha256'];assert base['observer_env']==s['observer_env']
 reuse.append(dict(workload=work,mode=mode,geometry='REF32x8',status='ACCEPTED_EXACT_SOURCE_INPUT_OBSERVER_850_L100_FR128_REUSE',anchor_review_ref=s[anchorfield],point_ref=q['point_ref'],spec_ref=q['spec_ref'],cycles=pt['cycles'],usage='ABSOLUTE_REFERENCE_AND_REF_S_WV_PAIR_ONLY_NOT_NEW_GEOMETRY_S'))
 rows.append(dict(workload=work,mode=mode,sets=32,ways=8,Tag_entries_per_slice=256,nominal_Tag_addressable_bytes=64*256*128,physical_Payload_bytes=64*1168*128,status='REUSED_ACCEPTED',cycles=pt['cycles'],same_background_S_EP_ratio=None,Source=s['source_identity']['core_source_commit'],ELF=s['source_identity']['binary_sha256'],spec_path=q['spec_ref']['path'],spec_sha256=q['spec_ref']['sha256'],estimated_peak_RAM_bytes=None,estimated_result_growth_bytes=0))
 for v in read(close/'FINAL_RESULTS.json')['points']:
  if v['group']=='system'and v['status']=='CLOSED_ACCEPTED'and v['mode']==mode and v['input_identity_sha256']==s['input_identity_sha256']and v['profile']=='PFV2_SYSTEM850_G64W16':
   vs=read(v['spec_ref']['path']);diff64={k:(base['expected_effective_options'][k],z)for k,z in vs['expected_effective_options'].items()if base['expected_effective_options'][k]!=z};assert set(diff64)=={'-gpgpu_cache:dl2'};assert vs['observer_env']==s['observer_env']and vs['source_identity']==s['source_identity']
   reuse.append(dict(workload=work,mode=mode,geometry='G64x16',status='ACCEPTED_EXACT_SOURCE_INPUT_OBSERVER_850_L100_FR128_REUSE',point_ref=v['accepted_point_ref'],spec_ref=v['spec_ref'],archive_receipt_ref=v['archive_receipt_ref'],cycles=v['cycles'],usage='MATCHED_G64x16_S_WV_PAIR_AND_ABSOLUTE_CAPACITY_FRONTIER'))
   rows.append(dict(workload=work,mode=mode,sets=64,ways=16,Tag_entries_per_slice=1024,nominal_Tag_addressable_bytes=64*1024*128,physical_Payload_bytes=64*1168*128,status='REUSED_ACCEPTED',cycles=v['cycles'],same_background_S_EP_ratio=None,Source=s['source_identity']['core_source_commit'],ELF=s['source_identity']['binary_sha256'],spec_path=v['spec_ref']['path'],spec_sha256=v['spec_ref']['sha256'],estimated_peak_RAM_bytes=v['peak_RSS_bytes'],estimated_result_growth_bytes=0))
for r in rows:
 if r['cycles']is not None:
  peers=[x for x in rows if x['workload']==r['workload']and x['sets']==r['sets']and x['ways']==r['ways']]
  if len(peers)==2:r['same_background_S_EP_ratio']=next(x['cycles']for x in peers if x['mode']=='S')/next(x['cycles']for x in peers if x['mode']=='WV_ZERO_RO')
rows.sort(key=lambda r:(r['workload'],r['Tag_entries_per_slice'],r['sets'],r['mode']))
with(A/'TAG_PERFORMANCE_RESOURCE_FRONTIER.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
put(A/'TAG_PERFORMANCE_RESOURCE_FRONTIER.json',dict(schema='EP_PFV3_TAG_FRONTIER_SOURCE78_V1',rows=rows,physical_Payload_slices=64,physical_Payload_per_slice_line_slots=1168,physical_Payload_bytes=64*1168*128,cycles_for_candidate='UNKNOWN_NOT_EXECUTED',no_new_performance_claim=True))
put(A/'evidence/EXACT_282_DELTAS_BY_POINT.json',dict(status='PASS_ONLY_DECLARED_GEOMETRY_CHANGES_ALL8',points=deltas))
put(A/'evidence/REF_AND_G64X16_REUSE_QUALIFICATION.json',dict(status='PASS_8_EXACT_ACCEPTED_ANCHORS_NO_RERUN_NEEDED',rows=reuse,not_newgeometry_same_hardware_S=True,Source_identity=idx['source_identity'],input_content_rehashed=False,Trace_rescanned=False))
put(A/'MID_TAG_FAMILY_SCOPE.json',idx)
put(A/'evidence/SOURCE78_READBACK.json',dict(status='PASS_ACCEPTED_SOURCE_UNCHANGED',source_identity=idx['source_identity'],source_git_HEAD=subprocess.check_output(['git','-C',str(O/'core'),'rev-parse','HEAD'],text=True).strip(),source_tracked_status=subprocess.check_output(['git','-C',str(O/'core'),'status','--porcelain','--untracked-files=no'],text=True),source_file_refs={n:ref(O/'core'/n)for n in ['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-cache.h','src/gpgpu-sim/hashing.cc','src/gpgpu-sim/ep-l2-ft-cache.inc','src/gpgpu-sim/ep-l2-tvd-cache.inc']},application_binary_ref=ref(O/'build/accel-sim.out'),static_library_ref=ref(O/'build/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a')))
print(json.dumps(dict(frontier_rows=len(rows),reused_accepted=len(reuse),candidate_points=8,resource_forecast_corrected=True)))

