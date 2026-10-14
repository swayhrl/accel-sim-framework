"""Archive completed legal evidence only; large assets and wheels stay private."""
import datetime,hashlib,json,pathlib,re,shutil,statistics,subprocess
from control import ROOT,WORK,state,check,allocated
OUT=WORK/'docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1'
def load(name):return json.loads((ROOT/name).read_text())
def sanitize(obj):
 if isinstance(obj,str):
  obj=obj.replace(str(ROOT),'<TASK_ROOT>').replace(str(WORK),'<WORKTREE>')
  obj=re.sub(r'/home/[^/\s"<>]+(?:/[^\s"<>]*)?','<PRIVATE_HOME_PATH>',obj)
  obj=obj.replace('/data/c16/env/cpython-3.10.12','<READONLY_BASE_CPYTHON>').replace('/data/c16/env/build-deps-cpython310','<READONLY_BASE_BUILD_LIB>')
  return obj
 if isinstance(obj,list):return [sanitize(x) for x in obj]
 if isinstance(obj,dict):return {k:sanitize(v) for k,v in obj.items()}
 return obj
def write(name,obj):(OUT/name).write_text(json.dumps(sanitize(obj),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def copyjson(dst,src):write(dst,load(src))
def rawcopy(src,dst):
 data=sanitize(src.read_text(errors='replace'));assert not re.search(r'/home/[^/ ]+|https?://10\.[0-9]+\.[0-9]+\.[0-9]+',data)
 target=OUT/dst;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(data,encoding='utf-8')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 assert (ROOT/'verified_late_native_supervisor_receipt.json').exists(),'final native stage has not closed'
 s=state();summary=load('native_measurement_summary.json')
 copyjson('TAR_SCAN_SAFETY.json','tar_scan_safety.json')
 write('SOURCE_PROVENANCE.json',{'original_stop_commit':'e760f332ed41c609d3d19548f87d90b3f11357d8','coord_commit':'b268bfa55390a67dad496d3ba71b31eac9aff2a2','author':'SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932','fixed_source_receipts':load('software_source_receipts.json'),'source_cache_identity':load('source_identity.json'),'source_math_not_patched':True})
 write('ASSET_MANIFEST.json',{'status':'REAL_SCENE_BYTE_AND_AUTHOR_PREPROCESS_QUALIFIED','archive':load('rubble-pixsfm.tgz.download.json'),'raw_files':load('extracted_asset_files.json'),'colmap':load('colmap_identity.json'),'derived_images':load('derived_image_manifest.json'),'unused_forward_metadata_not_changed':True})
 write('COLMAP_TRANSFER.json',{'camera_canary':load('colmap/camera_receipt.json'),'large_files':load('colmap_transfer_verified.json')})
 write('HTTP_DOWNLOAD.json',{'http_requests':[json.loads(x) for x in (ROOT/'http_receipts.jsonl').read_text().splitlines()],'parallel_archive_ranges':[json.loads(x) for x in (ROOT/'parallel_range_receipts.jsonl').read_text().splitlines()],'wheel_receipts':load('wheel_download_receipts.json'),'metric_weight':load('alexnet-owt-7be5be79.pth.download.json'),'interrupted_inflight_upper_charge_bytes':s.get('interrupted_http_conservative_charged_bytes',0),'controller_download_and_relay_counted':True})
 write('ENV_LOCK.json',{'qualified_environment':load('environment_qualified.json'),'locked_distributions':load('distribution_closure.json'),'platform_repairs':load('wheel_platform_fixes.json'),'core_filename_repairs':load('core_wheel_filename_fix.json'),'offline_install_check':load('offline_install_receipt.json'),'metric_evaluator_only':load('metric_weight_preflight.json')})
 write('BUILD_AND_THREAD.json',{'build_stage':load('build_and_thread_status.json'),'CPU_canary_preregister':load('cpu_adam_canary_preregister.json'),'actual_CPU_canary':load('cpu_adam_canary_receipt.json'),'original_64_threads_unchanged':True,'effective_policy':'OMP_THREAD_LIMIT=16, Torch/BLAS=1; DataLoader=4 as author source','original_core_versions_retained':True})
 quality={}
 for arm in ['host_wall','gpu_wall','host_diag','host_late','host_late_verified']:
  folder=ROOT/'native'/arm
  if (folder/'functional_quality.json').exists():quality[arm]=json.loads((folder/'functional_quality.json').read_text())
 write('NATIVE_FUNCTIONAL_QUALITY.json',{'status':'REAL_EARLY_FUNCTIONAL_PASS','arms':quality,'not_claimed':['bitwise algorithm equivalence','200k convergence quality','matched long time-to-PSNR'],'late_loss_numeric_monitor':'finite source loss description enforced in corrected replay; source parameters/input unmodified'})
 copyjson('MEASUREMENT_WINDOWS.json','native_measurement_summary.json')
 receipts=[load(x) for x in ['build_and_thread_status.json','native_attempt1/native_supervisor_receipt.json','native_supervisor_receipt.json','late_native_supervisor_receipt.json','verified_late_native_supervisor_receipt.json']]
 samples=[]
 for name in ['native_attempt1/native_resource_samples.json','native_resource_samples.json','late_native_resource_samples.json','verified_late_native_resource_samples.json']:
  if (ROOT/name).exists():samples+=load(name)
 latest=check()
 write('BUDGET_CUMULATIVE.json',{'limits':{'download_bytes':25*1024**3,'new_disk_bytes':60*1024**3,'filesystem_min_free_bytes':64*1024**3,'host_rss_bytes':48*1024**3,'CPU_effective_threads':24,'CPU_prepare_seconds':14400,'GPU_lock_seconds':7200,'GPU_process_bytes':14*1024**3},'prior_A26G':{'download_bytes':s['prior_http_bytes'],'CPU_prepare_seconds':s['prior_cpu_prepare_seconds'],'disk_conservative_bytes':s['prior_disk_conservative_bytes'],'GPU_lock_seconds':s['prior_gpu_lock_seconds']},'cumulative_http_accounted_upper_bytes':s['prior_http_bytes']+s['http_new_body_bytes']+s['controller_relay_bytes'],'uncertain_interrupted_range_body_upper_bytes':s.get('interrupted_http_conservative_charged_bytes',0),'controller_relay_bytes':s['controller_relay_bytes'],'task_all_new_disk_conservative_bytes':latest['task_allocated_bytes_conservative'],'filesystem_free_at_closeout_bytes':latest['free_bytes'],'cpu_prepare_cumulative_seconds':s['cpu_prepare_cumulative_at_qualification'],'excluded_requested_pause_idle_seconds':s['excluded_user_pause_idle_seconds'],'gpu_lock_cumulative_seconds':s['prior_gpu_lock_seconds']+s['new_gpu_lock_seconds'],'GPU_process_peak_sampled_mib':max((x.get('gpu_peak_sampled_mib',0) for x in receipts),default=0),'Torch_peak_allocated_reserved_by_arm':{arm:json.loads((ROOT/'native'/arm/'completed.json').read_text()) for arm in quality if (ROOT/'native'/arm/'completed.json').exists()},'host_process_tree_peak_rss_bytes':max((x.get('rss_bytes',0) for x in samples),default=0),'effective_running_threads_sampled_max':max((x.get('effective_running_threads',0) for x in samples),default=0),'GPU_sampling_interval_seconds':.5,'sampling_limit':'discrete samples plus 13GiB Torch allocator cap/1GiB context allowance; no instantaneous perfect peak claim','all_stage_lock_receipts':receipts,'no_budget_reset':True})
 write('GATES.json',{'R0':{'status':'PASS','source_resources_and_official_distribution_closure':True},'R1':{'status':'PASS','bounded_full_archive_scan_extract':True,'official_COLMAP_all_consumed_tracks_valid':True,'unused_forward_ID_anomaly_disclosed':6,'author_pixel_byte_replay_verified':True},'R2':{'status':'PASS','original_versions_and_source_builds':True,'CPUAdam_actual_limit_and_numeric_canary':True},'R3':{'status':'PASS_SCOPED_NATIVE_QUALIFICATION_AND_OBSERVATION','actual_reached_stage':'REAL_CONTINUOUS_STEP_15200','long_converged_quality':'NOT_EVALUATED','hardware_resource_causality':'NOT_QUALIFIED'},'R4':{'status':'PARTIAL','archive_ready':True,'publication':'pending commit/push/readback'}})
 write('ENGINEERING_RECEIPTS.json',{'download_strategy':load('download_strategy_change.json'),'input_reader_extra_constraint_fix':load('colmap_reader_engineering_fix.json'),'unused_feature_forward_ID_policy':'frozen author Parser consumes reverse point tracks; no input correction/removal','wrapper_module_cfg_fix':load('native_wrapper_fix.json'),'observer_direction_fix':load('observer_direction_fix.json'),'late_admission':load('late_window_admission.json'),'verification_replay_admission':load('observer_verification_replay_admission.json'),'pause_resume_accounting':load('resume_receipt.json'),'archive_safety_tests':load('engineering_safety_tests.json'),'ordinary_fixes_did_not_change_science':True})
 raw=OUT/'raw';raw.mkdir(exist_ok=True)
 for arm in quality:
  folder=ROOT/'native'/arm
  for f in folder.glob('*.json*'):rawcopy(f,pathlib.Path('raw')/arm/f.name)
 for name in ['native_attempt1/native_supervisor_receipt.json','native_supervisor_receipt.json','late_native_supervisor_receipt.json','verified_late_native_supervisor_receipt.json','native_resource_samples.json','late_native_resource_samples.json','verified_late_native_resource_samples.json']:
  if (ROOT/name).exists():copyjson('raw/'+name.replace('/','_'),name)
 for name in ['cpu_adam_build.log','fused_ssim_build.log','gsscale_build.log','native_attempt1/host_wall_native.log','native_supervisor_retry.log','late_native_supervisor.log','verified_late_native_supervisor.log']:
  if (ROOT/name).exists():rawcopy(ROOT/name,pathlib.Path('raw')/name.replace('/','_'))
 old=[]
 for suffix,head in [('a26g-gsscale-rubble-gated-native-109-v1','e760f332ed41c609d3d19548f87d90b3f11357d8'),('a16r1-greencontext-109-v1','6953ac1690b7a905b6000833a879f9164c7c9e43'),('nequip-static-batch-109-v1r1','1f69559df4f51290589de72876f36a756c5439f0')]:
  w=WORK.parent/('accel-sim-aiarch-'+suffix);actual=subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip();clean=not subprocess.check_output(['git','-C',str(w),'status','--porcelain'],text=True).strip();assert actual==head and clean;old.append({'task':suffix,'head':actual,'clean':clean})
 write('OLD_BRANCH_PRESERVATION.json',{'old_worktrees':old,'AWMA_C16_not_run_or_changed':True,'original_A26G_21_files_in_new_tree_unchanged':not subprocess.check_output(['git','diff','--name-only','e760f332ed41c609d3d19548f87d90b3f11357d8','--','docs/ai_workload_research/runs/AI_ARCH_A26G_GSSCALE_RUBBLE_109_V1','tools/aiarch_a26g'],text=True).strip()})
 print('ARCHIVE_READY',len(list(OUT.rglob('*'))),'BUDGET',latest)
if __name__=='__main__':main()
